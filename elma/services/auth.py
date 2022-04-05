from .base import Service
from .decorators import needs_auth, get

from datetime import datetime
import requests


LOGIN_WITH = "/API/REST/Authorization/LoginWith"


class AuthService(Service):
    def LoginWithUserName(self, username, password, app_token) -> dict:
        headers = {"ApplicationToken": app_token, "Content-Type": "application/json; charset=utf-8"}

        session = requests.Session()
        session.headers = headers

        response = session.post(f"{self.host}/{LOGIN_WITH.lstrip('/')}", params={"username": username}, data=password)

        try:
            parsed = response.json()
            new_headers = {
                "ApplicationToken": app_token,
                "Content-Type": "application/json; charset=utf-8",
                "AuthToken": parsed["AuthToken"],
                "SessionToken": parsed["SessionToken"],
            }
            self.headers = new_headers
            return new_headers
        except requests.RequestException:
            raise ConnectionError(response.text)

    def ServerTime(self, session):
        pass
