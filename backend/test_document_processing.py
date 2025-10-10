#!/usr/bin/env python3
"""
Test script for document processing and chunking capabilities
Creates sample files and processes them through the full pipeline
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.document_processor import DocumentProcessor
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.vectorstore_service import VectorStoreService

# Sample files to create and process
SAMPLE_FILES = {
    'main.py': '''
import os
from fastapi import FastAPI, HTTPException
from typing import List, Dict

app = FastAPI(title="Sample API")

class UserService:
    """Service for managing users"""
    
    def __init__(self):
        self.users = {}
    
    async def create_user(self, username: str, email: str) -> Dict:
        """Create a new user"""
        if username in self.users:
            raise HTTPException(status_code=400, detail="User exists")
        
        user = {
            "id": len(self.users) + 1,
            "username": username,
            "email": email,
            "active": True
        }
        self.users[username] = user
        return user
    
    async def get_user(self, username: str) -> Dict:
        """Get user by username"""
        if username not in self.users:
            raise HTTPException(status_code=404, detail="User not found")
        return self.users[username]

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Hello World"}

@app.post("/users")
async def create_user_endpoint(username: str, email: str):
    """Create user endpoint"""
    service = UserService()
    return await service.create_user(username, email)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
    
    'config.json': '''{
  "database": {
    "host": "localhost",
    "port": 5432,
    "name": "myapp",
    "user": "postgres",
    "password": "secret"
  },
  "redis": {
    "host": "localhost",
    "port": 6379,
    "db": 0
  },
  "api": {
    "title": "My API",
    "version": "1.0.0",
    "debug": false,
    "cors_origins": [
      "http://localhost:3000",
      "https://myapp.com"
    ]
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "handlers": ["console", "file"]
  }
}''',
    
    'README.md': '''# Sample Project

This is a sample FastAPI project demonstrating various features.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/user/sample-project.git
   cd sample-project
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## Usage

### Starting the Server

Run the development server:
```bash
python main.py
```

The API will be available at http://localhost:8000

### API Endpoints

#### Users

- `POST /users` - Create a new user
  - Parameters: `username`, `email`
  - Returns: User object with ID

- `GET /users/{username}` - Get user by username
  - Returns: User object or 404 error

#### Health Check

- `GET /` - Root endpoint
  - Returns: Welcome message

## Configuration

The application uses `config.json` for configuration:

- **Database**: PostgreSQL connection settings
- **Redis**: Cache configuration  
- **API**: Server settings and CORS
- **Logging**: Log level and format

## Development

### Code Structure

```
project/
├── main.py          # FastAPI application
├── config.json      # Configuration file
├── requirements.txt # Dependencies
└── README.md       # This file
```

### Testing

Run tests with:
```bash
pytest tests/
```

## Deployment

For production deployment:

1. Set environment variables
2. Use a production WSGI server like Gunicorn
3. Set up reverse proxy with Nginx
4. Configure SSL certificates

## License

MIT License - see LICENSE file for details.
''',
    
    'schema.sql': '''-- Database schema for sample project

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on username for faster lookups
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- Posts table
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    published BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on user_id for faster joins
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_published ON posts(published);

-- Comments table
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for comments
CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);

-- Insert sample data
INSERT INTO users (username, email, password_hash) VALUES 
('admin', 'admin@example.com', 'hashed_password_here'),
('user1', 'user1@example.com', 'hashed_password_here');
''',
    
    'styles.css': '''/* Main application styles */

:root {
  --primary-color: #007bff;
  --secondary-color: #6c757d;
  --success-color: #28a745;
  --danger-color: #dc3545;
  --warning-color: #ffc107;
  --info-color: #17a2b8;
  --light-color: #f8f9fa;
  --dark-color: #343a40;
}

/* Base styles */
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  margin: 0;
  padding: 0;
  background-color: var(--light-color);
  color: var(--dark-color);
}

/* Header styles */
.header {
  background-color: var(--primary-color);
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header h1 {
  margin: 0;
  font-size: 1.5rem;
}

/* Navigation */
.nav {
  background-color: var(--secondary-color);
  padding: 0.5rem 2rem;
}

.nav ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
}

.nav li {
  margin-right: 2rem;
}

.nav a {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.nav a:hover {
  background-color: rgba(255,255,255,0.1);
}

/* Main content */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

/* Forms */
.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-control {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1rem;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
}

/* Buttons */
.btn {
  display: inline-block;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.3s;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: var(--secondary-color);
  color: white;
}

/* Cards */
.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.card-header {
  font-size: 1.25rem;
  font-weight: 500;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #dee2e6;
}

/* Responsive design */
@media (max-width: 768px) {
  .container {
    padding: 1rem;
  }
  
  .nav ul {
    flex-direction: column;
  }
  
  .nav li {
    margin-right: 0;
    margin-bottom: 0.5rem;
  }
}
'''
}

async def test_document_processing():
    """Test the complete document processing pipeline"""
    print("🚀 Testing Document Processing Pipeline...")
    
    # Create temporary directory for test files
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Created temporary directory: {temp_dir}")
        
        # Create sample files
        file_paths = {}
        for filename, content in SAMPLE_FILES.items():
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            file_paths[filename] = file_path
            print(f"✅ Created {filename}")
        
        # Initialize services
        doc_processor = DocumentProcessor()
        chunking_service = ChunkingService()
        embedding_service = EmbeddingService()
        vectorstore_service = VectorStoreService()
        
        print("\n🔧 Services initialized")
        
        # Process each file
        all_chunks = []
        
        for filename, file_path in file_paths.items():
            print(f"\n📄 Processing {filename}...")
            
            try:
                # Step 1: Extract content
                content, metadata = await doc_processor.process_file(file_path, filename)
                print(f"  ✅ Extracted {len(content)} characters")
                print(f"  📋 Metadata: {metadata}")
                
                # Step 2: Chunk the content
                chunks = await chunking_service.chunk_document(content, metadata)
                print(f"  🔪 Created {len(chunks)} chunks")
                
                # Display chunk info
                for i, chunk in enumerate(chunks):
                    chunk_meta = chunk['metadata']
                    chunk_type = chunk_meta.get('chunk_type', 'unknown')
                    lines = chunk_meta.get('end_line', 0) - chunk_meta.get('start_line', 0) + 1
                    function_name = chunk_meta.get('function_name', '')
                    section_title = chunk_meta.get('section_title', '')
                    
                    info_parts = [f"Chunk {i+1}: {chunk_type}"]
                    if lines > 0:
                        info_parts.append(f"{lines} lines")
                    if function_name:
                        info_parts.append(f"function: {function_name}")
                    if section_title:
                        info_parts.append(f"section: {section_title}")
                    
                    print(f"    📝 {' | '.join(info_parts)}")
                    print(f"    📏 Content length: {len(chunk['content'])} chars")
                
                all_chunks.extend(chunks)
                
            except Exception as e:
                print(f"  ❌ Error processing {filename}: {str(e)}")
        
        print(f"\n📊 Total chunks created: {len(all_chunks)}")
        
        # Test embedding and vector store
        if all_chunks:
            print("\n🔢 Testing embeddings and vector store...")
            
            # Clear existing data
            await vectorstore_service.clear_collection()
            
            # Process chunks in batches
            batch_size = 5
            for i in range(0, len(all_chunks), batch_size):
                batch = all_chunks[i:i + batch_size]
                
                print(f"  📦 Processing batch {i//batch_size + 1}/{(len(all_chunks) + batch_size - 1)//batch_size}")
                
                # Extract content and metadata
                documents = [chunk['content'] for chunk in batch]
                metadatas = [chunk['metadata'] for chunk in batch]
                
                # Generate embeddings
                embeddings = await embedding_service.embed_texts(documents)
                print(f"    🔢 Generated {len(embeddings)} embeddings")
                
                # Add to vector store
                doc_ids = await vectorstore_service.add_documents(
                    documents=documents,
                    metadatas=metadatas,
                    embeddings=embeddings
                )
                print(f"    💾 Added {len(doc_ids)} documents to vector store")
            
            # Test retrieval
            print("\n🔍 Testing retrieval...")
            test_queries = [
                "How do I create a user?",
                "What's the database configuration?",
                "Show me the CSS styles",
                "How to install the project?"
            ]
            
            for query in test_queries:
                print(f"\n  🔎 Query: {query}")
                
                # Get query embedding
                query_embedding = await embedding_service.embed_text(query)
                
                # Search vector store
                results = await vectorstore_service.query_similar(
                    query_embedding=query_embedding,
                    n_results=3
                )
                
                print(f"    📋 Found {len(results['documents'])} relevant chunks:")
                
                for j, (doc, metadata, distance) in enumerate(zip(
                    results['documents'], 
                    results['metadatas'], 
                    results['distances']
                )):
                    filename = metadata.get('filename', 'unknown')
                    chunk_type = metadata.get('chunk_type', 'unknown')
                    function_name = metadata.get('function_name', '')
                    section_title = metadata.get('section_title', '')
                    similarity = 1 - distance
                    
                    info_parts = [f"{filename}"]
                    if function_name:
                        info_parts.append(f"function: {function_name}")
                    if section_title:
                        info_parts.append(f"section: {section_title}")
                    
                    print(f"      {j+1}. {' | '.join(info_parts)} (similarity: {similarity:.3f})")
                    print(f"         Preview: {doc[:100]}...")
        
        # Final statistics
        stats = await vectorstore_service.get_collection_stats()
        print(f"\n📈 Final Statistics:")
        print(f"  📊 Total chunks in vector store: {stats['total_chunks']}")
        print(f"  📁 File types processed: {list(stats['file_types'].keys())}")
        
        print("\n✅ Document processing pipeline test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_document_processing())
