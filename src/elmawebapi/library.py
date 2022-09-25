from html.parser import HTMLParser

from dataclasses import dataclass
import requests


@dataclass(frozen=True)
class Process:
    header: int | None = None
    token: str | None = None


class LibraryClass:
    # empty classes for depots
    uuids = (type("UUIDs", (object,), {}))()
    processes = (type("Processes", (object,), {}))()

    def register_uuid(self, name: str, uuid: str) -> None:
        setattr(self.uuids, name, uuid)

    def register_process(self, name: str, *, header: int = None, token: str = None) -> None:
        if not header and not token:
            raise ValueError("Некорректные аргументы для регистрации процесса")

        setattr(self.processes, name, Process(header=header, token=token))

    def load_from_help(self, host, url: str = "API/Help/Types") -> None:
        address = f'{host.strip("/")}/{url.strip("/")}/'

        try:
            page = str(requests.get(address).content)
        except requests.RequestException as e:
            raise RuntimeError(f"Невозможно получить страницу по адресу {address}").with_traceback(e.__traceback__)

        class Parser(HTMLParser):
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
