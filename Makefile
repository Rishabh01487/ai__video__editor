# Makefile for AI Video Editor

.PHONY: help up down logs build test db-reset db-backup clean

help:
	@echo "Available commands:"
	@echo "  make up          - Start all services with docker-compose"
	@echo "  make down        - Stop all services"
	@echo "  make logs        - View logs from all services"
	@echo "  make build       - Build all Docker images"
	@echo "  make api-shell   - Open shell in API container"
	@echo "  make db-init     - Initialize database"
	@echo "  make db-reset    - Reset database (WARNING: deletes data)"
	@echo "  make db-backup   - Backup database"
	@echo "  make test        - Run tests"
	@echo "  make clean       - Clean up Docker containers and volumes"
	@echo "  make seed        - Seed database with demo data"

up:
	docker-compose up -d
	@echo "✅ Services running at:"
	@echo "   Frontend: http://localhost:3000"
	@echo "   API: http://localhost:8000"
	@echo "   Docs: http://localhost:8000/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f

build:
	docker-compose build --no-cache

api-shell:
	docker-compose exec backend bash

backend-shell:
	docker-compose exec backend python

db-init:
	docker-compose exec backend python -c "from app.database import init_db; init_db()"
	@echo "✅ Database initialized"

db-reset: | down up
	@echo "Waiting for services..."
	sleep 5
	docker-compose exec backend python -c "from app.database import init_db; init_db()"
	@echo "✅ Database reset"

db-backup:
	docker-compose exec postgres pg_dump -U video_editor -d video_editor > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Database backed up"

test:
	docker-compose exec backend pytest -v

test-watch:
	docker-compose exec backend pytest -v --looponfail

clean:
	docker-compose down -v
	@echo "✅ Cleaned up"

seed:
	docker-compose exec backend python scripts/seed_data.py
	@echo "✅ Database seeded with demo data"

format:
	docker-compose exec backend black app/
	docker-compose exec backend isort app/

lint:
	docker-compose exec backend flake8 app/
	docker-compose exec backend mypy app/

install-deps-dev:
	cd backend && pip install -r requirements-dev.txt
	cd frontend && npm install

.DEFAULT_GOAL := help
