import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import document_bot, chatbot
from app.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Serri Flow Backend...")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Serri Flow Backend...")


# Create FastAPI app
app = FastAPI(
    title="Serri Flow Backend API",
    description="""
    Backend API for Serri Flow - A comprehensive solution combining:
    
    ## Document Bot Features
    - Upload and process documents (PDF/TXT)
    - Extract text and create embeddings for semantic search
    - Answer queries using Hugging Face QA pipeline
    - Feedback loop for response improvement
    - Comprehensive activity logging
    
    ## Serri AI Chatbot Features
    - Lead qualification and capture
    - Demo scheduling with Calendly integration
    - Objection handling with pre-defined responses
    - Follow-up automation
    - Conversation tracking and analytics
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(document_bot.router)
app.include_router(chatbot.router)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Serri Flow Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "features": [
            "Document processing and QA",
            "Lead qualification chatbot",
            "Demo scheduling",
            "Objection handling",
            "Activity logging"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "debug": settings.debug
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
