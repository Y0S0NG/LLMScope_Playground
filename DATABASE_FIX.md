# Database Connection Fix

## Problem
The migration script is trying to connect to `localhost` instead of your RDS database:
```
connection to server at "localhost" (127.0.0.1), port 5432 failed
```

## Root Cause
The `DATABASE_URL` environment variable is not set in Elastic Beanstalk.

## Solution

### Step 1: Verify Current Environment Variables

```bash
cd backend
eb printenv
```

**Expected output should include:**
```
DATABASE_URL = postgresql://postgres:...
ANTHROPIC_API_KEY = sk-ant-...
SECRET_KEY = ...
```

If `DATABASE_URL` is **missing or incorrect**, continue to Step 2.

### Step 2: Set DATABASE_URL

Replace `YOUR_PASSWORD` with your actual RDS master password:

```bash
eb setenv DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@database-1.c30yokmiwe2d.us-east-1.rds.amazonaws.com:5432/postgres"
```

**Example (with fake password):**
```bash
eb setenv DATABASE_URL="postgresql://postgres:MySecurePass123@database-1.c30yokmiwe2d.us-east-1.rds.amazonaws.com:5432/postgres"
```

### Step 3: Set All Required Environment Variables

Set all variables at once:

```bash
eb setenv \
  DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@database-1.c30yokmiwe2d.us-east-1.rds.amazonaws.com:5432/postgres" \
  ANTHROPIC_API_KEY="your-anthropic-api-key-here" \
  SECRET_KEY="$(openssl rand -hex 32)" \
  PORT=8000 \
  HOST=0.0.0.0
```

**Note:** Replace:
- `YOUR_PASSWORD` - Your RDS master password
- `your-anthropic-api-key-here` - Your Anthropic API key

### Step 4: Verify Environment Variables

```bash
eb printenv
```

Make sure all variables are now set correctly.

### Step 5: Redeploy

```bash
eb deploy
```

This will trigger a new deployment with the correct environment variables.

### Step 6: Monitor Deployment

```bash
# Watch deployment progress
eb health --refresh

# Or stream logs
eb logs --stream
```

### Step 7: Test Connection (After Deployment)

Once deployment succeeds:

```bash
# Get your backend URL
BACKEND_URL=$(eb status | grep CNAME | awk '{print $2}')

# Test health endpoint
curl http://$BACKEND_URL/health

# Expected response:
# {"status":"healthy","database":"connected","sessions":0,"events":0}
```

## Alternative: Verify RDS Security Group

If the environment variable is set correctly but still fails, check RDS security group:

### 1. Get EB Security Group ID

```bash
eb ssh
# Once connected, run:
curl -s http://169.254.169.254/latest/meta-data/security-groups
# Copy the security group name (e.g., sg-xxxxx)
exit
```

### 2. Update RDS Security Group

1. Go to [RDS Console](https://console.aws.amazon.com/rds/)
2. Click on `database-1`
3. Click on the **VPC security group** link
4. Click **"Edit inbound rules"**
5. Add rule:
   - Type: `PostgreSQL`
   - Port: `5432`
   - Source: Custom → Select your EB security group
6. Click **"Save rules"**

### 3. Test Database Connection from EB Instance

```bash
eb ssh

# Test database connectivity
python3
>>> import psycopg2
>>> conn = psycopg2.connect("postgresql://postgres:YOUR_PASSWORD@database-1.c30yokmiwe2d.us-east-1.rds.amazonaws.com:5432/postgres")
>>> print("✅ Connected successfully!")
>>> conn.close()
>>> exit()

exit  # Exit SSH
```

## Quick Reference

### Check Environment Variables
```bash
eb printenv
```

### Set Single Variable
```bash
eb setenv KEY="value"
```

### View Logs
```bash
eb logs
eb logs --all
eb logs --stream
```

### Check Health
```bash
eb health
eb status
```

### SSH into Instance
```bash
eb ssh
```

### Redeploy
```bash
eb deploy
```

## Expected Successful Output

After `eb deploy` completes successfully, you should see:

```bash
$ eb health
Llmscope-backend-env                        Ok                 2024-10-18 23:55:00
  WebServer                                 Ruby 2 running    Ok
    i-0850fbfbd676924bb                     Ok

$ curl http://[your-url].elasticbeanstalk.com/health
{"status":"healthy","database":"connected","sessions":0,"events":0}
```

## Troubleshooting

### Issue: "Environment variable not taking effect"

**Solution:** Some changes require redeployment:
```bash
eb deploy --staged  # Use staged configuration
```

### Issue: "Migration still failing"

**Check migration hook:**
```bash
eb ssh
cd /var/app/current
cat .platform/hooks/predeploy/01_migrations.sh
```

**Run migration manually:**
```bash
eb ssh
cd /var/app/current
source /var/app/venv/*/bin/activate
export DATABASE_URL="postgresql://postgres:PASSWORD@database-1.c30yokmiwe2d.us-east-1.rds.amazonaws.com:5432/postgres"
alembic upgrade head
```

### Issue: "Cannot connect to RDS from EB"

**Security group issue** - See "Verify RDS Security Group" section above.

## Complete Command Sequence

Here's the complete fix in one go:

```bash
# Navigate to backend
cd backend

# Set environment variables (replace YOUR_PASSWORD and your-api-key)
eb setenv \
  DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@database-1.c30yokmiwe2d.us-east-1.rds.amazonaws.com:5432/postgres" \
  ANTHROPIC_API_KEY="your-api-key" \
  SECRET_KEY="$(openssl rand -hex 32)" \
  PORT=8000 \
  HOST=0.0.0.0

# Verify they're set
eb printenv | grep DATABASE_URL

# Deploy
eb deploy

# Monitor health
eb health --refresh

# Test endpoint
curl $(eb status | grep CNAME | awk '{print "http://" $2}')/health
```

## Next Steps After Success

Once your backend is healthy:

1. ✅ Backend URL: `http://[url].elasticbeanstalk.com`
2. 📚 API Docs: `http://[url].elasticbeanstalk.com/docs`
3. 🎨 Deploy frontend next
4. 🔒 Configure security groups properly
5. 🌐 Set up custom domain (optional)
