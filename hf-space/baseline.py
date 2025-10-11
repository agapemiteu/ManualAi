"""Baseline keyword-based search for car manual Q&A evaluation.

This module implements a simple keyword matching baseline that:
1. Extracts keywords from the question (removing stop words)
2. Scores each PDF page by counting keyword occurrences
3. Returns the page with the highest score

Usage:
    from baseline import keyword_baseline_search
    
    page_num = keyword_baseline_search('manual.pdf', 'What does the brake light mean?')
    print(f"Best match: page {page_num}")

Dependencies:
    - PyMuPDF (fitz): pip install pymupdf
"""

import fitz  # PyMuPDF
import re

# Stop words to filter out from question keywords
# These are common English words that don't help identify specific manual content
STOP_WORDS = set([
	"a", "an", "the", "in", "on", "what", "is", "how", "do", "i", "to",
	"for", "of", "should", "and", "my", "car", "it", "if", "your"
])


def keyword_baseline_search(pdf_path: str, question: str) -> int:
	"""Find the best matching page in a PDF based on keyword frequency.
	
	This is a naive baseline that counts how many times question keywords
	appear on each page. It returns the page number (1-based) with the
	highest keyword match score.
	
	Args:
		pdf_path: Path to the PDF file to search
		question: Natural language question string
		
	Returns:
		Page number (1-based) with the most keyword matches, or -1 if no keywords found
		
	Example:
		>>> keyword_baseline_search('manual.pdf', 'How do I check brake fluid?')
		420  # Returns page 420 if it has the most matches for 'check' and 'brake' and 'fluid'
	"""
	# Step 1: Extract keywords from question (filter stop words)
	question_words = set(re.findall(r'\w+', question.lower()))
	keywords = [word for word in question_words if word not in STOP_WORDS]
    
	if not keywords:
		return -1  # No searchable keywords after filtering
	
	# Step 2: Open PDF and prepare for scoring
	doc = fitz.open(pdf_path)
	best_page_num = -1
	max_score = -1

	# Step 3: Score each page by counting keyword occurrences
	for page_num, page in enumerate(doc):
		text = page.get_text("text").lower()
		score = 0
		
		# Count occurrences of each keyword on this page
		for word in keywords:
			score += text.count(word)
        
		# Track the page with the highest score
		if score > max_score:
			max_score = score
			best_page_num = page_num + 1  # Convert to 1-based page numbering
            
	doc.close()
	return best_page_num
