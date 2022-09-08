from typing import TYPE_CHECKING

from .error import ElmaError

import json
import requests

if TYPE_CHECKING:
    from .base import Service


def needs_auth(func):
    """
    Декоратор на метод объекта. Проверяет, что текущий объект имеет среди ``self.headers`` заголовок ``AuthToken``.
    Это означает, что текущий объект аутентифицирован на сервере Элмы.
    """

    def wrapper(self, *args, **kwargs):
        if not self.headers or not self.headers.get("AuthToken", None):
            raise ValueError("Требуется авторизация")
        return func(self, *args, **kwargs)

    return wrapper


def post(url: str):
    """
    Декоратор на метод сервиса. Помечает метод объекта как POST-запрос на прописанный ``url``. Сервис должен быть
    аутентифицирован в Элме: он должен иметь свойства ``session`` и ``host``.

    Декорируемый метод — это метод для **обработки** ответа на запрос, но вызываться он должен с данными для
    отправки через аргумент ``data``, который принимает словарь.

    Например, ::

        @post(url="/someurl/")
        def send_post(self, result: requests.Response, *args, **kwargs):
            return Parser.normalize(result.json())  # в самом методе обработка ответа result

        # но вызов с отправляемыми данными в data
        send_post(data={"data": "some info"})

    В этом примере json-строка ``'{"data": "some info"}'`` будет отправлена на "host/someurl/".

    Словарь отправляемых данных ``data`` будут автоматически преобразован в json-строку. ``args`` и ``kwargs`` будут
    переданы в метод обработки ответа.

    Результат ``result`` является объектом ``requests.Response``, из которого можно будет получить необходимую
    информацию.

    Помимо этого, можно изменить url отправления путем передачи в метод параметра ``uri``, например::

        @post(url="/someurl/")
        def send_post(self, result, *args, **kwargs):
            ...

        send_post(data={"data": "some_info"}, uri="/different/")

    В этом примере json-строка ``'{"data": "some info"}'`` будет отправлена на "host/different/".

    Это позволяет отправлять данные на адреса, которые заранее нельзя определить, например, url в которых прописан uid
    справочника в Элме.

    Args:
        url: url для отправки запроса.

    Raises:
        ElmaError: если запрос не отработал на сервере.
    """

    # noinspection PyMissingOrEmptyDocstring
    def decorator(func):
        # noinspection PyMissingOrEmptyDocstring
        def wrapper(self: "Service", *args, data: dict | None = None, uri: str | None = None, **kwargs):
            if data is None:
                data = {}

            uri = uri if uri else url

            if uri.startswith("http://") or uri.startswith("https://"):
                path = uri
            else:
                path = f"{self.host}/{uri.lstrip('/')}"

            retries = 0

            def repeat(datadict, url):
                nonlocal self, retries
                with self.session as session:
                    session: requests.Session
                    response = session.post(url, data=json.dumps(datadict, ensure_ascii=False).encode("utf-8"))

                if response.status_code != 200:
                    if (
                        response.status_code == 400
                        and '"StatusCode":401' in response.text
                        and retries < self.parent.settings.max_retries
                    ):
                        self.parent.headers = self.parent.reconnect()
                        retries += 1
                        return repeat(datadict, url)
                    raise ElmaError(response.text)
                return response

            result = repeat(data, path)

            return func(self, result, *args, **kwargs)

        return wrapper

    return decorator


def get(url: str):
    """
    Декоратор на метод сервиса. Помечает метод объекта как GET-запрос на прописанный ``url``. Сервис должен быть
    аутентифицирован в Элме: он должен иметь свойства ``session`` и ``host``.

    Декорируемый метод — это метод для **обработки** ответа на запрос, но вызываться он может с данными для
    запроса через аргумент ``params``, который принимает словарь.

    Например, ::

        @get(url="/someurl/")
        def send_get(self, result: requests.Response, *args, **kwargs):
            return Parser.normalize(result.json())  # в самом методе обработка ответа result

        # но вызов с отправляемыми данными в params
        send_get(params={"search": "SEARCH", "id": 1})

    В этом примере будет запрошена страница "host/someurl/?search=SEARCH&id=1".

    ``args`` и ``kwargs`` будут переданы в метод обработки ответа.

    Результат ``result`` является объектом ``requests.Response``, из которого можно будет получить необходимую
    информацию.

    Помимо этого, можно изменить url запроса путем передачи в метод параметра ``uri``, например::

        @get(url="/someurl/")
        def send_get(self, result, *args, **kwargs):
            ...

        send_get(params={"search": "SEARCH", "id": 1}, uri="/different/")

    В этом примере будет запрошена страница "host/different/?search=SEARCH&id=1".

    Это позволяет запрашивать данные с адресов, которые заранее нельзя определить, например, url в которых прописан uid
    справочника в Элме.

    Args:
        url: url для отправки запроса.

    Raises:
        ElmaError: если запрос не отработал на сервере.
    """

    # noinspection PyMissingOrEmptyDocstring
    def decorator(func):
        # noinspection PyMissingOrEmptyDocstring
        def wrapper(self: "Service", *args, params: dict | None = None, uri: str | None = None, **kwargs):
            uri = uri if uri else url

            if uri.startswith("http://") or uri.startswith("https://"):
                path = uri
            else:
                path = f"{self.host}/{uri.lstrip('/')}"

            if params:
                path += "?" + "&".join(f"{k}={v}" for k, v in params.items())

            retries = 0

            def repeat(url):
                nonlocal self, retries
                with self.session as session:
                    session: requests.Session
                    response = session.get(url)

                if response.status_code != 200:
                    if (
                        response.status_code == 400
                        and '"StatusCode":401' in response.text
                        and retries < self.parent.settings.max_retries
                    ):
                        self.parent.headers = self.parent.reconnect()
                        retries += 1
                        return repeat(url)
                    raise ElmaError(response.text)
                return response

            result = repeat(path)

            return func(self, result, *args, **kwargs)

        return wrapper

    return decorator
