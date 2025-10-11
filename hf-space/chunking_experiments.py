"""Phase 2: Chunking Strategy Experiments

This script systematically tests different chunking strategies to find the optimal
configuration for car manual Q&A retrieval.

What we're testing:
- Different chunk sizes (how much text per chunk)
- Different overlap amounts (how much chunks share with neighbors)
- Impact on retrieval accuracy and speed

Goal: Beat the keyword baseline and find the best chunking strategy!
"""

import json
import time
from pathlib import Path
from typing import List, Tuple
import sys

# Import our document loader functions
from document_loader import _load_pdf_fast, _enrich_metadata
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# --- Configuration ---
EVALUATION_FILE = str(Path(__file__).parent.parent / 'data' / 'evaluation_set.json')
PDF_PATH = str(Path(__file__).parent.parent / 'data' / '2023-Toyota-4runner-Manual.pdf')


def simple_keyword_retriever(chunks: List[Document], question: str) -> Document:
    """
    Simple retriever that scores chunks based on keyword overlap.
    
    This mimics basic semantic search without embeddings:
    1. Extract keywords from question
    2. Score each chunk by counting keyword matches
    3. Return the highest-scoring chunk
    
    Args:
        chunks: List of document chunks to search
        question: User's question
        
    Returns:
        Best matching chunk (Document object with page_content and metadata)
    """
    # Extract keywords from question (simple tokenization)
    question_words = set(question.lower().split())
    # Remove common stop words
    stop_words = {'what', 'is', 'the', 'how', 'do', 'i', 'a', 'an', 'to', 'in', 'on', 'for', 'of'}
    keywords = [w for w in question_words if w not in stop_words and len(w) > 2]
    
    # Score each chunk
    best_chunk = None
    best_score = -1
    
    for chunk in chunks:
        text = chunk.page_content.lower()
        # Count how many keywords appear in this chunk
        score = sum(text.count(keyword) for keyword in keywords)
        
        if score > best_score:
            best_score = score
            best_chunk = chunk
    
    return best_chunk if best_chunk else chunks[0]  # Fallback to first chunk


def create_chunks_with_strategy(raw_docs: List[Document], chunk_size: int, chunk_overlap: int) -> List[Document]:
    """
    Apply a specific chunking strategy to raw documents.
    
    Args:
        raw_docs: Raw page-level documents from PDF
        chunk_size: Maximum characters per chunk
        chunk_overlap: Characters to overlap between adjacent chunks
        
    Returns:
        List of smaller document chunks with enriched metadata
    """
    # Create the text splitter with our parameters
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        # These separators tell the splitter where it's "safe" to break text
        # It tries them in order: paragraph breaks, then sentences, then words
        separators=["\n\n", "\n", ". ", ", ", " ", ""],
        keep_separator=True,  # Keep the separator character with the chunk
    )
    
    # Split the documents into smaller chunks
    chunks = splitter.split_documents(raw_docs)
    
    # Enrich each chunk with metadata (like document type, key terms)
    enriched_chunks = []
    for chunk in chunks:
        # The enrich_metadata function adds useful tags to help with retrieval
        enriched = _enrich_metadata(chunk)
        enriched_chunks.append(enriched)
    
    return enriched_chunks


def evaluate_chunking_strategy(
    raw_docs: List[Document],
    chunk_size: int,
    chunk_overlap: int,
    strategy_name: str
) -> dict:
    """
    Test a single chunking strategy against the evaluation set.
    
    Args:
        raw_docs: Raw documents from PDF
        chunk_size: Chunk size to test
        chunk_overlap: Overlap to test
        strategy_name: Human-readable name for this strategy
        
    Returns:
        Dictionary with results: accuracy, latency, chunk count, etc.
    """
    print(f"\n{'='*70}")
    print(f"Testing Strategy: {strategy_name}")
    print(f"  Chunk Size: {chunk_size} | Overlap: {chunk_overlap}")
    print(f"{'='*70}")
    
    # Step 1: Create chunks with this strategy
    chunk_start = time.time()
    chunks = create_chunks_with_strategy(raw_docs, chunk_size, chunk_overlap)
    chunk_time = time.time() - chunk_start
    
    print(f"  ✓ Created {len(chunks)} chunks in {chunk_time:.2f}s")
    
    # Step 2: Load evaluation questions
    with open(EVALUATION_FILE, 'r', encoding='utf-8') as f:
        eval_data = json.load(f)
    questions = eval_data.get('questions', [])
    
    # Step 3: Test each question
    correct_predictions = 0
    total_time = 0.0
    
    for i, item in enumerate(questions):
        question = item['question']
        correct_page = item['correct_page_number']
        
        # Time the retrieval
        start = time.time()
        best_chunk = simple_keyword_retriever(chunks, question)
        duration = time.time() - start
        total_time += duration
        
        # Extract the page number from the chunk's metadata
        predicted_page = best_chunk.metadata.get('page') or best_chunk.metadata.get('page_number')
        
        # Check if we got it right
        if predicted_page and int(predicted_page) == int(correct_page):
            correct_predictions += 1
        
        # Print progress every 10 questions
        if (i + 1) % 10 == 0:
            print(f"    Progress: {i+1}/{len(questions)} questions processed...")
    
    # Step 4: Calculate metrics
    accuracy = (correct_predictions / len(questions)) * 100 if questions else 0.0
    avg_latency = total_time / len(questions) if questions else 0.0
    
    # Step 5: Return results
    results = {
        'strategy_name': strategy_name,
        'chunk_size': chunk_size,
        'chunk_overlap': chunk_overlap,
        'num_chunks': len(chunks),
        'chunking_time': chunk_time,
        'correct_predictions': correct_predictions,
        'total_questions': len(questions),
        'accuracy': accuracy,
        'avg_latency': avg_latency,
        'total_eval_time': total_time
    }
    
    # Print summary for this strategy
    print(f"\n  📊 Results:")
    print(f"    Accuracy:        {accuracy:.2f}% ({correct_predictions}/{len(questions)})")
    print(f"    Avg Latency:     {avg_latency:.4f}s per question")
    print(f"    Total Chunks:    {len(chunks)}")
    
    return results


def run_all_experiments():
    """
    Run the complete chunking experiment suite.
    
    Tests multiple strategies:
    1. Small chunks (more precise, but may miss context)
    2. Medium chunks (balanced approach) - this is the current default
    3. Large chunks (more context, but less precise)
    4. Very small chunks (most granular)
    5. Very large chunks (maximum context)
    """
    print("\n" + "="*70)
    print("PHASE 2: CHUNKING STRATEGY EXPERIMENTS")
    print("="*70)
    print(f"PDF: {PDF_PATH}")
    print(f"Evaluation Set: {EVALUATION_FILE}")
    print("="*70)
    
    # Step 1: Load raw documents from PDF (page-level)
    print("\n📄 Loading PDF and extracting raw pages...")
    load_start = time.time()
    raw_docs = _load_pdf_fast(Path(PDF_PATH), disable_ocr=True)
    load_time = time.time() - load_start
    print(f"  ✓ Loaded {len(raw_docs)} pages in {load_time:.2f}s")
    
    # Step 2: Define chunking strategies to test
    # Format: (strategy_name, chunk_size, chunk_overlap)
    strategies = [
        ("Very Small Chunks", 300, 50),      # Most granular - great for specific facts
        ("Small Chunks", 400, 80),            # Good for precise answers
        ("Medium Chunks (Baseline)", 800, 150),  # Current default - balanced
        ("Large Chunks", 1200, 200),          # More context per chunk
        ("Very Large Chunks", 1600, 300),     # Maximum context - may be less precise
    ]
    
    # Step 3: Run experiments for each strategy
    all_results = []
    
    for strategy_name, chunk_size, chunk_overlap in strategies:
        results = evaluate_chunking_strategy(
            raw_docs=raw_docs,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            strategy_name=strategy_name
        )
        all_results.append(results)
    
    # Step 4: Compare all strategies and find the winner
    print("\n" + "="*70)
    print("FINAL COMPARISON - ALL STRATEGIES")
    print("="*70)
    print(f"\n{'Strategy':<30} {'Chunks':<10} {'Accuracy':<12} {'Latency':<12}")
    print("-" * 70)
    
    best_strategy = None
    best_accuracy = -1
    
    for result in all_results:
        print(f"{result['strategy_name']:<30} "
              f"{result['num_chunks']:<10} "
              f"{result['accuracy']:.2f}%{'':<7} "
              f"{result['avg_latency']:.4f}s")
        
        # Track the best performing strategy
        if result['accuracy'] > best_accuracy:
            best_accuracy = result['accuracy']
            best_strategy = result
    
    # Step 5: Announce the winner!
    print("\n" + "="*70)
    print("🏆 WINNING STRATEGY")
    print("="*70)
    print(f"Strategy:        {best_strategy['strategy_name']}")
    print(f"Chunk Size:      {best_strategy['chunk_size']}")
    print(f"Chunk Overlap:   {best_strategy['chunk_overlap']}")
    print(f"Accuracy:        {best_strategy['accuracy']:.2f}%")
    print(f"Avg Latency:     {best_strategy['avg_latency']:.4f}s")
    print(f"Total Chunks:    {best_strategy['num_chunks']}")
    print("="*70)
    
    # Step 6: Save results to a file for later reference
    results_file = Path(__file__).parent / 'chunking_results.json'
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'pdf_source': PDF_PATH,
            'all_results': all_results,
            'best_strategy': best_strategy
        }, f, indent=2)
    
    print(f"\n📁 Results saved to: {results_file}")
    print("\n✅ Phase 2 Complete! You can now use the winning strategy in your RAG system.\n")


if __name__ == "__main__":
    """
    Run all chunking experiments and find the best strategy.
    
    This will:
    1. Load your PDF
    2. Test 5 different chunking strategies
    3. Evaluate each against your 50-question test set
    4. Report the winner with detailed metrics
    5. Save results to chunking_results.json
    """
    run_all_experiments()
