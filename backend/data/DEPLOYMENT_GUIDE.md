# Deployment Guide

## 🚀 Docker Deployment

### Prerequisites
- Docker Desktop installed
- Docker Compose available
- GROQ API key

### Quick Start
```bash
# 1. Clone/navigate to project directory
cd chatgpt

# 2. Set up environment variables
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# 3. Start the application
docker-compose up --build

# 4. Access the application
# Frontend: http://localhost:8501
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 🔧 Configuration Files

### Docker Compose (`docker-compose.yml`)
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: rag_backend
    ports:
      - "8000:8000"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - CHROMA_PERSIST_DIR=/data/chroma
    volumes:
      - chroma_data:/data/chroma
      - ./backend:/app
    networks:
      - rag-network

  frontend:
    build: ./frontend
    container_name: rag_frontend
    ports:
      - "8501:8501"
    environment:
      - BACKEND_URL=http://backend:8000
    depends_on:
      backend:
        condition: service_healthy
    networks:
      - rag-network

volumes:
  chroma_data:
    driver: local

networks:
  rag-network:
    driver: bridge
```

### Backend Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### Frontend Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Start Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 🌍 Environment Configuration

### Environment Variables (`.env`)
```bash
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional (with defaults)
GROQ_CHAT_MODEL=llama-3.1-8b-instant
CHROMA_PERSIST_DIR=/data/chroma
DEBUG=false
APP_NAME=Code Assistant AI
APP_VERSION=1.0.0
```

### Alternative Models
```bash
# High-performance model (slower but better quality)
GROQ_CHAT_MODEL=llama-3.1-70b-versatile

# Google's model
GROQ_CHAT_MODEL=gemma2-9b-it

# Default (fast and efficient)
GROQ_CHAT_MODEL=llama-3.1-8b-instant
```

## 🔄 Container Management

### Start Services
```bash
# Build and start all services
docker-compose up --build

# Start in background
docker-compose up -d

# Start specific service
docker-compose up backend
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop specific service
docker-compose stop backend
```

### Restart Services
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### View Logs
```bash
# View all logs
docker-compose logs

# Follow logs
docker-compose logs -f

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
```

## 📊 Health Monitoring

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Container health status
docker-compose ps
```

### Service Status
```bash
# Check if services are running
docker ps

# View resource usage
docker stats

# Inspect containers
docker inspect rag_backend
docker inspect rag_frontend
```

## 💾 Data Management

### ChromaDB Data
```bash
# View ChromaDB volume
docker volume inspect chatgpt_chroma_data

# Backup ChromaDB data
docker run --rm -v chatgpt_chroma_data:/data -v $(pwd):/backup alpine tar czf /backup/chroma_backup.tar.gz -C /data .

# Restore ChromaDB data
docker run --rm -v chatgpt_chroma_data:/data -v $(pwd):/backup alpine tar xzf /backup/chroma_backup.tar.gz -C /data
```

### Application Data
```bash
# Add documents to RAG system
# 1. Place files in backend/data/ directory
# 2. Restart backend container
docker-compose restart backend
```

## 🔧 Development Mode

### Local Development
```bash
# Backend development
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend development
cd frontend
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

### Hot Reload
- Backend: Enabled by default with `--reload` flag
- Frontend: Streamlit auto-reloads on file changes
- Docker volumes mount source code for development

## 🚨 Troubleshooting

### Common Issues

#### 1. GROQ API Key Error
```bash
# Error: "The model 'llama3-8b-8192' has been decommissioned"
# Solution: Update model in config.py or .env
GROQ_CHAT_MODEL=llama-3.1-8b-instant
```

#### 2. Container Won't Start
```bash
# Check logs
docker-compose logs backend

# Check if ports are available
netstat -an | grep 8000
netstat -an | grep 8501

# Restart Docker Desktop
```

#### 3. ChromaDB Connection Issues
```bash
# Check volume permissions
docker volume inspect chatgpt_chroma_data

# Recreate volume
docker-compose down -v
docker-compose up --build
```

#### 4. Frontend Can't Connect to Backend
```bash
# Check network connectivity
docker network ls
docker network inspect chatgpt_rag-network

# Verify backend is healthy
curl http://localhost:8000/health
```

### Debug Commands
```bash
# Enter backend container
docker exec -it rag_backend bash

# Enter frontend container
docker exec -it rag_frontend bash

# View container processes
docker exec rag_backend ps aux

# Check file system
docker exec rag_backend ls -la /app
docker exec rag_backend ls -la /data
```

## 📈 Performance Optimization

### Resource Limits
```yaml
# Add to docker-compose.yml services
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '0.5'
    reservations:
      memory: 512M
      cpus: '0.25'
```

### Build Optimization
```bash
# Use BuildKit for faster builds
DOCKER_BUILDKIT=1 docker-compose build

# Multi-stage builds (already implemented)
# Cached layers for dependencies
```

## 🔐 Security Considerations

### Production Deployment
- Use secrets management for API keys
- Enable HTTPS with reverse proxy
- Implement rate limiting
- Add authentication if needed
- Regular security updates

### Network Security
```yaml
# Restrict external access
networks:
  rag-network:
    driver: bridge
    internal: true  # No external access
```

## 📝 Maintenance

### Regular Tasks
- Monitor disk usage (ChromaDB data)
- Update dependencies
- Backup ChromaDB data
- Monitor API usage (GROQ)
- Check logs for errors

### Updates
```bash
# Update application
git pull
docker-compose build --no-cache
docker-compose up -d

# Update dependencies
# Edit requirements.txt files
docker-compose build --no-cache
```
