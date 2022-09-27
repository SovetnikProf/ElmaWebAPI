# Elma Web-API Connector (ElmaWebAPI)

[![Project version](https://img.shields.io/pypi/v/elmawebapi.svg)](https://pypi.python.org/pypi/elmawebapi)

Библиотека, предоставляющая упрощенный способ взаимодействия с
[Web API Elma3](https://www.elma-bpm.ru/KB/article-5613.html) из python.


## Установка и использование

Для работы библиотеки необходим python версии 3.10 или выше.

```bash
pip install elmawebapi
```

Для доступа к серверу неоходимо при создании инстанса `ElmaAPI` указать ссылку на хост сервера Elma, имя и пароль
пользователя, от лица которого будут запрашиваться и отправляться данные, а также создать токен внешнего приложения.

Стоит учитывать, что ограничения на пользователя влияют и на получаемые через API данные, т.е. если пользователь
не имеет доступ к какому-либо объекту или процессу, то через API он так же не будет иметь к ним доступ.

Пример обновления наименования контрагента с Id равному 1:

```python
from elmawebapi import ElmaAPI

API = ElmaAPI(HOST, USERNAME, PASSWORD, APP_TOKEN)
API.EntityService.Update({"Name": "Тестовый контрагент"}, "1fb7545c-b103-44b1-9b01-dacb986db75d", 1)
```

где `HOST` — ссылка на сервер Elma, `USERNAME` — имя пользователя, `PASSWORD` — пароль пользователя,
`APP_TOKEN` — токен приложения, а `1fb7545c-b103-44b1-9b01-dacb986db75d` — UID типа объекта "Контрагент".

Поскольку постоянно копировать UIDы не очень удобно, можно воспользоваться хранилищем данных `Library`, скормив ему
ссылку на таблицу с типами данных (обычно она находится по адресу `‹Хост›/API/Help/Types`). Тогда этот же пример можно
переписать следующим образом:

```python
from elmawebapi import ElmaAPI, Library

Library.load_from_help(HOST)  # по умолчанию второй параметр равен "/API/Help/Types", т.е. ссылка на страницу
API = ElmaAPI(HOST, USERNAME, PASSWORD, APP_TOKEN)
API.EntityService.Update({"Name": "Тестовый контрагент"}, Library.uuids.Contractor, 1)
```

Таким образом, UIDы и кастомных объектов окажутся доступными из `Library`, и не надо будет вспоминать какой тип
представляет тот или иной uuid. Помимо этого, `Library` создается синглтоном при подключении библиотеки, т.е. единожды
добавив в него данные, они будут доступны в любой части проекта (технически — не синглтон, это инстанс класса
`LibraryClass`, подробнее можно почитать в [документации](docs/library.md#libraryclass)).

Для запуска процессов необходимо передать или _ProcessHeaderId_ процесса, или же его токен запуска:
```python
from elmawebapi import ElmaAPI

API = ElmaAPI(HOST, USERNAME, PASSWORD, APP_TOKEN)
API.WorkflowService.StartProcess(process_header=PHEADER, process_token=PTOKEN, process_name=PNAME, context=PCTX)
```

где `PHEADER` — _ProcessHeaderId_ процесса, `PTOKEN` — токен запуска процесса, `PNAME` — имя созданного экземпляра
процесса, `PCTX` — контекстные переменные. Для запуска необходимо передать _либо_ `process_header`, _либо_
`process_token`, но не оба сразу. Имя экземпляра процесса указывать необязательно, особенно если оно создается по
шаблону. `context` принимает в себя словарь вида `{"имя контекстной переменной": "значение"}`.

Опять же, вручную вести `ProcessHeaderId` и токены запуска не очень удобно, поэтому для этих целей тоже можно
использовать `Library`:
```python
from elmawebapi import ElmaAPI, Library

Library.register_process("MyProcess", header=PHEADER, token=PTOKEN)
API = ElmaAPI(HOST, USERNAME, PASSWORD, APP_TOKEN)
API.WorkflowService.StartProcess(
    process_header=Library.processes.MyProcess.header,
    process_token=Library.processes.MyProcess.token,
    process_name=PNAME,
    context=PCTX
)
```

Для хранения процесса необязательно указывать и токен, и id заголовка, можно указать что-то одно, тогда значение
второго будет равно `None`.

Поскольку Elma оперирует данными в формате `CLR: WebData`, то для их упрощения можно использовать `Parser`:

```python
from elmawebapi import ElmaAPI, Library, Parser

API = ElmaAPI(HOST, USERNAME, PASSWORD, APP_TOKEN)
# на самом деле Load возвращает уже нормализованный вариант, так что пример чисто для показа работы Parser
data = API.EntityService.Load(params={"type": Library.uuids.Contractor, "id": 1})
print(data)
# {"Items": [
#     {"Name": "Id", "Value": "1", "Data": None, "DataArray": []},
#     {"Name": "Name", "Value": "Тестовый контрагент", "Data": None, "DataArray": []},
#     ...
# ], "Value": ""}
data = Parser.normalize(data)
print(data)
# {"Id": "1", "Name": "Тестовый контрагент", ...}
```

Более детальное описание всех сервисов и вспомогательных утилит можно почитать в [документации](docs).
