from typing import Type

from .base import Service
from .error import ElmaError

import json
import requests


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


def _check_service(obj: Service | Type) -> bool:
    return isinstance(obj, Service) or hasattr(obj, "session") and hasattr(obj, "host")


def post(url: str):
    """
    Декоратор на метод объекта. Помечает метод объекта как POST-запрос на прописанный ``url``. Объект должен быть
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
        TypeError: если декорируемый метод не является методом объекта класса Service или же объекта с параметрами
                   session и host.
    """

    # noinspection PyMissingOrEmptyDocstring
    def decorator(func):
        # noinspection PyMissingOrEmptyDocstring
        def wrapper(self, *args, data: dict | None = None, uri: str | None = None, **kwargs):
            if not _check_service(self):
                raise TypeError(
                    '"post" can only work from Service instances or from objects with session and host attributes'
                )

            if data is None:
                data = {}

            uri = uri if uri else url

            if uri.startswith("http://") or uri.startswith("https://"):
                path = uri
            else:
                path = f"{self.host}/{uri.lstrip('/')}"

            session: requests.Session = self.session

            result = session.post(path, data=json.dumps(data, ensure_ascii=False).encode("utf-8"))

            if result.status_code == 500:
                raise ElmaError(result.text)

            return func(self, result, *args, **kwargs)

        return wrapper

    return decorator


def get(url: str):
    """
    Декоратор на метод объекта. Помечает метод объекта как GET-запрос на прописанный ``url``. Объект должен быть
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
        TypeError: если декорируемый метод не является методом объекта класса Service или же объекта с параметрами
                   session и host.
    """

    # noinspection PyMissingOrEmptyDocstring
    def decorator(func):
        # noinspection PyMissingOrEmptyDocstring
        def wrapper(self, *args, params: dict | None = None, uri: str | None = None, **kwargs):
            if not _check_service(self):
                raise TypeError(
                    '"get" can only work from Service instances or from objects with session and host attributes'
                )

            session: requests.Session = self.session

            uri = uri if uri else url

            if uri.startswith("http://") or uri.startswith("https://"):
                path = uri
            else:
                path = f"{self.host}/{uri.lstrip('/')}"

            if params:
                path += "?" + "&".join(f"{k}={v}" for k, v in params.items())

            result = session.get(path)

            if result.status_code == 500:
                raise ElmaError(result.text)

            return func(self, result, *args, **kwargs)

        return wrapper

    return decorator
