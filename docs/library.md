### Хранение типов данных и информации о процессах `Library`


- [работа с API-сервисами Elma _ElmaAPI_](services.md)
- **хранение типов данных и информации о процессах _Library_**
  - [_Library.load_from_help_](#libraryload_from_help)
  - [_Library.register_process_](#libraryregister_process)
  - [_Library.register_uuid_](#libraryregister_uuid)
  - [_LibraryClass_](#libraryclass)
- [парсер данных Elma _Parser_](parser.md)

---

Представляет собой хранилище данных об объектах и процессах в Elma. Является синглтоном ([не совсем](#libraryclass)).
Предоставляет два свойства: `uuids` и `processes`.

В первом хранятся все uuid-ы зарегистрированных типов данных (их можно увидеть, например, в API самой Elma по адресу
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

Изначально данные в объект необходимо каким-либо образом загрузить для последующего использования.

Для заполнения используются три метода: `load_from_help`, `register_process` и `register_uuid`.


## Library.load_from_help

<sub>[↺ к оглавлению](#-------library)
· [↓ _Library.register_process_](#libraryregister_process)
</sub>

Загружает данные из API-справки сервера Elma в хранилище uuid-ов.

Сигнатура метода: `Library.load_from_help(host: str, url: str) -> None`.

По умолчанию `url = "/API/Help/Types"` — ссылка на страницу с данными на хосте.

Использование:
```pycon
>>> Library.load_from_help(elma_host)
>>> Library.uuid.Contractor
"1fb7545c-b103-44b1-9b01-dacb986db75d"
```

Технически, метод загружает страницу и парсит ее в поисках ссылок. Атрибут `href` ссылки считается UID-ом, а текст
ссылки — именем типа данных. После чего вызывается метод [`register_uuid`](#libraryregister_uuid) с собранными
данными.


## Library.register_process

Поскольку данных о _ProcessHeaderId_ и, тем более, _ProcessToken_ в справке не находится, то для заполнения данных
о них используется метод `register_process`.

<sub>[↺ к оглавлению](#-------library)
· [↑ _Library.load_from_help_](#libraryload_from_help)
· [↓ _Library.register_uuid_](#libraryregister_uuid)
</sub>

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


## Library.register_uuid

<sub>[↺ к оглавлению](#-------library)
· [↑ _Library.register_process_](#libraryregister_process)
· [↓ _LibraryClass_](#libraryclass)
</sub>

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
[`load_from_help`](#libraryload_from_help). Однако, если по какой-либо причине невозможно или нет смысла использовать
этот метод, то можно вручную воспользоваться `register_uuid`.


## LibraryClass

<sub>[↺ к оглавлению](#-------library)
· [↑ _Library.register_uuid_](#libraryregister_uuid)
</sub>

Как уже было упомянуто, `Library` — не совсем синглтон. Это объект класса `LibraryClass`, который в свою очередь можно
импортировать в проект и иметь несколько библиотек одновременно. Это может быть полезно при наличии нескольких
серверов, например, боевого и тестового. При сохранении имен классов и процессов, можно вести обе библиотеки
одновременно и переключаться между ними при переносе процессов и компонент с тестового сервера на боевой.

```python
from elmawebapi import ElmaAPI
from elmawebapi.library import Library, LibraryClass

library_test = LibraryClass()
library_prod = Library

library_test.load_from_help("HOST_URL_TEST")
library_prod.load_from_help("HOST_URL_PRODUCTION")

library_test.register_process("CustomProcess", header=20)
library_prod.register_process("CustomProcess", header=32)

def start_custom_process(library: LibraryClass, context: dict):
    API = ElmaAPI(...)
    API.WorkflowService.StartProcess(process_header=library.processes.CustomProcess, context=context)

start_custom_process(library_test, {})  # запустит процесс с ProcessHeaderId = 20
start_custom_process(library_prod, {})  # запустит процесс с ProcessHeaderId = 32
```

Таким образом, если идентификационные данные процессов или же UIDы типов данных будут отличаться, это не повлечет за
собой поиск и изменение необходимых значений, а решится переключением используемого хранилища `Library`.
