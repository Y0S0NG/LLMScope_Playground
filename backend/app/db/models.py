"""SQLAlchemy models for Playground application"""
from sqlalchemy import Column, String, DateTime, Integer, Boolean, Text, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base
import uuid


class Session(Base):
    """Session model for session-based isolation (no user accounts needed)"""
    __tablename__ = "playground_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    session_metadata = Column(JSONB, default={})  # Store any session-specific data

    # Session state
    is_active = Column(Boolean, default=True)

    # Relationships
    events = relationship("LLMEvent", back_populates="session", cascade="all, delete-orphan")


class LLMEvent(Base):
    """LLM events hypertable model"""
    __tablename__ = "playground_events"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)

    # Session tracking (instead of tenant/project for playground)
    session_id = Column(UUID(as_uuid=True), ForeignKey('playground_sessions.id', ondelete='CASCADE'), nullable=False, index=True)

    # Request metadata
    model = Column(String(50), index=True)
    provider = Column(String(50), index=True)
    endpoint = Column(String(255))

    # User tracking (optional, for playground context)
    user_id = Column(String(255), index=True)

    # Token usage
    tokens_prompt = Column(Integer)
    tokens_completion = Column(Integer)
    tokens_total = Column(Integer)

    # Performance metrics
    latency_ms = Column(Integer)
    time_to_first_token_ms = Column(Integer)

    # Cost tracking
    cost_usd = Column(DECIMAL(10, 6))

    # Content (compressed)
    messages = Column(JSONB)
    response = Column(Text)

    # Model parameters
    temperature = Column(DECIMAL(3, 2))
    max_tokens = Column(Integer)
    top_p = Column(DECIMAL(3, 2))

    # Status and flags
    status = Column(String(20))
    error_message = Column(Text)
    has_error = Column(Boolean, default=False)
    pii_detected = Column(Boolean, default=False)

    # Relationships
    session = relationship("Session", back_populates="events")
