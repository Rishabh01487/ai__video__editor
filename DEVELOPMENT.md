# Development Environment Configuration

## System Requirements

### Minimum Specifications
- CPU: 4 cores (8+ recommended for video processing)
- RAM: 8 GB (16+ for smooth video processing)
- Storage: 50 GB free (for Docker images and video files)
- OS: Linux, macOS, or Windows with WSL 2

### Software Requirements
- Docker 20.10+
- Docker Compose 2.0+
- Git
- (Optional) Node.js 18+ for frontend development
- (Optional) Python 3.11+ for backend development

## Local Development Setup

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd ai-video-editor-platform
```

### 2. Configure Environment Variables

```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env
```

Edit `.env` files with your settings:

**backend/.env**:
```
DATABASE_URL=postgresql://video_editor:password123@postgres:5432/video_editor
REDIS_URL=redis://redis:6379/0
DEBUG=true
SECRET_KEY=dev-secret-key-min-32-chars-change-in-production-!!!
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=video-editor
S3_REGION=us-east-1
S3_SECURE=false
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

**frontend/.env**:
```
REACT_APP_API_URL=http://localhost:8000
```

### 3. Start Services

```bash
# Using docker-compose
docker-compose up -d

# Or using make
make up
```

### 4. Initialize Database

```bash
# Using make
make db-init

# Or using docker-compose directly
docker-compose exec backend python -c "from app.database import init_db; init_db()"
```

### 5. Access Applications

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)

## IDE Configuration

### VS Code Extensions (Recommended)

Backend Development:
- Python
- Pylint
- Python Docstring Generator
- FastAPI
- SQLAlchemy

Frontend Development:
- ES7+ React/Redux/React-Native snippets
- Tailwind CSS IntelliSense
- Prettier - Code formatter
- ESLint

### PyCharm Settings

1. **Python Interpreter**:
   - Settings > Project > Python Interpreter
   - Set to Docker Compose (backend service)

2. **Run Configurations**:
   - Add FastAPI configuration pointing to `app/main.py`

### VS Code Launch Configuration

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": true
    }
  ]
}
```

## Backend Development

### Project Structure

```
backend/
├── app/                    # Main application
│   ├── main.py            # FastAPI entry point
│   ├── config.py          # Settings
│   ├── database.py        # SQLAlchemy setup
│   ├── models.py          # Database models
│   ├── schemas.py         # Pydantic schemas
│   ├── storage.py         # S3 client
│   ├── auth/              # Authentication
│   ├── projects/          # Project management
│   ├── assets/            # Media management
│   ├── jobs/              # Job management
│   └── ai_engine/         # Video processing
├── workers/               # Celery tasks
└── tests/                 # Unit tests
```

### Running Tests

```bash
# All tests
docker-compose exec backend pytest

# Specific test file
docker-compose exec backend pytest tests/test_auth.py

# With coverage
docker-compose exec backend pytest --cov=app tests/

# Watch mode (requires pytest-watch)
docker-compose exec backend ptw
```

### Code Style

```bash
# Format code
docker-compose exec backend black app/

# Sort imports
docker-compose exec backend isort app/

# Lint
docker-compose exec backend flake8 app/

# Type checking
docker-compose exec backend mypy app/
```

### Adding Dependencies

```bash
# Add to requirements.txt, then rebuild
docker-compose build backend
docker-compose up -d backend
```

### Database Management

```bash
# Initialize tables
make db-init

# Reset (WARNING: deletes all data)
make db-reset

# Backup
make db-backup

# Interactive shell
docker-compose exec postgres psql -U video_editor -d video_editor
```

### Running Celery Worker

Already running in docker-compose. To debug:

```bash
# View worker logs
docker-compose logs -f celery_worker

# Restart worker
docker-compose restart celery_worker

# Run in foreground for debugging
docker-compose run --rm celery_worker
```

## Frontend Development

### Project Structure

```
frontend/
├── public/                # Static files
├── src/
│   ├── components/        # React components
│   ├── contexts/          # Context API
│   ├── hooks/             # Custom hooks
│   ├── services/          # API client
│   ├── App.js             # Main component
│   └── index.js           # Entry point
├── package.json
└── tailwind.config.js
```

### Running Locally (Without Docker)

```bash
cd frontend
npm install
npm start  # Runs on http://localhost:3000
```

### Building

```bash
# Development build (with sourcemaps)
npm run build

# Production build
npm run build && npm start
```

### Component Development

1. Create component file: `src/components/MyComponent/MyComponent.jsx`
2. Create CSS module: `src/components/MyComponent/MyComponent.module.css`
3. Use Tailwind utilities in JSX
4. Export from component folder: `src/components/MyComponent/index.jsx`

### Adding Dependencies

```bash
# Inside frontend container
docker-compose exec frontend npm install package-name

# Or locally
cd frontend && npm install package-name
```

### Hot Reload

Both frontend and backend are configured for hot reload in docker-compose.yml. Changes automatically reload.

## Debugging

### Backend Debugging

Using VSCode debugger with pdb:

```python
# In your code
import pdb; pdb.set_trace()

# Or use breakpoint() in Python 3.7+
breakpoint()
```

Then access the container:
```bash
docker-compose exec backend python
```

### Frontend Debugging

Use React DevTools Chrome extension:
1. Install extension
2. Open http://localhost:3000
3. Press F12 to open DevTools
4. React tab shows component tree

### API Debugging

Use the interactive docs:
1. http://localhost:8000/docs (Swagger UI)
2. http://localhost:8000/redoc (ReDoc)

Or use curl/Postman:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"user","password":"password123"}'
```

### Container Debugging

```bash
# View logs
docker-compose logs [service-name] -f

# Execute command in container
docker-compose exec [service-name] [command]

# Interactive shell
docker-compose exec [service-name] bash

# View service status
docker-compose ps

# Inspect service
docker-compose exec [service-name] env
```

## Cleanup

### Remove Everything

```bash
# Stop containers and remove volumes
docker-compose down -v

# Remove unused Docker resources
docker system prune -a
```

### Remove Specific Service

```bash
# Stop and remove specific service
docker-compose rm -f [service-name]
```

### Clean Build Cache

```bash
# Rebuild without cache
docker-compose build --no-cache
```

## Performance Optimization

### Local Development

1. **Use FastAPI reload**: Already enabled in docker-compose.yml
2. **Disable debug logging**: Set DEBUG=false in .env
3. **Increase Docker resources**: 
   - Docker Desktop > Preferences > Resources
   - Set CPU and Memory appropriately

### Database

1. **Enable query logging**: `echo = True` in SQLAlchemy
2. **Create indexes**: `db.session.execute(text("CREATE INDEX ..."))`
3. **Monitor connections**: `SELECT * FROM pg_stat_activity`

### Video Processing

1. **Reduce frame samples**: Modify `sample_frames` in object_tagger.py
2. **Use GPU acceleration**: Configure Docker to use GPU
3. **Increase worker memory**: Modify docker-compose.yml

## Common Issues

### Port Already in Use

```bash
# Find what's using the port
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Database Connection Refused

```bash
# Check if postgres is running
docker-compose ps postgres

# Restart postgres
docker-compose restart postgres

# Wait for postgres to be healthy
docker-compose exec postgres pg_isready -U video_editor
```

### Celery Task Not Running

```bash
# Check worker logs
docker-compose logs celery_worker

# Check Redis connection
docker-compose exec redis redis-cli ping

# Restart worker
docker-compose restart celery_worker
```

### Frontend Not Loading

```bash
# Check frontend logs
docker-compose logs frontend

# Clear browser cache and reload
Ctrl + Shift + Delete (Chrome DevTools > Clear browsing data)
```

### Out of Memory

```bash
# Increase Docker memory limit
# Docker Desktop > Preferences > Resources > Memory

# Or cleanup old containers/images
docker system prune -a
```

## Useful Commands

```bash
# Database
make db-init          # Initialize database
make db-reset         # Reset database
make db-backup        # Backup database

# Services
make up               # Start all services
make down             # Stop all services
make logs             # View logs
make build            # Rebuild images

# Code Quality
make format           # Format code (black, isort)
make lint             # Lint code
make test             # Run tests

# Development
make api-shell        # Shell in API container
make backend-shell    # Python shell in backend
```

## Next Steps

1. Read the main [README.md](README.md)
2. Follow [API documentation](http://localhost:8000/docs)
3. Check [deployment guide](DEPLOYMENT_RAILWAY.md) for production
4. Explore test files for code examples

---

**Happy Coding!** 🚀
