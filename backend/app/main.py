"""FastAPI app entry point for LLMScope Playground"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text
import logging

from .config import settings
from .db.base import engine, SessionLocal
from .db.models import Session, LLMEvent
from .api import sessions, chat, events

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting LLMScope Playground API...")

    # Verify database connection
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful")

        # Check if tables exist
        session_count = db.query(Session).count()
        logger.info(f"✅ Found {session_count} existing sessions")

    except Exception as e:
        logger.error(f"⚠️  Database connection error: {str(e)}")
        logger.error("   Make sure to run database migrations: alembic upgrade head")
    finally:
        db.close()

    yield

    # Shutdown
    logger.info("Shutting down LLMScope Playground API...")


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    lifespan=lifespan,
    description="LLMScope Playground - Session-based LLM monitoring and analytics"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(sessions.router, prefix="/api/v1", tags=["sessions"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(events.router, prefix="/api/v1", tags=["events"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LLMScope Playground API",
        "version": settings.api_version,
        "docs": "/docs",
        "endpoints": {
            "sessions": "/api/v1/sessions",
            "health": "/health"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    db = SessionLocal()
    try:
        # Check database connection
        db.execute(text("SELECT 1"))

        # Get session count
        session_count = db.query(Session).count()
        event_count = db.query(LLMEvent).count()

        return {
            "status": "healthy",
            "database": "connected",
            "sessions": session_count,
            "events": event_count
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
    finally:
        db.close()


@app.get("/api/v1/cleanup/stats")
async def get_cleanup_stats():
    """
    Get statistics about sessions and cleanup targets.
    Useful for monitoring session health.
    """
    from .services.session_cleanup import SessionCleanupService

    try:
        stats = SessionCleanupService.get_cleanup_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting cleanup stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/cleanup/run")
async def run_cleanup(dry_run: bool = True):
    """
    Manually trigger session cleanup.
    By default runs in dry-run mode to preview what would be deleted.

    Query params:
        dry_run: If True (default), only shows what would be deleted
    """
    from .services.session_cleanup import SessionCleanupService

    try:
        result = SessionCleanupService.cleanup_expired_sessions(dry_run=dry_run)
        return result
    except Exception as e:
        logger.error(f"Error running cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,  # Different port from main backend
        reload=True
    )
