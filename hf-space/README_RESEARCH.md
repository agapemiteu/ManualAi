# Research & Experimentation Code

This folder contains the **research phase** code used for RAG experimentation and optimization.

## ⚠️ Note

**This code represents the experimental/research phase of the project.**  
The production deployment uses the code in `/api` folder.

## Contents

### Core Files
- `main.py` - FastAPI backend (research version)
- `rag_chain.py` - RAG chain implementation
- `document_loader.py` - Document processing with OCR experiments
- `vector_store.py` - ChromaDB vector store
- `Dockerfile` - Container configuration

### Experiment Scripts
These files contain various RAG optimization experiments:
- `rag_experiments*.py` - Multiple experimental configurations
- `chunking_experiments.py` - Chunk size optimization
- `evaluate.py` - Evaluation framework
- `baseline.py` - Baseline performance tests
- `analyze_*.py` - Results analysis

### Results Files
- `rag_results*.json` - Experimental results
- `chunking_results.json` - Chunking optimization data

### HuggingFace Deployment
- `app.py` - Gradio interface (not used in production)
- `start.sh`, `startup.py` - Deployment scripts
- `requirements_hf.txt` - HuggingFace-specific dependencies

## Key Findings from Experiments

### Chunking Optimization
- Tested chunk sizes: 250, 500, 1000, 1500, 2000 tokens
- Best performance: 500-1000 tokens
- Overlap: 50 tokens worked well

### RAG Configuration
- Tested various retrieval strategies (similarity, MMR, etc.)
- Experimented with reranking approaches
- Optimized number of retrieved documents (k=3-5 optimal)

### Document Processing
- Compared PyMuPDF vs unstructured library
- Tested OCR configurations
- **Finding**: Simple PyMuPDF outperformed complex OCR setup

## Evolution to Production

The experiments in this folder led to the production system in `/api`:

1. **Research Phase** (this folder):
   - 64% accuracy with complex setup
   - Multiple dependencies
   - OCR experimentation

2. **Production Phase** (`/api` folder):
   - 76% accuracy with simpler setup  
   - Fewer dependencies
   - No OCR (PyMuPDF only)

## Reproducing Experiments

To run the experiments:

```bash
cd hf-space

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run experiments
python rag_experiments.py
python chunking_experiments.py

# Evaluate results
python evaluate.py
python analyze_rag_results.py
```

## Why Keep This Folder?

1. **Documentation** - Shows the research process
2. **Reproducibility** - Others can verify experiments
3. **Learning** - Demonstrates iterative improvement
4. **Context** - Explains why production is designed as it is

## Production Code

For the actual production deployment code, see:
- **Backend**: `/api` folder
- **Frontend**: `/app` folder  
- **Case Study**: `PRODUCTION_CASE_STUDY.md`

---

**Note**: This folder is kept for historical/research purposes.  
Production deployment does NOT use this code.
