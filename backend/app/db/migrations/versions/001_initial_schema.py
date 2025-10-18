"""Initial schema with sessions and llm_events tables

Revision ID: 001_initial_schema
Revises:
Create Date: 2024-10-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create playground_sessions table
    op.create_table(
        'playground_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_activity', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('session_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )
    op.create_index(op.f('ix_playground_sessions_session_id'), 'playground_sessions', ['session_id'], unique=False)

    # Create playground_events table
    op.create_table(
        'playground_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('model', sa.String(length=50), nullable=True),
        sa.Column('provider', sa.String(length=50), nullable=True),
        sa.Column('endpoint', sa.String(length=255), nullable=True),
        sa.Column('user_id', sa.String(length=255), nullable=True),
        sa.Column('tokens_prompt', sa.Integer(), nullable=True),
        sa.Column('tokens_completion', sa.Integer(), nullable=True),
        sa.Column('tokens_total', sa.Integer(), nullable=True),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('time_to_first_token_ms', sa.Integer(), nullable=True),
        sa.Column('cost_usd', sa.DECIMAL(precision=10, scale=6), nullable=True),
        sa.Column('messages', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('response', sa.Text(), nullable=True),
        sa.Column('temperature', sa.DECIMAL(precision=3, scale=2), nullable=True),
        sa.Column('max_tokens', sa.Integer(), nullable=True),
        sa.Column('top_p', sa.DECIMAL(precision=3, scale=2), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('has_error', sa.Boolean(), nullable=True),
        sa.Column('pii_detected', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['playground_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', 'time')
    )
    op.create_index(op.f('ix_playground_events_session_id'), 'playground_events', ['session_id'], unique=False)
    op.create_index(op.f('ix_playground_events_model'), 'playground_events', ['model'], unique=False)
    op.create_index(op.f('ix_playground_events_provider'), 'playground_events', ['provider'], unique=False)
    op.create_index(op.f('ix_playground_events_user_id'), 'playground_events', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_playground_events_user_id'), table_name='playground_events')
    op.drop_index(op.f('ix_playground_events_provider'), table_name='playground_events')
    op.drop_index(op.f('ix_playground_events_model'), table_name='playground_events')
    op.drop_index(op.f('ix_playground_events_session_id'), table_name='playground_events')
    op.drop_table('playground_events')
    op.drop_index(op.f('ix_playground_sessions_session_id'), table_name='playground_sessions')
    op.drop_table('playground_sessions')
