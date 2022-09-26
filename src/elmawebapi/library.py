from dataclasses import dataclass
from html.parser import HTMLParser

import requests


@dataclass(frozen=True)
class Process:
    """
    Данные о процессе.
    """

    header: int | None = None
    token: str | None = None


class LibraryClass:
    """
    Хранилище данных для взаимодействия с Elma.
    """

    uuids = (type("UUIDs", (object,), {}))()  # empty classes for depots
    processes = (type("Processes", (object,), {}))()  # empty classes for depotsи

    def register_uuid(self, name: str, uuid: str) -> None:
        """
        Зарегистрировать тип данных.

        Args:
            name: имя типа данных для доступа через uuids.<name>
            uuid: значение uuid
        """
        setattr(self.uuids, name, uuid)

    def register_process(self, name: str, *, header: int = None, token: str = None) -> None:
        """
        Зарегистрировать процесс.

        Args:
            name: имя процесса для доступа через processes.<name>
            header: ProcessHeaderId процесса
            token: токен запуска процесса

        Raises:
            ValueError: при передаче некорректных данных
        """
        if not isinstance(header, int) and not isinstance(token, str) or not header and not token:
            raise ValueError("Некорректные аргументы для регистрации процесса")

        setattr(self.processes, name, Process(header=header, token=token))

    def load_from_help(self, host: str, url: str = "API/Help/Types") -> None:
        """
        Загрузить типы данных со страницы Elma.

        Args:
            host: адрес сервера Elma
            url: адрес страницы со списком типов данных

        Raises:
            ConnectionError: при ошибке получения данных со страницы
        """
        address = f'{host.strip("/")}/{url.strip("/")}/'

        try:
            page = str(requests.get(address).content)
        except requests.RequestException as err:
            raise ConnectionError(f"Невозможно получить страницу по адресу {address}").with_traceback(err.__traceback__)

        class Parser(HTMLParser):
            """
            Парсер HTML для сохранения uid-ов и имен типов данных.
            """

            types = []
            current_uid = None

            def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
                if tag.lower() == "a":
                    href = [x[1] for x in attrs if x[0] == "href"][0]
                    href = href.replace(url, "")  # /API/Help/Type?uid=<uid> → ?uid=<uid>
                    self.current_uid = href.split("=")[-1]

            def handle_data(self, data: str) -> None:
                if self.current_uid is None:
                    return
                self.types.append((data, self.current_uid))
                self.current_uid = None

        parser = Parser()
        parser.feed(page)

        for name, uid in parser.types:
            self.register_uuid(name, uid)


Library = LibraryClass()
