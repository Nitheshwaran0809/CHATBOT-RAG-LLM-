# ChatGPT Clone with RAG Code Assistant

A production-ready conversational AI platform with integrated RAG system for code generation assistance.

## Features

- **General Chat Mode**: Standard conversational AI powered by Groq LLM
- **Code Assistant Mode**: RAG-enhanced mode with intelligent code generation, debugging, and technical guidance
- **Multi-format Document Processing**: Support for code files, configs, docs, and more
- **ChatGPT-inspired Dark Theme**: Modern, responsive UI with glassmorphism effects
- **Streaming Responses**: Real-time token-by-token response generation
- **Session Management**: Persistent conversation history per user session

## Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: Streamlit with custom dark theme
- **Vector DB**: ChromaDB (persistent storage)
- **LLM/Embeddings**: Groq API + sentence-transformers (fallback)
- **Containerization**: Docker + Docker Compose

## Quick Start

1. **Clone and setup**:
   ```bash
   git clone <repository>
   cd chatgpt-clone
   cp .env.example .env
   ```

2. **Configure environment**:
   Edit `.env` and add your Groq API key:
   ```
   GROQ_API_KEY=your_actual_groq_api_key_here
   ```

3. **Run with Docker**:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Usage

### General Chat Mode
- Standard conversational AI
- No file upload required
- Direct Groq LLM responses

### Code Assistant Mode
1. Upload your project files (code, configs, docs)
2. Ask questions like:
   - "Generate authentication code"
   - "Fix this error in my database connection"
   - "How do I implement JWT tokens?"
3. Get responses based on your uploaded project context

## Supported File Types

- **Code**: `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.go`, `.rs`, etc.
- **Config**: `.json`, `.yaml`, `.toml`, `.env`, `.xml`
- **Docs**: `.md`, `.txt`, `.pdf`, `.docx`
- **Database**: `.sql`, `.db`
- **Web**: `.html`, `.css`, `.scss`
- **Data**: `.csv`, `.xlsx`

## Architecture

```
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── models/    # Pydantic schemas
│   │   ├── services/  # Business logic (RAG, LLM, etc.)
│   │   ├── routers/   # API endpoints
│   │   └── core/      # Prompts, constants
│   └── data/chroma/   # Vector database storage
│
├── frontend/          # Streamlit application
│   ├── components/    # UI components
│   ├── services/      # API client
│   ├── styles/        # CSS themes
│   └── utils/         # Helpers
│
└── docker-compose.yml # Container orchestration
```

## Development

### Phase 1: Core Chat (No RAG)
- ✅ Basic FastAPI backend
- ✅ Groq LLM integration
- ✅ Streamlit frontend with dark theme
- ✅ General conversation mode

### Phase 2: RAG Infrastructure
- ✅ ChromaDB integration
- ✅ Custom RAG pipeline (no frameworks)
- ✅ Code assistant endpoint

### Phase 3: Document Processing
- ✅ Multi-format file processing
- ✅ Intelligent chunking (code-aware)
- ✅ Embedding generation

### Phase 4: Code Assistant Features
- ✅ Context-aware code generation
- ✅ Metadata-rich retrieval
- ✅ Custom prompts for coding tasks

### Phase 5: Data Ingestion UI
- ✅ File upload interface
- ✅ Progress indicators
- ✅ Document management

## API Endpoints

- `POST /api/chat/general` - Standard chat
- `POST /api/chat/code-assistant` - RAG-enhanced chat
- `POST /api/code-assistant/ingest` - Upload files
- `GET /api/code-assistant/status` - Check upload status
- `DELETE /api/code-assistant/clear` - Clear documents
- `GET /health` - Health check

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details
