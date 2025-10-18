"""Session management API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func, and_
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from ..db.models import Session, LLMEvent
from ..db.base import get_db
from ..dependencies import get_session_id, get_current_session
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions", tags=["sessions"])


class SessionResponse(BaseModel):
    """Session response model"""
    session_id: str
    created_at: datetime
    last_activity: datetime
    is_active: bool
    metadata: Dict[str, Any]
    event_count: int
    total_tokens: int
    total_cost: float

    class Config:
        from_attributes = True


class CreateSessionResponse(BaseModel):
    """Response for session creation"""
    session_id: str
    message: str


class SessionMetrics(BaseModel):
    """Session metrics model"""
    session_id: str
    event_count: int
    total_tokens: int
    total_cost: float
    models_used: list


@router.post("/create", response_model=CreateSessionResponse)
async def create_session(
    response: Response,
    db: DBSession = Depends(get_db)
):
    """
    Create a new session.
    Returns the session_id and sets it in a cookie.
    """
    import uuid

    # Generate new session ID
    session_id = str(uuid.uuid4())

    # Create session in database
    new_session = Session(
        session_id=session_id,
        is_active=True,
        session_metadata={}
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    # Set session cookie
    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_id,
        httponly=True,
        max_age=settings.session_ttl_days * 24 * 60 * 60,  # Convert days to seconds
        samesite="lax"
    )

    logger.info(f"Created new session: {session_id}")

    return CreateSessionResponse(
        session_id=session_id,
        message="Session created successfully"
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: DBSession = Depends(get_db)
):
    """
    Get session information by session_id.
    Returns session metadata and aggregated metrics.
    """
    # Query session
    session = db.query(Session).filter(Session.session_id == session_id).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get aggregated metrics
    metrics = db.query(
        func.count(LLMEvent.id).label('event_count'),
        func.coalesce(func.sum(LLMEvent.tokens_total), 0).label('total_tokens'),
        func.coalesce(func.sum(LLMEvent.cost_usd), 0.0).label('total_cost')
    ).filter(LLMEvent.session_id == session.id).first()

    return SessionResponse(
        session_id=session.session_id,
        created_at=session.created_at,
        last_activity=session.last_activity,
        is_active=session.is_active,
        metadata=session.session_metadata or {},
        event_count=metrics.event_count or 0,
        total_tokens=int(metrics.total_tokens or 0),
        total_cost=float(metrics.total_cost or 0.0)
    )


@router.get("/current/info", response_model=SessionResponse)
async def get_current_session_info(
    session: Session = Depends(get_current_session),
    db: DBSession = Depends(get_db)
):
    """
    Get current session information (from cookie or header).
    Returns session metadata and aggregated metrics.
    """
    # Get aggregated metrics
    metrics = db.query(
        func.count(LLMEvent.id).label('event_count'),
        func.coalesce(func.sum(LLMEvent.tokens_total), 0).label('total_tokens'),
        func.coalesce(func.sum(LLMEvent.cost_usd), 0.0).label('total_cost')
    ).filter(LLMEvent.session_id == session.id).first()

    return SessionResponse(
        session_id=session.session_id,
        created_at=session.created_at,
        last_activity=session.last_activity,
        is_active=session.is_active,
        metadata=session.session_metadata or {},
        event_count=metrics.event_count or 0,
        total_tokens=int(metrics.total_tokens or 0),
        total_cost=float(metrics.total_cost or 0.0)
    )


@router.post("/{session_id}/reset")
async def reset_session(
    session_id: str,
    db: DBSession = Depends(get_db)
):
    """
    Reset a session by deleting all its events.
    The session itself remains active but with clean slate.
    """
    # Query session
    session = db.query(Session).filter(Session.session_id == session_id).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Delete all events for this session
    deleted_count = db.query(LLMEvent).filter(LLMEvent.session_id == session.id).delete()

    # Reset session metadata
    session.session_metadata = {}
    session.last_activity = func.now()

    db.commit()

    logger.info(f"Reset session {session_id}: deleted {deleted_count} events")

    return {
        "success": True,
        "message": f"Session reset successfully. Deleted {deleted_count} events.",
        "session_id": session_id
    }


@router.post("/current/reset")
async def reset_current_session(
    session: Session = Depends(get_current_session),
    db: DBSession = Depends(get_db)
):
    """
    Reset the current session (from cookie or header).
    Deletes all events for this session.
    """
    # Delete all events for this session
    deleted_count = db.query(LLMEvent).filter(LLMEvent.session_id == session.id).delete()

    # Reset session metadata
    session.session_metadata = {}
    session.last_activity = func.now()

    db.commit()

    logger.info(f"Reset current session {session.session_id}: deleted {deleted_count} events")

    return {
        "success": True,
        "message": f"Session reset successfully. Deleted {deleted_count} events.",
        "session_id": session.session_id
    }


@router.get("/current/metrics", response_model=SessionMetrics)
async def get_current_session_metrics(
    session: Session = Depends(get_current_session),
    db: DBSession = Depends(get_db)
):
    """
    Get metrics for the current session.
    Returns aggregated statistics about the session's events.
    """
    # Get aggregated metrics
    metrics = db.query(
        func.count(LLMEvent.id).label('event_count'),
        func.coalesce(func.sum(LLMEvent.tokens_total), 0).label('total_tokens'),
        func.coalesce(func.sum(LLMEvent.cost_usd), 0.0).label('total_cost')
    ).filter(LLMEvent.session_id == session.id).first()

    # Get unique models used
    models = db.query(LLMEvent.model).filter(
        and_(LLMEvent.session_id == session.id, LLMEvent.model.isnot(None))
    ).distinct().all()

    models_used = [model[0] for model in models] if models else []

    return SessionMetrics(
        session_id=session.session_id,
        event_count=metrics.event_count or 0,
        total_tokens=int(metrics.total_tokens or 0),
        total_cost=float(metrics.total_cost or 0.0),
        models_used=models_used
    )


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    db: DBSession = Depends(get_db)
):
    """
    Permanently delete a session and all its events.
    This action cannot be undone.
    """
    # Query session
    session = db.query(Session).filter(Session.session_id == session_id).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Delete session (cascade will delete all events)
    db.delete(session)
    db.commit()

    logger.info(f"Deleted session {session_id}")

    return {
        "success": True,
        "message": "Session deleted successfully",
        "session_id": session_id
    }
