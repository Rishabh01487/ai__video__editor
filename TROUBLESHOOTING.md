# Troubleshooting Guide

## Quick Diagnostics

Run this to check service health:

```bash
# Check all services
docker-compose ps

# Test backend
curl http://localhost:8000/health

# Test database
docker-compose exec postgres pg_isready -U video_editor

# Test Redis
docker-compose exec redis redis-cli ping

# Check logs
docker-compose logs --tail=50
```

---

## Common Issues & Solutions

### 1. Services Won't Start

**Problem**: `docker-compose up` fails

**Solutions**:

```bash
# Clean rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up

# Check Docker daemon
docker ps          # Should list containers

# Check port availability
# Port 3000: frontend
# Port 8000: backend
# Port 5432: postgres
# Port 6379: redis
# Port 9000: minio
```

**If still failing**:
```bash
# View detailed logs
docker-compose logs

# Check individual service
docker-compose logs backend -f
docker-compose logs postgres -f

# Rebuild specific service
docker-compose build backend --no-cache
```

---

### 2. Database Connection Failed

**Error**: 
```
psycopg2.OperationalError: could not connect to server: Connection refused
```

**Solutions**:

```bash
# Check postgres is running
docker-compose ps postgres

# Check postgres is healthy
docker-compose exec postgres pg_isready -U video_editor

# Restart postgres
docker-compose restart postgres

# Wait for it to be healthy
docker-compose up postgres
# Wait 10 seconds for startup

# Verify connection manually
docker-compose exec postgres psql -U video_editor -d video_editor -c "SELECT 1"
```

**If database is corrupted**:
```bash
# Backup existing data
docker-compose exec postgres pg_dump -U video_editor -d video_editor > backup.sql

# Reset database
docker-compose down -v postgres
docker-compose up -d postgres
docker-compose exec backend python -c "from app.database import init_db; init_db()"
```

---

### 3. Redis Connection Failed

**Error**:
```
redis.exceptions.ConnectionError: Cannot connect to Redis
```

**Solutions**:

```bash
# Check redis is running
docker-compose ps redis

# Test redis connection
docker-compose exec redis redis-cli ping
# Should return "PONG"

# Restart redis
docker-compose restart redis

# Check redis logs
docker-compose logs redis -f
```

---

### 4. Celery Workers Not Processing Tasks

**Problem**: Jobs stay in "processing" state forever

**Solutions**:

```bash
# Check worker is running
docker-compose ps celery_worker

# View worker logs
docker-compose logs celery_worker -f

# Check Redis connection from worker
docker-compose exec celery_worker redis-cli -h redis ping

# Restart worker
docker-compose restart celery_worker

# Check task queue
docker-compose exec redis redis-cli lrange celery 0 -1

# Flush queue if stuck (WARNING: deletes pending tasks)
docker-compose exec redis redis-cli FLUSHDB
```

**If worker crashes**:
```bash
# Check for out of memory
docker stats celery_worker

# Set memory limit in docker-compose.yml
docker-compose.yml:
  celery_worker:
    mem_limit: 2g
    memswap_limit: 2g
```

---

### 5. Video Processing Hangs or Fails

**Problem**: Jobs timeout or error during rendering

**Solutions**:

```bash
# Check worker logs
docker-compose logs celery_worker -f

# Check disk space
docker exec video-editor-api df -h

# Increase task timeout in config.py
# task_time_limit: 30 * 60 (change to higher value)

# Reduce processing complexity
# Reduce sample_frames in backend/app/ai_engine/object_tagger.py
```

**If job errors with "out of memory"**:

```bash
# Increase worker memory
# Edit docker-compose.yml
celery_worker:
  mem_limit: 4g

docker-compose up -d celery_worker
```

**If video outputs are corrupted**:

```bash
# Check FFmpeg is installed
docker-compose exec backend which ffmpeg

# Rebuild backend image
docker-compose build backend --no-cache
```

---

### 6. S3/MinIO Upload Fails

**Problem**: Asset upload returns error

**Solutions**:

```bash
# Check MinIO is running
docker-compose ps minio

# Check bucket exists
docker-compose exec minio mc ls minio/video-editor/

# Create bucket if missing
docker-compose exec minio mc mb minio/video-editor

# Check MinIO logs
docker-compose logs minio -f

# Verify credentials
# Check .env:
# S3_ACCESS_KEY=minioadmin
# S3_SECRET_KEY=minioadmin
```

**For AWS S3 or Backblaze B2**:

```bash
# Test credentials manually
aws s3 ls s3://YOUR_BUCKET_NAME

# or for B2
b2 ls YOUR_BUCKET

# If error: InvalidAccessKeyId
# Check S3_ACCESS_KEY and S3_SECRET_KEY in .env
```

---

### 7. Frontend Doesn't Load

**Problem**: Browser shows blank page or cannot connect

**Solutions**:

```bash
# Check frontend is running
docker-compose ps frontend

# Check frontend logs
docker-compose logs frontend -f

# Check API is reachable from frontend
docker-compose exec frontend curl http://backend:8000/health

# Clear browser cache
# Chrome: Ctrl + Shift + Delete
# Safari: Cmd + Shift + Delete
# Firefox: Ctrl + Shift + Delete
```

**If 404 errors**:

```bash
# Rebuild frontend
docker-compose build frontend --no-cache
docker-compose up -d frontend

# Check nginx config
docker-compose exec frontend nginx -t
```

**If API calls fail**:

```bash
# Check REACT_APP_API_URL
docker-compose exec frontend env | grep REACT_APP

# Should be pointing to backend service/domain

# For local development: http://localhost:8000 or http://backend:8000
# For Railway: https://yourdomain-api.railway.app
```

---

### 8. CORS Errors

**Error**: Browser shows CORS error in console

**Solutions**:

```bash
# Check CORS_ORIGINS in .env
# Example: http://localhost:3000,http://localhost:8000

# Restart backend
docker-compose restart backend

# Verify it's working
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     http://localhost:8000/auth/register
# Should include Access-Control-* headers
```

**For production (Railway)**:

```bash
# Update CORS_ORIGINS
# Set to: https://yourdomain.com,https://www.yourdomain.com
```

---

### 9. Authentication Issues

**Problem**: "Invalid token" or cannot login

**Solutions**:

```bash
# Check SECRET_KEY is consistent
# Should be same on all services
docker-compose exec backend echo $SECRET_KEY

# Clear browser localStorage
# Browser DevTools > Application > Local Storage > Clear All

# Verify password hashing works
docker-compose exec backend python -c \
  "from app.auth.jwt import hash_password, verify_password; \
   h = hash_password('test'); \
   print(verify_password('test', h))"
# Should print True

# Check JWT time (server clock sync)
date
# Should be accurate
```

---

### 10. Out of Disk Space

**Error**: `No space left on device`

**Solutions**:

```bash
# Check available space
docker system df

# Remove unused images
docker image prune -a

# Remove old containers
docker container prune

# Remove dangling volumes
docker volume prune

# Clean everything (WARNING: removes all unused Docker data)
docker system prune -a

# Check specific service size
docker inspect --format='{{.GraphDriver.Data.MergedDir}}' CONTAINER_ID
du -sh /path/from/above
```

---

### 11. Permission Denied Errors

**Error**: `permission denied` when accessing files

**Solutions**:

```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Rebuild containers
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

### 12. DNS Resolution Fails

**Error**: `Name does not resolve` or `getaddrinfo failed`

**Solutions**:

```bash
# Check service names resolve
docker-compose exec backend ping postgres     # Should work
docker-compose exec backend ping redis       # Should work

# Check network
docker network ls

# Inspect network
docker network inspect ai-video-editor_default

# Restart docker
sudo systemctl restart docker        # Linux
# or restart Docker Desktop         # macOS/Windows
```

---

## Performance Troubleshooting

### Slow Video Processing

```bash
# Check CPU usage
docker stats celery_worker

#Check if processing is I/O bound
docker-compose logs celery_worker | grep -i "frame\|detection\|rendering"

# Solutions:
# 1. Reduce sample frames in object_tagger.py
#    sample_frames: int = 3  (instead of 5)

# 2. Use faster model (smaller version)
#    YOLO("yolov8n.pt")  # nano version

# 3. Increase resources
#    docker-compose.yml: cpus: "2" or higher
```

### Slow API Response

```bash
# Check database queries
docker-compose exec backend python -c \
  "from app.database import engine; \
   engine.echo = True"

# Check for missing indexes
docker-compose exec postgres psql -U video_editor -d video_editor
\d+ users
\d+ projects
```

### High Memory Usage

```bash
# Check memory
docker stats

# Identify memory leak
docker-compose logs celery_worker | grep "memory\|GC"

# Restart service that uses most memory
docker-compose restart celery_worker

# Reduce task concurrency (in docker-compose.yml)
command: celery -A app.workers.celery_app worker --concurrency=1 --loglevel=info
```

---

## Testing & Validation

### Verify All Services

```bash
# Health check script
#!/bin/bash
echo "Checking services..."

# Frontend
curl -s http://localhost:3000 > /dev/null && echo "✓ Frontend" || echo "✗ Frontend"

# Backend
curl -s http://localhost:8000/health | grep -q "ok" && echo "✓ Backend" || echo "✗ Backend"

# Database
docker-compose exec postgres pg_isready -U video_editor > /dev/null && echo "✓ Database" || echo "✗ Database"

# Redis
docker-compose exec redis redis-cli ping | grep -q "PONG" && echo "✓ Redis" || echo "✗ Redis"

# MinIO
curl -s http://localhost:9000 > /dev/null && echo "✓ MinIO" || echo "✗ MinIO"

echo "All checks complete"
```

### Test API Endpoints

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"password123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Save token
TOKEN="your_token_here"

# Get current user
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Create project
curl -X POST http://localhost:8000/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Project"}'
```

---

## Log Files

### View Logs

```bash
# All services
docker-compose logs --tail=100 -f

# Specific service
docker-compose logs backend -f
docker-compose logs celery_worker -f
docker-compose logs postgres -f

# Filter logs
docker-compose logs | grep ERROR
docker-compose logs | grep WARNING

# Timestamps
docker-compose logs --timestamps
```

### Save Logs

```bash
# Save to file
docker-compose logs > debug.log 2>&1

# Export and compress
docker-compose logs | gzip > logs_$(date +%Y%m%d_%H%M%S).log.gz
```

---

## Getting Help

1. **Check logs first**:
   ```bash
   docker-compose logs --tail=100
   ```

2. **Search issues**: 
   - GitHub Issues: https://github.com/yourusername/ai-video-editor

3. **Community Help**:
   - FastAPI Docs: https://fastapi.tiangolo.com
   - React Docs: https://react.dev
   - Docker Docs: https://docs.docker.com

4. **Report Bug**: Include:
   - Docker version: `docker --version`
   - OS: `uname -a`
   - Error logs: `docker-compose logs --tail=500`
   - Steps to reproduce
   - Expected vs actual behavior

---

## Emergency Procedures

### Disaster Recovery

```bash
# Backup everything
docker-compose exec postgres pg_dump -U video_editor -d video_editor > backup.sql
docker-compose exec minio mc mirror minio/video-editor ./backup_s3

# Complete reset
docker-compose down -v
docker system prune -a
docker-compose build --no-cache
docker-compose up -d
make db-init

# Restore from backup
docker-compose exec postgres psql -U video_editor -d video_editor < backup.sql
```

### Kill Stuck Processes

```bash
# Force stop all containers
docker-compose kill

# Remove them
docker-compose rm -f

# Clean up
docker system prune -a

# Start fresh
docker-compose up
```

---

Last updated: February 2026
