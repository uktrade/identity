from ninja import Router
from ninja.security import HttpBearer, SessionAuth

from .models.models import User


router = Router()


class AuthUser(HttpBearer):
    def authenticate(self, request, token):
        if token == "supersecret":
            return token


@router.post("/add")
def add_user(request, username: str):
    user = User.objects.create_user(username=username)
    return {"user": user.username}


@router.get("/all", auth=AuthUser())
def show_users(request):
    users = User.objects.all()
    return {"users": [{"id": user.id, "username": user.username} for user in users]}
