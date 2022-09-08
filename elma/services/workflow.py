from typing import TYPE_CHECKING

from . import base, decorators
from ..structure import Parser

if TYPE_CHECKING:
    from requests import Response


START_PROCESS_ASYNC = "/API/REST/Workflow/StartProcessAsync"
STARTABLE_PROCESSES = "/API/REST/Workflow/StartableProcesses"


class WorkflowService(base.Service):
    """Сервис для работы с процессами"""

    @decorators.needs_auth
    @decorators.post(url=START_PROCESS_ASYNC)
    def _start_process(self, result: "Response") -> dict:
        """Стандартная функция API элмы для запуска процесса.

        На вход необходимо передать словарь. Для конкретизации процесса в словаре должен быть один из двух следующих
        параметров:
            - ProcessHeaderId: Id заголовка процесса
            - ProcessToken: токен запуска процесса (находится в параметрах запуска в дизайнере)

        Помимо этого, в словарь необходимо положить контекст процесса Context.

        Args:
            result: результат запуска процесса (передается декоратором автоматически)

        Returns:
            dict: нормализованный словарь результата запуска процесса

        Examples:
            Запуск процесса с заголовком id=1 с передачей в контекст значения "value" в параметр ContextParameter

                result = StartProcess({"ProcessHeaderId": 1, "Context": {"ContextParameter": "value"}})
        """
        return Parser.normalize(result.json())

    @decorators.needs_auth
    @decorators.post(url=STARTABLE_PROCESSES)
    def StartableProcesses(self, result: "Response"):
        return Parser.normalize(result.json())

    def StartProcess(
        self, *, process_header: int = 0, process_token: str = "", process_name: str = "", context: dict | None = None
    ) -> dict:
        """Запуск процесса в элме. Выбор производится через Id заголовка процесса process_header или же через
        токен запуска процесса process_token. Если процесс в элме не имеет автоматическую генерацию наименований
        экземпляров, то необходимо передать параметр process_name.

        Args:
            process_header: заголовок процесса
            process_token: токен процесса
            process_name: наименование экземпляра процесса
            context: контекстные переменные процесса

        Returns:
            dict: результат запуска процесса

        Raises:
            ValueError: если не передан ни один из параметров process_header и process_token, или переданы оба
        """
        if (
            (not isinstance(process_header, int) or process_header < 1)
            and not process_token
            or process_token
            and process_header
        ):
            raise ValueError("Для запуска необходимо передать или process_header, или process_token")

        if process_token:
            data = {"ProcessToken": process_token}
        else:
            data = {"ProcessHeaderId": process_header}

        data["Context"] = context if context else {}

        # не создаем такой параметр вообще, если не задан process_name
        if process_name:
            data["ProcessName"] = process_name

        data = Parser.uglify(data)
        return self._start_process(data=data)
