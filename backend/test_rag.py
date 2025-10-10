#!/usr/bin/env python3
"""
Test script to add sample documents to ChromaDB for RAG testing
Run this after starting the backend to test RAG functionality
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.rag_pipeline import RAGPipeline
from app.services.embedding_service import EmbeddingService
from app.services.vectorstore_service import VectorStoreService

# Sample code documents for testing
SAMPLE_DOCUMENTS = [
    {
        "content": """
def connect_to_database():
    \"\"\"
    Connect to PostgreSQL database using environment variables
    \"\"\"
    import psycopg2
    import os
    
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'myapp'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'password'),
        port=os.getenv('DB_PORT', 5432)
    )
    return conn

def create_user_table():
    \"\"\"Create users table if it doesn't exist\"\"\"
    conn = connect_to_database()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()
""",
        "metadata": {
            "filename": "database.py",
            "file_type": ".py",
            "language": "python",
            "function_name": "connect_to_database",
            "start_line": 1,
            "end_line": 35
        }
    },
    {
        "content": """
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: timedelta = None):
    \"\"\"
    Create JWT access token
    \"\"\"
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str = Depends(security)):
    \"\"\"
    Verify JWT token and return user data
    \"\"\"
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
""",
        "metadata": {
            "filename": "auth.py",
            "file_type": ".py",
            "language": "python",
            "function_name": "create_access_token",
            "start_line": 1,
            "end_line": 40
        }
    },
    {
        "content": """
{
  "name": "my-project",
  "version": "1.0.0",
  "description": "A sample Node.js project",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "dev": "nodemon index.js",
    "test": "jest"
  },
  "dependencies": {
    "express": "^4.18.0",
    "mongoose": "^6.5.0",
    "jsonwebtoken": "^8.5.1",
    "bcryptjs": "^2.4.3",
    "cors": "^2.8.5",
    "dotenv": "^16.0.1"
  },
  "devDependencies": {
    "nodemon": "^2.0.19",
    "jest": "^28.1.3"
  }
}
""",
        "metadata": {
            "filename": "package.json",
            "file_type": ".json",
            "config_type": "npm",
            "start_line": 1,
            "end_line": 25
        }
    },
    {
        "content": """
# Project Setup

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/user/my-project.git
   cd my-project
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. Run the application:
   ```bash
   npm start
   ```

## API Endpoints

- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /users/profile` - Get user profile (requires auth)
- `PUT /users/profile` - Update user profile (requires auth)

## Database Schema

The application uses PostgreSQL with the following tables:
- `users` - User accounts and profiles
- `posts` - User posts and content
- `comments` - Comments on posts
""",
        "metadata": {
            "filename": "README.md",
            "file_type": ".md",
            "section_title": "Project Setup",
            "start_line": 1,
            "end_line": 35
        }
    }
]

async def test_rag_pipeline():
    """Test the RAG pipeline by adding sample documents"""
    print("🚀 Testing RAG Pipeline...")
    
    try:
        # Initialize services
        embedding_service = EmbeddingService()
        vectorstore_service = VectorStoreService()
        rag_pipeline = RAGPipeline()
        
        print("✅ Services initialized")
        
        # Check initial status
        initial_status = await rag_pipeline.get_pipeline_status()
        print(f"📊 Initial status: {initial_status['total_chunks']} chunks")
        
        # Clear existing documents
        if initial_status['total_chunks'] > 0:
            print("🗑️ Clearing existing documents...")
            await rag_pipeline.clear_knowledge_base()
        
        # Add sample documents
        print("📝 Adding sample documents...")
        documents = [doc["content"] for doc in SAMPLE_DOCUMENTS]
        metadatas = [doc["metadata"] for doc in SAMPLE_DOCUMENTS]
        
        # Generate embeddings
        print("🔢 Generating embeddings...")
        embeddings = await embedding_service.embed_texts(documents)
        
        # Add to vector store
        print("💾 Adding to vector store...")
        doc_ids = await vectorstore_service.add_documents(
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
        
        print(f"✅ Added {len(doc_ids)} documents to vector store")
        
        # Check final status
        final_status = await rag_pipeline.get_pipeline_status()
        print(f"📊 Final status: {final_status}")
        
        # Test query
        print("\n🔍 Testing query...")
        test_query = "How do I connect to the database?"
        
        print(f"Query: {test_query}")
        print("Response:")
        
        async for token in rag_pipeline.process_query(
            query=test_query,
            session_id="test-session",
            conversation_history=[],
            top_k=3
        ):
            print(token, end="", flush=True)
        
        print("\n\n✅ RAG Pipeline test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing RAG pipeline: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_rag_pipeline())
