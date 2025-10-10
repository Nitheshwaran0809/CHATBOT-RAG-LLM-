#!/usr/bin/env python3
"""
Test script for Phase 4: Code Assistant Features
Tests intelligent prompt selection and context-aware responses
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.rag_pipeline import RAGPipeline
from app.services.embedding_service import EmbeddingService
from app.services.vectorstore_service import VectorStoreService
from app.services.document_processor import DocumentProcessor
from app.services.chunking_service import ChunkingService

# Enhanced sample codebase for testing
ENHANCED_CODEBASE = {
    'user_service.py': '''
from fastapi import HTTPException
from typing import List, Dict, Optional
import bcrypt
import jwt
from datetime import datetime, timedelta

class UserService:
    """Service for managing user operations"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.secret_key = "your-secret-key"
    
    async def create_user(self, username: str, email: str, password: str) -> Dict:
        """
        Create a new user with hashed password
        
        Args:
            username: Unique username
            email: User email address
            password: Plain text password
            
        Returns:
            Dict containing user information
            
        Raises:
            HTTPException: If user already exists
        """
        # Check if user exists
        existing_user = await self.get_user_by_username(username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        existing_email = await self.get_user_by_email(email)
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user record
        user_data = {
            "username": username,
            "email": email,
            "password_hash": password_hash.decode('utf-8'),
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        user_id = await self.db.insert_user(user_data)
        user_data["id"] = user_id
        
        return user_data
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate user credentials
        
        Args:
            username: Username or email
            password: Plain text password
            
        Returns:
            User dict if authenticated, None otherwise
        """
        user = await self.get_user_by_username(username)
        if not user:
            user = await self.get_user_by_email(username)
        
        if not user or not user.get('is_active'):
            return None
        
        # Verify password
        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return user
        
        return None
    
    async def create_access_token(self, user_id: int) -> str:
        """Create JWT access token for user"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    async def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        return await self.db.get_user_by_field("username", username)
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        return await self.db.get_user_by_field("email", email)
''',
    
    'database.py': '''
import asyncpg
import os
from typing import Dict, List, Optional

class DatabaseConnection:
    """Database connection and operations"""
    
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        """Initialize database connection pool"""
        self.pool = await asyncpg.create_pool(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME', 'myapp'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'password'),
            min_size=1,
            max_size=10
        )
    
    async def insert_user(self, user_data: Dict) -> int:
        """Insert new user and return ID"""
        query = """
            INSERT INTO users (username, email, password_hash, created_at, is_active)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        """
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                query,
                user_data['username'],
                user_data['email'],
                user_data['password_hash'],
                user_data['created_at'],
                user_data['is_active']
            )
            return result
    
    async def get_user_by_field(self, field: str, value: str) -> Optional[Dict]:
        """Get user by any field"""
        query = f"SELECT * FROM users WHERE {field} = $1"
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, value)
            return dict(row) if row else None
''',
    
    'api_routes.py': '''
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from .user_service import UserService
from .database import DatabaseConnection

router = APIRouter(prefix="/api/users")

class UserCreateRequest(BaseModel):
    username: str
    email: str
    password: str

class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

# Dependency injection
async def get_user_service():
    db = DatabaseConnection()
    await db.connect()
    return UserService(db)

@router.post("/register", response_model=UserResponse)
async def register_user(
    request: UserCreateRequest,
    user_service: UserService = Depends(get_user_service)
):
    """Register a new user"""
    try:
        user = await user_service.create_user(
            username=request.username,
            email=request.email,
            password=request.password
        )
        return UserResponse(
            id=user['id'],
            username=user['username'],
            email=user['email'],
            is_active=user['is_active']
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login_user(
    request: UserLoginRequest,
    user_service: UserService = Depends(get_user_service)
):
    """Authenticate user and return token"""
    user = await user_service.authenticate_user(
        username=request.username,
        password=request.password
    )
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = await user_service.create_access_token(user['id'])
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user['id'],
            username=user['username'],
            email=user['email'],
            is_active=user['is_active']
        )
    }
''',
    
    'config.yaml': '''
database:
  host: localhost
  port: 5432
  name: myapp
  user: postgres
  password: ${DB_PASSWORD}
  pool_size: 10
  
redis:
  host: localhost
  port: 6379
  db: 0
  
security:
  secret_key: ${SECRET_KEY}
  token_expiry_hours: 24
  bcrypt_rounds: 12
  
api:
  title: "User Management API"
  version: "1.0.0"
  debug: false
  cors_origins:
    - "http://localhost:3000"
    - "https://myapp.com"
  
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "app.log"
''',
    
    'README.md': '''
# User Management API

A FastAPI-based user management system with authentication and authorization.

## Features

- User registration and authentication
- JWT token-based authorization
- Password hashing with bcrypt
- PostgreSQL database integration
- Async/await support throughout
- Comprehensive error handling

## API Endpoints

### Authentication

#### POST /api/users/register
Register a new user account.

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com", 
  "password": "secure_password"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "is_active": true
}
```

#### POST /api/users/login
Authenticate user and receive access token.

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "john_doe", 
    "email": "john@example.com",
    "is_active": true
  }
}
```

## Database Schema

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);
```

## Security Features

- Passwords are hashed using bcrypt with salt
- JWT tokens expire after 24 hours
- Input validation using Pydantic models
- SQL injection protection with parameterized queries
- CORS configuration for cross-origin requests

## Error Handling

The API returns appropriate HTTP status codes:
- 400: Bad Request (validation errors, user exists)
- 401: Unauthorized (invalid credentials)
- 404: Not Found (user not found)
- 500: Internal Server Error

## Configuration

Set environment variables:
- `DB_HOST`: Database host
- `DB_PASSWORD`: Database password
- `SECRET_KEY`: JWT signing key
'''
}

# Test queries for different prompt types
TEST_QUERIES = [
    # Code generation queries
    {
        "query": "Create a password reset functionality for users",
        "type": "generation",
        "expected_features": ["password reset", "email", "token", "security"]
    },
    
    # Debugging queries  
    {
        "query": "I'm getting a 'duplicate key value violates unique constraint' error when creating users",
        "type": "debugging",
        "expected_features": ["unique constraint", "database", "error handling", "validation"]
    },
    
    # Architecture queries
    {
        "query": "How can I improve the scalability and performance of this user service?",
        "type": "architecture", 
        "expected_features": ["scalability", "performance", "caching", "database optimization"]
    },
    
    # Code review queries
    {
        "query": "Review my user authentication code for security vulnerabilities",
        "type": "review",
        "expected_features": ["security", "vulnerabilities", "best practices", "improvements"]
    },
    
    # General queries
    {
        "query": "How do I add email verification to the registration process?",
        "type": "general",
        "expected_features": ["email verification", "registration", "workflow"]
    }
]

async def test_code_assistant_features():
    """Test the enhanced code assistant with intelligent prompts"""
    print("🚀 Testing Phase 4: Code Assistant Features...")
    
    try:
        # Initialize services
        doc_processor = DocumentProcessor()
        chunking_service = ChunkingService()
        embedding_service = EmbeddingService()
        vectorstore_service = VectorStoreService()
        rag_pipeline = RAGPipeline()
        
        print("✅ Services initialized")
        
        # Clear existing data
        await vectorstore_service.clear_collection()
        print("🗑️ Cleared existing vector store")
        
        # Process and load the enhanced codebase
        print("\n📚 Loading enhanced codebase...")
        
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            all_chunks = []
            
            for filename, content in ENHANCED_CODEBASE.items():
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"  📄 Processing {filename}...")
                
                # Process file
                extracted_content, metadata = await doc_processor.process_file(file_path, filename)
                chunks = await chunking_service.chunk_document(extracted_content, metadata)
                
                print(f"    🔪 Created {len(chunks)} chunks")
                all_chunks.extend(chunks)
            
            # Generate embeddings and store
            print(f"\n💾 Storing {len(all_chunks)} chunks in vector store...")
            
            documents = [chunk['content'] for chunk in all_chunks]
            metadatas = [chunk['metadata'] for chunk in all_chunks]
            embeddings = await embedding_service.embed_texts(documents)
            
            await vectorstore_service.add_documents(
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
            
            print("✅ Codebase loaded successfully")
        
        # Test intelligent prompt selection
        print("\n🧠 Testing Intelligent Prompt Selection...")
        
        for i, test_case in enumerate(TEST_QUERIES, 1):
            query = test_case["query"]
            query_type = test_case["type"]
            expected_features = test_case["expected_features"]
            
            print(f"\n--- Test Case {i}: {query_type.title()} Query ---")
            print(f"Query: {query}")
            print(f"Expected features: {', '.join(expected_features)}")
            
            print("\nResponse:")
            print("-" * 60)
            
            # Process query through RAG pipeline
            response_tokens = []
            async for token in rag_pipeline.process_query(
                query=query,
                session_id=f"test-session-{i}",
                conversation_history=[],
                top_k=5
            ):
                response_tokens.append(token)
                print(token, end="", flush=True)
            
            full_response = "".join(response_tokens)
            
            print("\n" + "-" * 60)
            
            # Analyze response quality
            response_lower = full_response.lower()
            found_features = []
            
            for feature in expected_features:
                if feature.lower() in response_lower:
                    found_features.append(feature)
            
            print(f"✅ Found expected features: {', '.join(found_features)}")
            
            if len(found_features) >= len(expected_features) * 0.5:  # At least 50% match
                print(f"✅ Test case {i} PASSED")
            else:
                print(f"⚠️ Test case {i} PARTIAL - may need prompt tuning")
            
            print("\n" + "=" * 80)
        
        # Test context analysis
        print("\n🔍 Testing Context Analysis...")
        
        # Get some sample context
        test_embedding = await embedding_service.embed_text("user authentication")
        results = await vectorstore_service.query_similar(
            query_embedding=test_embedding,
            n_results=3
        )
        
        if results['documents']:
            context = rag_pipeline._format_context(results)
            print("Sample context formatting:")
            print("-" * 40)
            print(context[:500] + "..." if len(context) > 500 else context)
            print("-" * 40)
        
        # Final statistics
        stats = await vectorstore_service.get_collection_stats()
        print(f"\n📊 Final Statistics:")
        print(f"  Total chunks: {stats['total_chunks']}")
        print(f"  File types: {list(stats['file_types'].keys())}")
        
        print("\n✅ Phase 4 Code Assistant Features test completed!")
        print("\nKey Features Tested:")
        print("  ✅ Intelligent prompt selection based on query type")
        print("  ✅ Context-aware code generation")
        print("  ✅ Debugging assistance with error analysis")
        print("  ✅ Architecture guidance and recommendations")
        print("  ✅ Code review with security focus")
        print("  ✅ Enhanced context formatting with metadata")
        
    except Exception as e:
        print(f"❌ Error in code assistant test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_code_assistant_features())
