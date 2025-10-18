# LLMScope Playground - Deployment Guide

This guide covers deploying the LLMScope Playground to various hosting platforms.

## Prerequisites

1. **PostgreSQL Database** (required)
   - Get a free PostgreSQL database from:
     - [Supabase](https://supabase.com) (recommended, generous free tier)
     - [Neon](https://neon.tech) (serverless Postgres)
     - [Railway](https://railway.app) (includes Postgres)
     - [Render](https://render.com) (includes Postgres)

2. **Anthropic API Key** (required for chat features)
   - Get from [Anthropic Console](https://console.anthropic.com/)

## Quick Deploy Options

### Option 1: Railway (Recommended - Easiest)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

1. Click "Deploy on Railway" button
2. Connect your GitHub repository
3. Add environment variables:
   ```
   DATABASE_URL=<your-postgres-url>
   ANTHROPIC_API_KEY=<your-api-key>
   SECRET_KEY=<random-string>
   ```
4. Railway will auto-detect and deploy!

**Cost**: ~$5/month for the app, Postgres included in free tier

### Option 2: Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your repository
4. Configure:
   - **Build Command**: `cd playground/backend && pip install -r requirements.txt`
   - **Start Command**: `cd playground/backend && ./start.sh`
   - **Environment**: Python 3
5. Add environment variables (see below)
6. Click "Create Web Service"

**Cost**: Free tier available (spins down after inactivity)

### Option 3: Heroku

```bash
# Install Heroku CLI
brew install heroku  # or download from heroku.com

# Login and create app
heroku login
cd playground/backend
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:essential-0

# Set environment variables
heroku config:set ANTHROPIC_API_KEY=your-key
heroku config:set SECRET_KEY=$(openssl rand -hex 32)

# Deploy
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

**Cost**: $5/month for Eco dynos, $5/month for Essential Postgres

### Option 4: DigitalOcean App Platform

1. Go to [DigitalOcean Apps](https://cloud.digitalocean.com/apps)
2. Click "Create App" → Connect GitHub
3. Select your repository and `playground/backend` directory
4. Configure:
   - **Run Command**: `./start.sh`
   - **Build Command**: `pip install -r requirements.txt`
5. Add PostgreSQL database from Components
6. Set environment variables
7. Deploy!

**Cost**: $5/month for app, $15/month for managed Postgres

### Option 5: Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login and launch
cd playground/backend
fly auth login
fly launch

# Add PostgreSQL
fly postgres create

# Connect app to database
fly postgres attach <postgres-app-name>

# Set environment variables
fly secrets set ANTHROPIC_API_KEY=your-key
fly secrets set SECRET_KEY=$(openssl rand -hex 32)

# Deploy
fly deploy
```

**Cost**: Generous free tier, ~$5/month beyond that

## Required Environment Variables

Set these on your hosting platform:

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | ✅ Yes | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `ANTHROPIC_API_KEY` | ✅ Yes | Your Anthropic API key | `sk-ant-...` |
| `SECRET_KEY` | ✅ Yes | Random secret for security | Generate with `openssl rand -hex 32` |
| `PORT` | ⚠️ Auto | Server port (set by platform) | `8001` |
| `HOST` | ⚠️ Auto | Server host | `0.0.0.0` |

### Optional Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PLAYGROUND_SESSION_TTL_DAYS` | `7` | Days before session expires |
| `PLAYGROUND_CORS_ORIGINS` | `*` | Allowed CORS origins |
| `PLAYGROUND_RATE_LIMIT_REQUESTS_PER_SESSION` | `100` | Rate limit per session |

## Database Setup

### Using Supabase (Recommended)

1. Create account at [supabase.com](https://supabase.com)
2. Create new project
3. Go to Settings → Database
4. Copy the connection string (use "Connection Pooling" for production)
5. Use this as your `DATABASE_URL`

**Format**: `postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres`

### Using Neon

1. Create account at [neon.tech](https://neon.tech)
2. Create new project
3. Copy connection string from dashboard
4. Use this as your `DATABASE_URL`

**Format**: `postgresql://[user]:[password]@[endpoint].neon.tech/[database]`

### Using Railway Postgres

Railway automatically sets `DATABASE_URL` when you add a Postgres service. No manual configuration needed!

## Manual Deployment (VPS)

If deploying to your own server (AWS EC2, DigitalOcean Droplet, etc.):

### 1. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install PostgreSQL client (for migrations)
sudo apt install postgresql-client -y
```

### 2. Setup Application

```bash
# Clone repository
git clone <your-repo-url>
cd playground/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Create .env file
cat > .env << EOL
DATABASE_URL=postgresql://user:pass@host:5432/database
ANTHROPIC_API_KEY=your-key-here
SECRET_KEY=$(openssl rand -hex 32)
PORT=8001
HOST=0.0.0.0
EOL
```

### 4. Run Migrations

```bash
alembic upgrade head
```

### 5. Start with systemd (Production)

Create `/etc/systemd/system/llmscope-playground.service`:

```ini
[Unit]
Description=LLMScope Playground API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/playground/backend
Environment="PATH=/path/to/playground/backend/venv/bin"
EnvironmentFile=/path/to/playground/backend/.env
ExecStart=/path/to/playground/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable llmscope-playground
sudo systemctl start llmscope-playground
sudo systemctl status llmscope-playground
```

### 6. Nginx Reverse Proxy (Optional)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable SSL with Certbot:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Local Development

For local development without deployment:

```bash
cd playground/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your local database URL and API keys

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8001
```

Access at: http://localhost:8001

## Verification

After deployment, verify everything works:

### 1. Health Check

```bash
curl https://your-app-url.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "sessions": 0,
  "events": 0
}
```

### 2. Create Session

```bash
curl -X POST https://your-app-url.com/api/v1/sessions/create
```

Expected response:
```json
{
  "session_id": "550e8400-...",
  "message": "Session created successfully"
}
```

### 3. API Documentation

Visit: `https://your-app-url.com/docs`

You should see the interactive Swagger UI.

## Troubleshooting

### "Database connection failed"

- Verify `DATABASE_URL` is correct
- Check database allows connections from your app's IP
- For Supabase, use connection pooling URL (port 6543)
- Ensure database exists and is accessible

### "Migration failed"

```bash
# Check current migration status
alembic current

# Show migration history
alembic history

# Force upgrade
alembic upgrade head
```

### "Port already in use"

- Check if another process is using the port
- Platform may set `PORT` automatically - don't hardcode it

### "Import errors"

```bash
# Ensure all dependencies installed
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.11+
```

## Monitoring

### Application Logs

- **Railway**: View in dashboard
- **Render**: View in dashboard → Logs
- **Heroku**: `heroku logs --tail`
- **Systemd**: `sudo journalctl -u llmscope-playground -f`

### Database Monitoring

Most platforms provide database metrics in their dashboard:
- Connection count
- Query performance
- Storage usage

### Session Cleanup

Schedule cleanup job on your platform:

**Railway/Render** - Use their cron service:
```bash
python -m app.services.session_cleanup
```

**Heroku** - Use Heroku Scheduler addon

**Manual Cron** on VPS:
```bash
# Add to crontab
0 2 * * * cd /path/to/backend && /path/to/venv/bin/python -m app.services.session_cleanup
```

## Cost Estimates

| Platform | App Cost | Database Cost | Total/Month |
|----------|----------|---------------|-------------|
| Railway | $5 | Included | ~$5 |
| Render | Free* | Free* | $0 (with limits) |
| Heroku | $5 | $5 | $10 |
| DigitalOcean | $5 | $15 | $20 |
| Fly.io | $0-5 | $0-5 | $0-10 |
| VPS (DigitalOcean) | $6 | Included | $6 |

*Free tiers have limitations (spins down, limited hours, etc.)

## Security Checklist

Before going to production:

- [ ] Set strong `SECRET_KEY` (use `openssl rand -hex 32`)
- [ ] Set `ANTHROPIC_API_KEY` securely (use platform secrets)
- [ ] Configure `PLAYGROUND_CORS_ORIGINS` to your domain (not `*`)
- [ ] Use HTTPS (most platforms provide this automatically)
- [ ] Enable database SSL if available
- [ ] Set up regular database backups
- [ ] Monitor API usage and costs
- [ ] Set up error tracking (optional: Sentry)

## Next Steps

After deployment:

1. **Test all endpoints** using the `/docs` page
2. **Set up monitoring** for errors and performance
3. **Configure domain** if using custom domain
4. **Implement Phase 2** - Add the frontend application
5. **Set up CI/CD** for automatic deployments

## Support

For deployment issues:
- Check platform documentation
- Review application logs
- Verify environment variables
- Test database connection separately

For application issues:
- Check [README.md](README.md) for API documentation
- Run tests locally first
- Check [TESTING_GUIDE.md](TESTING_GUIDE.md)
