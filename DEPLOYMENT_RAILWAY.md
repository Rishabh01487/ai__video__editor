# AI Video Editor - Deployment Guide for Railway

## Prerequisites

Before deploying to Railway, ensure you have:

1. **Railway Account** - Sign up at https://railway.app
2. **Git Repository** - Push your code to GitHub/GitLab
3. **S3 or B2 Account** - For object storage
4. **Domain Name** (optional) - For custom domains

## Step-by-Step Deployment

### 1. Prepare Your Repository

Push all code to your Git repository:

```bash
git init
git add .
git commit -m "Initial commit: AI Video Editor"
git push origin main
```

### 2. Create Railway Project

1. Log in to Railway dashboard
2. Click "New Project"
3. Select "Blank Project"
4. Name it "AI Video Editor"

### 3. Add PostgreSQL Database

1. In your project, click "+ Add"
2. Select "Database"
3. Choose "PostgreSQL"
4. Railway will auto-configure, copy the `DATABASE_URL` variable

### 4. Add Redis Service

1. Click "+ Add"
2. Select "Database"
3. Choose "Redis"
4. Railway will auto-configure, copy the `REDIS_URL` variable

### 5. Deploy Backend API

1. Click "+ Add"
2. Select "GitHub" or "GitLab" (connect your repository)
3. Configure:
   - **Name**: api
   - **Root Directory**: `backend`
   - **Build Command**: Leave default or use pip
   - **Start Command**: 
     ```
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```

4. Add Environment Variables:
   ```
   DATABASE_URL = (from PostgreSQL)
   REDIS_URL = (from Redis)
   SECRET_KEY = (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
   S3_ENDPOINT = https://s3.backblazeb2.com  (or AWS S3)
   S3_ACCESS_KEY = (from B2/AWS)
   S3_SECRET_KEY = (from B2/AWS)
   S3_BUCKET = video-editor
   S3_REGION = us-west-002  (for B2) or us-west-2 (for AWS)
   S3_SECURE = true
   CORS_ORIGINS = https://yourdomain.com,https://app.yourdomain.com
   ```

5. Deploy - Railway automatically builds on save

### 6. Deploy Celery Worker

1. Click "+ Add"
2. Select "GitHub" or "GitLab" (same repository)
3. Configure:
   - **Name**: worker
   - **Root Directory**: `backend`
   - **Build Command**: Leave default
   - **Start Command**: 
     ```
     celery -A app.workers.celery_app worker --loglevel=info
     ```

4. Copy all environment variables from API service
5. Link to same PostgreSQL and Redis services
6. Deploy

### 7. Deploy Frontend

1. Click "+ Add"
2. Select "GitHub" or "GitLab" (same repository)
3. Configure:
   - **Name**: web
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Start Command**: `nginx -g 'daemon off;'`

4. Add Environment Variable:
   ```
   REACT_APP_API_URL = https://api.yourdomain.com
   ```

5. Deploy

### 8. Configure S3 Storage

#### Option A: Backblaze B2 (Recommended)

1. Create B2 account at https://www.backblaze.com/b2
2. Create bucket:
   - Name: `video-editor` (or your choice)
   - Type: Private
   - Enable CORS (for file uploads)
   
3. Create application key:
   - Go to Account > App Keys
   - Create new app key with access to your bucket
   - Save: `Application Key ID` and `Application Key`

4. Configure Railway environment variables:
   ```
   S3_ENDPOINT = https://s3.backblazeb2.com
   S3_ACCESS_KEY = (App Key ID)
   S3_SECRET_KEY = (Application Key)
   S3_BUCKET = video-editor
   S3_REGION = us-west-002
   S3_SECURE = true
   ```

#### Option B: AWS S3

1. Create S3 bucket:
   - Region: us-west-2 (or your choice)
   - Block public access: Yes

2. Create IAM user for S3 access:
   - Go to IAM > Users > Create User
   - Attach policy: AmazonS3FullAccess
   - Create access key

3. Configure Railway environment variables:
   ```
   S3_ENDPOINT = https://s3.amazonaws.com
   S3_ACCESS_KEY = (IAM Access Key)
   S3_SECRET_KEY = (IAM Secret Key)
   S3_BUCKET = video-editor
   S3_REGION = us-west-2
   S3_SECURE = true
   ```

### 9. Configure Custom Domain (Optional)

1. In Railway project settings
2. Under "Domains"
3. Add your domain
4. Update DNS records as shown (CNAME)

### 10. Verify Deployment

1. **Check Backend**: `https://api.yourdomain.com/docs`
2. **Check Frontend**: `https://yourdomain.com`
3. **Check Health**: `https://api.yourdomain.com/health`

Run test requests:
```bash
# Register user
curl -X POST https://api.yourdomain.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"password123"}'

# Create project
curl -X POST https://api.yourdomain.com/projects \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Project"}'
```

## Monitoring

### View Logs

1. In Railway dashboard, select each service
2. Click "Logs" tab
3. Filter by time range

### Monitor Resources

1. In Railway dashboard
2. Check "Metrics" for:
   - CPU usage
   - Memory usage
   - Network traffic
3. Adjust resources if needed

## Troubleshooting

### Build Failures

Check build logs:
1. Select service
2. Click "Deployment" 
3. View build logs
4. Common issues:
   - Missing dependencies: Update requirements.txt
   - Wrong Python version: Specify in pyproject.toml or Dockerfile
   - Port conflicts: Use $PORT environment variable

### Runtime Errors

1. Check "Logs" tab
2. Look for error messages
3. Common issues:
   - Database connection: Verify DATABASE_URL
   - S3 credentials: Test manually
   - Missing environment variables: Add them in service settings

### Performance Issues

1. **Video Processing Slow**:
   - Add more memory to worker
   - Reduce sample frames in object detection
   - Use smaller model

2. **Database Slow**:
   - Check connection limits
   - Add database indexes
   - Scale up PostgreSQL

3. **Memory Leaks**:
   - Check Celery worker logs
   - Reduce task concurrency
   - Restart workers periodically

## Maintenance

### Regular Tasks

1. **Database Backup**:
   - Railway auto-backups daily
   - Export manually from Railway dashboard

2. **Monitor Logs**:
   - Check error logs weekly
   - Review performance metrics
   - Alert on failures

3. **Update Dependencies**:
   - Regularly update Python packages
   - Security patches first
   - Test in staging before production

### Database Management

Access PostgreSQL console:
```bash
# Via Railway CLI
railway database shell

# Or use pgAdmin for GUI management
```

## Cost Optimization

1. **Celery Worker**: Scale down when not in use
2. **Database**: Use smallest tier initially
3. **Storage**: Monitor S3/B2 usage
4. **Bandwidth**: Compress videos efficiently

## Scaling

As traffic grows:

1. **Add API Replicas**: In service settings, increase replicas
2. **Add Workers**: Deploy additional Celery workers
3. **Upgrade Database**: Increase PostgreSQL resources
4. **Cache**: Redis already configured
5. **CDN**: Consider CloudFlare for frontend

## Security Checklist

- [ ] Generate new SECRET_KEY
- [ ] Use strong database password
- [ ] Enable S3 bucket encryption
- [ ] Configure CORS properly
- [ ] Set up firewall rules
- [ ] Enable HTTPS only
- [ ] Rotate S3 credentials regularly
- [ ] Monitor access logs
- [ ] Set up alerts for errors

## Rollback

If deployment fails:

1. In Railway, go to the service
2. Click "Deployment"
3. Select previous working version
4. Click "Rewind to this Deployment"

## Support

For Railway-specific issues:
- Documentation: https://docs.railway.app
- Community: https://railway.app/forms/support
- Status: https://status.railway.app

---

**Deployment Complete!** 🎉

Your AI Video Editor is now live. Users can:
1. Register and login
2. Create projects
3. Upload videos/images
4. Generate edited videos with AI

Monitor the dashboard regularly and scale as needed.
