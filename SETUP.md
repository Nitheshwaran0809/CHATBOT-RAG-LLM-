# Setup Instructions

## Phase 1: Core Chat (No RAG) - COMPLETED ✅

This phase provides a fully functional ChatGPT-like interface with Groq LLM integration.

### Prerequisites

1. **Docker & Docker Compose** installed
2. **Groq API Key** - Get one from [Groq Console](https://console.groq.com/)

### Quick Start

1. **Clone/Download the project**
2. **Configure environment**:
   ```bash
   copy .env.example .env
   ```
   Edit `.env` and add your Groq API key:
   ```
   GROQ_API_KEY=your_actual_groq_api_key_here
   ```

3. **Start the application**:
   ```bash
   # Windows
   start.bat
   
   # Or manually
   docker-compose up --build
   ```

4. **Access the application**:
   - **Frontend**: http://localhost:8501
   - **Backend API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs

### What's Working in Phase 1

✅ **General Chat Mode**: 
- Full conversational AI powered by Groq LLM
- Streaming responses (token by token)
- Session management
- Conversation history
- ChatGPT-inspired dark theme

✅ **Backend API**:
- FastAPI with proper error handling
- Health check endpoint
- Session management
- Streaming chat completions

✅ **Frontend UI**:
- Streamlit with custom CSS
- Dark theme with glassmorphism effects
- Mode selector (General vs Code Assistant)
- Message bubbles with timestamps
- Responsive design

### Testing Phase 1

1. Open http://localhost:8501
2. Select "General Chat" mode
3. Start chatting - you should see:
   - Streaming responses
   - Message history
   - Session persistence
   - Professional dark UI

### Troubleshooting

**Backend not starting?**
- Check if Groq API key is set in `.env`
- Verify Docker is running
- Check logs: `docker-compose logs backend`

**Frontend not connecting?**
- Ensure backend is healthy: http://localhost:8000/health
- Check frontend logs: `docker-compose logs frontend`

**Streaming not working?**
- This is normal behavior - responses should appear token by token
- If responses appear all at once, check browser network tab

### Next Phases (Coming Soon)

🔄 **Phase 2**: RAG Infrastructure (ChromaDB, vector store)
🔄 **Phase 3**: Document Processing (multi-format file support)
🔄 **Phase 4**: Code Assistant Features (context-aware generation)
🔄 **Phase 5**: File Upload UI (drag & drop interface)

### Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │
│   (Streamlit)   │◄──►│   (FastAPI)     │
│   Port: 8501    │    │   Port: 8000    │
└─────────────────┘    └─────────────────┘
                              │
                       ┌─────────────────┐
                       │   Groq LLM      │
                       │   (External)    │
                       └─────────────────┘
```

### File Structure

```
chatgpt/
├── docker-compose.yml          # Container orchestration
├── .env.example               # Environment template
├── start.bat                  # Windows startup script
│
├── backend/                   # FastAPI application
│   ├── app/
│   │   ├── main.py           # FastAPI entry point
│   │   ├── config.py         # Settings & environment
│   │   ├── models/           # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   ├── routers/          # API endpoints
│   │   └── core/             # Constants & prompts
│   ├── Dockerfile
│   └── requirements.txt
│
└── frontend/                  # Streamlit application
    ├── app.py                # Main Streamlit app
    ├── components/           # UI components
    ├── services/             # API client
    ├── styles/               # CSS themes
    ├── utils/                # Helpers
    ├── Dockerfile
    └── requirements.txt
```

Ready to test Phase 1! 🚀
