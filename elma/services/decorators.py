from .base import Service

import json
import requests


def needs_auth(func):
    def wrapper(self, *args, **kwargs):
        if not self.headers or not self.headers.get("AuthToken", None):
            raise ValueError("Требуется авторизация")
        return func(self, *args, **kwargs)

    return wrapper


def post(url: str):  # decorator with args
    def decorator(func):  # actual decorator
        def wrapper(self, data: dict, *args, **kwargs):  # func caller
            # needs data dict to send to given url

            # check if self is service, so we can use self.session and self.host
            if not isinstance(self, Service) or not (hasattr(self, "session") and hasattr(self, "host")):
                raise TypeError(
                    '"post" can only work from Service instances or from objects with session and host attributes'
                )
            # get new requests.Session with correct headers
            session: requests.Session = self.session
            # get result from host
            # NOTE: json.dumps is executing here, no need to pass string to data
            result = session.post(f"{self.host}/{url.lstrip('/')}", data=json.dumps(data))

            return func(self, result, *args, **kwargs)

        return wrapper

    return decorator


def get(url: str):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if not isinstance(self, Service):
                raise TypeError('"post" can only work from Service instances')
            session: requests.Session = self.session
            result = session.get(f"{self.host}/{url.lstrip('/')}")

            return func(self, result, *args, **kwargs)

        return wrapper

    return decorator
