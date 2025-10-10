# ChatGPT Clone with RAG System - Project Overview

## 🚀 Project Description
This is a production-ready ChatGPT clone with integrated RAG (Retrieval-Augmented Generation) system for code generation assistance. The system provides both general conversational AI and context-aware code assistance.

## 🏗️ Architecture Overview

### Tech Stack
- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit
- **LLM**: Groq API (llama-3.1-8b-instant)
- **Vector Database**: ChromaDB
- **Containerization**: Docker & Docker Compose
- **Embeddings**: Hash-based fallback system

### System Components
1. **Frontend (Streamlit)**: User interface with chat functionality
2. **Backend (FastAPI)**: API server with RAG pipeline
3. **ChromaDB**: Vector storage for document embeddings
4. **Groq LLM**: Language model for chat responses
5. **RAG Pipeline**: Document processing and retrieval system

## 📁 Project Structure
```
chatgpt/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI application entry point
│   │   ├── config.py       # Configuration settings
│   │   ├── routers/        # API route handlers
│   │   ├── services/       # Business logic services
│   │   └── models/         # Pydantic models
│   ├── data/               # Manual data directory for RAG
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Backend container config
├── frontend/               # Streamlit frontend
│   ├── app.py             # Main Streamlit app
│   ├── components/        # UI components
│   ├── services/          # Frontend services
│   └── styles/            # CSS styling
├── docker-compose.yml     # Container orchestration
├── .env                   # Environment variables
└── chroma_viewer.html     # ChromaDB admin interface
```

## 🔧 Key Features

### Chat Modes
1. **General Chat Mode**: Standard conversational AI
2. **Code Assistant Mode**: RAG-enhanced with project context

### RAG System
- Document ingestion from `/backend/data/` directory
- Intelligent chunking by file type
- Vector similarity search
- Context-aware response generation

### Optimizations
- Lightweight build (removed heavy ML dependencies)
- Hash-based embeddings fallback
- Manual data setup instead of file upload
- Fast container startup (~2 minutes)

## 🚀 Deployment
- Dockerized with docker-compose
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- ChromaDB Viewer: chroma_viewer.html

## 🔑 Environment Configuration
- GROQ_API_KEY: Required for LLM functionality
- Model: llama-3.1-8b-instant (current default)
- ChromaDB: Persistent storage in Docker volume

## 📊 Current Status
- ✅ Core chat functionality working
- ✅ RAG pipeline implemented
- ✅ Manual data setup configured
- ✅ Optimized for fast builds
- ✅ Clean, minimal UI
