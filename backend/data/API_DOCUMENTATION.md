# API Documentation

## 🌐 FastAPI Backend API Reference

Base URL: `http://localhost:8000`

## 🔐 Authentication
- GROQ API Key required in environment variables
- No user authentication implemented (single-user system)

## 📡 Chat Endpoints

### General Chat
**POST** `/api/chat/general`

Send a message to the general chat (direct LLM communication).

**Request Body:**
```json
{
    "message": "Hello, how are you?",
    "session_id": "unique-session-id"
}
```

**Response:** Server-Sent Events (SSE) stream
```
data: {"token": "Hello", "session_id": "session-id", "complete": false}
data: {"token": "! I'm", "session_id": "session-id", "complete": false}
data: {"token": " doing well", "session_id": "session-id", "complete": true}
```

### Code Assistant Chat
**POST** `/api/chat/code-assistant`

Send a message to the RAG-enhanced code assistant.

**Request Body:**
```json
{
    "message": "How do I create a new API endpoint?",
    "session_id": "unique-session-id",
    "conversation_history": [
        {"role": "user", "content": "Previous message"},
        {"role": "assistant", "content": "Previous response"}
    ]
}
```

**Response:** Server-Sent Events (SSE) stream
```
data: {"token": "To create", "session_id": "session-id", "complete": false}
data: {"token": " a new API", "session_id": "session-id", "complete": false}
data: {"token": " endpoint...", "session_id": "session-id", "complete": true}
```

## 🤖 Code Assistant Endpoints

### Get Status
**GET** `/api/code-assistant/status`

Get the current status of the RAG system.

**Response:**
```json
{
    "documents_count": 15,
    "chunks_count": 234,
    "last_updated": null,
    "is_ready": true
}
```

### Clear Knowledge Base
**DELETE** `/api/code-assistant/clear`

Clear all documents from the vector store.

**Response:**
```json
{
    "status": "cleared",
    "chunks_deleted": 234,
    "message": "Knowledge base cleared successfully"
}
```

## 👥 Session Management

### Clear Session
**POST** `/api/sessions/{session_id}/clear`

Clear conversation history for a specific session.

**Parameters:**
- `session_id` (path): The session identifier

**Response:**
```json
{
    "status": "cleared",
    "session_id": "session-id",
    "message": "Session cleared successfully"
}
```

## 🔧 Admin Endpoints

### ChromaDB Status
**GET** `/api/admin/chroma/status`

Get detailed ChromaDB status information.

**Response:**
```json
{
    "status": "connected",
    "collection_name": "code_assistant_collection",
    "total_documents": 234,
    "file_types": {
        "python": 45,
        "markdown": 12,
        "json": 8
    },
    "health": true
}
```

### View Documents
**GET** `/api/admin/chroma/documents`

Retrieve stored documents from ChromaDB.

**Query Parameters:**
- `limit` (optional): Number of documents to return (default: 50)

**Response:**
```json
{
    "total_documents": 234,
    "documents": [
        {
            "id": "doc-id-1",
            "content": "Document content...",
            "metadata": {
                "file_name": "main.py",
                "file_type": "python",
                "chunk_type": "function"
            }
        }
    ],
    "limit": 50
}
```

### Search Documents
**GET** `/api/admin/chroma/search`

Search documents using vector similarity.

**Query Parameters:**
- `query` (required): Search query string
- `limit` (optional): Number of results (default: 10)

**Response:**
```json
{
    "query": "authentication",
    "results_count": 5,
    "documents": ["Document content 1", "Document content 2"],
    "metadatas": [{"file_name": "auth.py"}, {"file_name": "login.py"}],
    "distances": [0.1234, 0.2345]
}
```

### List Collections
**GET** `/api/admin/chroma/collections`

List all ChromaDB collections.

**Response:**
```json
{
    "collections": [
        {
            "name": "code_assistant_collection",
            "id": "collection-id",
            "document_count": 234,
            "metadata": {}
        }
    ],
    "total_collections": 1
}
```

### Clear Database
**DELETE** `/api/admin/chroma/clear`

Clear all data from ChromaDB.

**Response:**
```json
{
    "status": "success",
    "deleted_chunks": 234,
    "message": "Database cleared successfully"
}
```

## 🏥 Health Check

### System Health
**GET** `/health`

Check overall system health.

**Response:**
```json
{
    "status": "healthy",
    "app": "ChatGPT Clone with RAG Code Assistant",
    "version": "1.0.0",
    "groq_api": "configured",
    "chroma_db": "connected",
    "rag_pipeline": {
        "ready": true,
        "chunks": 234,
        "embedding_provider": "groq"
    }
}
```

## 📊 Response Formats

### Success Response
```json
{
    "status": "success",
    "data": { /* response data */ },
    "message": "Operation completed successfully"
}
```

### Error Response
```json
{
    "detail": "Error description",
    "status_code": 400,
    "error_type": "ValidationError"
}
```

### Streaming Response (SSE)
```
data: {"token": "partial", "complete": false}
data: {"token": " response", "complete": true}
```

## 🔧 Configuration

### Environment Variables
```bash
GROQ_API_KEY=your_api_key_here
GROQ_CHAT_MODEL=llama-3.1-8b-instant
CHROMA_PERSIST_DIR=/data/chroma
DEBUG=false
```

### Model Configuration
- **Default Model**: `llama-3.1-8b-instant`
- **Alternative Models**: `llama-3.1-70b-versatile`, `gemma2-9b-it`
- **Max Tokens**: 2048
- **Temperature**: 0.7

## 🚀 Usage Examples

### cURL Examples

#### General Chat
```bash
curl -X POST "http://localhost:8000/api/chat/general" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "session_id": "test-session"}'
```

#### Check Status
```bash
curl "http://localhost:8000/api/code-assistant/status"
```

#### Search Documents
```bash
curl "http://localhost:8000/api/admin/chroma/search?query=authentication&limit=5"
```

### JavaScript/Frontend Examples

#### Streaming Chat
```javascript
const response = await fetch('/api/chat/general', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message: 'Hello!',
        session_id: 'session-123'
    })
});

// Handle streaming response
const reader = response.body.getReader();
while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    const chunk = new TextDecoder().decode(value);
    const lines = chunk.split('\n');
    
    for (const line of lines) {
        if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            console.log(data.token);
        }
    }
}
```

## 🔍 Interactive API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation where you can:
- Test all endpoints
- View request/response schemas
- See parameter descriptions
- Execute API calls directly
