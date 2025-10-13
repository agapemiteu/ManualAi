"""
Production Accuracy Evaluation - Batch Mode
Test the deployed RAG system in smaller batches with resume capability
"""

import json
import requests
import time
from pathlib import Path
from typing import List, Dict, Tuple
import sys

# Configuration
API_BASE_URL = "https://agapemiteu-manualai.hf.space"
MANUAL_ID = "manual-77c2314e"
EVAL_SET_PATH = Path(__file__).parent / "data" / "evaluation_set.json"
RESULTS_PATH = Path(__file__).parent / "production_evaluation_results.json"
BATCH_SIZE = 10  # Process 10 questions at a time
DELAY_BETWEEN_REQUESTS = 2  # 2 seconds between requests
RETRY_DELAY = 5  # 5 seconds if error

def load_evaluation_set() -> List[Dict]:
    """Load the ground truth evaluation set"""
    with open(EVAL_SET_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    questions = data.get('questions', [])
    # Normalize field names
    for q in questions:
        if 'question_text' in q and 'question' not in q:
            q['question'] = q['question_text']
        if 'correct_page_number' in q and 'answer_page' not in q:
            q['answer_page'] = q['correct_page_number']
    return questions

def load_existing_results() -> Dict:
    """Load existing results if available"""
    if RESULTS_PATH.exists():
        with open(RESULTS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'exact_match': 0,
        'within_2_pages': 0,
        'within_5_pages': 0,
        'within_10_pages': 0,
        'total': 0,
        'details': []
    }

def save_results(results: Dict):
    """Save results to file"""
    with open(RESULTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

def query_rag_system(manual_id: str, question: str, timeout: int = 60) -> Tuple[str, List[int], str]:
    """
    Query the production RAG system
    Returns: (answer_text, list of page numbers, status)
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
            return f"Error: {response.status_code}", [], "error"
        
        data = response.json()
        answer = data.get("answer", "")
        
        # Extract page numbers from answer
        import re
        page_numbers = []
        
        # Pattern: "page 123" or "pages 123"
        matches = re.findall(r'\bpages?\s+(\d+)', answer.lower())
        page_numbers.extend([int(m) for m in matches])
        
        # Pattern: "(page 123)"
        matches = re.findall(r'\(page\s+(\d+)\)', answer.lower())
        page_numbers.extend([int(m) for m in matches])
        
        # Remove duplicates and sort
        page_numbers = sorted(list(set(page_numbers)))
        
        return answer, page_numbers, "success"
        
    except requests.exceptions.Timeout:
        return "Timeout", [], "timeout"
    except requests.exceptions.RequestException as e:
        return f"Request error: {str(e)[:100]}", [], "error"
    except Exception as e:
        return f"Exception: {str(e)[:100]}", [], "error"

def calculate_accuracy(retrieved_pages: List[int], ground_truth_page: int, tolerance: int = 2) -> bool:
    """Check if any retrieved page is within tolerance"""
    if not retrieved_pages:
        return False
    
    for page in retrieved_pages:
        if abs(page - ground_truth_page) <= tolerance:
            return True
    return False

def run_batch_evaluation(start_index: int = 0):
    """Run evaluation in batches"""
    print("=" * 80)
    print("📊 PRODUCTION RAG SYSTEM ACCURACY EVALUATION (BATCH MODE)")
    print("=" * 80)
    print()
    
    # Load evaluation set
    questions = load_evaluation_set()
    total_questions = len(questions)
    
    # Load existing results
    results = load_existing_results()
    processed_ids = {d['question_id'] for d in results.get('details', [])}
    
    print(f"Total questions: {total_questions}")
    print(f"Already processed: {len(processed_ids)}")
    print(f"Starting from index: {start_index}")
    print()
    
    # Process remaining questions
    for i in range(start_index, total_questions):
        q = questions[i]
        q_id = q.get('question_id', f'Q{i+1}')
        
        # Skip if already processed
        if q_id in processed_ids:
            print(f"[{i+1}/{total_questions}] {q_id} - Already processed, skipping")
            continue
        
        question_text = q.get('question', '')
        ground_truth_page = q.get('answer_page')
        category = q.get('category', 'unknown')
        
        print(f"\n[{i+1}/{total_questions}] {q_id}")
        print(f"Q: {question_text[:80]}...")
        print(f"Ground Truth: Page {ground_truth_page}")
        
        # Query the system
        answer, retrieved_pages, status = query_rag_system(MANUAL_ID, question_text)
        
        if status == "timeout":
            print("⏱️  Timeout - retrying after delay...")
            time.sleep(RETRY_DELAY)
            answer, retrieved_pages, status = query_rag_system(MANUAL_ID, question_text)
        
        if status == "error":
            print(f"❌ Error: {answer[:100]}")
            print("Saving progress and stopping...")
            save_results(results)
            print(f"\nProgress saved. Resume with: python {sys.argv[0]} --start {i}")
            return False
        
        print(f"Retrieved: {retrieved_pages if retrieved_pages else 'None'}")
        
        # Calculate accuracy
        exact = calculate_accuracy(retrieved_pages, ground_truth_page, tolerance=0)
        within_2 = calculate_accuracy(retrieved_pages, ground_truth_page, tolerance=2)
        within_5 = calculate_accuracy(retrieved_pages, ground_truth_page, tolerance=5)
        within_10 = calculate_accuracy(retrieved_pages, ground_truth_page, tolerance=10)
        
        # Update counts
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
        
        results['total'] = i + 1
        
        # Store details
        results['details'].append({
            'question_id': q_id,
            'question': question_text,
            'category': category,
            'ground_truth': ground_truth_page,
            'retrieved': retrieved_pages,
            'answer_preview': answer[:200] if answer else '',
            'exact': exact,
            'within_2': within_2,
            'within_5': within_5,
            'within_10': within_10,
            'status': status
        })
        
        # Save progress every 5 questions
        if (i + 1) % 5 == 0:
            save_results(results)
            print(f"\n💾 Progress saved ({i+1}/{total_questions})")
        
        # Rate limiting
        time.sleep(DELAY_BETWEEN_REQUESTS)
    
    # Final save
    save_results(results)
    print_final_results(results)
    return True

def print_final_results(results: Dict):
    """Print final evaluation results"""
    print()
    print("=" * 80)
    print("📊 FINAL RESULTS")
    print("=" * 80)
    print()
    
    total = results['total']
    exact_pct = (results['exact_match'] / total) * 100 if total > 0 else 0
    within_2_pct = ((results['exact_match'] + results['within_2_pages']) / total) * 100 if total > 0 else 0
    within_5_pct = ((results['exact_match'] + results['within_2_pages'] + results['within_5_pages']) / total) * 100 if total > 0 else 0
    within_10_pct = ((results['exact_match'] + results['within_2_pages'] + results['within_5_pages'] + results['within_10_pages']) / total) * 100 if total > 0 else 0
    
    print(f"Questions Evaluated: {total}")
    print()
    print(f"Exact Match (±0 pages):     {results['exact_match']:3d} / {total} = {exact_pct:5.1f}%")
    print(f"Within ±2 pages:             {results['exact_match'] + results['within_2_pages']:3d} / {total} = {within_2_pct:5.1f}% ⭐")
    print(f"Within ±5 pages:             {results['exact_match'] + results['within_2_pages'] + results['within_5_pages']:3d} / {total} = {within_5_pct:5.1f}%")
    print(f"Within ±10 pages:            {results['exact_match'] + results['within_2_pages'] + results['within_5_pages'] + results['within_10_pages']:3d} / {total} = {within_10_pct:5.1f}%")
    print()
    print("=" * 80)

if __name__ == "__main__":
    # Check for resume flag
    start_idx = 0
    if len(sys.argv) > 2 and sys.argv[1] == "--start":
        start_idx = int(sys.argv[2])
    
    success = run_batch_evaluation(start_idx)
    
    if success:
        print("\n✅ Evaluation complete!")
        print(f"📊 Full results saved to: {RESULTS_PATH}")
    else:
        print("\n⚠️  Evaluation paused due to errors")
        print("💡 Resume later with the command shown above")
