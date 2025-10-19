# AWS Elastic Beanstalk Deployment Guide

Complete guide to deploying LLMScope Playground on AWS using the Free Tier.

## Overview

This deployment uses:
- **AWS Elastic Beanstalk**: Managed application platform (Backend + Frontend)
- **AWS RDS PostgreSQL**: Managed database (Free tier eligible)
- **AWS Free Tier**: 12 months free (750 hours EC2 + 20GB RDS storage)

**Estimated Monthly Cost:**
- **First 12 months**: FREE (within free tier limits)
- **After free tier**: ~$30-40/month

## Prerequisites

- [ ] AWS Account (sign up at [aws.amazon.com](https://aws.amazon.com))
- [ ] AWS CLI installed
- [ ] EB CLI installed
- [ ] Anthropic API key from [console.anthropic.com](https://console.anthropic.com)
- [ ] Git repository with your code

## Step-by-Step Deployment

### 1. Install Required Tools

#### Install AWS CLI

**macOS:**
```bash
brew install awscli
```

**Linux:**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

**Windows:**
Download from: https://aws.amazon.com/cli/

**Verify:**
```bash
aws --version
# Should show: aws-cli/2.x.x
```

#### Install Elastic Beanstalk CLI

**macOS:**
```bash
brew install awsebcli
```

**Linux/Windows (via pip):**
```bash
pip install awsebcli --upgrade --user
```

**Verify:**
```bash
eb --version
# Should show: EB CLI 3.x.x
```

### 2. Configure AWS Credentials

```bash
aws configure
```

You'll be prompted for:
1. **AWS Access Key ID**: Get from AWS Console → IAM → Users → Security Credentials
2. **AWS Secret Access Key**: Shown when creating access key
3. **Default region**: `us-east-1` (or your preferred region)
4. **Default output format**: `json`

**Create IAM User (if needed):**
1. Go to AWS Console → IAM → Users
2. Click "Add users"
3. Username: `eb-deployer`
4. Access type: Programmatic access
5. Attach policies:
   - `AWSElasticBeanstalkFullAccess`
   - `AmazonRDSFullAccess`
   - `IAMFullAccess`
6. Save the Access Key ID and Secret Access Key

### 3. Create RDS PostgreSQL Database

#### Option A: Via AWS Console (Recommended for first-time users)

1. Go to [AWS RDS Console](https://console.aws.amazon.com/rds/)
2. Click **"Create database"**
3. Configure:

**Engine options:**
- Engine type: `PostgreSQL`
- Version: `PostgreSQL 15.x` (latest)

**Templates:**
- Select: `Free tier` ✅

**Settings:**
- DB instance identifier: `llmscope-db`
- Master username: `postgres`
- Master password: Create a strong password (save this!)
- Confirm password

**DB instance class:**
- `db.t3.micro` (2 vCPUs, 1 GiB RAM) - Free tier eligible ✅

**Storage:**
- Storage type: `General Purpose SSD (gp2)`
- Allocated storage: `20 GB` (free tier max) ✅
- Disable storage autoscaling (to stay in free tier)

**Connectivity:**
- Public access: `Yes` (required for EB to connect)
- VPC security group: `Create new`
- New VPC security group name: `llmscope-db-sg`

**Additional configuration:**
- Initial database name: `postgres`
- Backup retention: `1 day` (minimum for free tier)

4. Click **"Create database"**
5. Wait 5-10 minutes for database to become available
6. Once available, click on the database name
7. Copy the **Endpoint** (e.g., `llmscope-db.c9akkkahx3vw.us-east-1.rds.amazonaws.com`)

#### Option B: Via AWS CLI

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier llmscope-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.3 \
  --master-username postgres \
  --master-user-password YOUR_SECURE_PASSWORD \
  --allocated-storage 20 \
  --publicly-accessible \
  --no-multi-az \
  --backup-retention-period 1

# Wait for database to be available
aws rds wait db-instance-available --db-instance-identifier llmscope-db

# Get database endpoint
aws rds describe-db-instances \
  --db-instance-identifier llmscope-db \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text
```

**Save your database connection string:**
```
postgresql://postgres:[YOUR_PASSWORD]@[ENDPOINT]:5432/postgres
```

Example:
```
postgresql://postgres:MySecurePass123@llmscope-db.c9akkkahx3vw.us-east-1.rds.amazonaws.com:5432/postgres
```

### 4. Deploy Backend API

```bash
# Navigate to backend directory
cd backend

# Initialize Elastic Beanstalk application
eb init -p python-3.11 llmscope-backend --region us-east-1

# When prompted:
# - Application name: llmscope-backend (or press enter)
# - Set up SSH: Yes (recommended for debugging)
# - Select keypair or create new one

# Create environment with free tier settings
eb create llmscope-backend-env \
  --instance-type t3.micro \
  --single \
  --envvars \
    DATABASE_URL="postgresql://postgres:[PASSWORD]@[ENDPOINT]:5432/postgres",\
    ANTHROPIC_API_KEY="sk-ant-your-key-here",\
    SECRET_KEY="$(openssl rand -hex 32)",\
    PORT=8000,\
    HOST=0.0.0.0,\
    PLAYGROUND_CORS_ORIGINS="*"

# This will take 5-10 minutes
# You'll see output like:
# Creating application version archive "app-231018_154230".
# Uploading llmscope-backend/app-231018_154230.zip to S3...
# Environment details for: llmscope-backend-env
# ...
```

**Alternative: Set environment variables after creation**

If you prefer to set environment variables separately:

```bash
# Create environment without env vars
eb create llmscope-backend-env \
  --instance-type t3.micro \
  --single

# Set environment variables
eb setenv \
  DATABASE_URL="postgresql://postgres:[PASSWORD]@[ENDPOINT]:5432/postgres" \
  ANTHROPIC_API_KEY="sk-ant-your-key-here" \
  SECRET_KEY="$(openssl rand -hex 32)" \
  PORT=8000 \
  HOST=0.0.0.0 \
  PLAYGROUND_CORS_ORIGINS="*"

# Deploy
eb deploy
```

**Verify deployment:**

```bash
# Check environment status
eb status

# Get the backend URL
eb status | grep CNAME

# Test health endpoint
BACKEND_URL=$(eb status | grep CNAME | awk '{print $2}')
curl http://$BACKEND_URL/health

# Should return:
# {"status":"healthy","database":"connected","sessions":0,"events":0}

# Open in browser
eb open
```

### 5. Deploy Frontend

```bash
# Navigate to frontend directory
cd ../frontend

# Initialize Elastic Beanstalk application
eb init -p node.js-18 llmscope-frontend --region us-east-1

# Create environment
eb create llmscope-frontend-env \
  --instance-type t3.micro \
  --single

# Get backend URL for frontend configuration
cd ../backend
BACKEND_URL=$(eb status | grep CNAME | awk '{print $2}')
echo "Backend URL: http://$BACKEND_URL"

# Set frontend environment variable
cd ../frontend
eb setenv VITE_API_URL="http://$BACKEND_URL"

# Deploy frontend
eb deploy

# Open frontend in browser
eb open
```

**Update frontend to use backend API (if needed):**

If your frontend has API configuration, update it:

```bash
# Check if you have a config file
ls src/config.ts src/config/api.ts .env.production

# Create .env.production if needed
cat > .env.production << EOF
VITE_API_URL=http://[your-backend-url].elasticbeanstalk.com
EOF

# Rebuild and redeploy
npm run build
eb deploy
```

### 6. Configure Security Groups

**Secure your RDS database to only accept connections from your EB instances:**

1. Go to [RDS Console](https://console.aws.amazon.com/rds/)
2. Click on your database: `llmscope-db`
3. Click on the **VPC security group** link (e.g., `llmscope-db-sg`)
4. Click **"Edit inbound rules"**
5. Find the rule allowing `0.0.0.0/0` on port 5432
6. Click **"Delete"** to remove public access
7. Click **"Add rule"**:
   - Type: `PostgreSQL`
   - Port: `5432`
   - Source: Custom → Search for and select your EB environment security group
     - Usually named: `sg-xxxxx (elasticbeanstalk-...)`
8. Click **"Save rules"**

**To find your EB security group:**

```bash
cd backend
eb ssh llmscope-backend-env -c "curl -s http://169.254.169.254/latest/meta-data/security-groups"
```

Or via AWS Console:
- EC2 → Instances → Find your EB instance → Security tab → Security groups

### 7. Set Up HTTPS (Optional but Recommended)

#### Enable HTTPS with AWS Certificate Manager (Free)

1. Go to [AWS Certificate Manager](https://console.aws.amazon.com/acm/)
2. Click **"Request certificate"**
3. Select **"Request a public certificate"**
4. Add domain names:
   - `api.yourdomain.com`
   - `app.yourdomain.com`
5. Validation method: **DNS validation**
6. Follow instructions to add CNAME records to your DNS
7. Wait for certificate to be validated

#### Configure Load Balancer (requires upgrading from single instance)

**Note:** This will increase costs beyond free tier.

```bash
# Add HTTPS listener to backend
cd backend
eb config

# In the editor, find:
#   aws:elbv2:listener:443:
#     Protocol: HTTPS
#     SSLCertificateArns: arn:aws:acm:us-east-1:xxxx:certificate/xxxx
```

For free tier, use HTTP and rely on application-level security.

### 8. Testing Your Deployment

#### Test Backend API

```bash
# Health check
curl http://[backend-url].elasticbeanstalk.com/health

# API docs
open http://[backend-url].elasticbeanstalk.com/docs

# Create session
curl -X POST http://[backend-url].elasticbeanstalk.com/api/v1/sessions/create

# Should return:
# {"session_id":"550e8400-...","message":"Session created successfully"}
```

#### Test Frontend

```bash
open http://[frontend-url].elasticbeanstalk.com
```

### 9. Monitoring and Maintenance

#### View Logs

```bash
# Backend logs
cd backend
eb logs

# Real-time logs
eb logs --stream

# Download all logs
eb logs --all
```

#### Monitor Environment Health

```bash
# Check status
eb status

# Check health
eb health

# View in AWS Console
eb console
```

#### SSH into Instance

```bash
# SSH into backend
cd backend
eb ssh

# Once connected:
cd /var/app/current
source /var/app/venv/*/bin/activate
python -c "import app; print(app.__file__)"

# Check logs
tail -f /var/log/eb-engine.log
tail -f /var/log/web.stdout.log
```

#### Update Application

```bash
# After making code changes:

# Backend
cd backend
git pull  # or make changes
eb deploy

# Frontend
cd frontend
git pull  # or make changes
npm run build
eb deploy
```

## Cost Management

### Free Tier Limits (12 months)

- ✅ 750 hours/month EC2 (t2.micro or t3.micro)
- ✅ 750 hours/month RDS (db.t3.micro)
- ✅ 20 GB RDS storage
- ✅ 5 GB S3 storage
- ✅ 20,000 RDS read/write requests

**With 2 instances (backend + frontend):**
- Each runs 24/7 = 720 hours/month
- Total: 1,440 hours/month
- **⚠️ This exceeds free tier by 690 hours!**

**To stay within free tier:**

**Option 1: Deploy backend only, frontend on Netlify/Vercel (free)**
```bash
# Only deploy backend to AWS
# Deploy frontend to Netlify (free tier)
```

**Option 2: Combine backend + frontend in one instance**
- More complex setup
- Serve React build from FastAPI

**Option 3: Use on-demand (start/stop instances)**
```bash
# Stop environments when not in use
eb terminate llmscope-frontend-env
eb terminate llmscope-backend-env

# Recreate when needed (within 750 hours/month)
```

### Set Up Billing Alerts

1. Go to [AWS Billing Console](https://console.aws.amazon.com/billing/)
2. Click **"Budgets"** → **"Create budget"**
3. Select **"Cost budget"**
4. Set budget amount: $1 (to catch unexpected charges)
5. Set alert threshold: 80% ($0.80)
6. Add email notification
7. Create budget

### Monitor Costs

```bash
# Check current month costs
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost

# Or use AWS Cost Explorer in console
```

## Troubleshooting

### Common Issues

#### 1. "Database connection failed"

```bash
# Test database connectivity
eb ssh
python3
>>> import psycopg2
>>> conn = psycopg2.connect("postgresql://postgres:[pass]@[endpoint]:5432/postgres")
>>> conn.close()
>>> exit()

# Common fixes:
# - Check DATABASE_URL is correct
# - Verify RDS security group allows EB instance
# - Ensure RDS is in same VPC as EB
```

#### 2. "Migrations not running"

```bash
# SSH and run migrations manually
eb ssh
cd /var/app/current
source /var/app/venv/*/bin/activate
alembic upgrade head
```

#### 3. "502 Bad Gateway"

```bash
# Check application logs
eb logs --all

# Common causes:
# - App not binding to correct port (should be 8000)
# - App crashing on startup
# - Dependencies not installed

# Check if app is running
eb ssh
curl localhost:8000/health
```

#### 4. "Environment creation failed"

```bash
# Check events
eb events --follow

# Common issues:
# - Invalid instance type (use t3.micro for free tier)
# - Insufficient permissions (check IAM policies)
# - Region not supported
```

#### 5. "Out of memory"

```bash
# t3.micro has only 1GB RAM
# Check memory usage
eb ssh
free -h
top

# Solutions:
# - Reduce number of uvicorn workers
# - Upgrade to larger instance (costs more)
```

### Get Help

```bash
# View EB CLI help
eb --help

# View specific command help
eb create --help

# View environment events
eb events

# View health status
eb health --refresh
```

## Clean Up (Avoid Charges)

When you're done testing or want to remove everything:

```bash
# Terminate environments
cd backend
eb terminate llmscope-backend-env --force

cd ../frontend
eb terminate llmscope-frontend-env --force

# Delete RDS database
aws rds delete-db-instance \
  --db-instance-identifier llmscope-db \
  --skip-final-snapshot

# Delete EB applications
eb terminate --all

# Verify cleanup
aws elasticbeanstalk describe-environments
aws rds describe-db-instances
```

## Production Checklist

Before going to production:

- [ ] Use HTTPS (set up ACM certificate)
- [ ] Configure custom domain
- [ ] Restrict CORS origins (not `*`)
- [ ] Set up database backups
- [ ] Enable RDS encryption at rest
- [ ] Use secrets manager for sensitive data
- [ ] Set up CloudWatch alarms
- [ ] Configure auto-scaling (if needed)
- [ ] Enable AWS WAF for DDoS protection
- [ ] Set up CI/CD pipeline
- [ ] Configure log aggregation
- [ ] Enable database connection pooling
- [ ] Set up health check monitoring
- [ ] Configure rate limiting
- [ ] Enable database multi-AZ (costs extra)

## Next Steps

1. **Set up custom domain**: Use Route 53 or your DNS provider
2. **Configure CI/CD**: Use GitHub Actions or AWS CodePipeline
3. **Add monitoring**: CloudWatch, Sentry, or DataDog
4. **Performance optimization**: CloudFront CDN, database indexing
5. **Security hardening**: IAM roles, VPC configuration, WAF

## Resources

- [AWS Elastic Beanstalk Documentation](https://docs.aws.amazon.com/elasticbeanstalk/)
- [AWS Free Tier Details](https://aws.amazon.com/free/)
- [EB CLI Command Reference](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html)
- [RDS PostgreSQL Documentation](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)
