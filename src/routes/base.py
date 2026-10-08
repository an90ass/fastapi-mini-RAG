from fastapi import APIRouter ,Depends

from dependencies.SettingsDependency import get_app_settings

base_router = APIRouter(
    prefix="/api/v1/base",
    tags=["base"],
    responses={404: {"description": "Not found"}},


)

@base_router.get("/")
async def welcome(app_settings = Depends(get_app_settings)):
    
    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION
    return {"message": f"Welcome to {app_name} version {app_version}"}
