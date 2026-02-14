#!/bin/bash
# Database management script

set -e

DB_CONTAINER="video-editor-postgres"
DB_USER="video_editor"
DB_NAME="video_editor"

case "$1" in
    init)
        echo "📦 Initializing database..."
        docker-compose exec backend python -c "from app.database import init_db; init_db()"
        echo "✅ Database initialized"
        ;;
    reset)
        echo "⚠️  Resetting database (deleting all data)..."
        read -p "Are you sure? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose exec postgres psql -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS jobs CASCADE;"
            docker-compose exec postgres psql -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS assets CASCADE;"
            docker-compose exec postgres psql -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS projects CASCADE;"
            docker-compose exec postgres psql -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS users CASCADE;"
            echo "📦 Reinitializing database..."
            docker-compose exec backend python -c "from app.database import init_db; init_db()"
            echo "✅ Database reset complete"
        else
            echo "❌ Cancelled"
        fi
        ;;
    backup)
        echo "💾 Backing up database..."
        docker-compose exec postgres pg_dump -U $DB_USER -d $DB_NAME > backup_$(date +%Y%m%d_%H%M%S).sql
        echo "✅ Backup created"
        ;;
    *)
        echo "Usage: $0 {init|reset|backup}"
        echo "  init   - Initialize database tables"
        echo "  reset  - Reset database (WARNING: deletes all data)"
        echo "  backup - Create database backup"
        exit 1
        ;;
esac
