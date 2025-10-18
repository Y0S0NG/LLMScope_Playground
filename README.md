# LLMScope Playground

A standalone session-based LLM monitoring and analytics demo application.

## Features

- **Session Management**: UUID-based session isolation without user accounts
- **Event Tracking**: Monitor LLM API calls with detailed metrics
- **Analytics**: Track tokens, costs, latency, and errors per session
- **Auto Cleanup**: Automatic session expiration after 7 days of inactivity
- **RESTful API**: Complete API with auto-generated documentation

## Quick Deploy

### One-Click Deploy

**Railway** (Recommended):
1. Click the "Deploy on Railway" button
2. Add PostgreSQL service
3. Set environment variables (see below)
4. Deploy!

**Render**:
1. Fork this repository
2. Connect to Render
3. Add PostgreSQL database
4. Set environment variables
5. Deploy from `playground/backend` directory

### Required Environment Variables

```bash
DATABASE_URL=postgresql://user:pass@host:5432/database
ANTHROPIC_API_KEY=sk-ant-your-key-here
SECRET_KEY=your-random-secret-key
```

**Generate SECRET_KEY**:
```bash
openssl rand -hex 32
```

## Local Development

```bash
cd playground/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL and ANTHROPIC_API_KEY

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8001
```

Visit http://localhost:8001/docs for API documentation.

## API Endpoints

### Session Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/sessions/create` | Create new session |
| GET | `/api/v1/sessions/current/info` | Get current session info |
| GET | `/api/v1/sessions/current/metrics` | Get session metrics |
| POST | `/api/v1/sessions/current/reset` | Clear session events |
| DELETE | `/api/v1/sessions/{id}` | Delete session |

### Monitoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/cleanup/stats` | Cleanup statistics |
| POST | `/api/v1/cleanup/run` | Run cleanup job |

## Usage Example

```bash
# Create a session
SESSION_ID=$(curl -s -X POST http://localhost:8001/api/v1/sessions/create | jq -r .session_id)

# Get session info
curl -H "X-Session-ID: $SESSION_ID" http://localhost:8001/api/v1/sessions/current/info

# Get metrics
curl -H "X-Session-ID: $SESSION_ID" http://localhost:8001/api/v1/sessions/current/metrics

# Reset session
curl -X POST -H "X-Session-ID: $SESSION_ID" http://localhost:8001/api/v1/sessions/current/reset
```

## Project Structure

```
playground/backend/
├── app/
│   ├── api/              # API endpoints
│   │   └── sessions.py   # Session management
│   ├── db/
│   │   ├── models.py     # Database models
│   │   ├── base.py       # Database connection
│   │   └── migrations/   # Alembic migrations
│   ├── services/
│   │   └── session_cleanup.py  # Cleanup service
│   ├── main.py          # FastAPI application
│   ├── config.py        # Configuration
│   └── dependencies.py  # Session injection
├── requirements.txt
├── Procfile            # For Heroku/Railway/Render
├── start.sh           # Production startup script
└── alembic.ini        # Migration config
```

## Database Schema

### Sessions Table
- `id`: UUID primary key
- `session_id`: Unique session identifier
- `created_at`: Creation timestamp
- `last_activity`: Last activity timestamp
- `is_active`: Active status flag
- `metadata`: JSON metadata

### LLM Events Table
- `id`: UUID primary key
- `time`: Event timestamp
- `session_id`: Foreign key to sessions
- `model`, `provider`: Model information
- `tokens_prompt`, `tokens_completion`, `tokens_total`: Token usage
- `cost_usd`: Cost tracking
- `latency_ms`: Performance metrics
- `status`, `error_message`: Status tracking

## Configuration

All configuration via environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `ANTHROPIC_API_KEY` | Yes | - | Anthropic API key |
| `SECRET_KEY` | Yes | - | Application secret key |
| `PORT` | No | 8001 | Server port |
| `PLAYGROUND_SESSION_TTL_DAYS` | No | 7 | Session expiration (days) |
| `PLAYGROUND_CORS_ORIGINS` | No | * | Allowed CORS origins |

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment guides for:
- Railway
- Render
- Heroku
- Fly.io
- DigitalOcean
- Manual VPS deployment

### Quick Deploy Command

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server (production)
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8001}
```

Or use the startup script:
```bash
./start.sh
```

## Testing

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing instructions.

Quick health check:
```bash
curl http://localhost:8001/health
```

## Session Cleanup

Automatic cleanup removes sessions inactive for more than 7 days.

**Manual cleanup**:
```bash
# Dry run (preview)
curl -X POST "http://localhost:8001/api/v1/cleanup/run?dry_run=true"

# Execute cleanup
curl -X POST "http://localhost:8001/api/v1/cleanup/run?dry_run=false"
```

**Scheduled cleanup** (add to cron):
```bash
0 2 * * * cd /path/to/backend && python -m app.services.session_cleanup
```

## Monitoring

### Health Endpoint
```bash
curl http://your-app-url.com/health
```

Returns:
```json
{
  "status": "healthy",
  "database": "connected",
  "sessions": 150,
  "events": 4203
}
```

### Cleanup Statistics
```bash
curl http://your-app-url.com/api/v1/cleanup/stats
```

Returns session statistics and cleanup targets.

## API Documentation

Interactive API documentation is automatically available at:
- **Swagger UI**: http://your-app-url.com/docs
- **ReDoc**: http://your-app-url.com/redoc
- **OpenAPI JSON**: http://your-app-url.com/openapi.json

## Architecture

### Session-Based Isolation
- No user accounts required
- Each visitor gets a unique session
- Sessions tracked via cookies or headers
- Automatic session creation on first visit

### Database Strategy
- PostgreSQL for persistence
- Session-scoped events
- Cascade deletion (delete session → delete events)
- Indexed for performance

### Security
- Cookie-based session persistence
- Environment-based secrets
- CORS configuration
- Rate limiting per session

## Development Roadmap

### Phase 1: Session Management ✅ (Current)
- Session CRUD operations
- Event tracking schema
- Cleanup service
- API endpoints
- Deployment configuration

### Phase 2: Frontend (Next)
- React SPA with routing
- Landing page
- Playground UI (chat + metrics)
- Dashboard with analytics
- WebSocket real-time updates

### Phase 3: Advanced Features
- User authentication (optional)
- Export functionality
- Advanced analytics
- Alert configuration

## Troubleshooting

### Database Connection Errors
```bash
# Verify DATABASE_URL format
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### Migration Issues
```bash
# Check migration status
alembic current

# Reset migrations (WARNING: deletes data)
alembic downgrade base
alembic upgrade head
```

### Application Errors
```bash
# Check logs (platform-specific)
# Railway: View in dashboard
# Render: Dashboard → Logs
# Heroku: heroku logs --tail
# Local: Check terminal output
```

## Support

- **Documentation**: See [DEPLOYMENT.md](DEPLOYMENT.md) and [TESTING_GUIDE.md](TESTING_GUIDE.md)
- **API Reference**: Visit `/docs` endpoint
- **Issues**: Report bugs in GitHub issues
- **Implementation**: See [PHASE1_SUMMARY.md](PHASE1_SUMMARY.md)

## License

MIT License - See LICENSE file for details

---

**Ready to deploy?** See [DEPLOYMENT.md](DEPLOYMENT.md) for platform-specific guides.
