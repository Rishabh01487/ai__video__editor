# Railway Deployment - Fixed Configuration

## ✅ What Was Fixed

The Nixpacks build error occurred because Railway couldn't auto-detect the project type in a monorepo structure. This has been fixed with:

### 1. **Dockerfile-based Build** (Instead of Nixpacks)
- Created `Dockerfile.api` - Builds the FastAPI backend service
- Uses Docker for consistent, reliable builds

### 2. **Updated railway.json**
- Changed `builder` from `"nixpacks"` to `"dockerfile"`
- Specifies `dockerfile: "Dockerfile.api"`
- Explicitly defines all environment variables

### 3. **New Configuration Files**
- `railway.worker.json` - Configuration for Celery worker service
- `frontend/railway.json` - Configuration for React frontend service
- `.nixpacks` - Prevents Nixpacks fallback

---

## 🚀 New Deployment Instructions

### **Step 1: Create Railway Project**

1. Go to https://railway.app
2. Click "New Project"
3. Connect your GitHub repository (ai__video__editor)
4. Railway should detect the railway.json configuration

### **Step 2: Deploy API Service (Main Deployment)**

1. Railway will automatically detect and deploy using `Dockerfile.api`
2. Wait for build to complete (~5-10 minutes)
3. Once deployed, note the API URL (e.g., `https://api-production-xxxx.railway.app`)

### **Step 3: Add PostgreSQL Database**

1. In Railway project, click "Add"
2. Select "Add Service" → "Database" → "PostgreSQL"
3. Wait for PostgreSQL to start
4. Copy the `DATABASE_URL` provided by Railway
5. **Go to API service settings** → Environment → Add `DATABASE_URL` variable
6. Paste PostgreSQL URL

### **Step 4: Add Redis Cache**

1. In Railway project, click "Add"
2. Select "Add Service" → "Database" → "Redis"
3. Wait for Redis to start
4. Copy the Redis URL
5. **Go to API service settings** → Environment → Add `REDIS_URL` variable
6. Paste Redis URL

### **Step 5: Configure S3 Storage**

**Option A: AWS S3**
1. Go to AWS console → S3
2. Create a new bucket (e.g., `video-editor-prod`)
3. Create an IAM user with S3 access
4. Get Access Key and Secret Key
5. Go to API service settings → Environment → Add:
   - `S3_ENDPOINT`: `https://s3.amazonaws.com`
   - `S3_ACCESS_KEY`: Your AWS access key
   - `S3_SECRET_KEY`: Your AWS secret key
   - `S3_BUCKET`: `video-editor-prod`
   - `S3_REGION`: (e.g., `us-west-2`)
   - `S3_SECURE`: `true`

**Option B: Backblaze B2**
1. Go to Backblaze B2 console
2. Create a new bucket (e.g., `video-editor-prod`)
3. Create application key
4. Go to API service settings → Environment → Add:
   - `S3_ENDPOINT`: `https://s3.us-west-000.backblazeb2.com`
   - `S3_ACCESS_KEY`: Your B2 application key ID
   - `S3_SECRET_KEY`: Your B2 application key
   - `S3_BUCKET`: `video-editor-prod`
   - `S3_REGION`: `us-west-000`
   - `S3_SECURE`: `true`

### **Step 6: Configure Security**

1. Generate a secret key:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. Go to API service settings → Environment → Add:
   - `SECRET_KEY`: Paste generated key
   - `DEBUG`: `false` (for production)
   - `CORS_ORIGINS`: Your frontend URL (e.g., `https://yourdomain.com`)

### **Step 7: Deploy Worker Service**

1. Click "Add" → "GitHub Repo" → Select same repository
2. Click the new service and change it to listen to `railway.worker.json`
3. Or manually create a service:
   - Set root directory to `/`
   - Set build command: `docker build -f backend/Dockerfile -t worker .`
   - Set start command: `celery -A app.workers.celery_app worker --loglevel=info`
   - Add same `DATABASE_URL` and `REDIS_URL`
   - Add same S3 credentials

### **Step 8: Deploy Frontend Service**

1. Click "Add" → "GitHub Repo" → Select same repository
2. Make sure it uses `frontend/railway.json`
3. Or manually create a service:
   - Set root directory to `frontend`
   - Set build command: `npm run build`
   - Add `REACT_APP_API_URL`: `https://your-api-url.railway.app`
   - Add `NODE_ENV`: `production`

### **Step 9: Verify Deployment**

1. Check all services are running (green status)
2. Frontend URL: Click on frontend service → "View Deployment"
3. Test API:
   ```bash
   curl https://your-api-url/health
   ```
   Should return: `{"status": "ok"}`

4. Test frontend loads at frontend URL
5. Try creating an account and uploading a file

---

## 🔧 Troubleshooting Deployment

### Build Still Fails?

1. Check Railway logs:
   - Click service → "View Logs"
   - Look for error messages
   - Common issues:
     - Missing `requirements.txt`
     - Permission errors
     - Out of memory during build

2. Rebuild:
   - Click service → Click "..." menu → "Redeploy"
   - Or push new commit to trigger rebuild

### Services Can't Connect?

1. Verify environment variables:
   - API service has `DATABASE_URL`, `REDIS_URL`, S3 keys
   - Worker service has same DATABASE_URL, REDIS_URL, S3 keys
   - Frontend has `REACT_APP_API_URL`

2. Test connectivity:
   - SSH into API service (if available)
   - Test database: `psql $DATABASE_URL -c "SELECT 1"`
   - Test Redis: `redis-cli -u $REDIS_URL ping`

### Videos Not Processing?

1. Check worker logs:
   - Worker service → "View Logs"
   - Look for Celery task errors

2. Verify S3 credentials:
   - Test by uploading a file
   - Check if file appears in S3 bucket

3. Ensure worker is running:
   - Worker service status should be green
   - Check memory usage (might need more resources)

---

## 📊 Resource Recommendations

### For Production:

| Service | Resource | Notes |
|---------|----------|-------|
| API | 512MB RAM | Handles requests, ~50-100 concurrent |
| Worker | 1GB RAM | Video processing intensive |
| PostgreSQL | 256MB RAM | Database queries, cache |
| Redis | 128MB RAM | Message broker, caching |
| Frontend | 256MB RAM | Static serving, edge caching |

### Scale Worker for More Concurrency:

1. Worker service → "Settings"
2. Increase RAM to 2GB for processing 2+ videos simultaneously
3. Increase replicas if needed (though Celery handles queue)

---

## 🎯 Next Steps After Deployment

1. **Set Custom Domain** (Optional):
   - Railway Dashboard → Project Settings
   - Add custom domain
   - Update DNS records
   - Frontend and API should have different domains if possible

2. **Enable Monitoring**:
   - Check Railway dashboard for resource usage
   - Set up alerts for failures
   - Monitor logs regularly

3. **Backup Database**:
   - Enable automated backups in PostgreSQL service
   - Set retention to 7-30 days

4. **Test End-to-End**:
   1. Create account
   2. Create project
   3. Upload test video
   4. Enter prompt (e.g., "30 second fast montage")
   5. Click "Generate"
   6. Monitor worker logs
   7. Download output

---

## 📝 Important Notes

- **First build takes 5-10 minutes** - Dependencies being downloaded and compiled
- **Subsequent builds are faster** - Docker caches layers
- **Worker might need tuning** - Adjust Celery settings based on video sizes
- **S3 costs** - Monitor usage to avoid unexpected bills
- **Database backups** - Enable automatic backups immediately

---

## ✅ Deployment Checklist

- [ ] Repository pushed to GitHub
- [ ] Docker build works locally (test with `docker build -f Dockerfile.api .`)
- [ ] railway.json uses "dockerfile" builder
- [ ] Dockerfile.api exists in project root
- [ ] PostgreSQL database added and DATABASE_URL set
- [ ] Redis cache added and REDIS_URL set
- [ ] S3 bucket created and credentials added
- [ ] SECRET_KEY generated and added
- [ ] CORS_ORIGINS set to frontend URL
- [ ] Worker service configured with Celery command
- [ ] Frontend service has REACT_APP_API_URL set
- [ ] All services are running (green status)
- [ ] API health check returns {"status": "ok"}
- [ ] Frontend loads and is accessible
- [ ] Test registration and login work
- [ ] Test video upload and processing

---

All set! Your Railway deployment should now work perfectly. 🚀
