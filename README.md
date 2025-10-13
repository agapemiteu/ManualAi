# ManualAi - AI-Powered Car Manual Assistant 🚗📚

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://manual-ai-psi.vercel.app)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> An intelligent RAG (Retrieval-Augmented Generation) system that helps you find information in car manuals instantly. Achieved **76% accuracy** in production, outperforming the research prototype by 12%.

![ManualAi Banner](public/images/banner.png)

---

## 🎯 Project Overview

**ManualAi** transforms how people interact with car owner's manuals. Instead of flipping through 600+ pages, users ask natural language questions and get instant, accurate answers with source page references.

### Key Features

✨ **Natural Language Queries** - Ask questions in plain English  
📄 **Large Document Support** - Process manuals up to 20MB (600+ pages)  
🎯 **High Accuracy** - 76% accuracy within ±2 pages  
⚡ **Fast Processing** - 65 seconds for 608-page manual  
🔍 **Source Attribution** - Always shows page numbers  
🌐 **Production Ready** - Deployed on Vercel + HuggingFace

---

## 📊 Performance Highlights

| Metric | Value |
|--------|-------|
| **Production Accuracy** | 76% (±2 pages) |
| **Research Prototype** | 64% (with OCR) |
| **Processing Speed** | 65s for 608 pages |
| **Document Size** | Up to 20MB supported |
| **Ground Truth Set** | 50 questions across 6 categories |

**Key Finding**: Simpler approach (PyMuPDF only) outperformed complex setup (OCR + NLTK) by 12%.

---

## 🚀 Live Demo

**Try it now**: [manual-ai-psi.vercel.app](https://manual-ai-psi.vercel.app)

1. Upload your car manual (PDF, up to 20MB)
2. Wait 1-3 minutes for processing
3. Ask questions in natural language
4. Get answers with page references

---

## 📓 Full Analysis Report

For detailed analysis, visualizations, and insights, see the full report in Google Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/agapemiteu/ManualAi/blob/main/notebooks/ManualAi_Full_Analysis.ipynb)

**What's in the report:**
- 📊 Detailed accuracy analysis and visualizations
- 🔬 Experiment results and methodology
- 💡 Personal insights and lessons learned
- 📈 Performance comparisons across configurations
- 🎯 Category-wise breakdown
- 🛠️ Technical deep dive

---

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Next.js   │─────▶│   FastAPI    │─────▶│  ChromaDB   │
│  Frontend   │      │   Backend    │      │ Vector Store│
│  (Vercel)   │      │(HuggingFace) │      │             │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   Groq API   │
                     │ (LLM Model)  │
                     └──────────────┘
```

**Tech Stack:**
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.10
- **Document Processing**: PyMuPDF (text extraction)
- **Embeddings**: sentence-transformers/all-mpnet-base-v2
- **Vector Store**: ChromaDB (HNSW index)
- **LLM**: Groq API (llama-3.1-8b-instant)

---

## 🛠️ Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+
- Groq API key ([get one here](https://groq.com))

### Installation

```bash
# Clone the repository
git clone https://github.com/agapemiteu/ManualAi.git
cd ManualAi

# Install frontend dependencies
npm install

# Install backend dependencies
cd api
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env.local
# Add your GROQ_API_KEY to .env.local
```

### Running Locally

```bash
# Terminal 1: Start backend
cd api
uvicorn main:app --reload --port 8000

# Terminal 2: Start frontend
npm run dev
```

Visit `http://localhost:3000`

---

## 📁 Project Structure

```
ManualAi/
├── api/                    # FastAPI backend
│   ├── main.py            # API endpoints
│   ├── rag_chain.py       # RAG implementation
│   ├── vector_store.py    # ChromaDB setup
│   └── document_loader.py # PDF processing
├── app/                   # Next.js frontend
│   ├── page.tsx          # Home page
│   └── upload/           # Upload interface
├── components/           # React components
├── scripts/             # Utility scripts
│   ├── evaluate_production.py
│   └── test_full_upload.py
├── data/                # Evaluation dataset
│   └── evaluation_set.json
├── notebooks/           # 📊 Analysis notebooks
│   └── ManualAi_Full_Analysis.ipynb
├── analysis/           # Results & visualizations
└── docs/              # GitHub Pages
```

---

## 📈 Evaluation Results

Tested on 50 ground truth questions from 2023 Toyota 4Runner Owner's Manual (608 pages):

### Accuracy by Tolerance

| Tolerance | Accuracy |
|-----------|----------|
| Exact match | 42% |
| Within ±2 pages | **76%** ⭐ |
| Within ±5 pages | 76% |
| Within ±10 pages | 78% |

### Performance by Category

| Category | Accuracy | Questions |
|----------|----------|-----------|
| System Knowledge | 88% | 8 |
| Advanced Systems | 83% | 6 |
| Maintenance | 78% | 9 |
| Safety | 75% | 8 |
| Troubleshooting | 75% | 8 |
| Miscellaneous | 64% | 11 |

**See detailed analysis in the [Colab notebook](https://colab.research.google.com/github/agapemiteu/ManualAi/blob/main/notebooks/ManualAi_Full_Analysis.ipynb)** 📊

---

## 🎓 Key Learnings

### 1. Simpler is Often Better
- Complex approach (OCR + NLTK): 64% accuracy
- Simple approach (PyMuPDF only): **76% accuracy**
- Lesson: Start simple, add complexity only when needed

### 2. Production ≠ Development
- What works locally may break in production
- Deployment constraints can lead to better solutions
- Always test in production-like environments

### 3. Evaluation is Critical
- Ground truth dataset essential for measuring progress
- Multiple tolerance levels reveal different insights
- Category-wise analysis shows where to focus improvements

---

## 🔮 Future Improvements

- [ ] Hybrid search (semantic + keyword)
- [ ] Cross-encoder reranking
- [ ] Multi-manual search
- [ ] Mobile app
- [ ] Voice queries
- [ ] Bookmark/save functionality

---

## 📚 Documentation

- **[Full Analysis Report](https://colab.research.google.com/github/agapemiteu/ManualAi/blob/main/notebooks/ManualAi_Full_Analysis.ipynb)** - Complete analysis with visualizations
- **[GitHub Pages](https://agapemiteu.github.io/ManualAi/)** - Project showcase
- **[Upload Guidelines](UPLOAD_GUIDELINES.md)** - How to prepare manuals
- **[Scripts README](scripts/README.md)** - Testing and evaluation tools

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Agape Miteu**

- GitHub: [@agapemiteu](https://github.com/agapemiteu)
- LinkedIn: [Add your LinkedIn]
- Portfolio: [Add your portfolio]

---

## 🙏 Acknowledgments

- Toyota for the 2023 4Runner Owner's Manual (used for evaluation)
- Groq for fast LLM inference API
- HuggingFace for free deployment hosting
- Vercel for frontend hosting

---

## ⭐ Show Your Support

If this project helped you or you found it interesting, please give it a ⭐️!

---

<div align="center">

**[Live Demo](https://manual-ai-psi.vercel.app)** • 
**[Analysis Report](https://colab.research.google.com/github/agapemiteu/ManualAi/blob/main/notebooks/ManualAi_Full_Analysis.ipynb)** • 
**[Documentation](https://agapemiteu.github.io/ManualAi/)**

Made with ❤️ by Agape Miteu

</div>
