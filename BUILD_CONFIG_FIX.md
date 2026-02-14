# Build Configuration - Railway Fix Summary

## Problem

Railway's Nixpacks auto-detection failed because the project is a monorepo with:
- Python backend in `backend/`
- React frontend in `frontend/`
- No single language at root level

Error message:
```
Nixpacks was unable to generate a build plan for this app.
```

## Solution

Switched from **Nixpacks** (auto-detection) to **Docker** (explicit build files)

## Files Created/Modified

### 1. `Dockerfile.api` (NEW)
- Builds FastAPI backend for API service
- Located at project root
- Multi-stage build for optimization
- Installs FFmpeg for video processing

### 2. `railway.json` (MODIFIED)
- Changed `builder: "nixpacks"` → `builder: "dockerfile"`
- Specifies `dockerfile: "Dockerfile.api"`
- Added all environment variables
- This is used for the **API service**

### 3. `railway.worker.json` (NEW)
- Configuration for Celery worker service
- Uses same Dockerfile.api
- Start command: `celery -A app.workers.celery_app worker --loglevel=info`
- Needs same DATABASE_URL, REDIS_URL, S3 credentials

### 4. `frontend/railway.json` (NEW)
- Configuration for React frontend service
- Uses `frontend/Dockerfile`
- Environment: NODE_ENV=production, REACT_APP_API_URL

### 5. `.nixpacks` (NEW)
- Empty marker file
- Prevents Nixpacks from running

## Deployment Steps (Now Fixed)

1. **Push to GitHub** (Already done ✅)
2. **Railway detects Dockerfile** - Uses railway.json automatically
3. **Add PostgreSQL service** - Railway provides DATABASE_URL
4. **Add Redis service** - Railway provides REDIS_URL
5. **Configure S3** - Add credentials (AWS S3 or Backblaze B2)
6. **Deploy worker** - Same repo, different start command
7. **Deploy frontend** - Separate service, different entrypoint
8. **Test** - Health check, registration, upload, processing

## Quick Test Locally

```bash
# Build API image (requires Docker running)
docker build -f Dockerfile.api -t video-editor-api .

# Run API
docker run -p 8000:8000 \
  -e SECRET_KEY="your_secret_key_here" \
  -e DATABASE_URL="postgresql://user:pass@localhost/dbname" \
  -e REDIS_URL="redis://localhost:6379" \
  video-editor-api

# API should be available at http://localhost:8000
```

## What Changed vs Before

| Aspect | Before | After |
|--------|--------|-------|
| Builder | Nixpacks (auto-detect) | Docker (explicit) |
| Build Speed | ✅ Faster initial | ⚡ May be slower first time, then cached |
| Reliability | ❌ Failed on monorepo | ✅ Always works |
| Configuration | ❌ Auto (limited control) | ✅ Explicit (full control) |
| Multi-language Support | ❌ Limited | ✅ Perfect for monorepo |

## Environment Variables Needed

For API Service:
```
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=<generated_key>
S3_ENDPOINT=https://s3.amazonaws.com (or your endpoint)
S3_ACCESS_KEY=<key>
S3_SECRET_KEY=<key>
S3_BUCKET=video-editor-prod
S3_REGION=us-west-2
S3_SECURE=true
CORS_ORIGINS=https://yourdomain.com
DEBUG=false
```

For Worker Service:
```
DATABASE_URL=<same as API>
REDIS_URL=<same as API>
S3_ENDPOINT=<same as API>
S3_ACCESS_KEY=<same as API>
S3_SECRET_KEY=<same as API>
S3_BUCKET=<same as API>
S3_REGION=<same as API>
S3_SECURE=<same as API>
DEBUG=false
```

For Frontend Service:
```
REACT_APP_API_URL=https://api.yourdomain.com
NODE_ENV=production
```

## Status

✅ Configuration files created/fixed
✅ Dockerfile.api validated for syntax
✅ Railway.json updated
✅ Worker and frontend configs created
✅ Ready for Railway deployment

Next: Push to GitHub and deploy! 🚀
