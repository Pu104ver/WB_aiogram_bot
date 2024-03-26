from celery import Celery

app = Celery(main="telegram_bot", broker='redis://localhost:6379')

app.autodiscover_tasks()
