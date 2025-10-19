# Backend Access Guide

## Your Backend URL

Get your backend URL:
```bash
cd backend
eb status | grep CNAME
```

Or:
```bash
BACKEND_URL=$(cd backend && eb status | grep CNAME | awk '{print $2}')
echo "http://$BACKEND_URL"
```

## Quick Access Commands

### Open in Browser
```bash
cd backend
eb open                                    # Open homepage
open "http://$(eb status | grep CNAME | awk '{print $2}')/docs"  # Open API docs
```

### Health Check
```bash
curl http://$(cd backend && eb status | grep CNAME | awk '{print $2}')/health
```

### View Logs
```bash
cd backend
eb logs                    # Recent logs
eb logs --stream           # Live logs
eb logs --all              # All logs
```

### Monitor Status
```bash
cd backend
eb status                  # Environment status
eb health                  # Health status
eb health --refresh        # Auto-refreshing health
```

## API Endpoints

### Interactive Documentation
- **Swagger UI**: `http://[your-url]/docs`
- **ReDoc**: `http://[your-url]/redoc`
- **OpenAPI**: `http://[your-url]/openapi.json`

### Health & Monitoring
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/cleanup/stats` | Cleanup statistics |
| POST | `/api/v1/cleanup/run` | Run cleanup job |

### Session Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/sessions/create` | Create new session |
| GET | `/api/v1/sessions/current/info` | Get current session info |
| GET | `/api/v1/sessions/current/metrics` | Get session metrics |
| POST | `/api/v1/sessions/current/reset` | Clear session events |
| DELETE | `/api/v1/sessions/{id}` | Delete session |

## Example Usage

### Setup
```bash
# Get backend URL
BACKEND_URL=$(cd backend && eb status | grep CNAME | awk '{print $2}')
```

### Create Session
```bash
# Create session
curl -X POST http://$BACKEND_URL/api/v1/sessions/create

# Response:
# {"session_id":"550e8400-...","message":"Session created successfully"}
```

### Use Session
```bash
# Save session ID
SESSION_ID="your-session-id-here"

# Get session info
curl -H "X-Session-ID: $SESSION_ID" \
  http://$BACKEND_URL/api/v1/sessions/current/info

# Get metrics
curl -H "X-Session-ID: $SESSION_ID" \
  http://$BACKEND_URL/api/v1/sessions/current/metrics

# Reset session
curl -X POST \
  -H "X-Session-ID: $SESSION_ID" \
  http://$BACKEND_URL/api/v1/sessions/current/reset
```

### Health Check
```bash
curl http://$BACKEND_URL/health

# Expected response:
# {
#   "status": "healthy",
#   "database": "connected",
#   "sessions": 0,
#   "events": 0
# }
```

## Management Commands

### Deploy Updates
```bash
cd backend
eb deploy
```

### View Logs
```bash
cd backend
eb logs                    # Recent logs
eb logs --stream           # Live streaming logs
eb logs --all              # Download all logs
```

### SSH into Instance
```bash
cd backend
eb ssh

# Once inside:
cd /var/app/current        # Application code
source /var/app/venv/*/bin/activate  # Activate Python venv
python check_env.py        # Check environment variables
exit                       # Exit SSH
```

### Environment Variables
```bash
cd backend
eb printenv                # View all env vars
eb setenv KEY=value        # Set env var
```

### Environment Control
```bash
cd backend
eb status                  # View status
eb health                  # View health
eb restart                 # Restart application
eb terminate               # Terminate environment (careful!)
```

## Troubleshooting

### Check Application Status
```bash
cd backend
eb health
```

### View Recent Errors
```bash
cd backend
eb logs | grep ERROR
```

### Test Database Connection
```bash
cd backend
eb ssh

# Inside instance:
python3
>>> import psycopg2
>>> conn = psycopg2.connect("postgresql://postgres:PASSWORD@database-1.c30yokmiwe2d.us-east-1.rds.amazonaws.com:5432/postgres")
>>> print("Connected!")
>>> conn.close()
>>> exit()
```

### Restart Application
```bash
cd backend
eb restart
```

## Cost Monitoring

### Check Current Costs
1. Go to [AWS Billing Dashboard](https://console.aws.amazon.com/billing/)
2. View "Bills" → Current month

### Set Up Billing Alert
1. Go to [AWS Budgets](https://console.aws.amazon.com/billing/home#/budgets)
2. Create budget
3. Set amount: $1, $5, $10
4. Add email notification

## Next Steps

### 1. Deploy Frontend

Now that your backend is working, deploy the frontend:

```bash
cd frontend

# Get backend URL for frontend config
BACKEND_URL=$(cd ../backend && eb status | grep CNAME | awk '{print $2}')

# Initialize EB
eb init -p node.js-18 llmscope-frontend --region us-east-1

# Create environment
eb create llmscope-frontend-env --instance-type t3.micro --single

# Set backend URL
eb setenv VITE_API_URL="http://$BACKEND_URL"

# Deploy
eb deploy

# Open
eb open
```

### 2. Set Up Custom Domain (Optional)

Use Route 53 or your DNS provider to point a domain to your backend:
- `api.yourdomain.com` → Your backend URL

### 3. Enable HTTPS (Production)

For production, set up SSL/TLS using AWS Certificate Manager.

## Resources

- **AWS Console**: https://console.aws.amazon.com/elasticbeanstalk/
- **RDS Console**: https://console.aws.amazon.com/rds/
- **Billing**: https://console.aws.amazon.com/billing/
- **EB Docs**: https://docs.aws.amazon.com/elasticbeanstalk/

## Quick Copy-Paste Commands

```bash
# Get backend URL
cd backend && eb status | grep CNAME

# Test health
curl $(cd backend && eb status | grep CNAME | awk '{print "http://" $2}')/health

# Open API docs
open "$(cd backend && eb status | grep CNAME | awk '{print "http://" $2}')/docs"

# View logs
cd backend && eb logs --stream

# SSH
cd backend && eb ssh
```
