from config.celery import celery_app
from core.utils import UkStaffLocationsS3Ingest


@celery_app.task(bind=True)
def ingest_uk_staff_locations(self):
    UkStaffLocationsS3Ingest()
