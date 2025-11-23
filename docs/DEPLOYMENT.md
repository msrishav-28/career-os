# Deployment Guide

Complete guide for deploying CareerOS to production.

## Prerequisites

- GitHub account
- Railway account (for backend)
- Vercel account (for frontend)
- Supabase account (database)
- OpenAI API key
- Redis instance (Railway provides this)

---

## Quick Deploy

### Option 1: One-Click Deploy

**Backend (Railway):**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

1. Click "Deploy on Railway"
2. Connect your GitHub repo
3. Add environment variables (see below)
4. Deploy

**Frontend (Vercel):**

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

1. Click "Deploy with Vercel"
2. Import your GitHub repo
3. Set environment variables
4. Deploy

### Option 2: Manual Deploy

See detailed steps below.

---

## Backend Deployment (Railway)

### 1. Create Railway Project

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init
```

### 2. Configure Environment Variables

In Railway dashboard, add these environment variables:

```bash
# Required
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key-min-32-chars

# Redis (Railway provides this automatically)
REDIS_URL=redis://...

# Optional
RESEND_API_KEY=re_...
SENTRY_DSN=https://...
```

### 3. Deploy Backend

```bash
# From project root
railway up

# Or link existing service
railway link
railway up
```

### 4. Setup Celery Workers

Add separate services in Railway:

**Service 1: Celery Worker**
```bash
celery -A tasks.celery_app worker --loglevel=info --pool=solo
```

**Service 2: Celery Beat**
```bash
celery -A tasks.celery_app beat --loglevel=info
```

### 5. Verify Deployment

```bash
# Check health
curl https://your-app.railway.app/health

# Check API docs
curl https://your-app.railway.app/docs
```

---

## Frontend Deployment (Vercel)

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Deploy Frontend

```bash
cd frontend

# Deploy
vercel

# Or deploy to production
vercel --prod
```

### 3. Configure Environment Variables

In Vercel dashboard, add:

```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

### 4. Configure Domain

1. Go to Vercel dashboard
2. Settings → Domains
3. Add your custom domain
4. Update DNS records

---

## Database Setup (Supabase)

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Note your credentials

### 2. Run Database Migrations

1. Go to Supabase SQL Editor
2. Copy content from `backend/scripts/setup_db.sql`
3. Run the SQL script

### 3. Verify Tables

Check that all tables are created:
- users
- contacts
- messages
- opportunities
- campaigns
- activity_log
- agent_insights

---

## Docker Deployment

### Using Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Individual Services

```bash
# Backend
docker build -t careeros-backend ./backend
docker run -p 8000:8000 careeros-backend

# Frontend
docker build -t careeros-frontend ./frontend
docker run -p 3000:3000 careeros-frontend
```

---

## Environment Configuration

### Production .env (Backend)

```bash
# API Keys
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...

# Database
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGc...
SUPABASE_SERVICE_KEY=eyJhbGc...
DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres

# Redis
REDIS_URL=redis://default:password@redis.railway.internal:6379

# Email
RESEND_API_KEY=re_xxxxx

# Security
SECRET_KEY=generate-with-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=production

# Rate Limits
LINKEDIN_CONNECTION_DAILY_LIMIT=15
LINKEDIN_PROFILE_VIEW_DAILY_LIMIT=80
EMAIL_DAILY_LIMIT=50

# Monitoring
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
```

### Production .env (Frontend)

```bash
NEXT_PUBLIC_API_URL=https://careeros-backend.railway.app
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
```

---

## SSL/HTTPS

Both Railway and Vercel provide automatic HTTPS.

**Custom Domain SSL:**
1. Add custom domain in platform dashboard
2. Update DNS records
3. SSL certificate is automatically provisioned

---

## Monitoring & Logging

### Sentry Setup

1. Create Sentry project
2. Add DSN to environment variables
3. Errors are automatically tracked

### Railway Logs

```bash
railway logs

# Follow logs
railway logs -f
```

### Vercel Logs

View in Vercel dashboard under "Logs" tab.

---

## Scaling

### Railway Scaling

1. Go to Service Settings
2. Adjust resources:
   - Memory: 1GB - 8GB
   - CPU: 1 - 4 cores
   - Replicas: 1 - 10

### Vercel Scaling

Automatic scaling included in all plans.

---

## CI/CD Pipeline

GitHub Actions automatically:
1. Run tests on PR
2. Deploy to staging on merge to `develop`
3. Deploy to production on merge to `main`

### Setup Secrets

In GitHub repository settings, add:

```bash
RAILWAY_TOKEN=xxx
VERCEL_TOKEN=xxx
VERCEL_ORG_ID=xxx
VERCEL_PROJECT_ID=xxx
```

---

## Backup Strategy

### Database Backups

Supabase automatic backups:
- Daily backups (free tier)
- Point-in-time recovery (pro tier)

### ChromaDB Backups

```bash
# Backup chroma_db directory
railway run tar -czf chroma_backup.tar.gz chroma_db/

# Download backup
railway run cat chroma_backup.tar.gz > local_backup.tar.gz
```

---

## Security Checklist

- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS/SSL
- [ ] Set strong SECRET_KEY
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Set up monitoring (Sentry)
- [ ] Regular security updates
- [ ] Database connection encryption
- [ ] API key rotation policy

---

## Cost Estimates

### Development
- Supabase: Free
- Railway: $5/month
- Vercel: Free
- Total: **$5/month**

### Production (100 users)
- Supabase: Free tier sufficient
- Railway: $20/month
- Vercel: Free tier sufficient
- OpenAI: ~$50/month
- Total: **$70/month**

### Scale (1000 users)
- Supabase: $25/month
- Railway: $100/month
- Vercel: $20/month
- OpenAI: ~$500/month
- Total: **$645/month**

---

## Troubleshooting

### Backend won't start

```bash
# Check logs
railway logs

# Verify environment variables
railway variables

# Restart service
railway restart
```

### Database connection issues

1. Verify DATABASE_URL is correct
2. Check Supabase project is running
3. Verify IP whitelist (Supabase allows all by default)

### Celery tasks not running

1. Verify Redis is running
2. Check REDIS_URL environment variable
3. Ensure Celery worker/beat services are running

### Frontend can't connect to backend

1. Verify NEXT_PUBLIC_API_URL is correct
2. Check CORS settings in backend
3. Verify backend is deployed and healthy

---

## Support

- Documentation: See `/docs` folder
- Issues: GitHub Issues
- Community: Discord (link in README)

---

## Next Steps

After deployment:
1. Test all features
2. Monitor error rates
3. Set up alerts
4. Configure backup schedule
5. Document any custom configurations
