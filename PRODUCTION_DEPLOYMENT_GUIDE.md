# Production Deployment Considerations for QA RAG Bot

## Overview

This document outlines important considerations for deploying your QA RAG Bot to production on Heroku.

## 1. Vector Database Persistence ⚠️ CRITICAL

### Current Implementation

Your app uses **Chroma DB** for vector embeddings, but the current setup has limitations:

**Problem**: Embeddings are stored in memory by default

- Lost when dyno restarts (daily or on code deployment)
- Not suitable for production
- Data loss on any dyno restart

### Solutions

#### Option 1: Use Chroma with Persistent Storage (Recommended for Small-Scale)

```python
# In your embeddings.py or configuration
import chromadb
from chromadb.config import Settings

# Create persistent client
settings = Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="/tmp/chroma_data",  # Heroku ephemeral storage
    anonymized_telemetry=False
)
client = chromadb.Client(settings)
```

**Limitation**: Heroku's `/tmp` is ephemeral (cleared on restart)

#### Option 2: Use Heroku Postgres + Chroma (Better for Production)

```bash
# Add Postgres to your app
heroku addons:create heroku-postgresql:basic

# Get connection string
heroku config:get DATABASE_URL
```

#### Option 3: Use External Vector Database (Best for Scale)

**Pinecone** (Recommended for ease of use):

```python
import pinecone

# Initialize
pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENVIRONMENT")
)

# Create index
pinecone.create_index("rag-bot", dimension=1536)
```

**Alternatives**:

- **Weaviate** (Self-hosted or cloud)
- **Milvus** (Open-source)
- **Qdrant** (Cloud or self-hosted)
- **Supabase Vector** (PostgreSQL + pgvector)

### Implementation Steps (Recommended: Pinecone)

1. **Sign up for Pinecone**: https://www.pinecone.io/
2. **Create API key** and get environment
3. **Install SDK**:
    ```bash
    pip install pinecone-client
    ```
4. **Set Heroku config**:
    ```bash
    heroku config:set PINECONE_API_KEY="your-key"
    heroku config:set PINECONE_ENVIRONMENT="us-west-2-aws"
    ```
5. **Update embeddings.py** to use Pinecone instead of Chroma

## 2. Environment Configuration

### Required Environment Variables

```bash
# Essential
OPENAI_API_KEY=sk-...

# For Vector Database (choose based on solution)
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=...

# Or for Postgres
DATABASE_URL=postgres://...

# Optional logging
LOG_LEVEL=INFO
```

### Set Variables

```powershell
# Individual
heroku config:set OPENAI_API_KEY="sk-..."
heroku config:set PINECONE_API_KEY="..."

# Or from file (if in format KEY=value)
heroku config:set $(cat .env | tr '\n' ' ')
```

### Verify

```bash
heroku config
```

## 3. Performance Optimization

### Dyno Type

```bash
# Current: Free (sleeps after 30 mins)
# Recommended for production:

# Eco (Recommended starting point)
heroku dyno:type eco

# Standard-1x (Better performance)
heroku dyno:type standard-1x

# Standard-2x (High performance)
heroku dyno:type standard-2x
```

### Worker Configuration (Procfile)

```
web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app
```

**Optimize based on dyno RAM**:

- **Free/Eco (512MB)**: `-w 2` (2 workers)
- **Standard-1x (512MB)**: `-w 4` (4 workers)
- **Standard-2x (1GB)**: `-w 4 --max-requests 1000` (add max-requests)

## 4. Database Scaling

### If Using Heroku Postgres

```bash
# View available plans
heroku addons:plans heroku-postgresql

# Upgrade
heroku addons:upgrade heroku-postgresql:standard-0

# Backup database
heroku pg:backups:capture

# Restore from backup
heroku pg:backups:restore BACKUP_ID
```

## 5. Security Checklist

- [ ] **API Keys**: All stored as config vars, NEVER in code
- [ ] **SSL/TLS**: Automatically enabled by Heroku
- [ ] **CORS**: Review FastAPI CORS settings if calling from web
- [ ] **Rate Limiting**: Consider adding to prevent abuse
- [ ] **Input Validation**: Already implemented, but review before production
- [ ] **Logging**: Remove sensitive data from logs
- [ ] **Dependencies**: Keep requirements.txt updated

### Add Rate Limiting (Optional)

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/ask")
@limiter.limit("30/minute")
async def ask_endpoint(request: AskRequest):
    # ... your code
```

Install: `pip install slowapi`

## 6. Monitoring & Alerts

### Heroku Metrics Dashboard

```bash
# View in browser
heroku apps:info your-app-name

# Or in CLI
heroku metrics
```

### Useful Monitoring Tools

1. **Heroku Dashboard**: https://dashboard.heroku.com/ (free)
2. **New Relic**: Free tier includes APM (Application Performance Monitoring)
3. **Sentry**: Error tracking (free tier)
4. **DataDog**: Comprehensive monitoring

### Add New Relic (Free)

```bash
heroku addons:create newrelic:wayne
```

## 7. Logging & Error Tracking

### View Logs

```bash
# Real-time
heroku logs --tail

# Recent errors
heroku logs --num=100 | grep ERROR

# Specific time range
heroku logs --dyno=web --num=50
```

### Implement Better Logging

```python
import logging

# Your code already has:
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Good! Just ensure sensitive data is not logged
logger.info(f"Processing query...")  # ✓ Good
logger.debug(f"API Key: {api_key}")  # ✗ Bad - don't log secrets
```

## 8. Backup Strategy

### For Vector Database

- **Pinecone**: Built-in backup (enterprise plans)
- **Postgres**: Use Heroku PG backups
    ```bash
    heroku pg:backups:capture
    heroku pg:backups:download b003 --output latest.dump
    ```

### For Code

- Use GitHub for version control (already doing this ✓)
- Tag releases: `git tag -a v1.0.0 -m "Production release"`

## 9. Scaling Considerations

### Horizontal Scaling (Multiple Dynos)

```bash
# Scale to 2 web dynos
heroku ps:scale web=2
```

### Vertical Scaling

```bash
# Upgrade dyno type
heroku dyno:type standard-2x
```

### Load Balancing

- Automatic with multiple dynos
- Heroku router distributes requests

## 10. Cost Estimates (Monthly)

| Component       | Cost    | Notes                              |
| --------------- | ------- | ---------------------------------- |
| Free Dyno       | $0      | Sleeps, slow, suitable for testing |
| Eco Dyno        | $5      | Recommended starting point         |
| Standard-1x     | $7      | Better performance                 |
| Standard-2x     | $25     | High performance                   |
| Heroku Postgres | $9-200+ | Depends on plan                    |
| Pinecone        | $0-100+ | Free up to 1M vectors              |
| External Domain | $3+     | Optional custom domain             |

**Example Production Setup**: Eco dyno ($5) + Pinecone free tier = $5/month

## 11. Deployment Workflow

### Before Each Production Deploy

```bash
# 1. Test locally
pytest tests/

# 2. Commit code
git add .
git commit -m "Feature: xyz"

# 3. Create backup of production data
heroku pg:backups:capture

# 4. Deploy
git push heroku main

# 5. Monitor
heroku logs --tail

# 6. Run tests against production (optional)
# curl https://your-app.herokuapp.com/
```

### Rollback if Issues

```bash
# View deployment history
heroku releases

# Rollback to previous version
heroku rollback v123
```

## 12. Maintenance Tasks

### Weekly

- [ ] Review logs for errors: `heroku logs --num=1000`
- [ ] Check metrics: `heroku metrics`
- [ ] Test key endpoints

### Monthly

- [ ] Update dependencies: `pip list --outdated`
- [ ] Backup data
- [ ] Review costs
- [ ] Check security updates

### Quarterly

- [ ] Major version updates
- [ ] Performance optimization review
- [ ] Capacity planning

## Quick Setup for Production

### Recommended Stack (Minimum)

```bash
# 1. Create app with eco dyno
heroku create your-app-name
heroku dyno:type eco

# 2. Set up Pinecone free tier
heroku config:set PINECONE_API_KEY="your-key"
heroku config:set PINECONE_ENVIRONMENT="us-west-2-aws"

# 3. Set OpenAI key
heroku config:set OPENAI_API_KEY="sk-..."

# 4. Deploy
git push heroku main

# 5. Monitor
heroku logs --tail
heroku open
```

### Premium Stack (If Budget Allows)

```bash
# All of above, plus:
heroku dyno:type standard-1x
heroku addons:create heroku-postgresql:standard-0
heroku addons:create newrelic:wayne
```

## Troubleshooting Production Issues

### API Endpoints Down

```bash
heroku logs --tail
heroku ps
heroku restart
```

### Slow Response Times

```bash
# Check metrics
heroku metrics

# Increase workers if using Standard+ dyno
# Edit Procfile and increase -w value

# Or upgrade dyno type
heroku dyno:type standard-2x
```

### Out of Memory

```bash
# Check logs
heroku logs | grep "MemoryError"

# Reduce workers in Procfile
# Or upgrade dyno type
```

### Database Issues

```bash
# Check Postgres
heroku pg:info

# View active connections
heroku pg:connections

# If stuck, restart
heroku restart --type=worker
```

## Resources

- **Heroku Docs**: https://devcenter.heroku.com/
- **Pinecone Docs**: https://docs.pinecone.io/
- **FastAPI Production**: https://fastapi.tiangolo.com/deployment/
- **Chroma Docs**: https://docs.trychroma.com/
- **Python in Production**: https://gunicorn.org/
- **Security**: https://owasp.org/www-project-secure-coding-practices/

---

**Last Updated**: January 30, 2026
**Heroku Python Support**: https://devcenter.heroku.com/articles/python-support
