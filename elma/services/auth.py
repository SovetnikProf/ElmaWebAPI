from .base import Service
from .decorators import needs_auth, get

from datetime import datetime
import requests


LOGIN_WITH = "/API/REST/Authorization/LoginWith"
SERVER_TIME = "/API/REST/Authorization/ServerTime"


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

    @needs_auth
    @get(url=SERVER_TIME)
    def ServerTime(self, result: requests.Response) -> datetime:
        # result.json() == "/Date(1234567890123+0300)/"
        time: str = result.json().strip("/").replace("Date(", "").replace(")", "")
        char = "+" if "+" in time else "-"
        ts, tz = time.split("+")

        ts = int(ts) / 1000.0  # python timestamp is 1234567890.123
        tz = datetime.strptime(f"{char}{tz}", "%z").tzinfo

        dt = datetime.fromtimestamp(ts, tz=tz)
        return dt
