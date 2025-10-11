"""
Advanced RAG Experiments with Hybrid Search & Reranking
========================================================

This script implements state-of-the-art RAG techniques to achieve 60%+ accuracy:
1. Better embedding models (all-mpnet-base-v2)
2. Hybrid search (semantic + BM25)
3. Cross-encoder reranking
4. Optimized Top-K retrieval

Author: ManualAi Team
Date: October 2025
"""

import json
import time
import os
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

# Import from existing codebase
import sys
sys.path.insert(0, str(Path(__file__).parent))
from document_loader import _load_pdf_fast, _enrich_metadata


# ============================================================================
# Configuration
# ============================================================================

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
PDF_PATH = DATA_DIR / "2023-Toyota-4runner-Manual.pdf"
EVAL_SET_PATH = DATA_DIR / "evaluation_set.json"

# Model Configuration
EMBEDDING_MODEL = "all-mpnet-base-v2"  # Better than MiniLM (768 dims)
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"  # Fast reranker

# Retrieval Configuration - OPTIMIZED FOR 60%+ ACCURACY
INITIAL_TOP_K = 40  # Retrieve MORE candidates for better reranking
FINAL_TOP_K = 8     # After reranking, use more top chunks for voting
BM25_WEIGHT = 0.4   # Increase keyword weight (40% BM25, 60% semantic)

# Chunking strategies to test - LARGER CHUNKS FOR BETTER CONTEXT
STRATEGIES = [
    {"name": "Large Chunks", "chunk_size": 1200, "chunk_overlap": 250},
    {"name": "Very Large Chunks", "chunk_size": 1600, "chunk_overlap": 400},
    {"name": "Extra Large Chunks", "chunk_size": 2000, "chunk_overlap": 500},
    {"name": "Mega Chunks", "chunk_size": 2400, "chunk_overlap": 600},
    {"name": "Ultra Chunks", "chunk_size": 3000, "chunk_overlap": 750},
]


# ============================================================================
# STEP 1: BM25 Implementation (Keyword Search Component)
# ============================================================================

class SimpleBM25:
    """
    Simple BM25 implementation for keyword-based retrieval.
    BM25 is a probabilistic ranking function used by search engines.
    """
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Args:
            k1: Controls term saturation (typically 1.2 to 2.0)
            b: Controls length normalization (typically 0.75)
        """
        self.k1 = k1
        self.b = b
        self.corpus = []
        self.doc_lengths = []
        self.avgdl = 0
        self.doc_freqs = []
        self.idf = {}
        
    def fit(self, corpus: List[str]):
        """Build BM25 index from corpus."""
        self.corpus = corpus
        self.doc_lengths = [len(doc.split()) for doc in corpus]
        self.avgdl = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0
        
        # Calculate document frequencies
        df = Counter()
        for doc in corpus:
            words = set(doc.lower().split())
            for word in words:
                df[word] += 1
        
        # Calculate IDF (inverse document frequency)
        num_docs = len(corpus)
        for word, freq in df.items():
            self.idf[word] = max(0.01, (num_docs - freq + 0.5) / (freq + 0.5))
    
    def search(self, query: str, top_k: int = 20) -> List[Tuple[int, float]]:
        """
        Search for most relevant documents.
        
        Returns:
            List of (doc_index, score) tuples
        """
        query_words = query.lower().split()
        scores = []
        
        for idx, doc in enumerate(self.corpus):
            doc_words = doc.lower().split()
            doc_len = self.doc_lengths[idx]
            score = 0
            
            for word in query_words:
                if word not in self.idf:
                    continue
                    
                # Count term frequency in document
                tf = doc_words.count(word)
                
                # BM25 formula
                idf = self.idf[word]
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)
                score += idf * (numerator / denominator)
            
            scores.append((idx, score))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


# ============================================================================
# STEP 2: Hybrid Retriever (Semantic + BM25 + Reranking)
# ============================================================================

class HybridRAGRetriever:
    """
    Advanced RAG retriever combining:
    1. Semantic search (dense embeddings)
    2. BM25 keyword search (sparse)
    3. Cross-encoder reranking
    """
    
    def __init__(
        self,
        embedding_model_name: str = EMBEDDING_MODEL,
        reranker_model_name: str = RERANKER_MODEL,
        bm25_weight: float = BM25_WEIGHT
    ):
        """Initialize hybrid retriever."""
        self.embedding_model_name = embedding_model_name
        self.reranker_model_name = reranker_model_name
        self.bm25_weight = bm25_weight
        self.semantic_weight = 1.0 - bm25_weight
        
        self.embedding_model = None
        self.reranker = None
        self.bm25 = None
        self.chroma_client = None
        self.collection = None
        self.chunks = []
    
    def index_chunks(self, chunks: List[Document]):
        """Index chunks for hybrid retrieval."""
        self.chunks = chunks
        chunk_texts = [doc.page_content for doc in chunks]
        
        print(f"  Loading embedding model: {self.embedding_model_name}...")
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        print(f"  ✓ Embedding model loaded ({embedding_dim} dimensions)")
        
        print(f"  Loading reranker: {self.reranker_model_name}...")
        self.reranker = CrossEncoder(self.reranker_model_name)
        print(f"  ✓ Reranker loaded")
        
        # Index with ChromaDB (semantic search)
        print(f"  Indexing {len(chunks)} chunks into ChromaDB...")
        self.chroma_client = chromadb.Client(Settings(anonymized_telemetry=False))
        
        # Delete existing collection if it exists
        try:
            self.chroma_client.delete_collection("rag_chunks")
        except:
            pass
        
        self.collection = self.chroma_client.create_collection(
            name="rag_chunks",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Batch embed and index
        batch_size = 32
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i+batch_size]
            batch_texts = [doc.page_content for doc in batch_chunks]
            batch_ids = [f"chunk_{i+j}" for j in range(len(batch_chunks))]
            batch_metadatas = [
                {"page": doc.metadata.get("page", -1)} 
                for doc in batch_chunks
            ]
            
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
        
        print(f"  ✓ Indexed {len(chunks)} chunks in ChromaDB")
        
        # Build BM25 index (keyword search)
        print(f"  Building BM25 index...")
        self.bm25 = SimpleBM25()
        self.bm25.fit(chunk_texts)
        print(f"  ✓ BM25 index built")
    
    def retrieve(
        self,
        question: str,
        initial_top_k: int = INITIAL_TOP_K,
        final_top_k: int = FINAL_TOP_K
    ) -> List[Tuple[str, int]]:
        """
        Hybrid retrieval with reranking.
        
        Steps:
        1. Semantic search: Get top candidates from ChromaDB
        2. BM25 search: Get top candidates from BM25
        3. Fusion: Combine scores with weights
        4. Rerank: Use cross-encoder to rerank combined results
        
        Returns:
            List of (chunk_text, page_number) tuples
        """
        # Step 1: Semantic search
        query_embedding = self.embedding_model.encode(
            [question],
            show_progress_bar=False,
            convert_to_numpy=True
        )[0].tolist()
        
        semantic_results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=initial_top_k
        )
        
        # Extract results
        semantic_docs = {}  # chunk_idx -> score
        if semantic_results['ids'] and semantic_results['ids'][0]:
            for idx, chunk_id, distance in zip(
                range(len(semantic_results['ids'][0])),
                semantic_results['ids'][0],
                semantic_results['distances'][0]
            ):
                chunk_idx = int(chunk_id.split('_')[1])
                # Convert distance to similarity (lower distance = higher similarity)
                similarity = 1.0 - distance
                semantic_docs[chunk_idx] = similarity
        
        # Step 2: BM25 search
        bm25_results = self.bm25.search(question, top_k=initial_top_k)
        bm25_docs = {idx: score for idx, score in bm25_results}
        
        # Step 3: Hybrid fusion (combine scores)
        # Normalize scores to [0, 1]
        max_semantic = max(semantic_docs.values()) if semantic_docs else 1.0
        max_bm25 = max(bm25_docs.values()) if bm25_docs else 1.0
        
        combined_scores = {}
        all_indices = set(semantic_docs.keys()) | set(bm25_docs.keys())
        
        for idx in all_indices:
            semantic_score = semantic_docs.get(idx, 0) / max_semantic
            bm25_score = bm25_docs.get(idx, 0) / max_bm25
            
            # Weighted combination
            combined_scores[idx] = (
                self.semantic_weight * semantic_score +
                self.bm25_weight * bm25_score
            )
        
        # Get top candidates for reranking
        top_candidates = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:initial_top_k]
        
        # Step 4: Rerank with cross-encoder
        if not top_candidates:
            return []
        
        # Prepare pairs for reranking
        pairs = []
        candidate_indices = []
        for idx, _ in top_candidates:
            pairs.append([question, self.chunks[idx].page_content])
            candidate_indices.append(idx)
        
        # Get reranking scores
        rerank_scores = self.reranker.predict(pairs, show_progress_bar=False)
        
        # Sort by rerank score
        reranked = sorted(
            zip(candidate_indices, rerank_scores),
            key=lambda x: x[1],
            reverse=True
        )[:final_top_k]
        
        # Return top-k after reranking
        results = []
        for idx, score in reranked:
            chunk = self.chunks[idx]
            page = chunk.metadata.get("page", -1)
            results.append((chunk.page_content, page))
        
        return results
    
    def predict_page(self, question: str) -> int:
        """
        Predict the page number for a question.
        Uses majority voting from top-k retrieved chunks.
        """
        retrieved = self.retrieve(question)
        
        if not retrieved:
            return -1
        
        # Count page occurrences
        page_counts = {}
        for _, page in retrieved:
            if page != -1:
                page_counts[page] = page_counts.get(page, 0) + 1
        
        if not page_counts:
            return -1
        
        # Return most common page
        return max(page_counts.items(), key=lambda x: x[1])[0]


# ============================================================================
# STEP 3: Evaluation
# ============================================================================

def create_chunks_with_strategy(
    raw_docs: List[Document],
    chunk_size: int,
    chunk_overlap: int
) -> List[Document]:
    """Create chunks using RecursiveCharacterTextSplitter."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )
    
    chunks = splitter.split_documents(raw_docs)
    
    # Enrich metadata for each chunk
    for chunk in chunks:
        _enrich_metadata(chunk)
    
    return chunks


def evaluate_strategy(
    strategy: Dict,
    raw_docs: List[Document],
    eval_set: List[Dict]
) -> Dict:
    """
    Evaluate one hybrid RAG strategy.
    
    Args:
        strategy: Dict with 'name', 'chunk_size', 'chunk_overlap'
        raw_docs: Raw documents from PDF
        eval_set: List of evaluation questions
    
    Returns:
        Results dictionary with metrics
    """
    print("\n" + "="*70)
    print(f"Testing Strategy: {strategy['name']}")
    print(f"  Chunk Size: {strategy['chunk_size']}")
    print(f"  Overlap: {strategy['chunk_overlap']}")
    print("="*70)
    
    # Create chunks
    print(f"  Creating chunks (size={strategy['chunk_size']}, overlap={strategy['chunk_overlap']})...")
    chunks = create_chunks_with_strategy(
        raw_docs,
        strategy['chunk_size'],
        strategy['chunk_overlap']
    )
    print(f"  ✓ Created {len(chunks)} chunks")
    
    # Initialize hybrid retriever
    retriever = HybridRAGRetriever()
    retriever.index_chunks(chunks)
    
    # Evaluate
    print(f"\n  Evaluating on {len(eval_set)} questions...")
    correct = 0
    total = 0
    latencies = []
    predictions = []
    
    for i, item in enumerate(eval_set):
        question = item["question"]
        ground_truth = item["correct_page_number"]
        
        # Measure latency
        start = time.time()
        predicted_page = retriever.predict_page(question)
        latency = time.time() - start
        
        latencies.append(latency)
        is_correct = (predicted_page == ground_truth)
        
        if is_correct:
            correct += 1
        
        total += 1
        
        predictions.append({
            "id": item["id"],
            "question": question,
            "ground_truth": ground_truth,
            "predicted": predicted_page,
            "correct": is_correct,
            "latency": latency
        })
        
        # Progress update every 10 questions
        if (i + 1) % 10 == 0:
            print(f"    Progress: {i+1}/{len(eval_set)} questions ({correct}/{i+1} correct so far)")
    
    accuracy = (correct / total * 100) if total > 0 else 0
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    
    print(f"\n  ✓ Evaluation complete!")
    print(f"    Accuracy: {accuracy:.1f}% ({correct}/{total})")
    print(f"    Avg Latency: {avg_latency:.3f}s")
    
    return {
        "strategy_name": strategy['name'],
        "chunk_size": strategy['chunk_size'],
        "chunk_overlap": strategy['chunk_overlap'],
        "num_chunks": len(chunks),
        "accuracy": accuracy,
        "correct": correct,
        "total": total,
        "avg_latency": avg_latency,
        "predictions": predictions
    }


# ============================================================================
# STEP 4: Run All Experiments
# ============================================================================

def run_all_advanced_experiments():
    """Run all advanced RAG experiments with hybrid search and reranking."""
    print("\n" + "="*70)
    print("ADVANCED RAG EXPERIMENTS")
    print("Hybrid Search (Semantic + BM25) + Cross-Encoder Reranking")
    print("="*70)
    print(f"PDF: {PDF_PATH}")
    print(f"Evaluation Set: {EVAL_SET_PATH}")
    print(f"Embedding Model: {EMBEDDING_MODEL}")
    print(f"Reranker: {RERANKER_MODEL}")
    print(f"Hybrid Weights: {int((1-BM25_WEIGHT)*100)}% semantic, {int(BM25_WEIGHT*100)}% BM25")
    print(f"Initial Top-K: {INITIAL_TOP_K}, Final Top-K: {FINAL_TOP_K}")
    print("="*70 + "\n")
    
    # Load PDF once
    print("Loading PDF...")
    raw_docs = _load_pdf_fast(str(PDF_PATH))
    print(f"✓ Loaded {len(raw_docs)} pages\n")
    
    # Load evaluation set
    print("Loading evaluation set...")
    with open(EVAL_SET_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if isinstance(data, dict) and "questions" in data:
            eval_set = data["questions"]
        else:
            eval_set = data
    print(f"✓ Loaded {len(eval_set)} questions\n")
    
    # Run experiments
    all_results = []
    for strategy in STRATEGIES:
        try:
            result = evaluate_strategy(strategy, raw_docs, eval_set)
            all_results.append(result)
        except Exception as e:
            print(f"\n❌ ERROR during {strategy['name']}: {e}")
            import traceback
            traceback.print_exc()
    
    # Save results
    output_path = Path(__file__).parent / "rag_results_advanced.json"
    results_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "config": {
            "embedding_model": EMBEDDING_MODEL,
            "reranker_model": RERANKER_MODEL,
            "initial_top_k": INITIAL_TOP_K,
            "final_top_k": FINAL_TOP_K,
            "bm25_weight": BM25_WEIGHT,
            "semantic_weight": 1.0 - BM25_WEIGHT
        },
        "results": all_results
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results_data, f, indent=2)
    
    print("\n" + "="*70)
    print(f"✓ Results saved to: {output_path}")
    print("="*70 + "\n")
    
    # Print summary
    print("SUMMARY OF RESULTS:")
    print("-"*70)
    print(f"{'Strategy':<25} {'Chunks':<10} {'Accuracy':<12} {'Latency':<10}")
    print("-"*70)
    
    best_accuracy = 0
    best_strategy = None
    
    for result in all_results:
        print(f"{result['strategy_name']:<25} {result['num_chunks']:<10} "
              f"{result['accuracy']:>6.1f}%      {result['avg_latency']:.3f}s")
        
        if result['accuracy'] > best_accuracy:
            best_accuracy = result['accuracy']
            best_strategy = result
    
    print("-"*70)
    
    if best_strategy:
        print(f"\n🏆 BEST STRATEGY: {best_strategy['strategy_name']}")
        print(f"   Accuracy: {best_strategy['accuracy']:.1f}%")
        print(f"   Chunks: {best_strategy['num_chunks']}")
        print(f"   Latency: {best_strategy['avg_latency']:.4f}s")
        
        print(f"\n📊 IMPROVEMENT OVER PREVIOUS METHODS:")
        print(f"   Keyword Baseline: 8% accuracy")
        print(f"   Basic Semantic (MiniLM): 26% accuracy")
        print(f"   Advanced Hybrid: {best_strategy['accuracy']:.1f}% accuracy")
        print(f"   Improvement over baseline: {best_strategy['accuracy'] - 8:.1f} percentage points")
        print(f"   Improvement over basic: {best_strategy['accuracy'] - 26:.1f} percentage points")
    
    print(f"\n✅ Advanced RAG experiments completed!")
    print(f"   Check {output_path} for detailed results.")


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    try:
        run_all_advanced_experiments()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
