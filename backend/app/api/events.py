"""Events API endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import desc
from typing import List
from pydantic import BaseModel
from datetime import datetime

from ..db.models import Session, LLMEvent
from ..db.base import get_db
from ..dependencies import get_current_session

router = APIRouter(prefix="/events", tags=["events"])

class EventResponse(BaseModel):
    id: str
    time: datetime
    model: str
    provider: str
    tokens_total: int
    tokens_prompt: int
    tokens_completion: int
    cost_usd: float
    latency_ms: int | None
    status: str
    has_error: bool
    error: str | None = None

    class Config:
        from_attributes = True

@router.get("/recent", response_model=List[EventResponse])
async def get_recent_events(
    limit: int = 50,
    session: Session = Depends(get_current_session),
    db: DBSession = Depends(get_db)
):
    """Get recent events for the current session"""
    events = db.query(LLMEvent).filter(
        LLMEvent.session_id == session.id
    ).order_by(desc(LLMEvent.time)).limit(limit).all()

    return [
        EventResponse(
            id=str(e.id),
            time=e.time,
            model=e.model or "unknown",
            provider=e.provider or "unknown",
            tokens_total=e.tokens_total or 0,
            tokens_prompt=e.tokens_prompt or 0,
            tokens_completion=e.tokens_completion or 0,
            cost_usd=float(e.cost_usd or 0),
            latency_ms=e.latency_ms,
            status=e.status or "unknown",
            has_error=e.has_error or False,
            error=e.error_message,
        )
        for e in events
    ]
