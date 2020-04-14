# Elma-Cabinet API Connector

Представляет собой сервис, предоставляющий API для связи между собой Элмы и кабинета.

## Описание API

## Документация

### structure.py

Преобразования структур Web API Элмы: _Item_, _Data_ и _DataArray_.

#### `make_item(name: AnyStr, value: Any = '', data: dict = {}, dataarray: list = []) -> dict`

Возвращает словарь, преставляющий элемент _Item_, параметры которого взяты из переданных аргументов.

```python
make_item('Id', value=20)
# {'Name': 'Id', 'Value': 20, 'Data': {}, 'DataArray': []}

make_item('Type', data=make_data([make_item('Id', 13)]))
# {'Name': 'Type', 'Value': '', 'Data': {'Items': [{'Name': 'Id', 'Value': 13, 'Data': {}, 'DataArray': []}]}, 'DataArray': []}
```

#### `make_data(items: list) -> dict`

Возвращает словарь, представляющий элемент _Data_, элементы которого взяты из переданного списка.

```python
make_data([make_item('Id', 13)])
# {'Items': [{'Name': 'Id', 'Value': 13, 'Data': {}, 'DataArray': []}]}
```

#### `normalize(data: Union[list, dict]) -> Union[list, dict]`

Преобразует словари ELMA Web Data и массивы ELMA Web DataArray в удобный формат словарей: убирает лишнюю информацию,
т.е. пустые значения `Value`, `Data` и `DataArray` из _Item_, а так же вынося значение параметра `Name` в качестве
ключа.

Если входным параметром является структура _Item_, а не _Data_, то он будет преобразован в структуру _Data_
с единственным элементом в массиве `Items`.

Все вложенные элементы будут преобразованы как и внешние.

Примеры:
```python
normalize({'Items': [ {'Name': 'Uid', 'Value': 'token', 'Data': {}, 'DataArray': []} ]})
# {'Uid': 'token'}

normalize({'Name': 'SubjectRF',
           'Value': '',
           'Data': {'Items': [ {'Name': 'Id', 'Value': 10, 'Data': {}, 'DataArray': []} ]},
           'DataArray': []})
# {'SubjectRF': {'Id': 10}}

normalize([ {'Items': [ {'Name': 'Id', 'Value': 2, 'Data': {}, 'DataArray': []},
                        {'Name': 'Uid', 'Value': 'qwerty', 'Data': {}, 'DataArray': []} ]},
            {'Items': [ {'Name': 'Id', 'Value': 5, 'Data': {}, 'DataArray': []},
                        {'Name': 'Uid', 'Value': 'qwerty', 'Data': {}, 'DataArray': []} ]} ])
# [{'Id': 2, 'Uid': 'qwerty'}, {'Id': 5, 'Uid': 'qwerty'}]
```

#### `jsonify(dictionary: Union[list, dict]) -> Union[list, dict]`

Преобразует обычные словари в форматы ELMA Web Data и ELMA Web DataArray. Является обратной операцией для `normalize`.

Поскольку `normalize` не оперирует со структурой _Item_ напрямую, то и результатом данной функции не может
являться структура _Item_.

Все вложенные элементы будут преобразованы как и внешние.

Примеры:
```python
jsonify({'Uid': 'token'})
# {'Items': [ {'Name': 'Uid', 'Value': 'token', 'Data': {}, 'DataArray': []} ]}

jsonify({'SubjectRF': {'Id': 10}})
# {'Items': [ {'Name': 'SubjectRF', 'Value': '',
#              'Data': {'Items': [ {'Name': 'Id', 'Value': 10, 'Data': {}, 'DataArray': []} ]},
#              'DataArray': []} ]}

jsonify([{'Id': 2, 'Uid': 'qwerty'}, {'Id': 5, 'Uid': 'qwerty'}])
# [ {'Items': [ {'Name': 'Id', 'Value': 2, 'Data': {}, 'DataArray': []},
#               {'Name': 'Uid', 'Value': 'qwerty', 'Data': {}, 'DataArray': []} ]},
#   {'Items': [ {'Name': 'Id', 'Value': 5, 'Data': {}, 'DataArray': []},
#               {'Name': 'Uid', 'Value': 'qwerty', 'Data': {}, 'DataArray': []} ]} ])
```
