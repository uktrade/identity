from config.celery import celery_app
from core.utils import CountriesS3Ingest


@celery_app.task()
def ingest_countries():
    CountriesS3Ingest()
