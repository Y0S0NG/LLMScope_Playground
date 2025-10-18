"""Chat API endpoint for playground"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession
import os
import time
import logging
from anthropic import Anthropic
from datetime import datetime
import uuid as uuid_lib

from ..db.models import Session, LLMEvent
from ..db.base import get_db
from ..dependencies import get_current_session
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/playground", tags=["playground"])

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    event_id: str

# Initialize Anthropic client
anthropic_client = None

def get_anthropic_client():
    global anthropic_client
    if anthropic_client is None:
        api_key = settings.anthropic_api_key
        if not api_key:
            raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")
        anthropic_client = Anthropic(api_key=api_key)
    return anthropic_client

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    session: Session = Depends(get_current_session),
    db: DBSession = Depends(get_db)
):
    """Chat with Claude and track the interaction"""
    try:
        logger.info(f"Received chat request: {request.message[:50]}...")
        client = get_anthropic_client()

        # Call Anthropic API
        start_time = time.time()
        logger.info("Calling Anthropic API...")
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": request.message}]
        )
        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)
        logger.info(f"Anthropic API call successful, latency: {latency_ms}ms")

        # Extract response
        assistant_message = response.content[0].text
        logger.info(f"Response extracted: {assistant_message[:50]}...")

        # Calculate cost (approximate for Claude 3.5 Sonnet)
        cost_per_1k_input = 0.003
        cost_per_1k_output = 0.015
        cost_usd = (
            (response.usage.input_tokens / 1000) * cost_per_1k_input +
            (response.usage.output_tokens / 1000) * cost_per_1k_output
        )

        # Create event
        event = LLMEvent(
            time=datetime.utcnow(),
            session_id=session.id,
            model="claude-3-5-sonnet-20241022",
            provider="anthropic",
            endpoint="/api/v1/playground/chat",
            tokens_prompt=response.usage.input_tokens,
            tokens_completion=response.usage.output_tokens,
            tokens_total=response.usage.input_tokens + response.usage.output_tokens,
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            messages=[{"role": "user", "content": request.message}],
            response=assistant_message,
            status="success",
            has_error=False,
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        return ChatResponse(
            response=assistant_message,
            event_id=str(event.id)
        )

    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        # Log error event
        try:
            error_event = LLMEvent(
                time=datetime.utcnow(),
                session_id=session.id,
                model="claude-3-5-sonnet-20241022",
                provider="anthropic",
                endpoint="/api/v1/playground/chat",
                status="error",
                has_error=True,
                error_message=str(e),
                tokens_prompt=0,
                tokens_completion=0,
                tokens_total=0,
            )
            db.add(error_event)
            db.commit()
        except Exception as db_error:
            logger.error(f"Failed to log error event: {str(db_error)}", exc_info=True)

        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
