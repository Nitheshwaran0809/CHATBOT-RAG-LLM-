# Backend Architecture Documentation

## 🏗️ FastAPI Backend Structure

### Core Components

#### 1. Main Application (`app/main.py`)
```python
# FastAPI app initialization
app = FastAPI(
    title="ChatGPT Clone with RAG Code Assistant",
    version="1.0.0"
)

# Key features:
- CORS middleware for frontend communication
- Router inclusion for modular API structure
- Startup/shutdown event handlers
- Service initialization and health checks
```

#### 2. Configuration (`app/config.py`)
```python
class Settings(BaseSettings):
    # API Configuration
    APP_NAME: str = "ChatGPT Clone with RAG Code Assistant"
    GROQ_API_KEY: str  # Required
    GROQ_CHAT_MODEL: str = "llama-3.1-8b-instant"
    
    # ChromaDB Configuration
    CHROMA_PERSIST_DIR: str = "/data/chroma"
    CHROMA_COLLECTION_NAME: str = "code_assistant_collection"
    
    # RAG Configuration
    RETRIEVAL_TOP_K: int = 8
    CHUNK_SIZE_TOKENS: int = 500
```

### API Routers

#### 1. Chat Router (`app/routers/chat.py`)
**Endpoints:**
- `POST /api/chat/general` - General chat with Groq LLM
- `POST /api/chat/code-assistant` - RAG-enhanced code assistance

**Features:**
- Streaming responses
- Session management
- Conversation history
- Error handling

#### 2. Code Assistant Router (`app/routers/code_assistant.py`)
**Endpoints:**
- `GET /api/code-assistant/status` - Get RAG system status
- `DELETE /api/code-assistant/clear` - Clear knowledge base

#### 3. Admin Router (`app/routers/admin.py`)
**Endpoints:**
- `GET /api/admin/chroma/status` - ChromaDB status
- `GET /api/admin/chroma/documents` - View stored documents
- `GET /api/admin/chroma/search` - Search documents
- `DELETE /api/admin/chroma/clear` - Clear database

### Services Layer

#### 1. LLM Service (`app/services/llm_service.py`)
```python
class LLMService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_CHAT_MODEL
    
    async def stream_chat_completion(self, messages, temperature=0.7):
        # Streaming chat completion with Groq API
```

#### 2. Vector Store Service (`app/services/vectorstore_service.py`)
```python
class VectorStoreService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME
        )
    
    # Methods:
    - add_documents()
    - search_similar()
    - get_collection_stats()
    - health_check()
```

#### 3. Embedding Service (`app/services/embedding_service.py`)
```python
class EmbeddingService:
    def __init__(self):
        self.embedding_provider = settings.EMBEDDING_PROVIDER
    
    # Features:
    - Hash-based embeddings (lightweight fallback)
    - Configurable embedding providers
    - Async text processing
```

#### 4. RAG Pipeline (`app/services/rag_pipeline.py`)
```python
class RAGPipeline:
    def __init__(self):
        self.vectorstore = VectorStoreService()
        self.llm = LLMService()
        self.embedding = EmbeddingService()
    
    # Key methods:
    - process_query() - Main RAG processing
    - search_similar_chunks() - Vector similarity search
    - generate_response() - LLM response generation
    - get_pipeline_status() - System status
```

#### 5. Document Processor (`app/services/document_processor.py`)
```python
class DocumentProcessor:
    # File type handlers for different formats
    - process_python_file()
    - process_json_file()
    - process_markdown_file()
    - process_text_file()
```

#### 6. Chunking Service (`app/services/chunking_service.py`)
```python
class ChunkingService:
    # Intelligent chunking strategies
    - chunk_code_file() - Function/class level chunking
    - chunk_markdown() - Section-based chunking
    - chunk_json() - Structure-aware chunking
```

### Data Models (`app/models/`)

#### Chat Models
```python
class GeneralChatRequest(BaseModel):
    message: str
    session_id: str

class CodeAssistantRequest(BaseModel):
    message: str
    session_id: str
    conversation_history: Optional[List[Dict[str, str]]] = []
```

#### Code Assistant Models
```python
class CodeAssistantStatus(BaseModel):
    documents_count: int
    chunks_count: int
    last_updated: Optional[str] = None
    is_ready: bool
```

### Error Handling
- Comprehensive try-catch blocks
- Structured error responses
- Logging with different levels
- Graceful degradation

### Security Features
- CORS configuration
- Environment variable protection
- API key validation
- Input sanitization

### Performance Optimizations
- Async/await throughout
- Connection pooling
- Efficient vector operations
- Streaming responses
- Lightweight dependencies
