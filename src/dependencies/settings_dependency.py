from fastapi import Depends
from helpers.config import get_settings, Settings


def get_app_settings(settings: Settings = Depends(get_settings)):
    return settings