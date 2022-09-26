from datetime import datetime
from json import JSONDecodeError

import requests

from . import base, decorators

LOGIN_WITH = "/API/REST/Authorization/LoginWith"
SERVER_TIME = "/API/REST/Authorization/ServerTime"
SERVER_TIME_UTC = "/API/REST/Authorization/ServerTimeUTC"


def _parse_time(server_response: str) -> datetime:
    time: str = server_response.strip("/").replace("Date(", "").replace(")", "")
    char = "+" if "+" in time else "-"
    try:
        ts, tz = time.split(char)
    except ValueError:
        ts, tz = time, "0000"

    ts = int(ts) / 1000.0  # python timestamp is 1234567890.123
    tz = datetime.strptime(f"{char}{tz}", "%z").tzinfo

    dt = datetime.fromtimestamp(ts, tz=tz)
    return dt


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
            ConnectionError: при ошибке запроса на авторизацию
            ValueError: ошибка авторизации
        """
        headers = {"ApplicationToken": app_token, "Content-Type": "application/json; charset=utf-8"}

        session = requests.Session()
        session.headers = headers

        if not password.startswith('"') or not password.endswith('"'):
            password = f'"{password}"'

        try:
            response = session.post(
                f"{self.parent.host}/{LOGIN_WITH.lstrip('/')}", params={"username": username}, data=password
            )
        except requests.ConnectionError as e:
            raise ConnectionError().with_traceback(e.__traceback__)
        finally:
            session.close()

        try:
            parsed = response.json()
            return {
                "ApplicationToken": app_token,
                "Content-Type": "application/json; charset=utf-8",
                "AuthToken": parsed["AuthToken"],
                "SessionToken": parsed["SessionToken"],
            }
        except JSONDecodeError:
            raise ValueError(f"Ошибка при декодировании json: {response.text}")  # pylint: disable=W0707
        except KeyError:
            raise ValueError("Невозможно авторизоваться с заданными параметрами")  # pylint: disable=W0707

    @decorators.needs_auth
    @decorators.get(url=SERVER_TIME)
    def ServerTime(self, result: requests.Response) -> datetime:
        """
        Получить текущее серверное время.

        Returns:
            datetime: объект datetime с текущим локальным временем на сервере
        """
        # result.json() == "/Date(1234567890123+0300)/"
        return _parse_time(result.json())

    @decorators.needs_auth
    @decorators.get(url=SERVER_TIME_UTC)
    def ServerTimeUTC(self, result: requests.Response) -> datetime:
        """
        Получить текущее серверное время в формате UTC.

        Returns:
            datetime: объект datetime с текущим локальным временем на сервере
        """
        # result.json() == "/Date(1234567890123+0300)/"
        return _parse_time(result.json())
