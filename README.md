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

Сигнатура: `Parser.normalize(data: list | dict) -> list | dict`

Преобразует объекты _Data_ и _DataArray_ в удобный формат словарей: убирает лишнюю информацию, т.е. пустые значения
`Value`, `Data` и `DataArray` из _Item_, а так же вынося значение параметра `Name` в качестве ключа.

Если входным параметром является структура _Item_, а не _Data_, то он будет преобразован в структуру _Data_
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

Сигнатура: `Parser.uglify(data: list | dict) -> list | dict`

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

Сигнатура `Parser.parse(string: str) -> dict`

Алиас для метода `json.loads(string)`.


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
'CreationDate': '07/06/2021 11:23:00', 'C_Id': '000032', 'FullName': None, 'Name': 'Удален. ТП уст. ПО по...
```

Результатом является список данных об объектах, очищенный через [`Parser.normalize`](#parsernormalize).

##### Insert (IEntityService.Insert)

Сохранить новый объект в системе.

Сигнатура метода: `EntityService.Insert(entityData: dict, typeuid: str) -> int`.

Использование:
```python
>>> id = API.EntityService.Insert(
...     typeuid=Library.UgF,
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

Обновить существующий объект в системе

Сигнатура метода: `EntityService.Update(entityData: dict, typeuid: str, entityid: int) -> int`.

Использование:
```python
>>> id = API.EntityService.Update(
...     typeuid=Library.UgF,
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

...
