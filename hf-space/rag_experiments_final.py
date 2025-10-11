"""
FINAL OPTIMIZED RAG - Target: 70%+ with ±2 pages
===================================================

Advanced improvements:
1. Section-Aware Retrieval - Boost relevant manual sections
2. Negative Filtering - Remove table of contents/index confusion
3. Question Type Classification - Adaptive strategies
4. Multi-pass Reranking - Double-check top results
5. Confidence-based Voting - Weight by retrieval confidence

Author: ManualAi Team
Date: October 2025
"""

import json
import time
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
from collections import Counter

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer, CrossEncoder
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Set HuggingFace token
# HF_TOKEN should be set as environment variable
# HUGGING_FACE_HUB_TOKEN should be set as environment variable

import sys
sys.path.insert(0, str(Path(__file__).parent))
from document_loader import _load_pdf_fast, _enrich_metadata


# ============================================================================
# Configuration
# ============================================================================

DATA_DIR = Path(__file__).parent.parent / "data"
PDF_PATH = DATA_DIR / "2023-Toyota-4runner-Manual.pdf"
EVAL_SET_PATH = DATA_DIR / "evaluation_set.json"

EMBEDDING_MODEL = "all-mpnet-base-v2"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Optimal settings from testing
INITIAL_TOP_K = 70
FINAL_TOP_K = 15
BM25_WEIGHT = 0.25  # More semantic
CHUNK_SIZE = 3000
CHUNK_OVERLAP = 900

# Section ranges in Toyota 4Runner manual
WARNING_LIGHTS_SECTION = (475, 495)  # Warning lights and messages
SAFETY_SECTION = (1, 100)  # Safety precautions
MAINTENANCE_SECTION = (400, 450)  # Maintenance
TROUBLESHOOTING_SECTION = (500, 600)  # Troubleshooting

# Pages to filter out (TOC, index, etc.)
EXCLUDED_PAGES = set(range(1, 30)) | set(range(580, 608))  # TOC and Index


# ============================================================================
# Question Classification
# ============================================================================

def classify_question(question: str) -> Dict[str, any]:
    """
    Classify question to determine optimal retrieval strategy.
    """
    question_lower = question.lower()
    
    classification = {
        'type': 'general',
        'target_section': None,
        'boost_factor': 1.0,
        'is_warning_light': False,
        'is_safety': False,
        'is_maintenance': False,
        'is_troubleshooting': False
    }
    
    # Warning light/message questions
    warning_keywords = ['warning', 'light', 'message', 'indicator', 'appears', 'displays', 'blinks', 'flashes', 'illuminates']
    if any(kw in question_lower for kw in warning_keywords):
        classification['type'] = 'warning_light'
        classification['target_section'] = WARNING_LIGHTS_SECTION
        classification['boost_factor'] = 2.0
        classification['is_warning_light'] = True
    
    # Safety questions
    safety_keywords = ['airbag', 'srs', 'seatbelt', 'seat belt', 'safety', 'crash', 'collision', 'scrapping', 'dispose']
    if any(kw in question_lower for kw in safety_keywords):
        classification['is_safety'] = True
        if classification['type'] == 'general':
            classification['type'] = 'safety'
            classification['target_section'] = SAFETY_SECTION
    
    # Maintenance questions
    maintenance_keywords = ['fluid', 'oil', 'coolant', 'brake fluid', 'washer', 'tire pressure', 'tpms', 'check', 'refill', 'replace']
    if any(kw in question_lower for kw in maintenance_keywords):
        classification['is_maintenance'] = True
        if classification['type'] == 'general':
            classification['type'] = 'maintenance'
            classification['target_section'] = MAINTENANCE_SECTION
    
    # Troubleshooting questions
    trouble_keywords = ['what should', 'how to fix', 'problem', 'issue', 'malfunction', 'not working', 'stopped']
    if any(kw in question_lower for kw in trouble_keywords):
        classification['is_troubleshooting'] = True
        if classification['type'] == 'general':
            classification['type'] = 'troubleshooting'
            classification['target_section'] = TROUBLESHOOTING_SECTION
    
    return classification


def expand_query(question: str, classification: Dict) -> List[str]:
    """Expand query based on classification."""
    queries = [question]
    
    # Add classification-specific expansions
    if classification['is_warning_light']:
        # Add common warning light terms
        queries.append(f"warning light indicator {question}")
        queries.append(f"dashboard {question}")
    
    # Simplified version
    question_words = ['what', 'when', 'where', 'why', 'how', 'which', 'who', 'does', 'do', 'did', 'is', 'are', 'was', 'were', 'should', 'can', 'could', 'will', 'would']
    simplified = question.lower()
    for qw in question_words:
        simplified = re.sub(r'\b' + qw + r'\b', '', simplified, flags=re.IGNORECASE)
    simplified = re.sub(r'\s+', ' ', simplified).strip()
    if simplified and simplified != question.lower():
        queries.append(simplified)
    
    # Key terms only
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'this', 'that', 'these', 'those', 'you', 'your', 'it', 'its', 'be', 'been', 'being', 'have', 'has', 'had', 'if', 'then'}
    words = re.findall(r'\b\w+\b', question.lower())
    key_terms = ' '.join([w for w in words if w not in stop_words and len(w) > 2])
    if key_terms:
        queries.append(key_terms)
    
    return queries[:3]  # Limit to top 3 variations


# ============================================================================
# Enhanced BM25
# ============================================================================

class EnhancedBM25:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus = []
        self.doc_lengths = []
        self.avgdl = 0
        self.tokenized_corpus = []
        self.idf = {}
        
    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        return [t for t in text.split() if len(t) > 1]
    
    def fit(self, corpus: List[str]):
        self.corpus = corpus
        self.tokenized_corpus = [self._tokenize(doc) for doc in corpus]
        self.doc_lengths = [len(doc) for doc in self.tokenized_corpus]
        self.avgdl = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0
        
        df = Counter()
        for doc in self.tokenized_corpus:
            for token in set(doc):
                df[token] += 1
        
        num_docs = len(self.tokenized_corpus)
        for token, freq in df.items():
            self.idf[token] = max(0.01, (num_docs - freq + 0.5) / (freq + 0.5))
    
    def search(self, query: str, top_k: int = 70) -> List[Tuple[int, float]]:
        query_tokens = self._tokenize(query)
        scores = []
        
        for idx, doc_tokens in enumerate(self.tokenized_corpus):
            doc_len = self.doc_lengths[idx]
            score = 0
            
            for token in query_tokens:
                if token not in self.idf:
                    continue
                tf = doc_tokens.count(token)
                idf = self.idf[token]
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)
                score += idf * (numerator / denominator)
            
            scores.append((idx, score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


# ============================================================================
# Final Optimized RAG Retriever
# ============================================================================

class FinalOptimizedRAG:
    def __init__(self):
        self.embedding_model = None
        self.reranker = None
        self.bm25 = None
        self.chroma_client = None
        self.collection = None
        self.chunks = []
        self.page_map = {}
    
    def index_chunks(self, chunks: List[Document]):
        self.chunks = chunks
        chunk_texts = [doc.page_content for doc in chunks]
        
        for idx, doc in enumerate(chunks):
            self.page_map[idx] = doc.metadata.get("page", -1)
        
        print(f"  Loading models...")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        self.reranker = CrossEncoder(RERANKER_MODEL)
        print(f"  ✓ Models loaded")
        
        print(f"  Indexing {len(chunks)} chunks...")
        self.chroma_client = chromadb.Client(Settings(anonymized_telemetry=False))
        
        try:
            self.chroma_client.delete_collection("final_rag")
        except:
            pass
        
        self.collection = self.chroma_client.create_collection(
            name="final_rag",
            metadata={"hnsw:space": "cosine"}
        )
        
        batch_size = 32
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i+batch_size]
            batch_texts = [doc.page_content for doc in batch_chunks]
            batch_ids = [f"chunk_{i+j}" for j in range(len(batch_chunks))]
            batch_metadatas = [{"page": doc.metadata.get("page", -1)} for doc in batch_chunks]
            
            embeddings = self.embedding_model.encode(
                batch_texts,
                show_progress_bar=False,
                convert_to_numpy=True
            ).tolist()
            
            self.collection.add(
                embeddings=embeddings,
                documents=batch_texts,
                ids=batch_ids,
                metadatas=batch_metadatas
            )
        
        self.bm25 = EnhancedBM25()
        self.bm25.fit(chunk_texts)
        print(f"  ✓ Indexing complete")
    
    def retrieve_adaptive(self, question: str, classification: Dict) -> List[Tuple[str, int, float]]:
        """Adaptive retrieval based on question classification."""
        query_variations = expand_query(question, classification)
        
        all_candidates = {}
        
        for query_idx, query in enumerate(query_variations):
            query_weight = 1.0 if query_idx == 0 else 0.6
            
            # Semantic search
            query_embedding = self.embedding_model.encode(
                [query],
                show_progress_bar=False,
                convert_to_numpy=True
            )[0].tolist()
            
            semantic_results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=INITIAL_TOP_K
            )
            
            semantic_docs = {}
            if semantic_results['ids'] and semantic_results['ids'][0]:
                for chunk_id, distance in zip(
                    semantic_results['ids'][0],
                    semantic_results['distances'][0]
                ):
                    chunk_idx = int(chunk_id.split('_')[1])
                    similarity = 1.0 - distance
                    semantic_docs[chunk_idx] = similarity
            
            # BM25 search
            bm25_results = self.bm25.search(query, top_k=INITIAL_TOP_K)
            bm25_docs = {idx: score for idx, score in bm25_results}
            
            # Combine with adaptive weighting
            max_semantic = max(semantic_docs.values()) if semantic_docs else 1.0
            max_bm25 = max(bm25_docs.values()) if bm25_docs else 1.0
            
            all_indices = set(semantic_docs.keys()) | set(bm25_docs.keys())
            
            for idx in all_indices:
                page = self.page_map.get(idx, -1)
                
                # Skip excluded pages (TOC, index)
                if page in EXCLUDED_PAGES:
                    continue
                
                semantic_score = semantic_docs.get(idx, 0) / max_semantic
                bm25_score = bm25_docs.get(idx, 0) / max_bm25
                
                combined_score = (
                    (1 - BM25_WEIGHT) * semantic_score +
                    BM25_WEIGHT * bm25_score
                ) * query_weight
                
                # Apply section boost
                if classification['target_section']:
                    section_start, section_end = classification['target_section']
                    if section_start <= page <= section_end:
                        combined_score *= classification['boost_factor']
                
                all_candidates[idx] = all_candidates.get(idx, 0) + combined_score
        
        # Get top candidates
        top_candidates = sorted(
            all_candidates.items(),
            key=lambda x: x[1],
            reverse=True
        )[:INITIAL_TOP_K]
        
        if not top_candidates:
            return []
        
        # Context expansion
        expanded = set()
        for idx, score in top_candidates:
            expanded.add(idx)
            if idx > 0:
                expanded.add(idx - 1)
            if idx < len(self.chunks) - 1:
                expanded.add(idx + 1)
        
        # Multi-pass reranking
        pairs = []
        candidate_indices = []
        for idx in expanded:
            if idx < len(self.chunks):
                page = self.page_map.get(idx, -1)
                if page not in EXCLUDED_PAGES:  # Filter again
                    pairs.append([question, self.chunks[idx].page_content])
                    candidate_indices.append(idx)
        
        if not pairs:
            return []
        
        # First pass reranking
        rerank_scores_1 = self.reranker.predict(pairs, show_progress_bar=False)
        
        # Take top 30 for second pass
        first_pass = sorted(
            zip(candidate_indices, rerank_scores_1),
            key=lambda x: x[1],
            reverse=True
        )[:30]
        
        # Second pass: re-rank with original question + simplified
        if len(query_variations) > 1:
            second_pass_pairs = []
            second_pass_indices = []
            for idx, _ in first_pass:
                # Use both original question and key terms
                combined_query = f"{question} {query_variations[-1]}"
                second_pass_pairs.append([combined_query, self.chunks[idx].page_content])
                second_pass_indices.append(idx)
            
            rerank_scores_2 = self.reranker.predict(second_pass_pairs, show_progress_bar=False)
            final_candidates = list(zip(second_pass_indices, rerank_scores_2))
        else:
            final_candidates = first_pass
        
        # Page-aware boosting
        page_groups = {}
        for idx, score in final_candidates:
            page = self.page_map.get(idx, -1)
            if page not in page_groups:
                page_groups[page] = []
            page_groups[page].append((idx, score))
        
        boosted_scores = []
        for page, chunks_on_page in page_groups.items():
            if len(chunks_on_page) > 1:
                # Strong boost for multiple chunks from same page
                boost = 1.8 if classification['is_warning_light'] else 1.6
                for idx, score in chunks_on_page:
                    boosted_scores.append((idx, score * boost))
            else:
                boosted_scores.extend(chunks_on_page)
        
        # Sort and return
        reranked = sorted(
            boosted_scores,
            key=lambda x: x[1],
            reverse=True
        )[:FINAL_TOP_K]
        
        results = []
        for idx, score in reranked:
            chunk = self.chunks[idx]
            page = chunk.metadata.get("page", -1)
            results.append((chunk.page_content, page, score))
        
        return results
    
    def predict_page(self, question: str) -> int:
        """Predict page with confidence-weighted voting."""
        classification = classify_question(question)
        retrieved = self.retrieve_adaptive(question, classification)
        
        if not retrieved:
            return -1
        
        # Super aggressive weighted voting with confidence
        page_scores = {}
        for rank, (_, page, confidence) in enumerate(retrieved):
            if page != -1:
                # Combine rank weight and confidence
                rank_weight = 4.0 ** (len(retrieved) - rank)
                confidence_weight = (1 + confidence) ** 2  # Quadratic boost for high confidence
                total_weight = rank_weight * confidence_weight
                page_scores[page] = page_scores.get(page, 0) + total_weight
        
        if not page_scores:
            return -1
        
        return max(page_scores.items(), key=lambda x: x[1])[0]


# ============================================================================
# Evaluation
# ============================================================================

def run_final_evaluation():
    print("\n" + "="*70)
    print("FINAL OPTIMIZED RAG - TARGET: 70%+ with ±2 pages")
    print("="*70)
    print(f"Configuration:")
    print(f"  Chunk Size: {CHUNK_SIZE}, Overlap: {CHUNK_OVERLAP}")
    print(f"  Initial Top-K: {INITIAL_TOP_K}, Final Top-K: {FINAL_TOP_K}")
    print(f"  Semantic Weight: {int((1-BM25_WEIGHT)*100)}%, BM25: {int(BM25_WEIGHT*100)}%")
    print(f"  Section-Aware: Yes, Negative Filtering: Yes")
    print(f"  Multi-pass Reranking: Yes")
    print("="*70 + "\n")
    
    print("Loading PDF...")
    raw_docs = _load_pdf_fast(str(PDF_PATH))
    print(f"✓ Loaded {len(raw_docs)} pages\n")
    
    print("Loading evaluation set...")
    with open(EVAL_SET_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        eval_set = data["questions"] if isinstance(data, dict) and "questions" in data else data
    print(f"✓ Loaded {len(eval_set)} questions\n")
    
    print(f"Creating chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = splitter.split_documents(raw_docs)
    for chunk in chunks:
        _enrich_metadata(chunk)
    print(f"✓ Created {len(chunks)} chunks\n")
    
    print("Initializing retriever...")
    retriever = FinalOptimizedRAG()
    retriever.index_chunks(chunks)
    print("✓ Ready\n")
    
    print(f"Evaluating on {len(eval_set)} questions...\n")
    correct_exact = 0
    correct_within_2 = 0
    correct_within_5 = 0
    total = 0
    latencies = []
    predictions = []
    
    for i, item in enumerate(eval_set):
        question = item["question"]
        ground_truth = item["correct_page_number"]
        
        start = time.time()
        predicted_page = retriever.predict_page(question)
        latency = time.time() - start
        
        latencies.append(latency)
        diff = abs(predicted_page - ground_truth)
        
        is_exact = (diff == 0)
        is_within_2 = (diff <= 2)
        is_within_5 = (diff <= 5)
        
        if is_exact:
            correct_exact += 1
        if is_within_2:
            correct_within_2 += 1
        if is_within_5:
            correct_within_5 += 1
        
        total += 1
        
        predictions.append({
            "id": item["id"],
            "question": question,
            "ground_truth": ground_truth,
            "predicted": predicted_page,
            "diff": diff,
            "exact": is_exact,
            "within_2": is_within_2,
            "within_5": is_within_5,
            "latency": latency
        })
        
        if (i + 1) % 10 == 0:
            print(f"  Progress: {i+1}/{len(eval_set)}")
            print(f"    Exact: {correct_exact}/{i+1} ({correct_exact/(i+1)*100:.1f}%)")
            print(f"    ±2: {correct_within_2}/{i+1} ({correct_within_2/(i+1)*100:.1f}%)")
            print(f"    ±5: {correct_within_5}/{i+1} ({correct_within_5/(i+1)*100:.1f}%)")
    
    accuracy_exact = (correct_exact / total * 100) if total > 0 else 0
    accuracy_within_2 = (correct_within_2 / total * 100) if total > 0 else 0
    accuracy_within_5 = (correct_within_5 / total * 100) if total > 0 else 0
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    
    print(f"\n" + "="*70)
    print("FINAL RESULTS:")
    print("="*70)
    print(f"Exact Match (±0):      {correct_exact}/{total} = {accuracy_exact:.1f}%")
    print(f"Close Match (±2):      {correct_within_2}/{total} = {accuracy_within_2:.1f}%")
    print(f"Reasonable Match (±5): {correct_within_5}/{total} = {accuracy_within_5:.1f}%")
    print(f"Avg Latency: {avg_latency:.3f}s")
    print("="*70)
    
    # Save results
    output_path = Path(__file__).parent / "rag_results_final.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "config": {
                "chunk_size": CHUNK_SIZE,
                "chunk_overlap": CHUNK_OVERLAP,
                "initial_top_k": INITIAL_TOP_K,
                "final_top_k": FINAL_TOP_K,
                "bm25_weight": BM25_WEIGHT
            },
            "results": {
                "accuracy_exact": accuracy_exact,
                "accuracy_within_2": accuracy_within_2,
                "accuracy_within_5": accuracy_within_5,
                "correct_exact": correct_exact,
                "correct_within_2": correct_within_2,
                "correct_within_5": correct_within_5,
                "total": total,
                "avg_latency": avg_latency
            },
            "predictions": predictions
        }, f, indent=2)
    
    print(f"\n✓ Saved to: {output_path}\n")
    
    print("="*70)
    print("PROGRESSION:")
    print("="*70)
    print(f"Keyword Baseline:     8%")
    print(f"Basic Semantic:       26%")
    print(f"Advanced Hybrid:      62% (±2)")
    print(f"Ultimate RAG:         64% (±2), 70% (±5)")
    print(f"FINAL OPTIMIZED:      {accuracy_within_2:.1f}% (±2), {accuracy_within_5:.1f}% (±5)")
    print("="*70)
    
    if accuracy_within_2 >= 70:
        print(f"\n🎉🎉🎉 TARGET ACHIEVED! {accuracy_within_2:.1f}% with ±2 pages! 🎉🎉🎉")
    elif accuracy_within_2 >= 65:
        print(f"\n✅ Excellent! {accuracy_within_2:.1f}% with ±2 pages!")
    else:
        print(f"\n📊 Result: {accuracy_within_2:.1f}% with ±2 pages")
    print("="*70)


if __name__ == "__main__":
    try:
        run_final_evaluation()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
