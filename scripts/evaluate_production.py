"""
Production Accuracy Evaluation
Test the deployed RAG system against the ground truth evaluation set
to measure real-world production accuracy.
"""

import json
import requests
import time
from pathlib import Path
from typing import List, Dict, Tuple

# Configuration
API_BASE_URL = "https://agapemiteu-manualai.hf.space"
MANUAL_ID = "manual-1de35b37"  # The uploaded full manual (updated after source_pages feature)
EVAL_SET_PATH = Path(__file__).parent / "data" / "evaluation_set.json"

def load_evaluation_set() -> List[Dict]:
    """Load the ground truth evaluation set"""
    with open(EVAL_SET_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # The file has questions with 'question_text' and 'correct_page_number'
    questions = data.get('questions', [])
    # Normalize the field names
    for q in questions:
        if 'question_text' in q and 'question' not in q:
            q['question'] = q['question_text']
        if 'correct_page_number' in q and 'answer_page' not in q:
            q['answer_page'] = q['correct_page_number']
    return questions

def query_rag_system(manual_id: str, question: str, timeout: int = 30) -> Tuple[str, List[int]]:
    """
    Query the production RAG system and get answer with source pages
    Returns: (answer_text, list of source page numbers)
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/chat",
            json={
                "manual_id": manual_id,
                "question": question,
                "stream": False
            },
            timeout=timeout
        )
        
        if response.status_code != 200:
            return f"Error: {response.status_code}", []
        
        data = response.json()
        answer = data.get("answer", "")
        source_pages = data.get("source_pages", [])  # Now directly from API!
        
        return answer, source_pages
        
    except Exception as e:
        return f"Exception: {str(e)}", []

def calculate_accuracy(retrieved_pages: List[int], ground_truth_page: int, tolerance: int = 2) -> bool:
    """
    Check if any retrieved page is within tolerance of ground truth
    tolerance=2 means ±2 pages is considered correct
    """
    if not retrieved_pages:
        return False
    
    for page in retrieved_pages:
        if abs(page - ground_truth_page) <= tolerance:
            return True
    return False

def run_evaluation():
    """Run full evaluation against production system"""
    print("=" * 80)
    print("📊 PRODUCTION RAG SYSTEM ACCURACY EVALUATION")
    print("=" * 80)
    print()
    print(f"API Endpoint: {API_BASE_URL}")
    print(f"Manual ID: {MANUAL_ID}")
    print(f"Evaluation Set: {EVAL_SET_PATH}")
    print()
    
    # Load evaluation set
    questions = load_evaluation_set()
    print(f"✅ Loaded {len(questions)} evaluation questions")
    print()
    
    # Results storage
    results = {
        'exact_match': 0,
        'within_2_pages': 0,
        'within_5_pages': 0,
        'within_10_pages': 0,
        'total': len(questions),
        'details': []
    }
    
    print("🔍 Testing questions...")
    print("-" * 80)
    
    for i, q in enumerate(questions, 1):
        question_text = q.get('question', '')
        ground_truth_page = q.get('correct_page_number')
        question_id = q.get('id', f'Q-{i}')
        
        print(f"\n[{i}/{len(questions)}] ID: {question_id}")
        print(f"Q: {question_text[:80]}...")
        print(f"Ground Truth Page: {ground_truth_page}")
        
        # Query the RAG system
        answer, retrieved_pages = query_rag_system(MANUAL_ID, question_text)
        
        print(f"Retrieved Pages: {retrieved_pages if retrieved_pages else 'None'}")
        
        # Calculate accuracy at different tolerance levels
        exact = calculate_accuracy(retrieved_pages, ground_truth_page, tolerance=0)
        within_2 = calculate_accuracy(retrieved_pages, ground_truth_page, tolerance=2)
        within_5 = calculate_accuracy(retrieved_pages, ground_truth_page, tolerance=5)
        within_10 = calculate_accuracy(retrieved_pages, ground_truth_page, tolerance=10)
        
        if exact:
            results['exact_match'] += 1
            print("✅ EXACT MATCH!")
        elif within_2:
            results['within_2_pages'] += 1
            print("✅ Within ±2 pages")
        elif within_5:
            results['within_5_pages'] += 1
            print("⚠️  Within ±5 pages")
        elif within_10:
            results['within_10_pages'] += 1
            print("⚠️  Within ±10 pages")
        else:
            print("❌ Miss")
        
        # Store details
        results['details'].append({
            'id': question_id,
            'question': question_text,
            'ground_truth': ground_truth_page,
            'retrieved': retrieved_pages,
            'answer_preview': answer[:200] if answer else '',
            'exact': exact,
            'within_2': within_2,
            'within_5': within_5,
            'within_10': within_10
        })
        
        # Rate limiting - don't overwhelm the free tier API
        time.sleep(1)
    
    # Calculate final metrics
    print()
    print("=" * 80)
    print("📊 FINAL RESULTS")
    print("=" * 80)
    print()
    
    exact_pct = (results['exact_match'] / results['total']) * 100
    within_2_pct = ((results['exact_match'] + results['within_2_pages']) / results['total']) * 100
    within_5_pct = ((results['exact_match'] + results['within_2_pages'] + results['within_5_pages']) / results['total']) * 100
    within_10_pct = ((results['exact_match'] + results['within_2_pages'] + results['within_5_pages'] + results['within_10_pages']) / results['total']) * 100
    
    print(f"Total Questions: {results['total']}")
    print()
    print(f"Exact Match (±0 pages):     {results['exact_match']:3d} / {results['total']} = {exact_pct:5.1f}%")
    print(f"Within ±2 pages:             {results['exact_match'] + results['within_2_pages']:3d} / {results['total']} = {within_2_pct:5.1f}% ⭐")
    print(f"Within ±5 pages:             {results['exact_match'] + results['within_2_pages'] + results['within_5_pages']:3d} / {results['total']} = {within_5_pct:5.1f}%")
    print(f"Within ±10 pages:            {results['exact_match'] + results['within_2_pages'] + results['within_5_pages'] + results['within_10_pages']:3d} / {results['total']} = {within_10_pct:5.1f}%")
    print()
    
    # Save detailed results
    output_path = Path(__file__).parent / "production_evaluation_results.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Detailed results saved to: {output_path}")
    print()
    
    # Compare to local evaluation
    print("=" * 80)
    print("📈 COMPARISON: Local Evaluation vs Production")
    print("=" * 80)
    print()
    print(f"{'Metric':<30} {'Local (with OCR)':<20} {'Production (no OCR)':<20}")
    print("-" * 80)
    print(f"{'Exact Match':<30} {'32%':<20} {f'{exact_pct:.1f}%':<20}")
    print(f"{'Within ±2 pages':<30} {'64%':<20} {f'{within_2_pct:.1f}%':<20}")
    print(f"{'Within ±5 pages':<30} {'70%':<20} {f'{within_5_pct:.1f}%':<20}")
    print()
    
    if within_2_pct >= 60:
        print("✅ Production accuracy is EXCELLENT (≥60% within ±2 pages)")
        print("   PyMuPDF-only text extraction works well for digital PDFs!")
    elif within_2_pct >= 50:
        print("✅ Production accuracy is GOOD (≥50% within ±2 pages)")
        print("   Acceptable performance for free tier deployment")
    else:
        print("⚠️  Production accuracy is LOWER than expected")
        print("   This could indicate issues with text extraction or retrieval")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    run_evaluation()
