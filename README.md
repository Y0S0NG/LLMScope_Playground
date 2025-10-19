# LLMScope Playground

A standalone session-based LLM monitoring and analytics demo application. Track your LLM API calls, analyze token usage, monitor costs, and measure performance—all without requiring user accounts.

## 🚀 Live Demo

**Try it now:** [https://llmscopeplaygroundfrontend-jt7rirsds-yosongyxp-7364s-projects.vercel.app](https://llmscopeplaygroundfrontend-jt7rirsds-yosongyxp-7364s-projects.vercel.app)

- **Backend API**: [https://llmscopeplaygroundbackend-production.up.railway.app](https://llmscopeplaygroundbackend-production.up.railway.app)
- **API Documentation**: [https://llmscopeplaygroundbackend-production.up.railway.app/docs](https://llmscopeplaygroundbackend-production.up.railway.app/docs)

---

## ✨ Features

- **Session Management**: UUID-based session isolation without user accounts
- **Real-time Chat**: Interactive chat interface with Claude AI
- **Event Tracking**: Monitor LLM API calls with detailed metrics
- **Analytics Dashboard**: Track tokens, costs, latency, and errors per session
- **Auto Cleanup**: Automatic session expiration after 7 days of inactivity
- **RESTful API**: Complete API with auto-generated Swagger documentation
- **Real-time Updates**: Live metrics and event streaming

---

## 🏗️ Architecture

### Tech Stack

**Frontend:**
- React 18 with TypeScript
- Vite for blazing-fast builds
- TailwindCSS for styling
- Recharts for analytics visualization
- Axios for API communication

**Backend:**
- FastAPI (Python 3.11+)
- PostgreSQL database
- SQLAlchemy ORM
- Alembic for migrations
- Anthropic Claude API integration

**Deployment:**
- Frontend: Vercel (HTTPS, auto-deploy)
- Backend: Railway (HTTPS, PostgreSQL included)
- Free tier hosting with production-ready setup

---

## 🚀 Quick Start

### Option 1: Use the Live Demo

Simply visit [the live playground](https://llmscopeplaygroundfrontend-jt7rirsds-yosongyxp-7364s-projects.vercel.app) - no setup required!

### Option 2: Local Development

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your DATABASE_URL and ANTHROPIC_API_KEY

# Run database migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

Backend will be available at http://localhost:8000

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
echo "VITE_API_URL=http://localhost:8000" > .env.development

# Start development server
npm run dev
```

Frontend will be available at http://localhost:5173

---

## 📦 Deployment

### Deploy Your Own Instance

#### Backend on Railway

1. **Create Railway Account**: [railway.app](https://railway.app)
2. **Deploy from CLI**:
   ```bash
   cd backend
   npm i -g @railway/cli
   railway login
   railway up
   ```
3. **Add PostgreSQL Database**:
   - In Railway dashboard → New → Database → PostgreSQL
   - `DATABASE_URL` is auto-configured
4. **Set Environment Variables**:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   SECRET_KEY=your-random-secret-key
   CORS_ORIGINS=*
   ```
5. **Generate Domain**: Settings → Networking → Generate Domain

#### Frontend on Vercel

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```
2. **Deploy**:
   ```bash
   cd frontend
   vercel --prod
   ```
3. **Set Environment Variable**:
   ```bash
   vercel env add VITE_API_URL production
   # Enter your Railway backend URL when prompted
   ```

For detailed deployment instructions, see [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md).

---

## 🔧 Configuration

### Backend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `ANTHROPIC_API_KEY` | Yes | - | Anthropic API key for Claude |
| `SECRET_KEY` | Yes | - | Application secret key |
| `PORT` | No | 8000 | Server port (Railway sets this) |
| `CORS_ORIGINS` | No | `*` | Allowed CORS origins |

### Frontend Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | Yes | Backend API URL (e.g., https://your-backend.up.railway.app) |

---

## 📖 API Reference

### Session Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/sessions/create` | Create new session |
| GET | `/api/v1/sessions/current/info` | Get current session info |
| GET | `/api/v1/sessions/current/metrics` | Get session analytics |
| POST | `/api/v1/sessions/current/reset` | Clear session events |

### Chat & Events

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/playground/chat` | Send chat message |
| GET | `/api/v1/playground/events` | Get all events for session |

### Monitoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check endpoint |
| GET | `/api/v1/cleanup/stats` | Session cleanup statistics |
| POST | `/api/v1/cleanup/run` | Manually trigger cleanup |

**Interactive API Documentation:**
- Swagger UI: [/docs](https://llmscopeplaygroundbackend-production.up.railway.app/docs)
- ReDoc: [/redoc](https://llmscopeplaygroundbackend-production.up.railway.app/redoc)

---

## 📊 Project Structure

```
LLMScope_Playground/
├── backend/
│   ├── app/
│   │   ├── api/              # API route handlers
│   │   │   ├── sessions.py   # Session management
│   │   │   ├── chat.py       # Chat endpoints
│   │   │   └── events.py     # Event tracking
│   │   ├── db/
│   │   │   ├── models.py     # SQLAlchemy models
│   │   │   ├── base.py       # Database connection
│   │   │   └── migrations/   # Alembic migrations
│   │   ├── services/
│   │   │   └── session_cleanup.py
│   │   ├── main.py           # FastAPI application
│   │   ├── config.py         # Configuration
│   │   └── dependencies.py   # Dependency injection
│   ├── init_db.py           # Database initialization
│   ├── start.sh             # Startup script
│   ├── railway.json         # Railway configuration
│   ├── Procfile             # Process definition
│   ├── requirements.txt     # Python dependencies
│   └── alembic.ini          # Migration config
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── api/             # API client
│   │   ├── types/           # TypeScript types
│   │   └── App.tsx          # Main app component
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

---

## 🗄️ Database Schema

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

---

## 🔐 Security Features

- **Session Isolation**: Each session is completely isolated
- **Cookie-based Authentication**: Secure session persistence
- **CORS Protection**: Configurable origin restrictions
- **Environment-based Secrets**: No hardcoded credentials
- **Rate Limiting**: Per-session request limiting
- **Auto Cleanup**: Expired sessions automatically removed

---

## 🧪 Testing

### Health Check
```bash
curl https://llmscopeplaygroundbackend-production.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "sessions": 42,
  "events": 1337
}
```

### Create Session
```bash
SESSION_ID=$(curl -s -X POST \
  https://llmscopeplaygroundbackend-production.up.railway.app/api/v1/sessions/create \
  | jq -r .session_id)

echo "Session ID: $SESSION_ID"
```

### Send Chat Message
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: $SESSION_ID" \
  -d '{"message": "Hello, Claude!"}' \
  https://llmscopeplaygroundbackend-production.up.railway.app/api/v1/playground/chat
```

---

## 🛠️ Development

### Run Tests
```bash
cd backend
pytest
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Code Formatting
```bash
# Backend
black app/
isort app/

# Frontend
npm run lint
npm run format
```

---

## 🐛 Troubleshooting

### Backend Issues

**Database Connection Error:**
```bash
# Verify DATABASE_URL is set
railway variables

# Test database connection
psql $DATABASE_URL -c "SELECT 1"
```

**Port Binding Error:**
- Ensure Railway sets `PORT` environment variable
- Start command uses `$PORT`: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend Issues

**API Connection Error:**
- Check `VITE_API_URL` in Vercel dashboard
- Ensure backend URL uses HTTPS
- Verify CORS is configured on backend

**Build Failures:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

## 📈 Performance

- **Cold Start**: < 2 seconds (Railway)
- **API Response**: < 100ms (session endpoints)
- **Chat Latency**: 1-3 seconds (depends on Claude API)
- **Database Queries**: < 50ms (indexed lookups)

---

## 🌟 Features Roadmap

### ✅ Phase 1: Core Backend (Completed)
- Session management API
- Event tracking system
- Database schema & migrations
- Session cleanup service
- Railway deployment

### ✅ Phase 2: Frontend (Completed)
- React SPA with routing
- Chat interface
- Real-time metrics dashboard
- Session management UI
- Vercel deployment

### 🔄 Phase 3: Enhancements (In Progress)
- [ ] WebSocket real-time updates
- [ ] Advanced analytics charts
- [ ] Export functionality (CSV, JSON)
- [ ] Multi-model support (GPT, Gemini)
- [ ] Cost optimization insights

### 🔮 Phase 4: Advanced Features
- [ ] User authentication (optional)
- [ ] Team collaboration
- [ ] Custom alert configuration
- [ ] API usage quotas
- [ ] Webhook integrations

---

## 💰 Cost Breakdown

### Free Tier Deployment

**Railway:**
- $5/month free credit
- PostgreSQL: 500 MB storage (free)
- Execution time: ~500 hours/month (free)
- Estimated usage: $2-3/month ✅

**Vercel:**
- 100 GB bandwidth/month (free)
- Unlimited deployments (free)
- HTTPS included (free)
- Estimated cost: $0/month ✅

**Total: $0-3/month** (within free tiers)

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📞 Support

- **Live Demo**: [Try it here](https://llmscopeplaygroundfrontend-jt7rirsds-yosongyxp-7364s-projects.vercel.app)
- **API Docs**: [Swagger UI](https://llmscopeplaygroundbackend-production.up.railway.app/docs)
- **Deployment Guide**: [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/LLMScope_Playground/issues)

---

**Built with ❤️ using FastAPI, React, and Railway**
