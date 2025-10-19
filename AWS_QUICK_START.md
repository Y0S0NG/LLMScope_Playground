# AWS Deployment Quick Reference

## Prerequisites Checklist

```bash
# Install tools
brew install awscli awsebcli  # macOS
# OR
pip install awsebcli --upgrade --user  # Linux/Windows

# Verify
aws --version
eb --version

# Configure AWS
aws configure
```

## 5-Minute Deployment

### 1. Create RDS Database (5 min)

**Via Console:**
1. Go to: https://console.aws.amazon.com/rds/
2. Click "Create database"
3. Choose:
   - Engine: PostgreSQL 15.x
   - Template: **Free tier**
   - Instance: `db.t3.micro`
   - Storage: 20 GB
   - Public access: Yes
4. Save endpoint URL

**Connection string:**
```
postgresql://postgres:[PASSWORD]@[ENDPOINT]:5432/postgres
```

### 2. Deploy Backend (5 min)

```bash
cd backend

# Initialize
eb init -p python-3.11 llmscope-backend --region us-east-1

# Create and deploy
eb create llmscope-backend-env \
  --instance-type t3.micro \
  --single \
  --envvars DATABASE_URL="postgresql://...",ANTHROPIC_API_KEY="sk-ant-...",SECRET_KEY="$(openssl rand -hex 32)"

# Verify
eb open
curl $(eb status | grep CNAME | awk '{print $2}')/health
```

### 3. Deploy Frontend (5 min)

```bash
cd ../frontend

# Initialize
eb init -p node.js-18 llmscope-frontend --region us-east-1

# Create and deploy
eb create llmscope-frontend-env \
  --instance-type t3.micro \
  --single

# Get backend URL and configure
BACKEND_URL=$(cd ../backend && eb status | grep CNAME | awk '{print $2}')
eb setenv VITE_API_URL="http://$BACKEND_URL"
eb deploy

# Open
eb open
```

## Essential Commands

```bash
# Deploy updates
eb deploy

# View logs
eb logs
eb logs --stream

# Environment status
eb status
eb health

# SSH into instance
eb ssh

# Set environment variable
eb setenv KEY=value

# Terminate (cleanup)
eb terminate env-name
```

## Free Tier Limits

✅ **What's Free (12 months):**
- 750 hrs/month EC2 (t3.micro)
- 750 hrs/month RDS (db.t3.micro)
- 20 GB RDS storage

⚠️ **WARNING:** 2 instances = 1,440 hrs/month (exceeds by 690 hrs)

**Solutions:**
1. Deploy backend only (750 hrs) + frontend on Netlify/Vercel (free)
2. Stop instances when not in use
3. Accept ~$5/month overage

## Troubleshooting

**Database connection failed:**
```bash
eb ssh
python3 -c "import psycopg2; psycopg2.connect('postgresql://...')"
```

**Migrations not running:**
```bash
eb ssh
cd /var/app/current
source /var/app/venv/*/bin/activate
alembic upgrade head
```

**502 Error:**
```bash
eb logs --all  # Check logs
eb ssh
curl localhost:8000/health  # Test locally
```

## Cost Monitoring

```bash
# Set up billing alert
# Go to: https://console.aws.amazon.com/billing/
# Create budget: $1 with 80% alert
```

## Cleanup (Avoid Charges)

```bash
# Terminate environments
cd backend && eb terminate llmscope-backend-env --force
cd ../frontend && eb terminate llmscope-frontend-env --force

# Delete RDS
aws rds delete-db-instance \
  --db-instance-identifier llmscope-db \
  --skip-final-snapshot
```

## Full Documentation

- Complete guide: [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)
- All platforms: [DEPLOYMENT.md](DEPLOYMENT.md)
- Project README: [README.md](README.md)

## Quick Links

- [AWS Console](https://console.aws.amazon.com/)
- [RDS Console](https://console.aws.amazon.com/rds/)
- [EB Console](https://console.aws.amazon.com/elasticbeanstalk/)
- [Billing Dashboard](https://console.aws.amazon.com/billing/)
- [Anthropic Console](https://console.anthropic.com/)
