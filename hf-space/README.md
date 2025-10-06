---
title: ManualAi Backend
emoji: 🚗
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# ManualAi Backend API

AI-powered car manual assistant backend using FastAPI, LangChain, and RAG.

## Features

- 🤖 RAG-based Q&A system
- 📚 Multi-manual support
- 🔍 Semantic search with embeddings
- ⚡ FastAPI REST API

## API Endpoints

- `GET /` - Health check
- `GET /api/manuals` - List all manuals
- `POST /api/manuals` - Upload new manual (`replace=true` to overwrite an existing manual_id)
- `DELETE /api/manuals/{manual_id}` - Remove a manual and its vector store artifacts
- `POST /api/chat` - Chat with manuals

## Tech Stack

- FastAPI
- LangChain
- ChromaDB
- Sentence Transformers
- Unstructured.io

## Frontend

Live at: https://manual-ai-psi.vercel.app

# Rebuild trigger - 2025-10-06 08:11:41


Last updated: 2025-10-06 09:00:57
