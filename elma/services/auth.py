from . import base, decorators

from datetime import datetime
import requests


LOGIN_WITH = "/API/REST/Authorization/LoginWith"
SERVER_TIME = "/API/REST/Authorization/ServerTime"


class AuthService(base.Service):
    """
    Реализация сервиса авторизации IAuthorizationService.
    """

    def LoginWithUserName(self, username: str, password: str, app_token: str) -> dict:
        """
        Авторизоваться на сервере как приложение с токеном ``app_token`` под пользователем ``username``
        используя пароль ``password``.

        Args:
            username: имя пользователя
            password: пароль от пользователя
            app_token: токен приложения из настроек элмы

        Returns:
            dict: заголовки, используемые для последующих запросов

        Raises:
            AttributeError: если у сервиса не определен хост
            ConnectionError: при ошибке запроса на авторизацию
        """
        if not hasattr(self, "host"):
            raise AttributeError("AuthService has no host")

        headers = {"ApplicationToken": app_token, "Content-Type": "application/json; charset=utf-8"}

        session = requests.Session()
        session.headers = headers

        if not password.startswith('"') or not password.endswith('"'):
            password = f'"{password}"'

        response = session.post(f"{self.host}/{LOGIN_WITH.lstrip('/')}", params={"username": username}, data=password)
        session.close()

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

    @decorators.needs_auth
    @decorators.get(url=SERVER_TIME)
    def ServerTime(self, result: requests.Response) -> datetime:
        """
        Получить текущее серверное время.

        Returns:
            datetime: объект datetime с текущим локальным временем на сервере
        """
        # result.json() == "/Date(1234567890123+0300)/"
        time: str = result.json().strip("/").replace("Date(", "").replace(")", "")
        char = "+" if "+" in time else "-"
        ts, tz = time.split("+")

        ts = int(ts) / 1000.0  # python timestamp is 1234567890.123
        tz = datetime.strptime(f"{char}{tz}", "%z").tzinfo

        dt = datetime.fromtimestamp(ts, tz=tz)
        return dt
