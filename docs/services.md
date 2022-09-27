# Работа с API-сервисами Elma `ElmaAPI`


- **работа с API-сервисами Elma _ElmaAPI_**
  - [_ElmaError_](#elmaerror)
  - [_AuthService_](#authservice)
  - [_EntityService_](#entityservice)
  - [_FeedService_](#feedservice)
  - [_FilesService_](#filesservice)
  - [_TaskService_](#taskservice)
  - [_WorkflowService_](#workflowservice)
  - [Собственные сервисы](#собственные-сервисы)
- [хранение типов данных и информации о процессах _Library_](library.md)
- [парсер данных Elma _Parser_](parser.md)

---

Для обращения к сервисам Web API Elma используется `ElmaAPI`:

```python
from elmawebapi import ElmaAPI

API = ElmaAPI(host, username, password, token, max_retries=5)
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


## ElmaError

<sub>[↺ к оглавлению](#работа-с-api-сервисами-elma-elmaapi)
· [↓ _AuthService_](#authservice)
</sub>


При возникновении ошибок, методы сервисов кидают ошибку класса `ElmaError`, в которой прописан текст ответа от Elma.

Для использования в блоках `try ... except` или `contextlib.suppress` импортировать класс ошибки можно напрямую из
`elmawebapi`:

```python
from elmawebapi import ElmaError

try:
  ...
except ElmaError:
  ...
```


## AuthService

<sub>[↺ к оглавлению](#работа-с-api-сервисами-elma-elmaapi)
· [↑ _ElmaError_](#elmaerror)
· [↳ _LoginWithUserName_](#loginwithusername-iauthorizationserviceloginwithusername)
· [↓ _EntityService_](#entityservice)
</sub>


Сервис для авторизации пользователей

### LoginWithUserName (IAuthorizationService.LoginWithUserName)

<sub>[↺ к оглавлению](#работа-с-api-сервисами-elma-elmaapi)
· [⇑ _AuthService_](#authservice)
· [↓ _ServerTime_](#servertime-iauthorizationserviceservertime)
· [⇓ _EntityService_](#entityservice)
</sub>


Авторизовать пользователя по логину и паролю. Этот метод вызывается при создании объекта `ElmaAPI`, так что
дополнительно его вызывать не нужно.

Сигнатура метода: `LoginWithUserName(username: str, password: str, app_token: str) -> dict`.

Использование:
```pycon
>>> API.AuthService.LoginWithUserName(username, password, token)
{"ApplicationToken": ..., "Content-Type": ..., "AuthToken": ..., "SessionToken": ...}
```

Результатом является словарь заголовков для использования в запросах.


### ServerTime (IAuthorizationService.ServerTime)

<sub>[↺ к оглавлению](#работа-с-api-сервисами-elma-elmaapi)
· [⇑ _AuthService_](#authservice)
· [↑ _LoginWithUserName_](#loginwithusername-iauthorizationserviceloginwithusername)
· [↓ _ServerTimeUTC_](#servertimeutc-iauthorizationserviceservertimeutc)
· [⇓ _EntityService_](#entityservice)
</sub>


Получить текущее серверное время в часовом поясе пользователя.

Сигнатура метода: `ServerTime() -> datetime`.

Использование:
```pycon
>>> API.AuthService.ServerTime()
2022-08-23 20:13:54.303000+03:00
```


### ServerTimeUTC (IAuthorizationService.ServerTimeUTC)

<sub>[↺ к оглавлению](#работа-с-api-сервисами-elma-elmaapi)
· [⇑ _AuthService_](#authservice)
· [↑ _ServerTime_](#servertime-iauthorizationserviceservertime)
· [⇓ _EntityService_](#entityservice)
</sub>


Получить текущее серверное время в часовом поясе UTC.

Сигнатура метода: `ServerTimeUTC() -> datetime`.

Использование:
```pycon
>>> API.AuthService.ServerTimeUTC()
2022-08-23 17:13:54.303000+00:00
```


## EntityService

<sub>[↺ к оглавлению](#работа-с-api-сервисами-elma-elmaapi)
· [↑ _AuthService_](#authservice)
· [↳ _Load_](#load-ientityserviceload)
· [↓ _FeedService_](#feedservice)
</sub>


Сервис для получения записей сущностей. Стоит учесть, что метода удаления объектов в API Elma не предусмотрено.


### Load (IEntityService.Load)

<sub>[↺ к оглавлению](#работа-с-api-сервисами-elma-elmaapi)
· [⇑ _EntityService_](#entityservice)
· [↓ _Count_](#count-ientityservicecount)
· [⇓ _FeedService_](#feedservice)
</sub>


Получить сущность по типу и идентификатору.

Сигнатура метода: `Load(params: dict) -> dict`.

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


### Count (IEntityService.Count)

<sub>[↺ к оглавлению](#работа-с-api-сервисами-elma-elmaapi)
· [⇑ _EntityService_](#entityservice)
· [↑ _Load_](#load-ientityserviceload)
· [↓ _Query_](#query-ientityservicequery)
· [⇓ _FeedService_](#feedservice)
</sub>


Получить количество сущностей данного типа.

Сигнатура метода: `Count(params: dict) -> int`.

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


### Query (IEntityService.Query)

<sub>[↺ к оглавлению](#работа-с-api-сервисами-elma-elmaapi)
· [⇑ _EntityService_](#entityservice)
· [↑ _Count_](#count-ientityservicecount)
· [↓ _Insert_](#insert-ientityserviceinsert)
· [⇓ _FeedService_](#feedservice)
</sub>


Получить все сущности данного типа, отфильтрованные по запросу.

Сигнатура метода: `Query(params: dict) -> dict`.

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


### Insert (IEntityService.Insert)

<sub>[↺ к оглавлению](#работа-с-api-сервисами-elma-elmaapi)
· [⇑ _EntityService_](#entityservice)
· [↑ _Query_](#query-ientityservicequery)
· [↓ _Update_](#update-ientityserviceupdate)
· [⇓ _FeedService_](#feedservice)
</sub>


Сохранить новый объект в системе.

Сигнатура метода: `Insert(entityData: dict, typeuid: str) -> int`.

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


### Update (IEntityService.Update)

<sub>[↺ к оглавлению](#работа-с-api-сервисами-elma-elmaapi)
· [⇑ _EntityService_](#entityservice)
· [↑ _Insert_](#insert-ientityserviceinsert)
· [⇓ _FeedService_](#feedservice)
</sub>


Обновить существующий объект в системе.

Сигнатура метода: `Update(entityData: dict, typeuid: str, entityid: int) -> int`.

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


## FeedService

<sub>[↺ к оглавлению](#работа-с-api-сервисами-elma-elmaapi)
· [↑ _EntityService_](#entityservice)
· [↓ _FilesService_](#filesservice)
</sub>


Не реализован.


## FilesService

<sub>[↺ к оглавлению](#работа-с-api-сервисами-elma-elmaapi)
· [↑ _FeedService_](#feedservice)
· [↓ _TaskService_](#taskservice)
</sub>


Не реализован.


## TaskService

<sub>[↺ к оглавлению](#работа-с-api-сервисами-elma-elmaapi)
· [↑ _FilesService_](#filesservice)
· [↓ _WorkflowService_](#workflowservice)
</sub>


Не реализован.


## WorkflowService

<sub>[↺ к оглавлению](#работа-с-api-сервисами-elma-elmaapi)
· [↑ _TaskService_](#taskservice)
· [↳ _StartableProcesses_](#startableprocesses-workflowstartableprocesses)
· [↓ Собственные сервисы](#собственные-сервисы)
</sub>


Сервис для работы с процессами.


### StartableProcesses (Workflow.StartableProcesses)

<sub>[↺ к оглавлению](#работа-с-api-сервисами-elma-elmaapi)
· [⇑ _WorkflowService_](#workflowservice)
· [↓ _StartProcess_](#startprocess-workflowstartprocessasync)
· [⇓ Собственные сервисы](#собственные-сервисы)
</sub>


Загрузить список доступных для запуска процессов.

Сигнатура метода: `StartableProcesses() -> dict`.

Использование:
```pycon
>>> API.WorkflowService.StartableProcesses()
{'Groups': [{'Id': '21', 'Name': 'Django/Helpdesk'}, {'Id': '12', 'Name': 'Учетные процессы'}, ...],
'Processes': [{'Id': '178', 'Name': '03. Перенос контактных данных', 'GroupId': '21'},
{'Id': '175', 'Name': '02-Б. Обработка исключений', 'GroupId': '21'}, ...]}
```

Результатом является словарь данных со списками групп `Groups` и процессов `Processes`.


### StartProcess (Workflow.StartProcessAsync)

<sub>[↺ к оглавлению](#работа-с-api-сервисами-elma-elmaapi)
· [⇑ _WorkflowService_](#workflowservice)
· [↑ _StartableProcesses_](#startableprocesses-workflowstartableprocesses)
· [⇓ Собственные сервисы](#собственные-сервисы)
</sub>


Запустить процесс.

Сигнатура метода: `StartProcess(self, *, process_header: int = 0, process_token: str = "", process_name: str = "",
context: dict | None = None) -> dict`.

Параметры:

  - `process_header` — идентификатор заголовка процесса,
  - `process_token` — токен запуска процесса,
  - `process_name` — наименование экземпляра процесса,
  - `context` — значения контекстных переменных.

Запуск может производиться двумя способами: либо передачей `process_token`, либо передачей `process_header`.
В первом случае токен берется из настроек бизнес-процесса в дизайнере (где разрешается запуск внешними приложениями),
во втором — это id связанного с процессом объекта `ProcessHeader`, значение которого можно, например, посмотреть в
мониторинге процессов (он будет написан в url: `InstanceFilter.ProcessHeader.Id=<нужное число>`).

Использование:
```pycon
>>> API.WorkflowService.StartProcess(
...     process_header=Library.processes.System02A.header,
...     context={
...         "processId": 540457,
...         "answer": (
...             '{"error": 0, "message": "Данные из кабинета 34201983 добавлены пользователю Nemy\n'
...             'Аккаунт кабинета 42195001 не был найден"}'
...         )
...     }
... )
{"Result": "True", "Status": "Executing", "ExecutionToken": "3c058fcb-13e8-4e15-9d32-98d830d0a1f5"}
```

Результатом является словарь данных о запуске процесса.


## Собственные сервисы

<sub>[↺ к оглавлению](#работа-с-api-сервисами-elma-elmaapi)
· [↑ _WorkflowService_](#workflowservice)
· [↳ Базовый класс _Service_](#базовый-класс-service)
</sub>


Все текущие сервисы наследуются от базового класса сервисов `Service`, в котором прописан родительский элемент
`ElmaAPI`, из которого сервисы получают данные о хосте и о заголовках сессии. Помимо этого методы реализованы с
использованием декораторов для оправки запросов. Более подробно о декораторах можно узнать в документации самих методов.


### Базовый класс Service

<sub>[↺ к оглавлению](#работа-с-api-сервисами-elma-elmaapi)
· [⇑ Собственные сервисы](#собственные-сервисы)
· [↓ Декоратор _needs_auth_](#декоратор-needs_auth)
</sub>


Базовый класс для сервисов. Содержит слот `parent` для связи с объектом `ElmaAPI` и свойство `session`, которое
создает новый экземпляр `request.Session` с заголовками из
[`LoginWithUserName`](#loginwithusername-iauthorizationserviceloginwithusername).

Использование:

```python
from elmawebapi.services.base import Service

class NewService(Service): ...
```


### Декоратор needs_auth

<sub>[↺ к оглавлению](#работа-с-api-сервисами-elma-elmaapi)
· [⇑ Собственные сервисы](#собственные-сервисы)
· [↑ Базовый класс _Service_](#базовый-класс-service)
· [↓ Декоратор _get_](#декоратор-get)
</sub>


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


### Декоратор get

<sub>[↺ к оглавлению](#работа-с-api-сервисами-elma-elmaapi)
· [⇑ Собственные сервисы](#собственные-сервисы)
· [↑ Декоратор _needs_auth_](#декоратор-needs_auth)
· [↓ Декоратор _post_](#декоратор-post)
</sub>


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


### Декоратор post

<sub>[↺ к оглавлению](#работа-с-api-сервисами-elma-elmaapi)
· [⇑ Собственные сервисы](#собственные-сервисы)
· [↑ Декоратор _get_](#декоратор-get)
· [↓ Примеры использования в существующих сервисах](#примеры-использования-в-существующих-сервисах)
</sub>


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


### Примеры использования в существующих сервисах

<sub>[↺ к оглавлению](#работа-с-api-сервисами-elma-elmaapi)
· [⇑ Собственные сервисы](#собственные-сервисы)
· [↑ Декоратор _post_](#декоратор-post)
</sub>


Для запуска процесса в [`WorkflowService`](#startprocess-workflowstartprocessasync) используются декораторы
`needs_auth` и `post` на метод `_start_process`, а метод `StartProcess` является лишь удобной обёрткой для его запуска.

```python
from elmawebapi.services import base, decorators
from elmawebapi.structure import Parser


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
from elmawebapi.services import base, decorators
from elmawebapi.structure import Parser


LOAD = "/API/REST/Entity/Load"


class EntityService(base.Service):
    @decorators.needs_auth
    @decorators.get(url=LOAD)
    def Load(self, result, *args, **kwargs):
        return Parser.normalize(result.json())
```
