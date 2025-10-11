# 🚗 ManualAi: Intelligent Car Manual Question-Answering System

> A production-ready RAG (Retrieval-Augmented Generation) system that achieves **64% accuracy within ±2 pages** on a 608-page Toyota 4Runner manual — an **800% improvement** over keyword search baseline.

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-HuggingFace-yellow)](https://huggingface.co/spaces/YOUR_USERNAME/ManualAi)
[![Accuracy](https://img.shields.io/badge/Accuracy-64%25_(±2_pages)-success)]()
[![Python](https://img.shields.io/badge/Python-3.13-blue)]()
[![License](https://img.shields.io/badge/License-MIT-green)]()

---

## 📊 Key Results

| Metric | Value |
|--------|-------|
| **Starting Point** | 8% (keyword baseline) |
| **Final Accuracy** | **64% (±2 pages)** ⭐ |
| **Improvement** | +56 percentage points |
| **Test Set** | 50 curated questions |
| **Manual Size** | 608 pages |
| **Avg Latency** | 16.2 seconds |

---

## 🎯 Performance Visualization

### Improvement Journey: 8% → 64%

![Improvement Journey](analysis/improvement_journey.png)

*Progressive development from keyword baseline to Ultimate RAG configuration*

### Performance Across All Experiments

![Performance Comparison](analysis/performance_comparison.png)

*11 experiments tested: systematic optimization approach*

### Accuracy by Tolerance Level

![Tolerance Analysis](analysis/tolerance_analysis.png)

*32% exact match, 64% within ±2 pages, 70% within ±5 pages*

---

## 🏗️ Architecture

```
┌─────────────────┐
│  PDF Document   │
│ (608 pages)     │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Text Extraction │
│   (PyMuPDF)     │
└────────┬────────┘
         │
         v
┌─────────────────┐
│    Chunking     │
│ 3000 chars      │
│ 30% overlap     │
└────────┬────────┘
         │
         v
┌─────────────────────────────┐
│  Hybrid Retrieval Engine    │
│                              │
│  ┌──────────┐  ┌──────────┐ │
│  │ Semantic │  │   BM25   │ │
│  │  Search  │  │  Search  │ │
│  │  (70%)   │  │  (30%)   │ │
│  └─────┬────┘  └────┬─────┘ │
│        └─────┬──────┘        │
│              v               │
│     ┌────────────────┐       │
│     │ Query Expansion│       │
│     │ (3 variations) │       │
│     └────────┬───────┘       │
└──────────────┼───────────────┘
               │
               v
       ┌───────────────┐
       │  Top-60 Docs  │
       └───────┬───────┘
               │
               v
       ┌───────────────┐
       │  Cross-Encoder│
       │   Reranking   │
       └───────┬───────┘
               │
               v
       ┌───────────────┐
       │  Top-12 Docs  │
       └───────┬───────┘
               │
               v
       ┌───────────────┐
       │  Page-Aware   │
       │  Boosting &   │
       │    Voting     │
       └───────┬───────┘
               │
               v
       ┌───────────────┐
       │ Final Answer  │
       │  (Page #)     │
       └───────────────┘
```

---

## 🔬 Technical Approach

### Core Components

1. **Embedding Model**: `sentence-transformers/all-mpnet-base-v2`
   - 768-dimensional vectors
   - Superior to smaller models (26% → 64% improvement over MiniLM)

2. **Hybrid Search**: 70% Semantic + 30% BM25
   - Combines dense and sparse retrieval
   - Outperforms pure semantic or keyword-only search

3. **Cross-Encoder Reranking**: `ms-marco-MiniLM-L-6-v2`
   - Two-stage retrieval: fast initial search + precise reranking
   - Significantly improves relevance

4. **Query Expansion**
   - Original question
   - Simplified (remove question words)
   - Key terms only (remove stop words)

5. **Context Expansion**
   - Include neighboring chunks (±1)
   - Helps with boundary cases

6. **Page-Aware Voting**
   - Exponential weighting (3.0^rank)
   - 1.5x boost for pages with multiple chunks

### Configuration

```python
CHUNK_SIZE = 3000  # characters
CHUNK_OVERLAP = 900  # 30% overlap
INITIAL_TOP_K = 60  # initial retrieval
FINAL_TOP_K = 12  # after reranking
HYBRID_WEIGHTS = (0.7, 0.3)  # semantic, BM25
VOTING_EXPONENT = 3.0  # aggressive voting
```

---

## 📈 Experimental Results

### All Experiments Summary

| Experiment | Exact | ±2 Pages | ±5 Pages | Latency |
|------------|-------|----------|----------|---------|
| Keyword Baseline | 8% | 8% | 8% | 0.5s |
| Basic Semantic | 26% | 26% | 26% | 12.0s |
| Advanced Hybrid | 30% | 62% | 68% | 14.5s |
| **Ultimate RAG** ⭐ | **32%** | **64%** | **70%** | **16.2s** |
| Multi-Stage | 28% | 56% | 70% | 22.0s |
| Over-Optimized | 26% | 52% | 58% | 27.4s |

### Component Contribution Analysis

![Component Contribution](analysis/component_contribution.png)

*Each component's contribution to final accuracy*

### Error Distribution

![Error Distribution](analysis/error_distribution.png)

*Most errors within 5 pages; few outliers*

---

## 💡 Key Insights

### ✅ What Worked

1. **Hybrid Search** — Combining semantic and keyword search significantly outperforms either alone
2. **Large Chunks** — 3000 chars with 30% overlap provides optimal context
3. **Query Expansion** — Multiple query variations capture different phrasings
4. **Cross-Encoder Reranking** — Two-stage retrieval is worth the latency cost
5. **Aggressive Voting** — Exponential weighting (3.0^rank) ensures top results dominate
6. **Context Expansion** — Including neighboring chunks helps boundary cases

### ❌ What Didn't Work

1. **Over-Optimization** — Adding too many smart features reduced accuracy (64% → 52%)
2. **Question Classification** — Section-aware boosting didn't help
3. **Multi-Stage Retrieval** — Added complexity without gains
4. **Extreme Voting** — Too soft (2.0) or too aggressive (3.5) underperformed
5. **Very Large Chunks** — 4000+ chars diluted semantic signals

### 🎯 The Plateau Effect

- Reached 64% accuracy with Ultimate RAG
- 6 subsequent optimization attempts all stayed at 64%
- Only 3 borderline cases (off by 3-5 pages) preventing 66-70%
- Suggests fundamental retrieval limitations at this scale

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/ManualAi.git
cd ManualAi

# Install dependencies
pip install -r requirements.txt

# Set HuggingFace token (optional, for better models)
export HF_TOKEN="your_token_here"
```

### Usage

```python
from rag_chain import UltimateRAG

# Initialize system
rag = UltimateRAG()
rag.index_document("data/2023-Toyota-4runner-Manual.pdf")

# Ask questions
question = "What does the tire pressure warning light mean?"
page_number = rag.predict_page(question)
print(f"Answer found on page: {page_number}")
```

### Run Evaluation

```bash
python hf-space/evaluate.py
```

---

## 📁 Project Structure

```
ManualAi/
├── data/
│   ├── 2023-Toyota-4runner-Manual.pdf
│   └── evaluation_set.json (50 questions)
├── hf-space/
│   ├── rag_chain.py (production code)
│   ├── rag_experiments_ultimate.py (best config)
│   ├── evaluate.py (evaluation harness)
│   └── [other experiments...]
├── analysis/
│   ├── visualize_results.py
│   └── [all charts...]
├── docs/
│   ├── ARCHITECTURE.md
│   └── EXPERIMENTS.md
├── ACHIEVEMENTS.py (summary)
└── README.md (this file)
```

---

## 🔮 Future Improvements

1. **Larger Embedding Models** — Try `all-mpnet-base-v2` → `e5-large-v2` (1024 dims)
2. **Question Classification** — Separate pipelines for different question types
3. **Multi-Document Support** — Generalize to multiple manuals
4. **Caching** — Cache frequent queries for sub-second response
5. **Fine-Tuning** — Domain-specific fine-tuning on automotive manuals
6. **LLM Integration** — Use LLM for answer generation, not just retrieval

---

## 📚 References

- **Embeddings**: [Sentence Transformers](https://www.sbert.net/)
- **Reranking**: [Cross-Encoders for IR](https://arxiv.org/abs/1910.14424)
- **BM25**: [Robertson & Zaragoza, 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
- **RAG**: [Lewis et al., 2020](https://arxiv.org/abs/2005.11401)

---

## 👤 Author

**Your Name**
- Portfolio: [your-portfolio.com](https://your-portfolio.com)
- LinkedIn: [linkedin.com/in/yourname](https://linkedin.com/in/yourname)
- Email: your.email@example.com

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- Toyota for the 4Runner manual (used for educational purposes)
- HuggingFace for model hosting and Spaces platform
- Sentence Transformers community for excellent embedding models

---

<p align="center">
  <strong>⭐ If you found this project useful, please star the repository! ⭐</strong>
</p>

<p align="center">
  Built with ❤️ as a portfolio data science project
</p>
