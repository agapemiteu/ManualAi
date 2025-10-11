"""
RAG Experiments with Semantic Embeddings

This script implements proper RAG evaluation using:
- Sentence-transformer embeddings for semantic similarity
- ChromaDB vector store for efficient retrieval
- Multiple chunking strategies tested with REAL semantic search

Expected improvement: 8% (keyword baseline) → 50-70% (semantic RAG)

Author: ManualAi Portfolio Project
Date: 2025-01-09
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Tuple
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Import existing document loader functions
from document_loader import _load_pdf_fast, _enrich_metadata


# ============================================================================
# CONFIGURATION
# ============================================================================

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
PDF_PATH = DATA_DIR / "2023-Toyota-4runner-Manual.pdf"
EVAL_SET_PATH = DATA_DIR / "evaluation_set.json"
RESULTS_PATH = Path(__file__).parent / "rag_results.json"

# Embedding model - using a lightweight, high-quality model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 384 dimensions, fast, good quality

# Chunking strategies to test (same as before, but now with semantic retrieval)
CHUNKING_STRATEGIES = [
    {"name": "Very Small Chunks", "chunk_size": 300, "chunk_overlap": 50},
    {"name": "Small Chunks", "chunk_size": 400, "chunk_overlap": 80},
    {"name": "Medium Chunks", "chunk_size": 800, "chunk_overlap": 150},
    {"name": "Large Chunks", "chunk_size": 1200, "chunk_overlap": 200},
    {"name": "Very Large Chunks", "chunk_size": 1600, "chunk_overlap": 300},
]

# Retrieval parameters
TOP_K = 5  # Number of chunks to retrieve per query


# ============================================================================
# STEP 1: Load and Chunk Documents
# ============================================================================

def create_chunks_with_strategy(
    raw_docs: List[Document],
    chunk_size: int,
    chunk_overlap: int
) -> List[Document]:
    """
    Create chunks using RecursiveCharacterTextSplitter.
    
    Args:
        raw_docs: List of raw documents from PDF
        chunk_size: Target size of each chunk
        chunk_overlap: Number of characters to overlap between chunks
    
    Returns:
        List of chunked documents with enriched metadata
    """
    print(f"  Creating chunks (size={chunk_size}, overlap={chunk_overlap})...")
    
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    # Split documents
    chunks = text_splitter.split_documents(raw_docs)
    
    # Enrich metadata (add page numbers, section info, etc.)
    # _enrich_metadata expects single documents, so we apply it to each chunk
    enriched_chunks = [_enrich_metadata(chunk) for chunk in chunks]
    
    print(f"  ✓ Created {len(enriched_chunks)} chunks")
    return enriched_chunks


# ============================================================================
# STEP 2: Semantic Retrieval with ChromaDB
# ============================================================================

class SemanticRetriever:
    """
    Semantic retriever using sentence-transformers + ChromaDB.
    
    This is REAL RAG - using embeddings to find semantically similar chunks,
    not just keyword matching!
    """
    
    def __init__(self, embedding_model_name: str = EMBEDDING_MODEL):
        """Initialize embedding model and ChromaDB client."""
        print(f"  Loading embedding model: {embedding_model_name}...")
        self.embedding_model = SentenceTransformer(embedding_model_name)
        
        # Create in-memory ChromaDB client for experiments
        self.client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            allow_reset=True
        ))
        
        self.collection = None
        print(f"  ✓ Embedding model loaded ({self.embedding_model.get_sentence_embedding_dimension()} dimensions)")
    
    def index_chunks(self, chunks: List[Document], collection_name: str = "manual_chunks"):
        """
        Index chunks into ChromaDB with embeddings.
        
        Args:
            chunks: List of document chunks to index
            collection_name: Name for the ChromaDB collection
        """
        print(f"  Indexing {len(chunks)} chunks into ChromaDB...")
        
        # Delete existing collection if it exists
        try:
            self.client.delete_collection(collection_name)
        except:
            pass
        
        # Create new collection
        self.collection = self.client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        
        # Prepare data for indexing
        texts = [chunk.page_content for chunk in chunks]
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        
        # Extract page numbers from metadata
        metadatas = []
        for chunk in chunks:
            page = chunk.metadata.get("page", "unknown")
            metadatas.append({"page": str(page)})
        
        # Generate embeddings (in batches to avoid memory issues)
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            batch_metadatas = metadatas[i:i+batch_size]
            
            # Encode texts to embeddings
            embeddings = self.embedding_model.encode(
                batch_texts,
                show_progress_bar=False,
                convert_to_numpy=True
            ).tolist()
            
            # Add to ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=batch_texts,
                ids=batch_ids,
                metadatas=batch_metadatas
            )
        
        print(f"  ✓ Indexed {len(chunks)} chunks")
    
    def retrieve(self, question: str, top_k: int = TOP_K) -> List[Tuple[str, int]]:
        """
        Retrieve top-k most relevant chunks for a question.
        
        Args:
            question: User question
            top_k: Number of chunks to retrieve
        
        Returns:
            List of (chunk_text, page_number) tuples
        """
        if self.collection is None:
            raise ValueError("No collection indexed! Call index_chunks() first.")
        
        # Encode question to embedding
        question_embedding = self.embedding_model.encode(
            [question],
            show_progress_bar=False,
            convert_to_numpy=True
        ).tolist()[0]
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[question_embedding],
            n_results=top_k
        )
        
        # Extract chunks and page numbers
        retrieved = []
        if results["documents"] and len(results["documents"]) > 0:
            for doc, metadata in zip(results["documents"][0], results["metadatas"][0]):
                page = metadata.get("page", "unknown")
                try:
                    page_num = int(page)
                except:
                    page_num = -1
                retrieved.append((doc, page_num))
        
        return retrieved
    
    def predict_page(self, question: str, top_k: int = TOP_K) -> int:
        """
        Predict the page number for a question.
        
        Uses majority voting: returns the most common page number
        among the top-k retrieved chunks.
        
        Args:
            question: User question
            top_k: Number of chunks to retrieve
        
        Returns:
            Predicted page number
        """
        retrieved = self.retrieve(question, top_k)
        
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
        predicted_page = max(page_counts.items(), key=lambda x: x[1])[0]
        return predicted_page


# ============================================================================
# STEP 3: Evaluation
# ============================================================================

def evaluate_rag_strategy(
    strategy: Dict,
    raw_docs: List[Document],
    eval_set: List[Dict]
) -> Dict:
    """
    Evaluate one RAG strategy (chunking + semantic retrieval).
    
    Args:
        strategy: Dict with 'name', 'chunk_size', 'chunk_overlap'
        raw_docs: Raw documents from PDF
        eval_set: Evaluation questions
    
    Returns:
        Dict with results: correct predictions, accuracy, latency, etc.
    """
    print(f"\n{'='*70}")
    print(f"Testing Strategy: {strategy['name']}")
    print(f"  Chunk Size: {strategy['chunk_size']}")
    print(f"  Overlap: {strategy['chunk_overlap']}")
    print(f"{'='*70}")
    
    # Create chunks
    chunks = create_chunks_with_strategy(
        raw_docs,
        strategy['chunk_size'],
        strategy['chunk_overlap']
    )
    
    # Initialize retriever and index chunks
    retriever = SemanticRetriever()
    retriever.index_chunks(chunks, collection_name=f"chunks_{strategy['chunk_size']}")
    
    # Evaluate on all questions
    correct = 0
    total = len(eval_set)
    predictions = []
    latencies = []
    
    print(f"\n  Evaluating on {total} questions...")
    for i, item in enumerate(eval_set, 1):
        question = item["question"]
        ground_truth_page = item["correct_page_number"]
        
        # Time the retrieval
        start_time = time.time()
        predicted_page = retriever.predict_page(question, top_k=TOP_K)
        latency = time.time() - start_time
        
        # Check if correct
        is_correct = (predicted_page == ground_truth_page)
        if is_correct:
            correct += 1
        
        # Store result
        predictions.append({
            "id": item["id"],
            "question": question,
            "predicted_page": predicted_page,
            "ground_truth_page": ground_truth_page,
            "correct": is_correct,
            "latency_seconds": latency
        })
        
        latencies.append(latency)
        
        # Progress update every 10 questions
        if i % 10 == 0:
            print(f"    Progress: {i}/{total} questions ({correct}/{i} correct so far)")
    
    # Calculate metrics
    accuracy = (correct / total) * 100
    avg_latency = sum(latencies) / len(latencies)
    
    print(f"\n  ✓ Evaluation complete!")
    print(f"    Accuracy: {accuracy:.1f}% ({correct}/{total})")
    print(f"    Avg Latency: {avg_latency:.3f}s")
    
    return {
        "strategy_name": strategy['name'],
        "chunk_size": strategy['chunk_size'],
        "chunk_overlap": strategy['chunk_overlap'],
        "num_chunks": len(chunks),
        "correct_predictions": correct,
        "total_questions": total,
        "accuracy_percent": round(accuracy, 2),
        "avg_latency_seconds": round(avg_latency, 4),
        "predictions": predictions
    }


# ============================================================================
# STEP 4: Run All Experiments
# ============================================================================

def run_all_rag_experiments():
    """
    Run RAG experiments with all chunking strategies.
    
    This tests the SAME chunking strategies as before, but now with
    proper semantic retrieval instead of keyword matching.
    
    Expected results: 50-70% accuracy (vs 8% with keywords)
    """
    print("\n" + "="*70)
    print("RAG EXPERIMENTS WITH SEMANTIC EMBEDDINGS")
    print("="*70)
    print(f"PDF: {PDF_PATH}")
    print(f"Evaluation Set: {EVAL_SET_PATH}")
    print(f"Embedding Model: {EMBEDDING_MODEL}")
    print(f"Top-K Retrieval: {TOP_K}")
    print("="*70 + "\n")
    
    # Load PDF once (reuse for all strategies)
    print("Loading PDF...")
    raw_docs = _load_pdf_fast(str(PDF_PATH))
    print(f"✓ Loaded {len(raw_docs)} pages\n")
    
    # Load evaluation set
    print("Loading evaluation set...")
    with open(EVAL_SET_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Handle both formats: direct array or wrapped in "questions" key
        if isinstance(data, dict) and "questions" in data:
            eval_set = data["questions"]
        else:
            eval_set = data
    print(f"✓ Loaded {len(eval_set)} questions\n")
    
    # Run experiments for each chunking strategy
    all_results = []
    for strategy in CHUNKING_STRATEGIES:
        result = evaluate_rag_strategy(strategy, raw_docs, eval_set)
        all_results.append(result)
    
    # Save results
    output = {
        "experiment_type": "RAG with Semantic Embeddings",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "embedding_model": EMBEDDING_MODEL,
        "top_k_retrieval": TOP_K,
        "results": all_results
    }
    
    with open(RESULTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*70}")
    print(f"✓ Results saved to: {RESULTS_PATH}")
    print(f"{'='*70}\n")
    
    # Print summary
    print("\nSUMMARY OF RESULTS:")
    print("-" * 70)
    print(f"{'Strategy':<25} {'Chunks':<10} {'Accuracy':<12} {'Latency':<12}")
    print("-" * 70)
    for result in all_results:
        print(f"{result['strategy_name']:<25} "
              f"{result['num_chunks']:<10} "
              f"{result['accuracy_percent']:>6.1f}%     "
              f"{result['avg_latency_seconds']:>6.3f}s")
    print("-" * 70)
    
    # Find best strategy
    best = max(all_results, key=lambda x: x['accuracy_percent'])
    print(f"\n🏆 BEST STRATEGY: {best['strategy_name']}")
    print(f"   Accuracy: {best['accuracy_percent']}%")
    print(f"   Chunks: {best['num_chunks']}")
    print(f"   Latency: {best['avg_latency_seconds']}s")
    
    # Compare to keyword baseline
    print(f"\n📊 IMPROVEMENT OVER KEYWORD BASELINE:")
    print(f"   Keyword Baseline: 8% accuracy")
    print(f"   Best RAG Strategy: {best['accuracy_percent']}% accuracy")
    print(f"   Improvement: {best['accuracy_percent'] - 8:.1f} percentage points")
    print(f"   Relative Gain: {((best['accuracy_percent'] / 8) - 1) * 100:.0f}% better")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Check dependencies
    if not PDF_PATH.exists():
        print(f"❌ ERROR: PDF not found at {PDF_PATH}")
        print("   Please ensure the manual PDF is in the data/ directory.")
        exit(1)
    
    if not EVAL_SET_PATH.exists():
        print(f"❌ ERROR: Evaluation set not found at {EVAL_SET_PATH}")
        print("   Please create the evaluation set first.")
        exit(1)
    
    # Run experiments
    try:
        run_all_rag_experiments()
        print("\n✅ RAG experiments completed successfully!")
        print(f"   Check {RESULTS_PATH} for detailed results.\n")
    except Exception as e:
        print(f"\n❌ ERROR during experiments: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
