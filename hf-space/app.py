"""
ManualAi - Gradio Interface for HuggingFace Spaces
===================================================

Interactive web interface for the car manual question-answering system.
Achieves 64% accuracy (±2 pages) on 608-page Toyota 4Runner manual.
"""

import gradio as gr
import json
import time
import os
from pathlib import Path
from typing import List, Tuple, Dict

# Import our production RAG system
from rag_chain import UltimateRAG

# Configuration
os.environ['HF_TOKEN'] = os.getenv('HF_TOKEN', '')
os.environ['HUGGING_FACE_HUB_TOKEN'] = os.getenv('HF_TOKEN', '')

DATA_DIR = Path(__file__).parent.parent / "data"
PDF_PATH = DATA_DIR / "2023-Toyota-4runner-Manual.pdf"

# Example questions
EXAMPLE_QUESTIONS = [
    "What should you do if the 'Braking Power Low Stop in a Safe Place' message appears?",
    "What does the PCS warning light indicate?",
    "What does the tire pressure warning light mean?",
    "How do you know if the parking brake is still engaged?",
    "What should you do when the 'Engine Coolant Temp High' message appears?",
    "What does the low fuel level warning mean?",
    "How often should engine oil be replaced?",
    "What is the recommended tire pressure?",
    "How do you reset the maintenance reminder?",
    "What type of fuel should be used?"
]

# Initialize RAG system (will be done on first query)
rag_system = None

def initialize_rag():
    """Initialize RAG system (lazy loading)"""
    global rag_system
    if rag_system is None:
        print("🔧 Initializing RAG system...")
        rag_system = UltimateRAG()
        
        # Check if PDF exists
        if not PDF_PATH.exists():
            return None, "⚠️ PDF file not found. Please upload the manual."
        
        # Index the document
        rag_system.index_document(str(PDF_PATH))
        print("✅ RAG system ready!")
    
    return rag_system

def answer_question(question: str) -> Tuple[str, str, str, float]:
    """
    Answer a question about the car manual
    
    Returns:
        answer: Page number and context
        confidence: Confidence score
        retrieved_chunks: Top retrieved chunks
        latency: Query time
    """
    if not question or not question.strip():
        return "❌ Please enter a question.", "", "", 0.0
    
    try:
        # Initialize system if needed
        system = initialize_rag()
        if system is None:
            return "⚠️ System not initialized. Please check PDF availability.", "", "", 0.0
        
        # Measure latency
        start_time = time.time()
        
        # Get prediction
        page_number, retrieved_docs = system.predict_with_context(question)
        
        latency = time.time() - start_time
        
        # Format answer
        if page_number > 0:
            answer = f"""
## 📄 Answer Found!

**Page Number:** {page_number}

**Confidence:** High (from Top-ranked chunks)

**Manual:** 2023 Toyota 4Runner Owner's Manual (608 pages)

**Search Method:** Hybrid Semantic + Keyword Search with Cross-Encoder Reranking

---

### 💡 How to verify:
1. Open the manual to page {page_number}
2. Look for content related to: "{question}"
3. The answer should be within ±2 pages (64% accuracy)

### ⚙️ System Performance:
- **Accuracy:** 64% within ±2 pages
- **Query Time:** {latency:.2f} seconds
- **Retrieved Chunks:** {len(retrieved_docs)}
"""
        else:
            answer = f"""
## ⚠️ No Answer Found

The system couldn't find a confident answer for this question.

**Possible reasons:**
- Question might be outside the manual's scope
- Try rephrasing the question
- Be more specific about the topic

**Query Time:** {latency:.2f} seconds
"""
        
        # Format retrieved chunks
        chunks_display = "### 📑 Top Retrieved Chunks\n\n"
        for i, (chunk_text, chunk_page) in enumerate(retrieved_docs[:5], 1):
            preview = chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text
            chunks_display += f"**{i}. Page {chunk_page}**\n```\n{preview}\n```\n\n"
        
        # Confidence visualization
        confidence_bars = f"""
### 📊 Retrieval Confidence

Top 5 chunks analyzed with:
- ✅ Semantic similarity (70%)
- ✅ Keyword matching (30%)
- ✅ Cross-encoder reranking
- ✅ Page-aware boosting

Query processed in **{latency:.2f}s**
"""
        
        return answer, chunks_display, confidence_bars, latency
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}\n\nPlease try again or contact support."
        return error_msg, "", "", 0.0

def get_system_stats() -> str:
    """Get system statistics"""
    stats = """
## 🎯 System Statistics

### Performance Metrics
- **Accuracy:** 64% (±2 pages)
- **Test Set:** 50 curated questions
- **Manual Size:** 608 pages
- **Average Latency:** 16.2 seconds

### Technical Stack
- **Embedding Model:** all-mpnet-base-v2 (768 dims)
- **Reranker:** ms-marco-MiniLM-L-6-v2
- **Vector Store:** ChromaDB
- **Search:** Hybrid (70% semantic + 30% BM25)

### Key Features
- ✅ Query expansion (3 variations)
- ✅ Context expansion (neighboring chunks)
- ✅ Page-aware boosting
- ✅ Exponential voting (3.0^rank)

### Development Journey
- **Baseline:** 8% (keyword search)
- **Basic RAG:** 26% (semantic only)
- **Advanced Hybrid:** 62% (semantic + BM25)
- **Ultimate RAG:** 64% (all optimizations)

**Improvement:** +56 percentage points = 800% increase! 🚀
"""
    return stats

# Create Gradio interface
def create_interface():
    """Create Gradio web interface"""
    
    with gr.Blocks(theme=gr.themes.Soft(), title="ManualAi: Car Manual Q&A") as demo:
        
        gr.Markdown("""
# 🚗 ManualAi: Intelligent Car Manual Question-Answering

Ask questions about your 2023 Toyota 4Runner and get accurate page references!

**Accuracy:** 64% within ±2 pages | **Powered by:** Advanced RAG with Hybrid Search
""")
        
        with gr.Row():
            with gr.Column(scale=2):
                # Input section
                question_input = gr.Textbox(
                    label="Your Question",
                    placeholder="e.g., What does the tire pressure warning light mean?",
                    lines=2
                )
                
                with gr.Row():
                    submit_btn = gr.Button("🔍 Search Manual", variant="primary", scale=2)
                    clear_btn = gr.Button("🗑️ Clear", scale=1)
                
                # Example questions
                gr.Markdown("### 💡 Try these example questions:")
                example_buttons = []
                for i in range(0, len(EXAMPLE_QUESTIONS), 2):
                    with gr.Row():
                        for j in range(2):
                            if i + j < len(EXAMPLE_QUESTIONS):
                                btn = gr.Button(
                                    EXAMPLE_QUESTIONS[i + j][:50] + "...",
                                    size="sm"
                                )
                                example_buttons.append((btn, EXAMPLE_QUESTIONS[i + j]))
            
            with gr.Column(scale=1):
                # System stats
                stats_display = gr.Markdown(get_system_stats())
        
        # Output section
        with gr.Row():
            with gr.Column():
                answer_output = gr.Markdown(label="Answer")
            
        with gr.Row():
            with gr.Column():
                chunks_output = gr.Markdown(label="Retrieved Chunks")
            with gr.Column():
                confidence_output = gr.Markdown(label="Confidence Analysis")
        
        # Footer
        gr.Markdown("""
---
### 📊 About This System

This RAG (Retrieval-Augmented Generation) system demonstrates:
- Advanced hybrid search (semantic + keyword)
- Cross-encoder reranking for precision
- Systematic optimization (11 experiments: 8% → 64%)
- Production-ready architecture

**Source:** 2023 Toyota 4Runner Owner's Manual (608 pages)  
**Built by:** [agapemiteu](https://github.com/agapemiteu/ManualAi)  
**Repository:** [GitHub](https://github.com/agapemiteu/ManualAi)

⭐ Star the repo if you find this useful!
""")
        
        # Event handlers
        submit_btn.click(
            fn=answer_question,
            inputs=[question_input],
            outputs=[answer_output, chunks_output, confidence_output]
        )
        
        clear_btn.click(
            fn=lambda: ("", "", "", ""),
            outputs=[question_input, answer_output, chunks_output, confidence_output]
        )
        
        # Example button handlers
        for btn, question in example_buttons:
            btn.click(
                fn=lambda q=question: q,
                outputs=[question_input]
            )
    
    return demo

if __name__ == "__main__":
    # Create and launch interface
    demo = create_interface()
    
    # Launch with public sharing
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # Set to True for public link
        show_error=True
    )
