# RAG System Implementation Guide

## 🧠 RAG (Retrieval-Augmented Generation) Overview

The RAG system enhances the ChatGPT clone with context-aware responses by combining document retrieval with language model generation.

## 🔄 RAG Pipeline Flow

### 1. Document Ingestion
```
Manual Files → Document Processor → Chunking → Embeddings → Vector Store
```

### 2. Query Processing
```
User Query → Embedding → Similarity Search → Context Retrieval → LLM Generation
```

### 3. Response Generation
```
Retrieved Context + User Query + Conversation History → Groq LLM → Streaming Response
```

## 📊 Core Components

### Vector Store (ChromaDB)
```python
# Configuration
CHROMA_PERSIST_DIR = "/data/chroma"
CHROMA_COLLECTION_NAME = "code_assistant_collection"

# Features:
- Persistent storage
- Similarity search
- Metadata filtering
- Batch operations
```

### Embedding System
```python
class EmbeddingService:
    # Hash-based fallback system (lightweight)
    def _simple_hash_embedding(self, text: str, dimension: int = 384):
        # Creates deterministic embeddings from text hash
        # Fallback when ML libraries unavailable
```

### Document Processing
```python
# Supported file types:
- Python (.py) - Function/class level chunking
- JavaScript (.js, .ts) - Module/function chunking  
- JSON (.json) - Structure-aware processing
- Markdown (.md) - Section-based chunking
- Text (.txt) - Paragraph chunking
- Configuration files (.yaml, .toml, .ini)
```

### Chunking Strategies
```python
# Code files:
- Function-level chunks
- Class-level chunks  
- Import statements
- Global variables

# Documentation:
- Section-based chunks
- Paragraph-level chunks
- Code block extraction

# Configuration:
- Key-value pair chunks
- Nested structure preservation
```

## 🔧 RAG Pipeline Implementation

### Main Pipeline Class
```python
class RAGPipeline:
    def __init__(self):
        self.vectorstore = VectorStoreService()
        self.llm = LLMService()
        self.embedding = EmbeddingService()
        self.chunking = ChunkingService()
        self.document_processor = DocumentProcessor()
```

### Key Methods

#### 1. Process Query
```python
async def process_query(
    self, 
    query: str, 
    session_id: str,
    conversation_history: List[Dict] = None,
    top_k: int = 8
) -> AsyncGenerator[str, None]:
    # Main RAG processing pipeline
    # 1. Search similar chunks
    # 2. Build context
    # 3. Generate response
    # 4. Stream tokens
```

#### 2. Search Similar Chunks
```python
async def search_similar_chunks(self, query: str, top_k: int = 8):
    # Vector similarity search
    # Returns relevant document chunks
    # Includes metadata and similarity scores
```

#### 3. Build Context
```python
def _build_context_from_chunks(self, chunks: List[Dict]) -> str:
    # Combines retrieved chunks into coherent context
    # Handles deduplication
    # Maintains source attribution
```

## 📝 Prompt Engineering

### Context Integration
```python
# System prompt template
SYSTEM_PROMPT = """
You are a helpful coding assistant with access to project documentation and code.

Context from project files:
{context}

Instructions: Answer based on the provided code context. 
If generating code, match the existing patterns and style.
Be specific and reference the relevant files when appropriate.
"""
```

### Query Types
1. **Code Generation**: "Create a new API endpoint for user management"
2. **Debugging**: "Fix this authentication error in the login function"  
3. **Architecture**: "How should I structure the database models?"
4. **Code Review**: "Review this function for security issues"
5. **Integration**: "How do I add JWT authentication to the API?"

## 🎯 RAG Optimizations

### Performance
- Async operations throughout
- Efficient vector operations
- Streaming responses
- Connection pooling
- Batch processing

### Quality
- Intelligent chunking by file type
- Metadata preservation
- Context relevance scoring
- Deduplication
- Source attribution

### Scalability
- Configurable chunk sizes
- Adjustable retrieval parameters
- Memory-efficient processing
- Incremental updates

## 📊 System Status and Monitoring

### Status Endpoint
```python
GET /api/code-assistant/status
{
    "documents_count": 15,
    "chunks_count": 234,
    "is_ready": true,
    "last_updated": "2025-01-01T00:00:00Z"
}
```

### Health Checks
- ChromaDB connectivity
- Embedding service status
- LLM API availability
- Pipeline readiness

## 🔍 Search and Retrieval

### Similarity Search
```python
# Vector similarity with metadata filtering
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=top_k,
    include=['documents', 'metadatas', 'distances']
)
```

### Metadata Filtering
```python
# Filter by file type, function name, etc.
metadata_filters = {
    "file_type": "python",
    "chunk_type": "function"
}
```

## 🛠️ Configuration Options

### RAG Parameters
```python
RETRIEVAL_TOP_K = 8          # Number of chunks to retrieve
CHUNK_SIZE_TOKENS = 500      # Maximum chunk size
CHUNK_OVERLAP_TOKENS = 50    # Overlap between chunks
MAX_CONVERSATION_HISTORY = 10 # History context limit
```

### Embedding Configuration
```python
EMBEDDING_PROVIDER = "groq"   # or "local"
EMBEDDING_DIMENSION = 384     # Vector dimension
```

## 🚀 Usage Examples

### Adding New Documents
1. Place files in `/backend/data/` directory
2. Restart backend container
3. Files automatically processed and indexed
4. Available for RAG queries

### Querying the System
```python
# Code generation
"Create a new FastAPI endpoint for user registration"

# Debugging  
"Why is my authentication middleware not working?"

# Architecture
"Show me the database schema for the user model"
```

### Clearing the Knowledge Base
```python
DELETE /api/code-assistant/clear
# Removes all documents from vector store
```

## 🔧 Troubleshooting

### Common Issues
1. **No documents found**: Check `/backend/data/` directory
2. **Poor search results**: Adjust `RETRIEVAL_TOP_K` parameter
3. **Slow responses**: Optimize chunk sizes
4. **Memory issues**: Reduce batch sizes

### Debug Endpoints
- `/api/admin/chroma/status` - System status
- `/api/admin/chroma/documents` - View stored documents
- `/api/admin/chroma/search` - Test search functionality
