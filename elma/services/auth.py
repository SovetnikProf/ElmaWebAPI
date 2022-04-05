import requests

from .common import Service


class AuthService(Service):
    def LoginWithUserName(self, username, password, app_token) -> dict:
        headers = {"ApplicationToken": app_token, "Content-Type": "application/json; charset=utf-8"}

        session = requests.Session()
        session.headers = headers

        response = session.post(
            f"{self.host}/API/REST/Authorization/LoginWith", params={"username": username}, data=password
        )

        try:
            parsed = response.json()
            new_headers = {
                "ApplicationToken": app_token,
                "Content-Type": "application/json; charset=utf-8",
                "AuthToken": parsed["AuthToken"],
                "SessionToken": parsed["SessionToken"],
            }
            self.headers = new_headers
            return headers
        except requests.RequestException:
            raise ConnectionError(response.text)

    def ServerTime(self, session):
        pass
