from ninja import NinjaAPI

from scim.api import router as scim_router


api = NinjaAPI()

api.add_router("", scim_router)
