from config.celery import celery_app
from core.utils import CountriesS3Ingest


@celery_app.task(bind=True)
def ingest_countries(self):
    CountriesS3Ingest()
