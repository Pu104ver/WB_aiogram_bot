from app.worker.celery import app as celery_app
from . import tasks

__all__ = ('celery_app',)
