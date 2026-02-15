# CareerOS: Operational Runbook

**Version:** 1.0
**Last Updated:** February 15, 2026
**Owner:** DevOps & Engineering Team

---

## System Architecture

### Component Overview

```
┌────────── EXTERNAL USERS ──────────┐
                    │
         ┌──────────┼──────────┐
         │  Cloudflare CDN    │
         └──────────┬──────────┘
                    │
    ┌───────────┼───────────┐
    │               │               │
┌───┼────┐  ┌─────┼────┐  ┌────┼────┐
│ Next.js │  │ FastAPI │  │ Workers │
│ Vercel  │  │ Railway │  │  Modal  │
└───┬────┘  └─────┬────┘  └────┬────┘
    │         ┌─────┼─────┐      │
┌───┼───┐  ┌─┼───────┼─┐  ┌──┼────┐
│ Supabase│  │PostgreSQL│  │ Redis │
│  Auth  │  │           │  │ Queue │
└────────┘  └───┬───────┘  └───────┘
                │
          ┌─────┼─────┐
          │  ChromaDB  │
          └───────────┘
```

### Service Endpoints

| Service | Production URL | Health Check |
|---------|---------------|-------------|
| Frontend | app.careeros.com | /api/health |
| Backend API | api.careeros.com | /health |
| PostgreSQL | Supabase connection | SELECT 1 |
| ChromaDB | internal:8000 | /api/v1/heartbeat |

---

## Monitoring & Alerting

### Monitoring Stack

**Application:**
- **Sentry** - Error tracking, performance
- **Vercel Analytics** - Frontend performance
- **Railway Metrics** - CPU, memory, network

**Infrastructure:**
- **Uptime Robot** - Endpoint availability (1-min checks)
- **Supabase Dashboard** - Database performance

**Logs:**
- **Railway Logs** - Application logs
- **Vercel Logs** - Frontend logs
- **Sentry Breadcrumbs** - User action trail

### Key Metrics

**System Health:**
- API response time (p50, p95, p99)
- Error rate (target: <0.5%)
- Uptime (target: 99.5%)
- Database connections (max: 100)

**Business:**
- Messages generated per hour
- Message approval rate
- Average quality score
- LinkedIn scraping success rate

**Resources:**
- CPU usage (alert >80% for 5 min)
- Memory usage (alert >85%)
- Disk space (alert <10% free)

### Alert Configuration

**Critical (Page On-Call):**
- System down (>5 minutes)
- Error rate >5%
- Database connection failures

**High Priority (Slack):**
- Error rate >1%
- API latency >2s for 5 minutes
- Background job failures

**Medium (Email):**
- Error rate >0.5%
- Slow queries (>1s)
- Cache miss rate >50%

---

## Incident Response

### Severity Levels

| Severity | Response Time | Example |
|----------|--------------|----------|
| **SEV-1** | <15 min | Service down |
| **SEV-2** | <1 hour | Major feature broken |
| **SEV-3** | <4 hours | Minor feature degraded |
| **SEV-4** | <1 day | Cosmetic issue |

### Playbook

**Step 1: Acknowledge (5 min)**
1. Acknowledge alert
2. Post to #incidents
3. Open incident doc

**Step 2: Assess (15 min)**
1. Check Sentry for errors
2. Check Uptime Robot status
3. Check resource usage
4. Identify affected users

**Step 3: Communicate**
- Internal: Update #incidents every 15 min
- External: Update status page
- Customers: Email if >1 hour downtime

**Step 4: Mitigate**
- Apply quick fix
- Consider rollback
- Enable degraded mode

**Step 5: Resolve**
1. Deploy fix
2. Verify resolution
3. Update status page
4. Close incident

**Step 6: Post-Mortem (48 hours)**
- Document root cause
- Timeline
- What went well/poorly
- Action items

---

## Common Issues & Quick Fixes

### 1. Backend API Unresponsive

**Symptoms:**
- 502/504 errors
- Timeout errors
- Health check fails

**Diagnosis:**
```bash
railway logs --tail 100
curl https://api.careeros.com/health
railway status
```

**Quick Fix:**
```bash
railway restart
# If that fails:
railway up
```

---

### 2. LinkedIn Scraping Blocked

**Symptoms:**
- 429 (rate limited) or 403 responses
- Scraping success rate drops

**Quick Fix:**
```python
# Enable proxy rotation
feature_flags.enable("use_proxies", percentage=100)

# Reduce frequency
update_config("scraping_rate_limit", 10)

# Switch to Proxycurl API
export ENABLE_PROXYCURL=true
railway restart
```

---

### 3. OpenAI API Errors

**Symptoms:**
- Message generation fails
- "Rate limit exceeded"
- Timeout errors

**Quick Fix:**
```python
# Enable cached responses
feature_flags.enable("use_cached_messages", 50)

# Fallback to templates
if openai_unavailable:
    return generate_template_message(contact, user)
```

---

### 4. Database Connection Pool Exhausted

**Symptoms:**
- "too many connections"
- Slow queries
- Backend crashes

**Diagnosis:**
```sql
SELECT COUNT(*) FROM pg_stat_activity;

-- Check long-running queries
SELECT pid, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC;
```

**Quick Fix:**
```sql
-- Kill long-running queries
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE now() - query_start > interval '5 minutes';
```

---

### 5. ChromaDB Out of Sync

**Symptoms:**
- Outdated search results
- Recently added contacts not appearing

**Quick Fix:**
```python
# Run sync job
python scripts/sync_chromadb.py
```

---

## Deployment Procedures

### Standard Deployment

**Pre-Deployment:**
- [ ] All tests pass
- [ ] Code reviewed
- [ ] Migrations tested on staging
- [ ] Feature flags configured
- [ ] Rollback plan documented

**Steps:**
```bash
# 1. Deploy to staging
git checkout main
git pull origin main
railway environment set staging
railway up

# 2. Run smoke tests
npm run test:staging

# 3. Deploy to production
railway environment set production
railway up

# 4. Monitor for 15 minutes
railway logs --tail 500
```

### Emergency Hotfix

```bash
# 1. Create hotfix branch
git checkout -b hotfix/critical-issue main

# 2. Make minimal fix
# ... edit code ...

# 3. Fast-track review
git commit -m "HOTFIX: Fix critical issue"
git push origin hotfix/critical-issue

# 4. Deploy directly
railway up --detach

# 5. Monitor closely
railway logs --tail 1000
```

### Rollback

```bash
# Revert to previous deployment
railway rollback <deployment-id>

# For database migrations
alembic downgrade -1

# For feature flags
curl -X POST https://api.careeros.com/admin/feature-flags/disable \
  -d '{"flag": "new_feature"}'
```

---

## Backup & Recovery

### Backup Schedule

**PostgreSQL:**
- Automated daily backups (Supabase)
- Manual backup before each deployment
- Retention: 30 days

**ChromaDB:**
- Daily export to S3
- Retention: 7 days

### Recovery

**Restore PostgreSQL:**
```bash
# Download backup
# (Via Supabase dashboard)

# Restore
psql $DATABASE_URL < backup_20260215.sql

# Update connection string
railway variables set DATABASE_URL=<new-url>
railway restart
```

**Rebuild ChromaDB:**
```python
python scripts/rebuild_chromadb.py
# Re-generates embeddings from PostgreSQL
# Takes ~10 minutes for 1000 contacts
```

---

## Security Procedures

### Token Rotation

**Rotate OpenAI API Key (Quarterly):**
```bash
# 1. Generate new key in OpenAI dashboard
# 2. Update environment variable
railway variables set OPENAI_API_KEY=<new-key>
# 3. Restart
railway restart
# 4. Delete old key
```

---

## On-Call Guide

### Responsibilities

**Business Hours (9 AM - 6 PM IST):**
- Respond to alerts within 15 min
- Monitor #incidents and #alerts
- Join war room for SEV-1

**After Hours:**
- Respond to SEV-1 within 15 min
- SEV-2 can wait until morning

### Escalation Path

```
Level 1: On-Call Engineer
   ↓ (30 min)
Level 2: Senior Engineer / Tech Lead
   ↓ (1 hour)
Level 3: CTO / Founder
```

---

## Conclusion

This runbook provides operational knowledge to keep CareerOS running smoothly.

**Best Practices:**
- Document every incident
- Update runbook after major incidents
- Practice procedures quarterly
- Keep on-call rotation sustainable

---

**Document Owner:** DevOps Team
**Review Cycle:** Monthly
**Last Updated:** February 15, 2026