# AWS Deployment Files Summary

## Files Created for AWS Elastic Beanstalk Deployment

### Backend Configuration Files

**Location: `backend/.ebextensions/`**

1. **`01_packages.config`**
   - Installs PostgreSQL development libraries
   - Configures Python WSGI path
   - Sets up Python environment

2. **`02_python.config`**
   - Configures Python application settings
   - Sets static file serving

**Location: `backend/.platform/hooks/predeploy/`**

3. **`01_migrations.sh`**
   - Executable script that runs Alembic migrations before deployment
   - Ensures database schema is up-to-date

**Modified:**

4. **`backend/Procfile`**
   - Updated to run on port 8000 (EB default)
   - Removed migration from Procfile (now in predeploy hook)

### Frontend Configuration Files

**Location: `frontend/.ebextensions/`**

5. **`01_nginx.config`**
   - Configures Nginx for React Router
   - Enables SPA routing (redirects to index.html)

6. **`02_environment.config`**
   - Sets Node.js version
   - Configures static file serving from `dist/`

7. **`frontend/Buildfile`**
   - Tells EB to run `npm run build` during deployment

8. **`frontend/Procfile`**
   - Serves the built React app using `serve` package
   - Runs on port 8080

**Modified:**

9. **`frontend/package.json`**
   - Added `serve` dependency
   - Added `start` script for production

### Documentation Files

10. **`AWS_DEPLOYMENT.md`**
    - Complete step-by-step deployment guide
    - Covers RDS setup, EB deployment, security configuration
    - Includes troubleshooting and cost management

11. **`AWS_QUICK_START.md`**
    - Quick reference guide
    - Essential commands
    - 5-minute deployment walkthrough

12. **`DEPLOYMENT.md`** (Updated)
    - Added AWS Elastic Beanstalk as Option 1
    - Detailed AWS deployment instructions inline

13. **`README.md`** (Updated)
    - Added AWS deployment reference
    - Links to AWS_DEPLOYMENT.md

14. **`.ebignore`**
    - Tells EB which files to exclude from deployment
    - Reduces deployment package size

## File Structure

```
LLMScope_Playground/
├── AWS_DEPLOYMENT.md           # Complete AWS guide
├── AWS_QUICK_START.md          # Quick reference
├── DEPLOYMENT.md               # Updated with AWS section
├── README.md                   # Updated with AWS link
├── .ebignore                   # EB ignore file
├── backend/
│   ├── .ebextensions/
│   │   ├── 01_packages.config
│   │   └── 02_python.config
│   ├── .platform/
│   │   └── hooks/
│   │       └── predeploy/
│   │           └── 01_migrations.sh  # Executable
│   └── Procfile                # Updated for port 8000
└── frontend/
    ├── .ebextensions/
    │   ├── 01_nginx.config
    │   └── 02_environment.config
    ├── Buildfile
    ├── Procfile
    └── package.json            # Updated with serve
```

## Next Steps

### 1. Install Required Tools

```bash
# macOS
brew install awscli awsebcli

# Linux/Windows
pip install awsebcli --upgrade --user
```

### 2. Configure AWS

```bash
aws configure
```

### 3. Follow Deployment Guide

Choose your preferred guide:
- **Quick Start**: [AWS_QUICK_START.md](AWS_QUICK_START.md) - 15 minutes
- **Complete Guide**: [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md) - 30 minutes with explanations

### 4. Deploy

```bash
# Deploy backend
cd backend
eb init -p python-3.11 llmscope-backend --region us-east-1
eb create llmscope-backend-env --instance-type t3.micro --single
eb setenv DATABASE_URL="..." ANTHROPIC_API_KEY="..." SECRET_KEY="..."
eb deploy

# Deploy frontend
cd ../frontend
eb init -p node.js-18 llmscope-frontend --region us-east-1
eb create llmscope-frontend-env --instance-type t3.micro --single
eb deploy
```

## Configuration Notes

### Environment Variables Required

**Backend:**
- `DATABASE_URL` - PostgreSQL connection string
- `ANTHROPIC_API_KEY` - Your Anthropic API key
- `SECRET_KEY` - Random secret (generate with `openssl rand -hex 32`)
- `PORT` - 8000 (default for EB)
- `HOST` - 0.0.0.0
- `PLAYGROUND_CORS_ORIGINS` - "*" or your domain

**Frontend:**
- `VITE_API_URL` - Your backend URL

### Free Tier Optimization

**To stay within AWS free tier:**
1. Use `t3.micro` instance type
2. Use `--single` flag (no load balancer)
3. Use `db.t3.micro` for RDS
4. Keep RDS storage ≤ 20GB
5. Monitor usage in billing dashboard
6. Set up billing alerts

**Cost warning:** Running both backend and frontend 24/7 exceeds free tier by ~690 hours/month.

**Solutions:**
- Deploy only backend to AWS, frontend to Netlify/Vercel (free)
- Stop instances when not in use
- Accept ~$5/month overage for convenience

## Testing Deployment

```bash
# Test backend
curl http://[backend-url].elasticbeanstalk.com/health

# Test frontend
open http://[frontend-url].elasticbeanstalk.com
```

## Monitoring

```bash
# View logs
eb logs
eb logs --stream

# Check status
eb status
eb health

# SSH into instance
eb ssh
```

## Cleanup

```bash
# To avoid charges
eb terminate llmscope-backend-env --force
eb terminate llmscope-frontend-env --force

aws rds delete-db-instance \
  --db-instance-identifier llmscope-db \
  --skip-final-snapshot
```

## Support

- AWS EB Docs: https://docs.aws.amazon.com/elasticbeanstalk/
- AWS Free Tier: https://aws.amazon.com/free/
- Issues: Check [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md) troubleshooting section
