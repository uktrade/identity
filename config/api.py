from ninja import NinjaAPI

from profiles.api import router as profiles_router
from user.api import router as user_router


api = NinjaAPI()


@api.get("/add")
def add(request, a: int, b: int):
    return {"result": a + b}


api.add_router("/profiles/", profiles_router)
api.add_router("/users/", user_router)
