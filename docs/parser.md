# Парсер данных Elma `Parser`


- [работа с API-сервисами Elma _ElmaAPI_](services.md)
- [хранение типов данных и информации о процессах _Library_](library.md)
- **парсер данных Elma _Parser_**
  - [_Parser.normalize_](#parsernormalize)
  - [_Parser.uglify_](#parseruglify)
  - [_Parser.parse_](#parserparse)
  - [_Parser.unwrap_](#parserunwrap)

---

Утилита для преобразования структур WebAPI Elma: _Item_, _Data_ и _DataArray_ в обычные словари и обратно.

Структуры представляют собой следующее:

- _Item_ (_Тип CLR: WebDataItem_) — словарь с наименованием _Name_ и тремя параметрами под значения — _Value_, _Data_
  и _DataArray_:
  ```python
  Item = {"Name": "Наименование", "Value": "Значение", "Data": None, "DataArray": []}
  ```
  _Value_ может принимать какое-либо значение "стандартных" типов — число, строка или булева, пустым значением 
  считается пустая строка. _Data_ может принимать значение типа _Data_, пустым значением считается `None`.
  _DataArray_ может принимать значение типа _DataArray_, пустым значением считается пустой массив.
- _Data_ (_Тип CLR: WebData_) — словарь со списком _Items_ объектов типа _Item_ и значением _Value_:
  ```python
  Data = {
    "Items": [{"Name": "Наименование", "Value": "Значение", "Data": None, "DataArray": []}, Item2, ...], 
    "Value": ""
  }
  ```
  Значение _Value_ является пустой строкой и, на текущий момент, не было замечено в передаче данных и каком-либо
  использовании.
- _DataArray_ (_Массив объектов WebData_ или _[i] Тип CLR: WebData_) — список объектов _Data_:
  ```python
  DataArray = [
    {"Items": [{"Name": "Наименование", "Value": "Значение", "Data": None, "DataArray": []}, Item2, ...], "Value": ""},
    Data2, ...
  ]
  ```

Если запрос в Elma производится с передачей данных, то, обычно, Elma работает с внешним объектом _Data_, который надо
либо передавать, либо принимать. Стоит так же учесть, что объекты типа _Item_ напрямую не участвует в передаче данных:
они всегда обернуты в объект _Data_.

Поскольку словари довольно громоздкие и имеют большое количество пустых полей, то их было бы неплохо преобразовывать 
в более наглядные словари и обратно. Для этого и был разработан данный модуль.


## Parser.normalize

<sub>[↺ к оглавлению](#парсер-данных-elma-parser)
· [↓ _Parser.uglify_](#parseruglify)
</sub>

Сигнатура: `Parser.normalize(data: list | dict) -> list | dict`. `list` и `dict` тут являются рекурсивно вложенными
друг в друга объектами _Item_, _Data_ и _DataArray_.

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


## Parser.uglify

<sub>[↺ к оглавлению](#парсер-данных-elma-parser)
· [↑ _Parser.normalize_](#parsernormalize)
· [↓ _Parser.parse_](#parserparse)
</sub>

Сигнатура: `Parser.uglify(data: list | dict) -> list | dict`. `list` и `dict` тут являются рекурсивно вложенными
друг в друга объектами _Item_, _Data_ и _DataArray_.

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


## Parser.parse

<sub>[↺ к оглавлению](#парсер-данных-elma-parser)
· [↑ _Parser.uglify_](#parseruglify)
· [↓ _Parser.unwrap_](#parserunwrap)
</sub>

Сигнатура `Parser.parse(string: str) -> dict`.

Алиас для метода `json.loads(string)`.


## Parser.unwrap

<sub>[↺ к оглавлению](#парсер-данных-elma-parser)
· [↑ _Parser.parse_](#parserparse)
</sub>

Сигнатура: `Parser.unwrap(seq: Iterable[dict], field: str = "Id", check_last: bool = False) -> dict`.

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
