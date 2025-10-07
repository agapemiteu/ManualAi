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

- 🤖 **AI-Powered RAG** - Natural conversations powered by Llama 3.1 8B via Groq API
- 📚 **Multi-Manual Support** - Upload, view, and delete multiple manuals
- 🔍 **Manual-Aware Responses** - AI cites specific page numbers from your manual
- 💬 **Human-Friendly Tone** - Conversational, helpful responses (not robotic)
- ⚡ **Lightning Fast** - Groq's inference speed delivers instant answers
- 📱 **Responsive UI** - Clean, mobile-friendly interface built with Next.js & Tailwind CSS
- 🗑️ **Manual Management** - Easy upload and deletion of manuals

---

## 🚀 Quick Start

### Try It Live

👉 **[https://manual-ai-psi.vercel.app](https://manual-ai-psi.vercel.app)** - No installation needed!

### Run Locally

#### Prerequisites
- **Node.js** 18+
- **Groq API Key** - Get free at [console.groq.com](https://console.groq.com)

#### 1. Clone & Install

```bash
git clone https://github.com/agapemiteu/ManualAi.git
cd ManualAi
npm install
```

#### 2. Configure Environment

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=https://agapemiteu-manualai.hf.space
```

Or run your own backend on HuggingFace Spaces (see `hf-space/` directory)

#### 3. Start Development Server

```bash
npm run dev
```

Open `http://localhost:3000`

---

## 🏗️ Architecture

```
Next.js Frontend → FastAPI Backend → ChromaDB → Groq API (Llama 3.1 8B)
     (Vercel)      (HuggingFace Spaces)   (Ephemeral)    (Free Tier)
```

**Tech Stack:**
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: FastAPI, LangChain
- **LLM**: Llama 3.1 8B Instant via Groq API
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector Store**: ChromaDB (ephemeral, session-based)
- **Deployment**: Vercel (frontend) + HuggingFace Spaces (backend)

---

## 🧠 How It Works

1. **Upload Your Manual** - PDF is processed and split into searchable chunks
2. **Embeddings Created** - Text converted to vectors using sentence-transformers
3. **Stored in ChromaDB** - Vector database enables semantic search
4. **Ask Questions** - Your query finds relevant manual sections
5. **AI Answers** - Groq's Llama 3.1 8B generates human-friendly responses with page references

---

## 🎯 Usage

1. **Upload** - Drop your car manual PDF, add make/model/year
2. **Wait ~30s** - Manual is processed and indexed
3. **Ask Anything** - "What does the check engine light mean?"
4. **Get Smart Answers** - AI responds with specific page references from YOUR manual
5. **Manage Manuals** - View uploaded manuals, delete when done

---

## 🌐 Deployment

**Live Site**: [manual-ai-psi.vercel.app](https://manual-ai-psi.vercel.app)

- **Frontend**: Vercel (auto-deploys from `main` branch)
- **Backend**: HuggingFace Spaces (Docker container)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/agapemiteu/ManualAi)

### Deploy Your Own Backend

1. Create account on [HuggingFace Spaces](https://huggingface.co/spaces)
2. Create new Space (Docker SDK)
3. Copy files from `hf-space/` directory
4. Add `GROQ_API_KEY` secret in Space settings
5. Update `NEXT_PUBLIC_API_URL` in your Vercel deployment

---

## 🔧 Configuration

**Frontend Environment** (`.env.local`):
```env
NEXT_PUBLIC_API_URL=https://agapemiteu-manualai.hf.space
```

**Backend Environment** (HuggingFace Spaces secrets):
```env
GROQ_API_KEY=your_groq_api_key_here
```

Get your free Groq API key at [console.groq.com](https://console.groq.com)

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

- [Groq](https://groq.com/) for lightning-fast LLM inference
- [LangChain](https://github.com/langchain-ai/langchain) for RAG framework
- [HuggingFace](https://huggingface.co/) for free backend hosting
- [Sentence-Transformers](https://www.sbert.net/) for embeddings
- [ChromaDB](https://www.trychroma.com/) for vector storage
- [Vercel](https://vercel.com/) for frontend hosting

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
