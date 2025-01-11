# Development Guide - Support Tool System

## Project Structure

```
support-tool/
├── README.md
├── requirements.txt
├── docker-compose.yml
├── .env.example
├── .gitignore
├── frontend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   │   ├── app.py
│   │   ├── config.py
│   │   ├── components/
│   │   │   ├── __init__.py
│   │   │   ├── search_panel.py
│   │   │   ├── results_display.py
│   │   │   ├── admin_dashboard.py
│   │   │   └── auth_components.py
│   │   ├── pages/
│   │   │   ├── __init__.py
│   │   │   ├── home.py
│   │   │   ├── search.py
│   │   │   └── admin.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       └── api_client.py
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── search.py
│   │   │   │   └── admin.py
│   │   │   └── dependencies.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── security.py
│   │   │   └── config.py
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user.py
│   │   │   │   └── ticket.py
│   │   │   └── vector_store.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── search.py
│   │   │   ├── embedding.py
│   │   │   └── admin.py
│   │   └── schemas/
│   │       ├── __init__.py
│   │       ├── user.py
│   │       └── ticket.py
└── tests/
    ├── frontend/
    │   └── test_components/
    └── backend/
        ├── test_api/
        └── test_services/

## Component Details

### Frontend Components

#### 1. Search Panel (`frontend/src/components/search_panel.py`)
```python
# filepath: frontend/src/components/search_panel.py
import streamlit as st
from typing import Dict, List
from utils.api_client import APIClient

class SearchPanel:
    def __init__(self):
        self.api_client = APIClient()
    
    def render(self):
        """Renders the search interface with filters and input fields"""
        # TODO: Implement search form
        pass
    
    def handle_search(self, query: Dict):
        """Processes search request and returns results"""
        # TODO: Implement search logic
        pass
```

#### 2. Results Display (`frontend/src/components/results_display.py`)
```python
# filepath: frontend/src/components/results_display.py
import streamlit as st
from typing import List, Dict

class ResultsDisplay:
    def render_results(self, results: List[Dict]):
        """Displays search results in a formatted manner"""
        # TODO: Implement results display logic
        pass
    
    def export_results(self, format: str):
        """Exports results in specified format (PDF/text)"""
        # TODO: Implement export functionality
        pass
```

### Backend Services

#### 1. Search Service (`backend/src/services/search.py`)
```python
# filepath: backend/src/services/search.py
from typing import List, Dict
from db.vector_store import VectorStore
from schemas.ticket import TicketSchema

class SearchService:
    def __init__(self):
        self.vector_store = VectorStore()
    
    async def search_similar_tickets(self, query: str, limit: int = 5) -> List[TicketSchema]:
        """Searches for similar tickets using vector similarity"""
        # TODO: Implement vector similarity search
        pass
    
    async def process_results(self, results: List[Dict]) -> Dict:
        """Processes and aggregates search results"""
        # TODO: Implement results processing
        pass
```

#### 2. Embedding Service (`backend/src/services/embedding.py`)
```python
# filepath: backend/src/services/embedding.py
from typing import List
import numpy as np
from azure.openai import AzureOpenAI

class EmbeddingService:
    def __init__(self):
        self.client = AzureOpenAI()
    
    async def generate_embedding(self, text: str) -> np.ndarray:
        """Generates embeddings using Azure OpenAI"""
        # TODO: Implement embedding generation
        pass
    
    async def batch_generate_embeddings(self, texts: List[str]):
        """Generates embeddings for multiple texts"""
        # TODO: Implement batch embedding generation
        pass
```

## Implementation Guide

### Phase 1: Core Setup

1. Environment Setup
```bash
# Create virtual environments for frontend and backend
python -m venv frontend/venv
python -m venv backend/venv

# Install dependencies
pip install -r frontend/requirements.txt
pip install -r backend/requirements.txt
```

2. Configuration
- Create `.env` file from `.env.example`
- Configure Azure OpenAI credentials
- Set up ChromaDB connection
- Configure authentication settings

### Phase 2: Implementation Steps

1. Backend Implementation
   - Start with database models and schemas
   - Implement authentication service
   - Set up vector store integration
   - Create search and embedding services
   - Implement API endpoints

2. Frontend Implementation
   - Set up basic Streamlit app structure
   - Implement authentication UI
   - Create search interface
   - Build results display component
   - Add admin dashboard

## Technology Documentation

### Core Technologies
- Streamlit: https://docs.streamlit.io/
- FastAPI: https://fastapi.tiangolo.com/
- ChromaDB: https://docs.trychroma.com/
- Azure OpenAI: https://learn.microsoft.com/en-us/azure/cognitive-services/openai/

### Important Implementation Notes

1. Vector Search Implementation
```python
# Example ChromaDB setup
from chromadb import Client, Settings

client = Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="db"
))

# Create collection
collection = client.create_collection(
    name="tickets",
    metadata={"hnsw:space": "cosine"}
)
```

2. Azure OpenAI Integration
```python
# Example embedding generation
from azure.openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

response = client.embeddings.create(
    model="text-embedding-ada-002",
    input="Sample text"
)
```

3. FastAPI Rate Limiting
```python
from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

## Testing Strategy

1. Unit Tests
   - Test individual components and services
   - Mock external services (Azure OpenAI, ChromaDB)
   - Test authentication flow

2. Integration Tests
   - Test API endpoints
   - Test vector search functionality
   - Test embedding generation

3. End-to-End Tests
   - Test complete search flow
   - Test admin functionality
   - Test export features

## Performance Considerations

1. Caching Strategy
   - Implement Redis for API response caching
   - Cache common search results
   - Cache embeddings for frequent queries

2. Database Optimization
   - Index optimization for ChromaDB
   - Connection pooling for SQL database
   - Batch processing for large datasets

3. Rate Limiting
   - Implement API rate limiting
   - Add request throttling
   - Monitor system resources

## Deployment Guide

1. Docker Setup
```yaml
# docker-compose.yml example
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "8501:8501"
    environment:
      - BACKEND_URL=http://backend:8000
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - AZURE_OPENAI_KEY=${AZURE_OPENAI_KEY}
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
    depends_on:
      - chromadb

  chromadb:
    image: chromadb/chroma
    ports:
      - "8000:8000"
    volumes:
      - ./data:/chroma/data
```

## Next Steps

1. Immediate Tasks
   - Set up development environment
   - Implement core authentication
   - Create basic search interface
   - Set up vector store integration

2. Future Enhancements
   - Add advanced analytics
   - Implement real-time collaboration
   - Add custom report generation
   - Integrate with ticket management systems