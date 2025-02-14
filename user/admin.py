from django.contrib import admin

from core.utils import StaffSSOUserS3Ingest
from user.models import User


@admin.register(User)
class SSOSyncUserAdmin(admin.ModelAdmin):
    actions = ["sync_sso_users"]

    @admin.action(description="Sync identity users with Staff SSO")
    def sync_sso_users(self, request, queryset) -> None:
        StaffSSOUserS3Ingest()
