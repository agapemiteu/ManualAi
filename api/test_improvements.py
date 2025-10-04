"""
Test script to verify RAG chatbot improvements
Run this to see the enhanced intelligence in action
"""

from rag_chain import (
    _expand_query,
    _extract_keywords,
    _calculate_relevance_score,
    _neutralize_brand_references,
    _extract_context_from_question,
    _is_procedural_question,
    _is_warning_question,
)

def test_query_expansion():
    print("=" * 60)
    print("TEST 1: Query Expansion")
    print("=" * 60)

    questions = [
        "How to fix my brakes?",
        "What does the engine light mean?",
        "My tire pressure is low",
    ]

    for q in questions:
        expanded = _expand_query(q)
        print(f"\nOriginal: {q}")
        print(f"Expanded: {expanded}")

def test_brand_neutralization():
    print("\n" + "=" * 60)
    print("TEST 2: Brand Neutralization")
    print("=" * 60)

    texts = [
        "Contact an MG Authorised Repairer as soon as possible.",
        "Visit your Lexus dealer for service.",
        "The BMW service center can help with this issue.",
    ]

    for text in texts:
        neutralized = _neutralize_brand_references(text)
        print(f"\nOriginal:    {text}")
        print(f"Neutralized: {neutralized}")

def test_context_extraction():
    print("\n" + "=" * 60)
    print("TEST 3: Context Extraction")
    print("=" * 60)

    questions = [
        "My brakes are failing, what can I do immediately?",
        "How do I change a tire?",
        "The engine won't start",
    ]

    for q in questions:
        context = _extract_context_from_question(q)
        print(f"\nQuestion: {q}")
        print(f"Context: {context}")

def test_question_type_detection():
    print("\n" + "=" * 60)
    print("TEST 4: Question Type Detection")
    print("=" * 60)

    questions = [
        "How do I fix my brakes?",
        "What does the brake warning light mean?",
        "Tell me about tire pressure",
    ]

    for q in questions:
        is_proc = _is_procedural_question(q)
        is_warn = _is_warning_question(q)
        print(f"\nQuestion: {q}")
        print(f"  Procedural: {is_proc}")
        print(f"  Warning: {is_warn}")

def test_relevance_scoring():
    print("\n" + "=" * 60)
    print("TEST 5: Relevance Scoring")
    print("=" * 60)

    question = "How to fix brake problems?"
    answers = [
        "Check brake fluid level and refill if low. Contact service center if issue persists.",
        "The engine oil should be checked regularly.",
        "Brake system malfunction. Stop vehicle safely and check brake fluid.",
    ]

    print(f"Question: {question}")
    for i, answer in enumerate(answers, 1):
        score = _calculate_relevance_score(question, answer)
        print(f"\nAnswer {i}: {answer}")
        print(f"  Score: {score:.2%}")

def test_keyword_extraction():
    print("\n" + "=" * 60)
    print("TEST 6: Keyword Extraction")
    print("=" * 60)

    texts = [
        "My car brakes are failing",
        "The engine warning light is on",
    ]

    for text in texts:
        keywords = _extract_keywords(text)
        print(f"\nText: {text}")
        print(f"Keywords: {keywords}")

if __name__ == "__main__":
    print("\nRAG CHATBOT INTELLIGENCE TESTS\n")

    test_query_expansion()
    test_brand_neutralization()
    test_context_extraction()
    test_question_type_detection()
    test_relevance_scoring()
    test_keyword_extraction()

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
    print("\nYour RAG chatbot is now smarter and more human-like!")
    print("Ready to test with real questions.\n")
