# Deployment Fixes Applied

## Issues Identified from EB Logs

### Issue 1: PostgreSQL Package Not Available
```
Error occurred during build: Yum does not have postgresql15-devel available for installation
```

**Cause:** Amazon Linux 2023 (AL2023) uses `dnf` instead of `yum`, and package names may differ.

**Fix Applied:** Updated `backend/.ebextensions/01_packages.config`
- Changed from `yum` packages to `dnf` command
- Added required dependencies: `postgresql15-devel`, `postgresql15`, `gcc`, `python3-devel`

### Issue 2: Virtual Environment Deployed
```
Error: chown /var/app/staging/venv/bin/python: no such file or directory
```

**Cause:** The local `venv/` directory was being uploaded to EB, which shouldn't happen.

**Fix Applied:** Created `backend/.ebignore`
- Explicitly excludes `venv/`, `env/`, `.venv/` directories
- Excludes other development files (tests, cache, docs)

## Files Modified

1. **backend/.ebextensions/01_packages.config** - Fixed package installation for AL2023
2. **backend/.ebextensions/02_python.config** - Simplified configuration
3. **backend/.ebignore** - Added to exclude unnecessary files
4. **backend/deploy.sh** - Created deployment helper script

## How to Redeploy

### Option 1: Using Deploy Script

```bash
cd backend
./deploy.sh
```

### Option 2: Manual Deployment

```bash
cd backend

# Clean up
rm -rf __pycache__ *.pyc .pytest_cache

# Deploy
eb deploy

# Check status
eb status
eb health
```

## Verification Steps

After deployment completes:

```bash
# 1. Check environment health
eb health

# 2. View recent logs
eb logs

# 3. Test health endpoint
BACKEND_URL=$(eb status | grep CNAME | awk '{print $2}')
curl http://$BACKEND_URL/health

# Expected response:
# {"status":"healthy","database":"connected","sessions":0,"events":0}

# 4. Open in browser
eb open
```

## If Deployment Still Fails

### Check Logs
```bash
# View all logs
eb logs --all

# Stream logs in real-time
eb logs --stream

# SSH and check manually
eb ssh
cd /var/app/current
ls -la
```

### Common Issues

**Database Connection:**
```bash
# SSH into instance
eb ssh

# Test database connection
python3
>>> import psycopg2
>>> conn = psycopg2.connect("postgresql://postgres:PASSWORD@database-1.c30yokmiwe2d.us-east-1.rds.amazonaws.com:5432/postgres")
>>> print("Connected!")
>>> conn.close()
```

**Security Group:**
- Go to RDS Console → database-1 → Security Groups
- Ensure EB security group can access port 5432

**Environment Variables:**
```bash
# Check they're set correctly
eb printenv

# Update if needed
eb setenv DATABASE_URL="postgresql://..."
```

## Current Configuration

**EB Configuration Files:**
- `.ebextensions/01_packages.config` - Installs PostgreSQL dependencies
- `.ebextensions/02_python.config` - Python environment settings
- `.platform/hooks/predeploy/01_migrations.sh` - Runs migrations before deploy
- `Procfile` - Starts uvicorn on port 8000
- `.ebignore` - Excludes files from deployment

**Expected Deployment Flow:**
1. EB receives deployment request
2. Installs system packages (PostgreSQL, gcc)
3. Installs Python dependencies from requirements.txt
4. Runs predeploy hook (database migrations)
5. Starts application via Procfile
6. Health check passes

## Next Steps After Successful Deployment

1. **Get backend URL:**
   ```bash
   eb status | grep CNAME
   ```

2. **Update frontend config:**
   ```bash
   cd ../frontend
   eb setenv VITE_API_URL="http://[backend-url].elasticbeanstalk.com"
   ```

3. **Test API:**
   ```bash
   # Visit API docs
   open http://[backend-url].elasticbeanstalk.com/docs
   ```

4. **Deploy frontend:**
   ```bash
   cd frontend
   eb init -p node.js-18 llmscope-frontend --region us-east-1
   eb create llmscope-frontend-env --instance-type t3.micro --single
   eb deploy
   ```
