import os

from celery import Celery
from celery.schedules import crontab
from dbt_copilot_python.celery_health_check import healthcheck


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

celery_app = Celery("DjangoCelery")
celery_app = healthcheck.setup(celery_app)
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()

celery_app.conf.beat_schedule = {
    "ingest_countries": {
        "task": "core.tasks.ingest_countries",
        "schedule": crontab(minute=0, hour=8),
    },
}
