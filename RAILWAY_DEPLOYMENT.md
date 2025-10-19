# Railway Deployment Guide

Complete guide to deploying your LLMScope Playground backend to Railway with free HTTPS.

## Why Railway?

- ✅ **Free HTTPS** included automatically
- ✅ **Free PostgreSQL** database (500 MB)
- ✅ **$5/month free credit** (enough for demo projects)
- ✅ **Auto-deploy** from GitHub
- ✅ **Environment variables** managed easily
- ✅ **Zero configuration** needed

---

## Step 1: Sign Up for Railway

1. Go to [railway.app](https://railway.app)
2. Click **Start a New Project** or **Login with GitHub**
3. Authorize Railway to access your repositories

---

## Step 2: Push Your Code to GitHub

If you haven't already pushed your code to GitHub:

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Prepare for Railway deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/LLMScope_Playground.git
git branch -M main
git push -u origin main
```

---

## Step 3: Create New Project on Railway

### Option A: Deploy from GitHub (Recommended)

1. **In Railway Dashboard**:
   - Click **New Project**
   - Select **Deploy from GitHub repo**
   - Choose your repository: `LLMScope_Playground`
   - Railway will detect your backend automatically

2. **Configure Root Directory**:
   - Railway will scan for `Procfile` and `requirements.txt`
   - If needed, set **Root Directory** to `backend/` in service settings

### Option B: Deploy via Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
cd backend
railway init

# Deploy
railway up
```

---

## Step 4: Add PostgreSQL Database

1. **In your Railway Project**:
   - Click **New** → **Database** → **Add PostgreSQL**
   - Railway will provision a free PostgreSQL instance

2. **Database is Auto-Configured**:
   - Railway automatically creates a `DATABASE_URL` environment variable
   - Your backend will use it automatically via `config.py`

---

## Step 5: Configure Environment Variables

1. **In Railway Dashboard**:
   - Click on your **backend service**
   - Go to **Variables** tab
   - Add the following variables:

```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key_here
SECRET_KEY=your_secret_key_here

# Optional (Railway auto-provides DATABASE_URL)
CORS_ORIGINS=*

# Redis (optional - add Redis service if needed)
# REDIS_URL=redis://...
```

**Note**: Railway automatically provides:
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - The port your app should listen on
- Other Railway-specific variables

### Get Your Current Environment Variables from AWS:

```bash
# From your local machine
eb printenv
```

Copy the values for:
- `ANTHROPIC_API_KEY`
- `SECRET_KEY`
- Any other custom variables you set

---

## Step 6: Deploy and Run Migrations

Railway will automatically:
1. Install dependencies from `requirements.txt`
2. Run the start command from `railway.json`:
   - `alembic upgrade head` (runs migrations)
   - `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Monitor deployment in the **Deployments** tab.

---

## Step 7: Get Your HTTPS URL

1. **In Railway Dashboard**:
   - Click on your backend service
   - Go to **Settings** tab
   - Scroll to **Networking** section
   - Click **Generate Domain**
   - Railway will generate a URL like: `https://your-app-name.up.railway.app`

2. **Copy the URL** - This is your new HTTPS backend URL!

---

## Step 8: Test Your Railway Backend

```bash
# Health check
curl https://your-app-name.up.railway.app/health

# Expected response:
# {"status":"healthy","timestamp":"2025-10-19T..."}

# API docs (automatically available)
# Open in browser: https://your-app-name.up.railway.app/docs
```

---

## Step 9: Update Frontend Configuration

```bash
cd frontend

# Update .env.production with Railway URL
echo "VITE_API_URL=https://your-app-name.up.railway.app" > .env.production

# Deploy to Vercel
vercel --prod
```

---

## Step 10: Test End-to-End

1. Open your Vercel frontend: `https://llmscopeplaygroundfrontend-ioq2f5eqf-yosongyxp-7364s-projects.vercel.app`
2. Send a chat message
3. Verify it works (no CORS errors, no mixed content errors)

---

## Railway Dashboard Overview

### Useful Tabs:

1. **Deployments**:
   - View deployment logs
   - See build status
   - Rollback if needed

2. **Variables**:
   - Manage environment variables
   - View auto-generated variables

3. **Metrics**:
   - Monitor CPU, memory, network usage
   - Track free credit usage

4. **Settings**:
   - Generate custom domain
   - Configure health checks
   - Set restart policies

---

## Troubleshooting

### Build Fails: "No Procfile Found"

**Solution**: Ensure `backend/Procfile` exists and is in the root directory you specified.

### Database Connection Error

**Solution**:
- Verify `DATABASE_URL` is set in Variables tab
- Railway auto-generates this when you add PostgreSQL
- Format: `postgresql://user:password@host:port/database`

### Port Binding Error

**Solution**: Ensure your `Procfile` uses `$PORT`:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Migrations Not Running

**Solution**: Check `railway.json` has the correct start command:
```json
{
  "deploy": {
    "startCommand": "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
  }
}
```

### CORS Errors

**Solution**: Add your Vercel frontend URL to `CORS_ORIGINS`:
```bash
CORS_ORIGINS=https://llmscopeplaygroundfrontend-ioq2f5eqf-yosongyxp-7364s-projects.vercel.app,https://your-other-frontend.vercel.app
```

Or use wildcard for testing:
```bash
CORS_ORIGINS=*
```

---

## Cost Breakdown

### Railway Free Tier:

- **Credit**: $5/month (renews monthly)
- **PostgreSQL**: Free (500 MB storage, 1 GB RAM)
- **Execution time**: ~500 hours/month (enough for demo)
- **Bandwidth**: 100 GB/month

### Usage Estimates:
- **Demo project**: ~$2-3/month (well within free tier)
- **Light production**: ~$5-10/month
- **Medium traffic**: ~$20-30/month

**For your demo project**: Should stay **100% FREE** within the $5 monthly credit.

---

## Comparison: Railway vs AWS EB

| Feature | Railway | AWS EB (Single Instance) |
|---------|---------|--------------------------|
| **HTTPS** | ✅ Free & Auto | ❌ Requires Load Balancer ($15/mo) |
| **Database** | ✅ Free PostgreSQL | AWS RDS (free tier 12 months) |
| **Setup Time** | 5 minutes | 30-60 minutes |
| **Cost (after free tier)** | ~$5-10/month | ~$30-50/month |
| **Auto-deploy** | ✅ GitHub integration | Manual via EB CLI |
| **Logs** | ✅ Real-time dashboard | CloudWatch (complex) |
| **Best for** | Demos, MVPs, small apps | Enterprise, complex infra |

---

## Next Steps After Railway Deployment

1. ✅ **Test thoroughly** - Send multiple chat requests
2. ✅ **Monitor usage** - Check Railway dashboard for credit usage
3. ✅ **Custom domain** (optional) - Point your own domain to Railway
4. ❌ **Terminate AWS EB** - Save costs (see cleanup section below)

---

## Cleaning Up AWS Resources (Optional)

Once Railway is working, you can terminate AWS resources to avoid charges:

```bash
# Terminate Elastic Beanstalk environment
eb terminate llmscope-backend-env

# Delete RDS database (via AWS Console)
# 1. Go to RDS Console
# 2. Select database-1
# 3. Actions → Delete
# 4. Uncheck "Create final snapshot" (for demo)
# 5. Type "delete me" to confirm
```

**Warning**: This will delete all data. Export any important data first!

---

## Advanced: Custom Domain on Railway

If you have a domain (e.g., `api.llmscope.com`):

1. **In Railway Settings** → **Networking**:
   - Add custom domain: `api.llmscope.com`
   - Railway provides DNS instructions

2. **In your DNS provider**:
   - Add CNAME record:
     - Name: `api`
     - Value: `your-app-name.up.railway.app`

3. **Update frontend**:
   ```bash
   echo "VITE_API_URL=https://api.llmscope.com" > frontend/.env.production
   vercel --prod
   ```

---

## Quick Reference Commands

```bash
# Deploy backend to Railway
cd backend
railway up

# View logs
railway logs

# Open dashboard
railway open

# Add environment variable
railway variables set ANTHROPIC_API_KEY=sk-ant-...

# Check service status
railway status

# Update frontend with Railway URL
cd ../frontend
echo "VITE_API_URL=https://your-app.up.railway.app" > .env.production
vercel --prod
```

---

## Support

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **Railway Status**: https://status.railway.app

---

## Summary

Railway provides the easiest path to a production-ready demo with HTTPS:

1. ✅ Push code to GitHub
2. ✅ Connect Railway to repo
3. ✅ Add PostgreSQL database
4. ✅ Set environment variables
5. ✅ Generate domain → Get free HTTPS
6. ✅ Update frontend with Railway URL
7. ✅ Deploy and test

**Total time**: ~15 minutes
**Cost**: $0 (within free tier)

Good luck with your deployment! 🚀
