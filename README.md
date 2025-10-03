# 🚗 ManualAi - AI-Powered Car Manual Assistant

<div align="center">
  
[![Next.js](https://img.shields.io/badge/Next.js-14.2-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

**Transform your car manual into an intelligent AI assistant**

[Live Demo](https://manual-ai-psi.vercel.app) • [Report Bug](https://github.com/agapemiteu/ManualAi/issues) • [Request Feature](https://github.com/agapemiteu/ManualAi/issues)

</div>

---

## ✨ Features

- 🤖 **AI-Powered RAG** - Natural conversations with your car manual using advanced retrieval-augmented generation
- 📚 **Multi-Manual Support** - Upload and manage multiple manuals simultaneously
- 🔍 **Smart Search** - Intelligent query expansion with semantic understanding
- 🎯 **Context-Aware Responses** - Detects urgency, safety concerns, and question types
- ⚠️ **Safety First** - Provides warnings and professional guidance when needed
- 🌐 **Brand Agnostic** - Neutralizes brand-specific references for universal answers
- 📱 **Responsive UI** - Mobile-friendly interface built with Tailwind CSS

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm/yarn
- **Python** 3.10+
- **pip** package manager

### 1. Clone the Repository

```bash
git clone https://github.com/agapemiteu/ManualAi.git
cd ManualAi
```

### 2. Install Frontend Dependencies

```bash
npm install
```

### 3. Install Backend Dependencies

```bash
cd api
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create `.env.local` in the root directory:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### 5. Start the Backend Server

```bash
cd api
uvicorn main:app --reload
```

Backend will run on `http://localhost:8000`

### 6. Start the Frontend

```bash
npm run dev
```

Frontend will run on `http://localhost:3000`

---

## 🏗️ Architecture

```
Next.js Frontend (TypeScript) → FastAPI Backend (Python) → ChromaDB Vector Store
```

**Tech Stack:**
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: FastAPI, LangChain RAG
- **Embeddings**: Sentence-Transformers (all-MiniLM-L6-v2)
- **Vector DB**: ChromaDB
- **Processing**: Unstructured.io

---

## 🧠 Intelligence Features

- **Query Expansion** - Automatically expands queries with synonyms and related terms
- **Relevance Scoring** - Ranks answers using Jaccard similarity (15% threshold)
- **Question Detection** - Identifies procedural vs. warning questions
- **Safety Context** - Detects urgent situations and adds warnings
- **Brand Neutralization** - Converts brand-specific terms to generic equivalents

---

## 📁 Project Structure

```
ManualAi/
├── app/              # Next.js frontend
├── components/       # React components
├── api/              # FastAPI backend
│   ├── main.py
│   ├── rag_chain.py
│   └── vector_store.py
└── data/             # Uploaded manuals
```

---

## 🎯 Usage

1. **Upload** - Select your car manual (PDF/HTML/Image), add details, wait ~30s
2. **Ask** - Type questions naturally ("What does the brake light mean?")
3. **Get Answers** - Receive intelligent, context-aware responses

---

## 🌐 Deployment

**Frontend**: Deployed on [Vercel](https://vercel.com)  
**Backend**: Deployed on [Render](https://render.com)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/agapemiteu/ManualAi)

For detailed instructions, see [RENDER-DEPLOYMENT.md](RENDER-DEPLOYMENT.md)

---

## 🔧 Configuration

Set `NEXT_PUBLIC_API_URL` in `.env.local` to your backend URL:

```env
NEXT_PUBLIC_API_URL=https://manualai-backend.onrender.com
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [LangChain](https://github.com/langchain-ai/langchain) for RAG framework
- [Sentence-Transformers](https://www.sbert.net/) for embeddings
- [ChromaDB](https://www.trychroma.com/) for vector storage
- [Unstructured.io](https://unstructured.io/) for document parsing
- [Vercel](https://vercel.com/) for hosting

---

## 📧 Contact

**Project Maintainer**: Agape Miteu

- Email: miteuagape@gmail.com
- Website: [https://manual-ai-psi.vercel.app](https://manual-ai-psi.vercel.app)

---

<div align="center">

**Built with ❤️ for car enthusiasts everywhere**

⭐ Star us on GitHub — it helps!

</div>
