# AWS Elastic Beanstalk HTTPS Setup Guide

This guide walks you through enabling HTTPS on your backend using AWS Certificate Manager (ACM) and Application Load Balancer (ALB).

## Overview

- **Current Backend**: `http://llmscope-backend-env.eba-bxmhbs4y.us-east-1.elasticbeanstalk.com`
- **Target**: `https://llmscope-backend-env.eba-bxmhbs4y.us-east-1.elasticbeanstalk.com`
- **Cost**: ~$15-18/month for Application Load Balancer (not free tier eligible)
- **Benefits**: Native HTTPS, no third-party proxies, production-ready

## Prerequisites

- AWS account with Elastic Beanstalk environment running
- Domain name (optional, but recommended for production)
- AWS CLI configured (or use AWS Console)

---

## Option A: Using Elastic Beanstalk Default Domain (Easiest)

This option uses AWS-managed certificates for the `.elasticbeanstalk.com` domain.

### Step 1: Enable Load Balancer in EB Environment

1. **Via AWS Console:**
   - Go to [Elastic Beanstalk Console](https://console.aws.amazon.com/elasticbeanstalk)
   - Select your environment: `llmscope-backend-env`
   - Click **Configuration** in the left sidebar
   - Find **Load balancer** section and click **Edit**
   - Change **Load balancer type** from "Classic" to **"Application Load Balancer"**
   - Click **Apply**

2. **Via EB CLI:**
   ```bash
   cd backend
   eb config
   ```
   Find the section `aws:elasticbeanstalk:environment:` and change:
   ```yaml
   LoadBalancerType: application
   ```

### Step 2: Request SSL Certificate from ACM

1. **Via AWS Console:**
   - Go to [AWS Certificate Manager](https://console.aws.amazon.com/acm)
   - Ensure you're in **us-east-1** region (same as your EB environment)
   - Click **Request a certificate**
   - Choose **Request a public certificate**
   - Enter domain name: `llmscope-backend-env.eba-bxmhbs4y.us-east-1.elasticbeanstalk.com`
   - Choose validation method: **DNS validation** (recommended)
   - Click **Request**
   - Follow DNS validation steps (AWS will provide CNAME records to add)

2. **Via AWS CLI:**
   ```bash
   aws acm request-certificate \
     --domain-name llmscope-backend-env.eba-bxmhbs4y.us-east-1.elasticbeanstalk.com \
     --validation-method DNS \
     --region us-east-1
   ```

   Note the Certificate ARN from the output.

### Step 3: Configure HTTPS Listener in Load Balancer

1. **Via AWS Console:**
   - Go back to EB Console > Configuration > Load balancer > Edit
   - Scroll to **Listeners** section
   - Click **Add listener**
   - Configure:
     - **Port**: 443
     - **Protocol**: HTTPS
     - **SSL certificate**: Select the certificate you created
     - **Processes**: default
   - Optionally, keep port 80 (HTTP) listener for redirects
   - Click **Apply**

2. **Via EB CLI configuration:**
   Create/update `backend/.ebextensions/03_https.config`:
   ```yaml
   option_settings:
     aws:elbv2:listener:443:
       ListenerEnabled: true
       Protocol: HTTPS
       SSLCertificateArns: arn:aws:acm:us-east-1:YOUR_ACCOUNT_ID:certificate/CERT_ID
   ```

### Step 4: Configure HTTP to HTTPS Redirect (Optional)

Create `backend/.ebextensions/04_https_redirect.config`:

```yaml
files:
  "/etc/nginx/conf.d/https_redirect.conf":
    mode: "000644"
    owner: root
    group: root
    content: |
      # Redirect HTTP to HTTPS
      if ($http_x_forwarded_proto = 'http') {
        return 301 https://$host$request_uri;
      }

container_commands:
  01_reload_nginx:
    command: "sudo systemctl reload nginx"
```

---

## Option B: Using Custom Domain (Production Recommended)

If you own a domain (e.g., `api.yourdomain.com`), this provides better branding and flexibility.

### Step 1: Register/Use Your Domain

- Use Route 53, GoDaddy, Namecheap, or any domain registrar
- Example: `api.llmscope.com`

### Step 2: Request SSL Certificate for Custom Domain

1. **Via AWS Console:**
   - Go to [AWS Certificate Manager](https://console.aws.amazon.com/acm)
   - Request certificate for: `api.llmscope.com`
   - Use DNS validation
   - Add the CNAME record to your domain's DNS

2. **Via AWS CLI:**
   ```bash
   aws acm request-certificate \
     --domain-name api.llmscope.com \
     --validation-method DNS \
     --region us-east-1
   ```

### Step 3: Configure Load Balancer (same as Option A Step 3)

Follow Step 3 from Option A above.

### Step 4: Point Domain to Load Balancer

1. **Get Load Balancer DNS:**
   - Go to EC2 Console > Load Balancers
   - Find the ALB created by Elastic Beanstalk
   - Copy the **DNS name** (e.g., `awseb-e-x-AWSEBLoa-XXXXXXXXXXXX.us-east-1.elb.amazonaws.com`)

2. **Create CNAME Record:**
   - In your DNS provider (Route 53, etc.)
   - Create CNAME record:
     - **Name**: `api` (or your subdomain)
     - **Type**: CNAME
     - **Value**: Load balancer DNS name

3. **Wait for DNS propagation** (5-60 minutes)

---

## Step 5: Update Frontend Configuration

Once HTTPS is enabled, update your frontend to use the HTTPS URL:

```bash
cd frontend
echo "VITE_API_URL=https://llmscope-backend-env.eba-bxmhbs4y.us-east-1.elasticbeanstalk.com" > .env.production

# Or if using custom domain:
# echo "VITE_API_URL=https://api.llmscope.com" > .env.production

# Redeploy to Vercel
vercel --prod
```

---

## Step 6: Verify HTTPS Setup

### Test HTTPS endpoint:

```bash
# Health check
curl -v https://llmscope-backend-env.eba-bxmhbs4y.us-east-1.elasticbeanstalk.com/health

# Should show:
# - SSL certificate valid
# - HTTP 200 response
# - {"status":"healthy"}
```

### Test from frontend:

1. Open your Vercel frontend
2. Send a test chat message
3. Check browser console (no mixed content errors)
4. Verify Network tab shows HTTPS requests

---

## Troubleshooting

### Certificate Validation Pending

**Issue**: Certificate stuck in "Pending validation"

**Solution**:
- Ensure you added the CNAME records to DNS
- Wait 5-30 minutes for validation
- Check ACM console for validation status

### Load Balancer Health Checks Failing

**Issue**: ALB shows unhealthy targets

**Solution**:
1. Check health check path in ALB configuration (should be `/health`)
2. Ensure security group allows ALB to connect to EC2 instances
3. Verify backend responds to health checks:
   ```bash
   curl http://llmscope-backend-env.eba-bxmhbs4y.us-east-1.elasticbeanstalk.com/health
   ```

### CORS Errors After HTTPS

**Issue**: CORS errors in browser console

**Solution**:
- Ensure `CORS_ORIGINS` includes your Vercel frontend URL
- Update EB environment variables:
  ```bash
  eb setenv CORS_ORIGINS="https://your-frontend.vercel.app,https://llmscopeplaygroundfrontend-ioq2f5eqf-yosongyxp-7364s-projects.vercel.app"
  ```

### Mixed Content Errors

**Issue**: Browser blocks HTTP requests from HTTPS page

**Solution**:
- This should be resolved once backend is on HTTPS
- Ensure frontend `.env.production` uses `https://` not `http://`

---

## Cost Breakdown

### AWS Elastic Beanstalk with Application Load Balancer

- **Application Load Balancer**: ~$16.20/month (730 hours × $0.0225/hour)
- **Load Balancer Capacity Units**: ~$5.84/month (730 LCU-hours × $0.008/LCU-hour)
- **EC2 instance (t3.micro)**: Free tier eligible (first 12 months)
- **RDS (db.t3.micro)**: Free tier eligible (first 12 months)
- **SSL Certificate (ACM)**: **FREE**

**Total estimated cost**: ~$15-22/month

### Free Tier Alternatives

If cost is a concern, consider:
1. **Railway**: Free tier with HTTPS included
2. **Render**: Free tier with HTTPS included
3. **Fly.io**: Free tier with HTTPS included

---

## Next Steps

1. **Enable Application Load Balancer** in EB environment
2. **Request SSL certificate** from ACM
3. **Configure HTTPS listener** on port 443
4. **Update frontend** to use HTTPS URL
5. **Test end-to-end** functionality

---

## Quick Start Commands

```bash
# Step 1: Configure EB to use ALB (via CLI)
cd backend
eb config
# Change LoadBalancerType to 'application', save and exit

# Step 2: Request certificate (replace with your domain)
aws acm request-certificate \
  --domain-name llmscope-backend-env.eba-bxmhbs4y.us-east-1.elasticbeanstalk.com \
  --validation-method DNS \
  --region us-east-1

# Step 3: After configuring HTTPS in console, update frontend
cd ../frontend
echo "VITE_API_URL=https://llmscope-backend-env.eba-bxmhbs4y.us-east-1.elasticbeanstalk.com" > .env.production
vercel --prod

# Step 4: Test
curl https://llmscope-backend-env.eba-bxmhbs4y.us-east-1.elasticbeanstalk.com/health
```

---

## Reference Links

- [AWS ACM Documentation](https://docs.aws.amazon.com/acm/)
- [EB HTTPS Configuration](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/configuring-https.html)
- [Application Load Balancer Pricing](https://aws.amazon.com/elasticloadbalancing/pricing/)
