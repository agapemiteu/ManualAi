"""Evaluation harness for car manual Q&A retrieval systems.

This script evaluates retrieval models by:
1. Loading a curated evaluation set with 50 questions from evaluation_set.json
2. Running each question through the model
3. Comparing predicted page numbers to ground truth
4. Calculating accuracy and average latency metrics

Usage:
    # Run from repository root or hf-space directory
    python hf-space/evaluate.py
    
    # Or run baseline directly:
    cd hf-space
    python evaluate.py

Expected Files:
    - ../data/evaluation_set.json (50 questions with ground truth page numbers)
    - ../data/2023-Toyota-4runner-Manual.pdf (source manual)

Output:
    - Per-question results (predicted vs actual page)
    - Summary metrics: accuracy, latency
"""

import json
import time
from baseline import keyword_baseline_search
from pathlib import Path

# --- Configuration ---
# Paths are relative to hf-space/ directory
EVALUATION_FILE = str(Path(__file__).parent.parent / 'data' / 'evaluation_set.json')
PDF_PATH = str(Path(__file__).parent.parent / 'data' / '2023-Toyota-4runner-Manual.pdf')


def run_evaluation(model_function):
	"""Run the evaluation pipeline for a given retrieval model.
	
	Measures two key metrics:
	- Retrieval Accuracy: % of questions where predicted page exactly matches ground truth
	- Average Latency: Mean time per question (in seconds)
    
	Args:
		model_function: A callable that takes (pdf_path: str, question: str) 
		                and returns page_number: int (1-based)
	
	Returns:
		None (prints results to stdout)
		
	Example:
		>>> def my_model(pdf_path, question):
		...     return 123  # Your retrieval logic here
		>>> run_evaluation(my_model)
	"""
	try:
		with open(EVALUATION_FILE, 'r', encoding='utf-8') as f:
			evaluation_set = json.load(f)
	except FileNotFoundError:
		print(f"Error: Evaluation file not found at '{EVALUATION_FILE}'")
		return

	questions = evaluation_set.get('questions', [])
	correct_predictions = 0
	total_time = 0.0
	total_questions = len(questions)

	print(f"\n{'='*60}")
	print(f"Starting Evaluation: {model_function.__name__}")
	print(f"{'='*60}")
	print(f"Evaluation Set: {EVALUATION_FILE}")
	print(f"PDF Source: {PDF_PATH}")
	print(f"Total Questions: {total_questions}\n")
    
	for i, item in enumerate(questions):
		question = item['question']
		correct_page = item['correct_page_number']

		start_time = time.time()
		predicted_page = model_function(PDF_PATH, question)
		end_time = time.time()

		duration = end_time - start_time
		total_time += duration

		is_correct = (predicted_page == correct_page)
		if is_correct:
			correct_predictions += 1
        
		status = "✅ Correct" if is_correct else f"❌ Incorrect (Predicted: {predicted_page})"
		print(f"({i+1}/{total_questions}) Q: '{question[:60]}...' | Actual: {correct_page} | Status: {status}")

	# --- Calculate and Print Final Metrics ---
	accuracy = (correct_predictions / total_questions) * 100 if total_questions else 0.0
	avg_latency = total_time / total_questions if total_questions else 0.0

	print(f"\n{'='*60}")
	print("EVALUATION SUMMARY")
	print(f"{'='*60}")
	print(f"Model:               {model_function.__name__}")
	print(f"Total Questions:     {total_questions}")
	print(f"Correct Predictions: {correct_predictions}")
	print(f"Retrieval Accuracy:  {accuracy:.2f}%")
	print(f"Average Latency:     {avg_latency:.4f} seconds/question")
	print(f"Total Time:          {total_time:.2f} seconds")
	print(f"{'='*60}\n")


if __name__ == "__main__":
	"""
	Phase 1 Baseline Evaluation
	
	This runs the keyword-based baseline model against the 50-question evaluation set.
	Use this as a reference point before experimenting with RAG improvements.
	"""
	print("\n" + "="*60)
	print("PHASE 1: BASELINE EVALUATION")
	print("="*60)
	print("Running keyword-based baseline search...")
	print("This establishes the performance floor for comparison.\n")
	
	# Evaluate the baseline model
	run_evaluation(keyword_baseline_search)
