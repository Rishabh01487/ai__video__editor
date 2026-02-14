"""Celery app module"""

from celery import Celery
from app.config import settings
import logging

logger = logging.getLogger(__name__)

celery_app = Celery(
    "video_editor",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)

logger.info("Celery app initialized")
