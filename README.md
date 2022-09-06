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
from elma import Parser
```

#### Parser.normalize

Сигнатура: `Parser.normalize(data: list | dict) -> list | dict`.

Преобразует объекты _Data_ и _DataArray_ в удобный формат словарей: убирает лишнюю информацию, т.е. пустые значения
`Value`, `Data` и `DataArray` из _Item_, а так же выносит значение параметра `Name` в качестве ключа.

Если входным параметром является структура _Item_, а не _Data_, то он будет обработан как структура _Data_
с единственным элементом в массиве `Items`.

Все вложенные элементы будут преобразованы по тому же принципу, что и внешние.

Примеры:
```python
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
```python
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
```python
>>> Parser.unwrap([{"Id": "1", "Value": "value"}, {"Id": "2", "Value": "string"}])
{"1": {"Value": "value"}, "2": {"Value": "string"}}

>>> Parser.unwrap([{"Id": "1", "Value": "value"}, {"Id": "2", "Value": "string"}], check_last=True)
{"1": "value", "2": "string"}

>>> Parser.unwrap([{"Id": "1", "Value": "value"}, {"Id": "2", "Value": "string"}], field="Value")
{"value": {"Id": "1"}, "string": {"Id": "2"}}
```


### library.py

Предоставляет хранилище данных об объектах, процессах и т.п. в Elma.

Использование:
```python
from elma import Library

>>> Library.uuids.Contractor
"1fb7545c-b103-44b1-9b01-dacb986db75d"
>>> Library.process_headers.System02A
177
```


### services

Для обращения к сервисам Web API Elma используется `ElmaAPI`:
```python
from elma import ElmaAPI

API = ElmaAPI(host, username, password, token)
```

Для авторизации приложения необходимо задать 4 параметра:

- `host`: веб-адрес Elma
- `username`: имя пользователя, от лица которого будет производится взаимодействие с Elma
- `password`: пароль этого пользователя
- `token`: токен веб-приложения, берется в Elma (Администрирование → Система → Внешние приложения)

При создании объекта автоматически будет произведена попытка подключения к системе.
После этого будет доступно 6 сервисов для работы:

- `AuthService` — частичное представление `IAuthorizationService`
- `EntityService` — частичное представление `IEntityService`
- `FeedService` — частичное представление `IMessageFeedService` и `Messages`
- `FilesService` — частичное представление `IFilesService`
- `TaskService` — частичное представление `Tasks`
- `WorkflowService` — частичное представление `Workflow`

#### AuthService

Сервис для авторизации пользователей

##### LoginWithUserName (IAuthorizationService.LoginWithUserName)

Авторизовать пользователя по логину и паролю. Этот метод вызывается при создании объекта `ElmaAPI`, так что
дополнительно его вызывать не нужно.

Сигнатура метода: `AuthService.LoginWithUserName(username: str, password: str, app_token: str) -> dict`.

Использование:
```python
>>> API.AuthService.LoginWithUserName(username, password, token)
{"ApplicationToken": ..., "Content-Type": ..., "AuthToken": ..., "SessionToken": ...}
```

Результатом является словарь заголовков для использования в запросах.

##### ServerTime (IAuthorizationService.ServerTime)

Получить текущее серверное время.

Сигнатура метода: `AuthService.ServerTime() -> datetime`.

Использование:
```python
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
```python
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
```python
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
```python
>>> API.EntityService.Query(params={"type": Library.uuids.SLA, "q": "ResponseSpeed='2 р/ч'"})
[{'Id': '32', 'TypeUid': '2fd01a0d-0784-44e2-bd8c-231acb60e049', 'Uid': '9047d294-c00b-49bc-a4da-978d979e4aa5',
'CreationDate': '07/06/2021 11:23:00', 'C_Id': '000032', 'FullName': None, 'Name': ...}]
```

Результатом является список данных об объектах, очищенный через [`Parser.normalize`](#parsernormalize).

##### Insert (IEntityService.Insert)

Сохранить новый объект в системе.

Сигнатура метода: `EntityService.Insert(entityData: dict, typeuid: str) -> int`.

Использование:
```python
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
```python
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

Under construction


#### FilesService

Under construction


#### TaskService

Under construction


#### WorkflowService

##### StartableProcesses (Workflow.StartableProcesses)

Загрузить список доступных для запуска процессов.

Сигнатура метода: `WorkflowService.StartableProcesses() -> dict`.

Использование:
```python
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
```python
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
