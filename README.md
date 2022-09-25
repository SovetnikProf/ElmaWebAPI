# Elma Web-API Connector

Сервис, предоставляющий API для связи с системой Elma.

## Описание API


### structure.py

Преобразования структур WebAPI Elma: _Item_, _Data_ и _DataArray_ в обычные словари и обратно.

Структуры представляют собой следующее:

- _Item_: словарь с наименованием _Name_ и тремя параметрами под значения — _Value_, _Data_ и _DataArray_:
  ```python
  Item = {"Name": "Наименование", "Value": "Значение", "Data": None, "DataArray": []}
  ```
  _Value_ может принимать какое-либо значение "стандартных" типов — число, строка или булева, пустым значением 
  считается пустая строка. _Data_ может принимать значение типа _Data_, пустым значением считается `None`.
  _DataArray_ может принимать значение типа _DataArray_, пустым значением считается пустой массив.
- _Data_: словарь со списком объектов _Item_ и значением _Value_:
  ```python
  Data = {
    "Items": [{"Name": "Наименование", "Value": "Значение", "Data": None, "DataArray": []}, Item2, ...], 
    "Value": ""
  }
  ```
  Значение _Value_ является пустой строкой и, на текущий момент, не было замечено в передаче данных.
- _DataArray_: список объектов _Data_:
  ```python
  DataArray = [
    {"Items": [{"Name": "Наименование", "Value": "Значение", "Data": None, "DataArray": []}, Item2, ...], "Value": ""},
    Data2, ...
  ]
  ```

Типичный запрос в Elma производится с передачей данных, обычно, Elma работает с внешним объектом _Data_
(в описании API это описывается как _Тип CLR: WebData_), который надо либо передавать, либо принимать.
Стоит так же учесть, что объект _Item_ напрямую не участвует в передаче данных: он всегда завернут в объект _Data_.

Поскольку словари довольно громоздкие и имеют большое количество пустых полей, то их было бы неплохо преобразовывать 
в более наглядные словари и обратно. Для этого и был разработан данный модуль.

Преобразования выполняются обращением к классу `Parser`:

```python
from elmawebapi import Parser
```


#### Parser.normalize

Сигнатура: `Parser.normalize(data: list | dict) -> list | dict`.

Преобразует объекты _Data_ и _DataArray_ в удобный формат словарей: убирает лишнюю информацию, т.е. пустые значения
`Value`, `Data` и `DataArray` из _Item_, а так же выносит значение параметра `Name` в качестве ключа.

Если входным параметром является структура _Item_, а не _Data_, то он будет обработан как структура _Data_
с единственным элементом в массиве `Items`.

Все вложенные элементы будут преобразованы по тому же принципу, что и внешние.

Примеры:
```pycon
>>> Parser.normalize({"Items": [ {"Name": "Uid", "Value": "token", "Data": None, "DataArray": []} ]})
{"Uid": "token"}

>>> Parser.normalize({
...     "Name": "SubjectRF",
...     "Value": "",
...     "Data": {"Items": [ {"Name": "Id", "Value": 10, "Data": None, "DataArray": []} ]},
...     'DataArray': []
... })
{"SubjectRF": {"Id": 10}}

>>> Parser.normalize([
...     {"Items": [
...         {"Name": "Id", "Value": 2, "Data": None, "DataArray": []},
...         {"Name": "Uid", "Value": "qwerty", "Data": None, "DataArray": []}
...     ]},
...     {"Items": [
...         {"Name": "Id", "Value": 5, "Data": None, "DataArray": []},
...         {"Name": "Uid", "Value": "qwerty", "Data": None, "DataArray": []}
...     ]}
... ])
[{"Id": 2, "Uid": "qwerty"}, {"Id": 5, "Uid": "qwerty"}]
```


#### Parser.uglify

Сигнатура: `Parser.uglify(data: list | dict) -> list | dict`.

Преобразует обычные словари в форматы ELMA Web Data и ELMA Web DataArray.
Является обратной операцией для `Parser.normalize`.

Поскольку `Parser.normalize` не оперирует со структурой _Item_ напрямую, то и результатом данной функции не может
являться структура _Item_, только _Data_ и _DataArray_.

Все вложенные элементы будут преобразованы по тому же принципу, что и внешние.

Примеры:
```pycon
>>> Parser.uglify({"Uid": "token"})
{"Items": [{"Name": "Uid", "Value": "token", "Data": None, "DataArray": []}], "Value"}

>>> Parser.uglify({"SubjectRF": {"Id": 10}})
{"Items": [
    {
        "Name": "SubjectRF",
        "Value": "",
        "Data": {"Items": [{"Name": "Id", "Value": 10, "Data": None, "DataArray": []}], "Value": ""},
        "DataArray": []
    }
], "Value": ""} 

>>> Parser.uglify([{"Id": 2, "Uid": "qwerty"}, {"Id": 5, "Uid": "qwerty"}])
[
    {"Items": [
        {"Name": "Id", "Value": 2, "Data": None, "DataArray": []},
        {"Name": "Uid", "Value": "qwerty", "Data": None, "DataArray": []}
    ], "Value": ""}, 
    {"Items": [
        {"Name": "Id", "Value": 5, "Data": None, "DataArray": []},
        {"Name": "Uid", "Value": "qwerty", "Data": None, "DataArray": []}
    ], "Value": ""}
]
```


#### Parser.parse

Сигнатура `Parser.parse(string: str) -> dict`.

Алиас для метода `json.loads(string)`.


#### Parser.unwrap

Сигнатура `Parser.unwrap(seq: Iterable[dict], field: str = "Id", check_last: bool = False) -> dict`.

Разворачивает список в словарь, где ключом выступает поле `field` (по умолчанию `Id`). Таким образом, список словарей
переходит в словарь словарей. Если задать `check_last=True`, то, если в элементе осталось только 1 значение, внутренние 
словари расформировываются, оставляя только внешний.

Подразумевается, что при использовании структура данных известна и значения выбираемого поля `field` в списке является
уникальным.

Примеры:
```pycon
>>> Parser.unwrap([{"Id": "1", "Value": "value"}, {"Id": "2", "Value": "string"}])
{"1": {"Value": "value"}, "2": {"Value": "string"}}

>>> Parser.unwrap([{"Id": "1", "Value": "value"}, {"Id": "2", "Value": "string"}], check_last=True)
{"1": "value", "2": "string"}

>>> Parser.unwrap([{"Id": "1", "Value": "value"}, {"Id": "2", "Value": "string"}], field="Value")
{"value": {"Id": "1"}, "string": {"Id": "2"}}
```



### library.py

Предоставляет хранилище данных об объектах и процессах в Elma.

Является синглтоном. Изначально данные в объект необходимо каким-либо образом загрузить для последующего использования.
Предоставляет два хранилища: `uuids` и `processes`.

В первом хранятся все uuid-ы зарегистрированных типов данных (их можно увидеть, например, в API самой элмы по адресу
`/API/Help/Types`). Во втором хранятся "способы" запуска процессов: по _ProcessHeaderId_ и по _ProcessToken_.
_ProcessHeaderId_ можно посмотреть, например, в мониторе процессов (его видно в url); а _ProcessToken_ создается в
дизайнере при выборе пункта «Запуск из внешних систем» в настройках бизнес-процесса.

Естественно все данные, хранимые в этом объекте, сугубо индивидуальные, поэтому "подсказок" и "автодополнения" у
хранилищ нет.

Использование:

```python
from elmawebapi import Library

Library.uuids.Contractor == "1fb7545c-b103-44b1-9b01-dacb986db75d"  # True
```

Для заполнения используются три метода: `load_from_help`, `register_process` и `register_uuid`.


#### Library.load_from_help

Загружает данные из API-справки самого сервера элмы в хранилище uuid-ов.

Сигнатура метода: `Library.load_from_help(host: str, url: str) -> None`.

По умолчанию `url = "/API/Help/Types"` — ссылка на страницу с данными на хосте.

Использование:
```pycon
>>> Library.load_from_help(elma_host)
>>> Library.uuid.Contractor
"1fb7545c-b103-44b1-9b01-dacb986db75d"
```

Поскольку данных о _ProcessHeaderId_ и, тем более, _ProcessToken_ в справке не находится, то для заполнения данных
о них используется метод `register_process`.

#### Library.register_process

Создает запись о процессе в хранилище `processes`.

Сигнатура метода: `Library.register_process(name: str, *, header: int, token: str) -> None`.

Для сохранения данных о процессе необходимо дать его наименование для обращения из хранилища, а так же либо id
заголовка, либо токен запуска, либо оба параметра вместе. В случае передачи одного из параметров, второй будет равен
`None`.

Использование:
```pycon
>>> Library.register_process("ProcessWithHeader", header=10)
>>> Library.register_process("ProcessWithToken", token="00000000-1111-2222-3333-444444444444")
>>> Library.register_process("ProcessWithBoth", header=11, token="11111111-2222-3333-4444-555555555555")
>>> Library.processes.ProcessWithHeader.header
10
>>> Library.processes.ProcessWithToken.token
"00000000-1111-2222-3333-444444444444"
>>> Library.processes.ProcessWithBoth.header
11
>>> Library.processes.ProcessWithBoth.token
"11111111-2222-3333-4444-555555555555"
```

#### Library.register_uuid

Создает запись о типе объектов в хранилище `uuids`.

Сигнатура метода: `Library.register_uuid(name: str, uuid: str) -> None`.

Для сохранения данных о типе необходимо дать его наименование для обращения из хранилища, а так же его uuid.

Использование:
```pycon
>>> Library.register_uuid("Custom", "00000000-1111-2222-3333-444444444444")
>>> Library.uuids.Custom
"00000000-1111-2222-3333-444444444444"
```

Как правило, этот метод не используется напрямую, поскольку для работы хватает загрузки при помощи
[`load_from_help`](#libraryregister_uuid). Однако, если по какой-либо причине невозможно или нет смысла использовать
этот метод, то можно вручную воспользоваться `register_uuid`.



### services

Для обращения к сервисам Web API Elma используется `ElmaAPI`:

```python
from elmawebapi import ElmaAPI

API = ElmaAPI(host, username, password, token)
```

Для авторизации приложения необходимо задать 4 параметра:

- `host`: веб-адрес Elma
- `username`: имя пользователя, от лица которого будет производится взаимодействие с Elma
- `password`: пароль этого пользователя
- `token`: токен веб-приложения, берется в Elma (Администрирование → Система → Внешние приложения)

Опциональные параметры:

- `max_retries`: максимальное количество попыток переподключения к серверу при ошибках <u>авторизации</u>. 

При создании объекта автоматически будет произведена попытка подключения к системе.
После этого будет доступно 6 сервисов для работы:

- `AuthService` — частичное представление `IAuthorizationService`;
- `EntityService` — частичное представление `IEntityService`;
- `FeedService` — частичное представление `IMessageFeedService` и `Messages`;
- `FilesService` — частичное представление `IFilesService`;
- `TaskService` — частичное представление `Tasks`;
- `WorkflowService` — частичное представление `Workflow`.

Помимо этого, у объекта `ElmaAPI` доступны:
- метод `reconnect`, возвращающий словарь заголовков для авторизации;
- свойство `host` — веб-адрес Elma;
- свойство `credentials` — кортеж из имени пользователя, пароля и токена веб-приложения;
- свойство `headers` — словарь заголовков для подключения к хосту;
- свойство `settings` — неизменяемый объект настроек с задаваемыми изначально свойствами
  `host`, `username`, `password`, `apptoken`, `max_retries`.

Во всех нижеперечисленных сервисах имеются следующие свойства:

- `parent` — ссылка на родительский объект `ElmaAPI`;
- `session` — сессия `requests.Session` с заголовками авторизации.


#### ElmaError

При возникновении ошибок, методы сервисов кидают ошибку класса `ElmaError`, в которой прописан текст ответа от Elma.

Для использования в блоках `try ... except` или `contextlib.suppress` импортировать класс ошибки можно напрямую из
`elma`:

```python
from elmawebapi import ElmaError

...

try:
  ...
except ElmaError:
  ...
```


#### AuthService

Сервис для авторизации пользователей

##### LoginWithUserName (IAuthorizationService.LoginWithUserName)

Авторизовать пользователя по логину и паролю. Этот метод вызывается при создании объекта `ElmaAPI`, так что
дополнительно его вызывать не нужно.

Сигнатура метода: `AuthService.LoginWithUserName(username: str, password: str, app_token: str) -> dict`.

Использование:
```pycon
>>> API.AuthService.LoginWithUserName(username, password, token)
{"ApplicationToken": ..., "Content-Type": ..., "AuthToken": ..., "SessionToken": ...}
```

Результатом является словарь заголовков для использования в запросах.

##### ServerTime (IAuthorizationService.ServerTime)

Получить текущее серверное время.

Сигнатура метода: `AuthService.ServerTime() -> datetime`.

Использование:
```pycon
>>> API.AuthService.ServerTime()
2022-08-23 20:13:54.303000+03:00
```


#### EntityService

Сервис для получения записей сущностей.

##### Load (IEntityService.Load)

Получить сущность по типу и идентификатору.

Сигнатура метода: `EntityService.Load(params: dict) -> dict`.

Словарь `params` должен состоять из двух значений — `type` и `id`:
```python
params={"type": TypeUID, "id": EntityID}
```
где `TypeUID` — uid типа загружаемого объекта в виде строки, `EntityID` — id загружаемого объекта.

Использование:
```pycon
>>> API.EntityService.Load(params={"type": Library.uuids.ContractorLegal, "id": 53827})["BKUKlient"]
True
```

Результатом является словарь данных об объекте, очищенный через [`Parser.normalize`](#parsernormalize).

##### Count (IEntityService.Count)

Получить количество сущностей данного типа.

Сигнатура метода: `EntityService.Count(params: dict) -> int`.

Словарь `params` должен содержать значение `type`, а так же может содержать несколько опциональных значений — `q`,
`filterProviderUid`, `filterProviderData` и `filter`:
```python
params={
  "type": TypeUID, "q": EQLQuery, "filterProviderUid": filterProviderUid,
  "filterProviderData": filterProviderData, "filter": filter
}
```
где `TypeUID` — uid типа подсчитываемых объектов в виде строки, `EQLQuery` — строковая выборка на языке EQL,
`filterProviderUid`, `filterProviderData`, `filter` — параметры для фильтров провайдера фильтрации Elma.

Использование:
```pycon
>>> API.EntityService.Count(params={"type": Library.uuids.SLA, "q": "ResponseSpeed='2 р/ч'"})
9
```

Результатом является число — количество объектов.

##### Query (IEntityService.Query)

Получить все сущности данного типа, отфильтрованные по запросу.

Сигнатура метода: `EntityService.Query(params: dict) -> dict`.

Словарь `params` должен содержать значение `type`, а так же может содержать несколько опциональных значений — `q`,
`sort`, `limit`, `offset`, `filterProviderUid`, `filterProviderData` и `filter`:
```python
params={
  "type": TypeUID, "q": EQLQuery, "sort": sort, "limit": limit, "offset": offset,
  "filterProviderUid": filterProviderUid, "filterProviderData": filterProviderData, "filter": filter
}
```
где `TypeUID` — uid типа подсчитываемых объектов в виде строки, `EQLQuery` — строковая выборка на языке EQL,
`sort` — сортировка, `limit` — предел количества загружаемых объектов, `offset` — начальный элемент,
`filterProviderUid`, `filterProviderData`, `filter` — параметры для фильтров провайдера фильтрации Elma.

Использование:
```pycon
>>> API.EntityService.Query(params={"type": Library.uuids.SLA, "q": "ResponseSpeed='2 р/ч'"})
[{'Id': '32', 'TypeUid': '2fd01a0d-0784-44e2-bd8c-231acb60e049', 'Uid': '9047d294-c00b-49bc-a4da-978d979e4aa5',
'CreationDate': '07/06/2021 11:23:00', 'C_Id': '000032', 'FullName': None, 'Name': ...}]
```

Результатом является список данных об объектах, очищенный через [`Parser.normalize`](#parsernormalize).

##### Insert (IEntityService.Insert)

Сохранить новый объект в системе.

Сигнатура метода: `EntityService.Insert(entityData: dict, typeuid: str) -> int`.

Использование:
```pycon
>>> id = API.EntityService.Insert(
...     typeuid=Library.uuids.UgF,
...     entityData=Parser.uglify(
...         {
...             "Name": "Тестовая УГФ",
...             "ShortName": "ТестУГФ",
...             "MinimaljnoeVremyaNaZadachuMin": 1,
...             "MaksimaljnoeVremyaNaZadachuMin": 120,
...         }
...     ),
... )
>>> print(id)
385
```

Результатом является число — id нового объекта.

##### Update (IEntityService.Update)

Обновить существующий объект в системе.

Сигнатура метода: `EntityService.Update(entityData: dict, typeuid: str, entityid: int) -> int`.

Использование:
```pycon
>>> id = API.EntityService.Update(
...     typeuid=Library.uuids.UgF,
...     entityid=385,
...     entityData=Parser.uglify({"MinimaljnoeVremyaNaZadachuMin": 10}),
... )
>>> print(id)
385
```

Результатом является число — id измененного объекта.


#### FeedService

Не реализован.


#### FilesService

Не реализован.


#### TaskService

Не реализован.


#### WorkflowService

##### StartableProcesses (Workflow.StartableProcesses)

Загрузить список доступных для запуска процессов.

Сигнатура метода: `WorkflowService.StartableProcesses() -> dict`.

Использование:
```pycon
>>> API.WorkflowService.StartableProcesses()
{'Groups': [{'Id': '21', 'Name': 'Django/Helpdesk'}, {'Id': '12', 'Name': 'Учетные процессы'}, ...],
'Processes': [{'Id': '178', 'Name': '03. Перенос контактных данных', 'GroupId': '21'},
{'Id': '175', 'Name': '02-Б. Обработка исключений', 'GroupId': '21'}, ...]}
```

Результатом является словарь данных со списками групп `Groups` и процессов `Processes`.

##### StartProcess (Workflow.StartProcessAsync)

Запустить процесс.

Сигнатура метода:
`WorkflowService.StartProcess(process_header: int, process_token: str, process_name: str, context: dict) -> dict`.

Параметры:

  - `process_header` — идентификатор заголовка процесса,
  - `process_token` — токен запуска процесса,
  - `process_name` — наименование экземпляра процесса,
  - `context` — значения контекстных переменных.

Запуск может производиться двумя способами: либо передачей `process_token`, либо передачей `process_header`.
В первом случае токен берется из настроек бизнес-процесса в дизайнере (где разрешается запуск внешними приложениями),
во втором — это id связанного с процессом объекта `ProcessHeader`, значение которого можно, например, посмотреть в
мониторинге процессов (он будет написан в url: `InstanceFilter.ProcessHeader.Id=<нужное число>`)

Использование:
```pycon
>>> API.WorkflowService.StartProcess(
...     process_header=Library.process_headers.System02A,
...     context={
...         "processId": 540457,
...         "answer": (
...             '{"error": 0, "message": "Данные из кабинета 34201983 добавлены пользователю Nemy\n'
...             'Аккаунт кабинета 42195001 не был найден"}'
...         )
...     }
... )
{'Result': 'True', 'Status': 'Executing', 'ExecutionToken': '3c058fcb-13e8-4e15-9d32-98d830d0a1f5'}
```

Результатом является словарь данных о запуске процесса.



### services/decorators.py

Предоставляет декораторы для методов сервисов. Более подробно о декораторах можно узнать в документации самих методов.


#### needs_auth

Проверяет у родителя сервиса (`ElmaAPI`) наличие свойства `headers`, а так же проверяет в нем значение `AuthToken` на 
пустоту. Если проверка не проходит, то декоратор изменяет `headers` через метод `ElmaAPI.reconnect`.

Использование:

```python
from elmawebapi.services import decorators
from elmawebapi.services.base import Service


class NewService(Service):
  @decorators.needs_auth
  def Method(self, *args, **kwargs): ...
```


#### get

Предваряет выполнение метода GET-запросом на указанный адрес. Сам метод должен принимать аргумент `result` — ответ 
запроса.

При вызове декорированного метода можно передать два аргумента:

- `params` — словарь, который после преобразуется в параметр поиска GET-запроса (`url?key1=value1&key2=value`);
- `uri` — перенаправление запроса на указанный адрес (например, если в адрес необходимо подставить переменную).

Остальные параметры будут напрямую переданы в метод.

Использование:

```python
from elmawebapi.services import decorators
from elmawebapi.services.base import Service


class NewService(Service):
    @decorators.get(url="/Service/Method")
    def GetMethod(self, result, uid, *args, **kwargs):
        # допустим, что по адресу "/Service/Method/{type_uid}?Id={id}" возвращается переданный Id в запросе
        return result["Id"], uid
```
```pycon
>>> type_uid = "1fb7545c-b103-44b1-9b01-dacb986db75d"
>>> API.NewService.GetMethod(params={"Id": 20}, uri=f"/Service/Method/{type_uid}/", uid=type_uid)
20, '1fb7545c-b103-44b1-9b01-dacb986db75d'
```


#### post

Предваряет выполнение метода POST-запросом на указанный адрес. Сам метод должен принимать аргумент `result` — ответ 
запроса.

При вызове декорированного метода можно передать два аргумента:

- `data` — словарь с данными, которые будут отправлены на указанный адрес;
- `uri` — перенаправление запроса на указанный адрес (например, если в адрес необходимо подставить переменную).

Остальные параметры будут напрямую переданы в метод.

Использование:

```python
from elmawebapi.services import decorators
from elmawebapi.services.base import Service


class NewService(Service):
    @decorators.post(url="/Service/Method")
    def PostMethod(self, result, uid, *args, **kwargs):
        # допустим, что при передаче Id в POST-запросе на адрес "/Service/Method/{type_uid}" возвращается 
        # этот самый Id
        return result["Id"], uid
```
```pycon
>>> type_uid = "1fb7545c-b103-44b1-9b01-dacb986db75d"
>>> API.NewService.PostMethod(data={"Id": 20}, uri=f"/Service/Method/{type_uid}/", uid=type_uid)
20, '1fb7545c-b103-44b1-9b01-dacb986db75d'
```


#### Примеры использования в существующих сервисах

Для запуска процесса в [`WorkflowService`](#startprocess-workflowstartprocessasync) используются декораторы
`needs_auth` и `post` на метод `_start_process`, а метод `StartProcess` является лишь удобной обёрткой для его запуска.

```python
from . import base, decorators
from ..structure import Parser


START_PROCESS_ASYNC = "/API/REST/Workflow/StartProcessAsync"


class WorkflowService(base.Service):
    @decorators.needs_auth
    @decorators.post(url=START_PROCESS_ASYNC)
    def _start_process(self, result):
        return Parser.normalize(result.json())
        
    def StartProcess(self, *, process_header, process_token, process_name, context):
        if (
            (not isinstance(process_header, int) or process_header < 1) and not process_token
            or process_token and process_header
        ):
            raise ValueError("Для запуска необходимо передать или process_header, или process_token")

        if process_token:
            data = {"ProcessToken": process_token}
        else:
            data = {"ProcessHeaderId": process_header}

        data["Context"] = context if context else {}

        if process_name:
            data["ProcessName"] = process_name

        data = Parser.uglify(data)
        return self._start_process(data=data) 
```

Для получения сущности в [`EntityService`](#load-ientityserviceload) используются декораторы `needs_auth` и `get` на
метод `Load`. Большинство методов, в которых происходит только GET-запрос, из-за декораторов внутри реализованы в одну 
строчку:

```python
from . import base, decorators
from ..structure import Parser


LOAD = "/API/REST/Entity/Load"


class EntityService(base.Service):
    @decorators.needs_auth
    @decorators.get(url=LOAD)
    def Load(self, result, *args, **kwargs):
        return Parser.normalize(result.json())
```
