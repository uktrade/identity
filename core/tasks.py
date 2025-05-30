from config.celery import celery_app
from core.utils import CountriesS3Ingest, SectorListS3Ingest, UkStaffLocationsS3Ingest


@celery_app.task()
def ingest_countries():
    CountriesS3Ingest()


@celery_app.task()
def ingest_uk_staff_locations():
    UkStaffLocationsS3Ingest()


@celery_app.task()
def ingest_sector_list():
    SectorListS3Ingest()
