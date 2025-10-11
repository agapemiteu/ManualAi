---
title: ManualAi - Car Manual Q&A
emoji: 🚗
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
license: mit
---

# ManualAi: Intelligent Car Manual Question-Answering System

🚗 **Ask questions about your car manual and get accurate page references!**

## 📊 Performance

- **Accuracy:** 64% within ±2 pages
- **Manual:** 2023 Toyota 4Runner (608 pages)
- **Test Set:** 50 curated questions
- **Improvement:** 800% over keyword baseline (8% → 64%)

## 🏗️ Architecture

Advanced RAG (Retrieval-Augmented Generation) system featuring:

- **Hybrid Search:** 70% semantic + 30% BM25
- **Embedding Model:** all-mpnet-base-v2 (768 dimensions)
- **Reranker:** ms-marco-MiniLM-L-6-v2
- **Query Expansion:** 3 variations per question
- **Context Expansion:** Neighboring chunks included
- **Page-Aware Voting:** Exponential weighting (3.0^rank)

## 🔬 Technical Approach

1. **Document Processing**
   - Chunk size: 3000 characters
   - Overlap: 900 characters (30%)
   
2. **Retrieval Pipeline**
   - Initial retrieval: Top-60 candidates
   - Cross-encoder reranking
   - Final selection: Top-12 chunks
   
3. **Voting Mechanism**
   - Exponential confidence weighting
   - Page clustering bonus (1.5x)

## 📈 Development Journey

| Phase | Accuracy | Method |
|-------|----------|--------|
| Baseline | 8% | Keyword search |
| Basic RAG | 26% | Semantic only |
| Advanced | 62% | Hybrid + reranking |
| **Ultimate** | **64%** | **All optimizations** |

## 🚀 Try It Out

Ask questions like:
- "What does the tire pressure warning light mean?"
- "How often should engine oil be replaced?"
- "What should I do if the braking power low message appears?"

## 📁 Repository

Full code, experiments, and visualizations available at:
**[github.com/agapemiteu/ManualAi](https://github.com/agapemiteu/ManualAi)**

## 👤 Author

**agapemiteu**
- GitHub: [@agapemiteu](https://github.com/agapemiteu)

## 📄 License

MIT License - See repository for details

---

<p align="center">
  <strong>⭐ Star the repo if you find this useful! ⭐</strong>
</p>
