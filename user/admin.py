from django.contrib import admin

from user.models import User
from user.utils import StaffSSOUserS3Ingest


# # Register your models here.


@admin.register(User)
class SSOSyncUserAdmin(admin.ModelAdmin):
    actions = ["sync_sso_users"]

    @admin.action(description="Sync identity users with Staff SSO")
    def sync_sso_users(self, request, queryset) -> None:
        StaffSSOUserS3Ingest()
