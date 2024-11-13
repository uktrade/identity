from django.contrib.auth import get_user_model
from django.db import DatabaseError


class CheckDatabase:
    name = "database"

    def check(self):
        try:
            user = get_user_model()
            user.objects.all().exists()
            return True, ""
        except DatabaseError as e:
            return False, e


services_to_check = (CheckDatabase,)
