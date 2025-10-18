"""Dependency injection for session management"""
from fastapi import Depends, HTTPException, Cookie, Request
from typing import Optional
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.sql import func
from .config import settings
from .db.base import get_db
from .db.models import Session
import uuid
import logging

logger = logging.getLogger(__name__)


async def get_session_id(
    request: Request,
    session_id: Optional[str] = Cookie(None, alias=settings.session_cookie_name)
) -> str:
    """
    Extract session ID from cookie or create a new one.
    This will be used by the frontend to maintain session state.
    """
    # Try to get session_id from cookie
    if session_id:
        logger.info(f"Session ID from cookie: {session_id}")
        return session_id

    # Try to get session_id from header (for API clients)
    header_session_id = request.headers.get("X-Session-ID")
    if header_session_id:
        logger.info(f"Session ID from header: {header_session_id}")
        return header_session_id

    # Generate new session ID
    new_session_id = str(uuid.uuid4())
    logger.info(f"Generated new session ID: {new_session_id}")
    return new_session_id


async def get_current_session(
    session_id: str = Depends(get_session_id),
    db: DBSession = Depends(get_db)
) -> Session:
    """
    Get or create current session from database.
    Updates last_activity timestamp on each access.
    """
    # Query session from database
    session = db.query(Session).filter(Session.session_id == session_id).first()

    if not session:
        # Create new session
        logger.info(f"Creating new session: {session_id}")
        session = Session(
            session_id=session_id,
            is_active=True,
            metadata={}
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    else:
        # Update last_activity timestamp
        session.last_activity = func.now()
        db.commit()
        db.refresh(session)
        logger.info(f"Updated session activity: {session_id}")

    return session


async def require_active_session(
    session: Session = Depends(get_current_session)
) -> Session:
    """
    Ensure session is active.
    This can be used as a dependency for endpoints that require an active session.
    """
    if not session.is_active:
        raise HTTPException(
            status_code=403,
            detail="Session is not active. Please create a new session."
        )

    return session


class SessionMiddleware:
    """
    Middleware to inject session context into requests.
    This ensures every request has access to the current session.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Add session context to request state
        if scope["type"] == "http":
            # Session will be injected via dependencies
            pass

        await self.app(scope, receive, send)
