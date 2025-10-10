# Troubleshooting Guide

## 🚨 Common Issues and Solutions

### 1. GROQ API Issues

#### Model Decommissioned Error
```
Error: The model 'mixtral-8x7b-32768' has been decommissioned
```

**Solution:**
```python
# Update config.py
GROQ_CHAT_MODEL: str = "llama-3.1-8b-instant"

# Or set in .env file
GROQ_CHAT_MODEL=llama-3.1-8b-instant
```

**Available Models:**
- `llama-3.1-8b-instant` - Fast and efficient (recommended)
- `llama-3.1-70b-versatile` - Higher quality, slower
- `gemma2-9b-it` - Google's Gemma model

#### API Key Issues
```
Error: Invalid API key or unauthorized access
```

**Solution:**
1. Check your API key in `.env` file
2. Verify key is active at https://console.groq.com/keys
3. Restart containers after updating key

```bash
# Restart to apply new API key
docker-compose restart backend
```

#### Rate Limit Exceeded
```
Error: Rate limit exceeded for API key
```

**Solution:**
- Wait for rate limit reset
- Consider upgrading GROQ plan
- Implement request queuing in code

### 2. ChromaDB Issues

#### Connection Failed
```
Error: ChromaDB connection failed
```

**Solution:**
```bash
# Check ChromaDB volume
docker volume inspect chatgpt_chroma_data

# Recreate volume if corrupted
docker-compose down -v
docker-compose up --build
```

#### Collection Not Found
```
Error: Collection 'code_assistant_collection' not found
```

**Solution:**
```python
# Auto-create collection in vectorstore_service.py
self.collection = self.client.get_or_create_collection(
    name=settings.CHROMA_COLLECTION_NAME
)
```

#### Embedding Dimension Mismatch
```
Error: Embedding dimension mismatch
```

**Solution:**
```python
# Clear collection and rebuild
DELETE /api/admin/chroma/clear

# Restart backend to reinitialize
docker-compose restart backend
```

### 3. Container Issues

#### Port Already in Use
```
Error: Port 8000 is already in use
```

**Solution:**
```bash
# Find process using port
netstat -ano | findstr :8000

# Kill process (Windows)
taskkill /PID <process_id> /F

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use different external port
```

#### Container Won't Start
```
Error: Container rag_backend exited with code 1
```

**Solution:**
```bash
# Check logs for specific error
docker-compose logs backend

# Common fixes:
# 1. Missing environment variables
# 2. Port conflicts
# 3. Volume permission issues
# 4. Dependency installation failures
```

#### Out of Memory
```
Error: Container killed due to memory limit
```

**Solution:**
```yaml
# Add to docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

### 4. Frontend Issues

#### Streamlit Won't Load
```
Error: This site can't be reached - localhost:8501
```

**Solution:**
```bash
# Check if frontend container is running
docker ps

# Check frontend logs
docker-compose logs frontend

# Restart frontend
docker-compose restart frontend
```

#### Backend Connection Error
```
Error: Connection error - Backend not responding
```

**Solution:**
1. Verify backend is healthy: `curl http://localhost:8000/health`
2. Check network connectivity between containers
3. Verify BACKEND_URL environment variable

```bash
# Check container network
docker network inspect chatgpt_rag-network

# Verify environment variables
docker exec rag_frontend env | grep BACKEND_URL
```

#### Streamlit Caching Issues
```
Error: Streamlit app not updating with changes
```

**Solution:**
```bash
# Clear Streamlit cache
# In browser: Settings > Clear Cache
# Or restart container
docker-compose restart frontend
```

### 5. RAG System Issues

#### No Documents Found
```
Warning: No documents in knowledge base
```

**Solution:**
1. Add files to `backend/data/` directory
2. Restart backend to process files
3. Verify files are supported formats

```bash
# Check data directory
ls -la backend/data/

# Restart backend
docker-compose restart backend

# Check processing logs
docker-compose logs backend | grep "processing"
```

#### Poor Search Results
```
Issue: RAG returns irrelevant results
```

**Solution:**
```python
# Adjust search parameters in config.py
RETRIEVAL_TOP_K: int = 10  # Increase for more context
CHUNK_SIZE_TOKENS: int = 300  # Smaller chunks for precision
CHUNK_OVERLAP_TOKENS: int = 100  # More overlap for context
```

#### Embedding Service Errors
```
Error: Embedding generation failed
```

**Solution:**
```python
# Check embedding service status
GET /api/admin/chroma/status

# Verify fallback is working
# Hash-based embeddings should work without ML libraries
```

### 6. Development Issues

#### Hot Reload Not Working
```
Issue: Changes not reflected in development
```

**Solution:**
```bash
# Ensure volumes are mounted correctly
# Check docker-compose.yml volumes section
volumes:
  - ./backend:/app
  - ./frontend:/app

# Restart with build
docker-compose up --build
```

#### Import Errors
```
Error: ModuleNotFoundError: No module named 'app'
```

**Solution:**
```python
# Check PYTHONPATH in Dockerfile
ENV PYTHONPATH=/app

# Verify __init__.py files exist
touch app/__init__.py
touch app/services/__init__.py
```

#### Database Migration Issues
```
Error: Database schema mismatch
```

**Solution:**
```bash
# Clear ChromaDB data
docker-compose down -v

# Rebuild with fresh data
docker-compose up --build
```

## 🔧 Debug Commands

### Container Debugging
```bash
# Enter backend container
docker exec -it rag_backend bash

# Enter frontend container
docker exec -it rag_frontend bash

# Check running processes
docker exec rag_backend ps aux

# Check file permissions
docker exec rag_backend ls -la /app
docker exec rag_backend ls -la /data
```

### Network Debugging
```bash
# Test backend from frontend container
docker exec rag_frontend curl http://backend:8000/health

# Test external connectivity
curl http://localhost:8000/health
curl http://localhost:8501
```

### Log Analysis
```bash
# Follow all logs
docker-compose logs -f

# Filter specific service logs
docker-compose logs backend | grep ERROR
docker-compose logs frontend | grep WARNING

# Export logs to file
docker-compose logs > debug.log
```

### API Testing
```bash
# Test health endpoint
curl -v http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/api/chat/general \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": "test"}'

# Test admin endpoints
curl http://localhost:8000/api/admin/chroma/status
curl http://localhost:8000/api/admin/chroma/documents?limit=5
```

## 🛠️ Performance Issues

### Slow Response Times
```
Issue: API responses are slow
```

**Solutions:**
1. **Reduce context size:**
```python
RETRIEVAL_TOP_K: int = 5  # Reduce from 8
CHUNK_SIZE_TOKENS: int = 300  # Reduce from 500
```

2. **Optimize embeddings:**
```python
# Use smaller embedding dimensions
EMBEDDING_DIMENSION: int = 256  # Reduce from 384
```

3. **Enable caching:**
```python
# Add caching to frequently accessed data
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_embedding(text: str):
    return embedding_service.embed_text(text)
```

### High Memory Usage
```
Issue: Containers using too much memory
```

**Solutions:**
1. **Set memory limits:**
```yaml
deploy:
  resources:
    limits:
      memory: 1G
```

2. **Optimize chunk processing:**
```python
# Process files in batches
BATCH_SIZE = 10
for i in range(0, len(files), BATCH_SIZE):
    batch = files[i:i+BATCH_SIZE]
    process_batch(batch)
```

3. **Clear unused data:**
```python
# Regular cleanup
import gc
gc.collect()
```

### Disk Space Issues
```
Issue: Running out of disk space
```

**Solutions:**
```bash
# Check Docker disk usage
docker system df

# Clean up unused resources
docker system prune -a

# Clean up volumes (careful - this removes data!)
docker volume prune
```

## 📊 Monitoring and Logging

### Health Monitoring
```python
# Add custom health checks
@app.get("/health/detailed")
async def detailed_health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "groq_api": check_groq_connection(),
            "chromadb": vectorstore.health_check(),
            "embedding": embedding_service.health_check()
        },
        "metrics": {
            "total_documents": get_document_count(),
            "memory_usage": get_memory_usage(),
            "uptime": get_uptime()
        }
    }
```

### Structured Logging
```python
import logging
import json

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Log with context
logger.info(
    "RAG query processed",
    extra={
        "query": query,
        "results_count": len(results),
        "processing_time": elapsed_time,
        "session_id": session_id
    }
)
```

### Metrics Collection
```python
# Simple metrics tracking
class MetricsCollector:
    def __init__(self):
        self.metrics = {
            "requests_total": 0,
            "errors_total": 0,
            "response_times": []
        }
    
    def record_request(self, response_time: float, error: bool = False):
        self.metrics["requests_total"] += 1
        if error:
            self.metrics["errors_total"] += 1
        self.metrics["response_times"].append(response_time)
    
    def get_stats(self):
        response_times = self.metrics["response_times"]
        return {
            "total_requests": self.metrics["requests_total"],
            "total_errors": self.metrics["errors_total"],
            "error_rate": self.metrics["errors_total"] / max(1, self.metrics["requests_total"]),
            "avg_response_time": sum(response_times) / max(1, len(response_times)),
            "max_response_time": max(response_times) if response_times else 0
        }
```

This troubleshooting guide covers the most common issues you'll encounter and provides practical solutions for each problem.
