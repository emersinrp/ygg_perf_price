import requests
from config import settings

def get_token():
    data = {
        "client_id": settings.CLIENT_ID,
        "grant_type": "client_credentials",
        "client_secret": settings.CLIENT_SECRET_PRD,
        "scope": "openid"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(settings.TOKEN_URL, data=data, headers=headers)
    response.raise_for_status()
    return response.json().get("access_token")