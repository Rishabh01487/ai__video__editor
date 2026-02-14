# AI-Powered Video Editing Platform

A complete, production-ready web application for AI-powered video editing. Users upload videos/images, provide text prompts describing desired edits, and the system automatically generates edited videos.

## Features

- **User Authentication**: JWT-based authentication with email registration/login
- **Project Management**: Create, edit, and manage video editing projects
- **Media Upload**: Upload videos and images with presigned S3 URLs
- **AI Video Analysis**:
  - Scene detection using PySceneDetect
  - Object detection using YOLOv8-nano
  - Rule-based prompt parsing for editing directives
- **Automatic Video Editing**:
  - Scene selection using dynamic programming
  - Visual filters (vintage, grayscale, sepia, etc.)
  - Speed modifications (slow motion, fast forward)
  - Background music integration
  - Video rendering with MoviePy + FFmpeg
- **Job Tracking**: Real-time job status with progress updates
- **Responsive UI**: React with Tailwind CSS for beautiful, responsive design

## Tech Stack

### Frontend
- React 18 with Functional Components & Hooks
- React Router for navigation
- Tailwind CSS for styling
- React Dropzone for file uploads
- Axios for API calls

### Backend
- FastAPI (Python 3.11)
- SQLAlchemy ORM
- Pydantic for validation
- JWT authentication
- PostgreSQL database
- Redis for caching & message broker
- Celery for async task processing

### AI/Video Processing
- PySceneDetect for scene detection
- YOLOv8-nano for object detection (~6 MB)
- MoviePy for video rendering
- FFmpeg for video processing
- Rule-based prompt parser (no LLM container for size efficiency)

### Infrastructure
- Docker & Docker Compose for local development
- Railway for production deployment
- S3-compatible object storage (MinIO locally, Backblaze B2 or AWS S3 on Railway)

## Project Structure

```
ai-video-editor-platform/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app
│   │   ├── config.py               # Configuration
│   │   ├── database.py             # Database setup
│   │   ├── models.py               # SQLAlchemy models
│   │   ├── schemas.py              # Pydantic schemas
│   │   ├── storage.py              # S3 client
│   │   ├── auth/
│   │   │   ├── jwt.py              # Tokenization
│   │   │   ├── routes.py           # Auth endpoints
│   │   │   └── dependencies.py     # Auth middleware
│   │   ├── projects/
│   │   │   └── routes.py           # Project endpoints
│   │   ├── assets/
│   │   │   └── routes.py           # Asset upload endpoints
│   │   ├── jobs/
│   │   │   └── routes.py           # Job status endpoints
│   │   └── ai_engine/
│   │       ├── scene_detector.py   # PySceneDetect wrapper
│   │       ├── object_tagger.py    # YOLOv8 wrapper
│   │       ├── prompt_parser.py    # Rule-based parser
│   │       ├── shot_selector.py    # DP-based selection
│   │       └── renderer.py         # MoviePy renderer
│   ├── workers/
│   │   ├── celery_app.py           # Celery configuration
│   │   └── tasks.py                # Edit job task
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                  # Backend image build
│   ├── .dockerignore
│   └── .env.example
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── Auth/Login.jsx
│   │   │   ├── Dashboard/
│   │   │   ├── ProjectEditor/Editor.jsx
│   │   │   ├── UploadZone/
│   │   │   ├── ProcessingStatus/
│   │   │   └── VideoPlayer/
│   │   ├── contexts/AuthContext.jsx
│   │   ├── hooks/useJobs.js
│   │   ├── services/api.js
│   │   ├── App.js
│   │   ├── index.js
│   │   └── index.css
│   ├── package.json
│   ├── tailwind.config.js
│   ├── Dockerfile
│   ├── .dockerignore
│   └── .env.example
├── docker-compose.yml              # Local development
├── railway.json                   # Railway deployment config
└── README.md
```

## Getting Started

### Prerequisites

- Docker & Docker Compose (for local development)
- Node.js 18+ (if running frontend locally without Docker)
- Python 3.11+ (if running backend locally without Docker)

### Local Development with Docker Compose

1. **Clone the repository**
   ```bash
   cd ai-video-editor-platform
   ```

2. **Create environment files**
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

3. **Start all services**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - MinIO Console: http://localhost:9001 (minioadmin/minioadmin)

### Creating Test User

1. Go to http://localhost:3000
2. Click "Sign Up" and create an account
3. You can now create projects and start editing videos

### Example Prompt

In the editor, try prompts like:
- "Create a 30-second fast-paced montage with upbeat music"
- "Make a vintage-style video, slow motion, with sepia filter"
- "Include only people, exclude cars, add background music"

## Database Setup

The backend automatically initializes the database on startup. If you need to manually reset:

```bash
# Drop all tables and recreate
docker-compose exec backend python -c "from app.database import init_db; init_db()"
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user

### Projects
- `POST /projects` - Create project
- `GET /projects` - List projects
- `GET /projects/{id}` - Get project
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project

### Assets
- `POST /assets/presigned-url` - Get S3 presigned URL
- `POST /assets/{project_id}` - Create asset record
- `GET /assets/project/{project_id}` - List project assets
- `DELETE /assets/{id}` - Delete asset

### Jobs
- `POST /jobs/start-edit` - Start editing job
- `GET /jobs/{id}` - Get job status
- `GET /jobs/project/{project_id}/latest` - Get latest job

## Deployment on Railway

### Prerequisites
- Railway account (https://railway.app)
- AWS S3 bucket OR Backblaze B2 account
- Git repository with this code

### Step 1: Prepare Environment Variables

Generate a secure secret key:
```python
import secrets
secrets.token_urlsafe(32)
```

### Step 2: Create Railway Services

1. **Database Service**
   - Add PostgreSQL plugin
   - Railway will provide `DATABASE_URL`

2. **Redis Service**
   - Add Redis plugin
   - Railway will provide `REDIS_URL`

3. **Backend API**
   - Repository: Your GitHub/GitLab repo
   - Root Directory: `backend`
   - Build Command: (leave default or use `pip install -r requirements.txt`)
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Environment variables:
     ```
     DATABASE_URL=<from PostgreSQL plugin>
     REDIS_URL=<from Redis plugin>
     SECRET_KEY=<generated key>
     S3_ENDPOINT=<your S3 or B2 endpoint>
     S3_ACCESS_KEY=<your access key>
     S3_SECRET_KEY=<your secret key>
     S3_BUCKET=video-editor
     S3_REGION=<your region>
     S3_SECURE=true
     CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
     ```

4. **Celery Worker**
   - Same repository as backend
   - Root Directory: `backend`
   - Build Command: (same as API)
   - Start Command: `celery -A app.workers.celery_app worker --loglevel=info`
   - Share environment variables with Backend service

5. **Frontend**
   - Repository: Your GitHub/GitLab repo
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Start Command: `nginx -g 'daemon off;'`
   - Environment variables:
     ```
     REACT_APP_API_URL=https://yourdomain-api.railway.app
     ```

### Step 3: Configure S3 Storage

#### Option A: AWS S3
1. Create S3 bucket
2. Create IAM user with S3 access
3. Set environment variables:
   ```
   S3_ENDPOINT=https://s3.amazonaws.com
   S3_ACCESS_KEY=<IAM access key>
   S3_SECRET_KEY=<IAM secret key>
   S3_REGION=us-west-2
   S3_SECURE=true
   ```

#### Option B: Backblaze B2 (recommended - free tier available)
1. Create B2 bucket
2. Create application key
3. Set environment variables:
   ```
   S3_ENDPOINT=https://s3.backblazeb2.com
   S3_ACCESS_KEY=<B2 app key ID>
   S3_SECRET_KEY=<B2 app key>
   S3_BUCKET=your-bucket-name
   S3_REGION=us-west-002
   S3_SECURE=true
   ```

### Step 4: Deploy

1. Push code to repository
2. Railway automatically deploys on push
3. Monitor build logs in Railway dashboard
4. Once deployed, access application at your custom domain

## Docker Image Sizes

The application is optimized for small Docker images:

- **Backend**: ~800 MB (python:3.11-slim + dependencies)
- **Frontend**: ~25 MB (nginx:alpine + React build)
- **Worker**: ~800 MB (shared with backend)
- **Total**: ~1.6 GB (all services)

### Size Optimization Techniques

- Multi-stage Docker builds
- `python:3.11-slim` base image (not full image)
- `nginx:alpine` for frontend
- YOLOv8-nano model (~6 MB) instead of larger variants
- No Ollama container (rule-based parser instead)
- `.dockerignore` to exclude unnecessary files
- `NullPool` database connections to avoid memory leaks

## Performance Tuning

### Backend
- Connection pooling: `NullPool` (stateless)
- Celery worker concurrency: 1 (for memory efficiency)
- Task timeout: 30 minutes

### Frontend
- Lazy loading of components
- Optimized Tailwind build
- Asset caching

### Database
- Connection timeout: 30 seconds
- Indexes on foreign keys

## Troubleshooting

### Celery Task Failures
Check worker logs:
```bash
docker-compose logs celery_worker
```

### Database Connection Issues
Verify PostgreSQL is running:
```bash
docker-compose logs postgres
```

### Video Processing Slow
- Check available CPU/memory
- YOLOv8 inference may be slow on low-end hardware
- Consider reducing sample frames in `object_tagger.py`

### S3 Upload Failures
- Verify bucket exists and is accessible
- Check IAM/auth key permissions
- Verify CORS configuration if applicable

## Testing

### Unit Tests
```bash
docker-compose exec backend pytest
```

### Integration Tests
```bash
docker-compose exec backend pytest -v
```

### Health Check
```bash
curl http://localhost:8000/health
```

## Security Considerations

1. **Secrets Management**: Use Railway secrets manager
2. **Database**: PostgreSQL with strong password
3. **S3 Credentials**: Never commit to git, use environment variables
4. **JWT**: Generate secure secret key
5. **CORS**: Configure specific origins only
6. **Input Validation**: Pydantic validates all inputs
7. **Rate Limiting**: Consider adding rate limiting in production

## Customization

### Adding More Filters
Edit `backend/app/ai_engine/renderer.py` and add methods like `_apply_cool_filter()`

### Changing AI Models
Replace YOLOv8-nano with other models in `backend/app/ai_engine/object_tagger.py`

### Custom Prompt Parsing
Extend `backend/app/ai_engine/prompt_parser.py` with more keywords and directives

### Frontend Styling
Modify `frontend/tailwind.config.js` for custom colors and styles

## Contributing

1. Create feature branch
2. Commit changes
3. Push and create pull request

## License

MIT License - see LICENSE file

## Support

For issues and questions:
1. Check existing GitHub issues
2. Create new issue with detailed reproduction steps
3. Include Docker version, OS, and relevant logs

## Future Enhancements

- [ ] Real-time preview during editing
- [ ] Multiple output format support (4K, social media sizes)
- [ ] Batch processing for multiple projects
- [ ] Advanced color grading
- [ ] Audio editing and effects
- [ ] Subtitle generation with AI
- [ ] Custom font overlays
- [ ] Transition effects library
- [ ] Webhook notifications for job completion
- [ ] Analytics and usage metrics

## Performance Metrics

- Average video processing time: 2-5 minutes (depends on video length and hardware)
- Memory usage per job: 500MB-1GB
- Maximum concurrent jobs: Limited by available resources
- API response time: <100ms for most endpoints

## Monitoring

Recommended monitoring tools for production:
- **Logs**: CloudWatch (AWS) or equivalent
- **Metrics**: Prometheus + Grafana
- **Uptime**: UptimeRobot or similar
- **Error Tracking**: Sentry or equivalent

---

**Last Updated**: February 2026
**Version**: 1.0.0
