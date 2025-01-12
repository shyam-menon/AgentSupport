import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import admin, auth, search
from src.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Set log level for specific loggers
logging.getLogger('src').setLevel(logging.DEBUG)
logging.getLogger('chromadb').setLevel(logging.INFO)
logging.getLogger('uvicorn').setLevel(logging.INFO)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for searching and managing support tickets"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

@app.get("/")
async def root():
    return {"message": "Welcome to Support Ticket Search API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
