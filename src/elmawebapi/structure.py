import copy
import json
from typing import TYPE_CHECKING, Any, Iterable, Optional, Union

if TYPE_CHECKING:
    Value = str | int | float | bool
    Item = dict[str, Union[Value, "Data", "DataArray"]]
    Data = dict[str, Union[str, list[Item]]] | None
    DataArray = list[Data]


class Parser:
    """
    Преобразование и очистка типов данных Elma.
    """

    @staticmethod
    def _make_item(
        name: str,
        value: Optional["Value"] = None,
        data: Optional["Data"] = None,
        dataarray: Optional["DataArray"] = None,
    ) -> dict:
        """
        Возвращает словарь, представляющий собой структуру Item.
        """
        result = {
            "Name": name,
            "Value": value if value is not None else "",
            "Data": data,
            "DataArray": dataarray if dataarray is not None else [],
        }
        return result

    @staticmethod
    def _make_data(items: list["Item"]) -> dict:
        """
        Возвращает словарь, представляющий собой структуру Data.
        """
        return {"Items": items, "Value": ""}

    @classmethod
    def normalize(cls, data: Union["Data", "DataArray"]) -> ["Data", "DataArray"]:
        """
        Преобразует словарь Data в удобочитаемый словарь. Вкратце, убирает пустые значения и лишние вложенности.

        Например, словарь Data
            {"Items": [ {"Name": "Uid", "Value": "token", "Data": None, "DataArray": []} ], "Value": ""}
        будет преобразован в
            {"Uid": "token"}

        Тип Item трактуется как тип Data с одним элементом в списке "Items", поэтому словарь
            {"Name": "SubjectRF", "Value": "", "DataArray": [],
             "Data": {"Items": [ {"Name": "Id", "Value": "10", "Data": None, "DataArray": []} ]}
            }
        будет преобразован в
            {"SubjectRF": {"Id": "10"}}

        Тип DataArray считается списком элементов типа Data dictionaries, и следующий список
            [ {"Items": [ {"Name": "Id", "Value": "2", "Data": None, "DataArray": []},
                          {"Name": "Uid", "Value": "qwerty", "Data": None, "DataArray": []} ]},
              {"Items": [ {"Name": "Id", "Value": "5", "Data": None, "DataArray": []},
                          {"Name": "Uid", "Value": "qwerty", "Data": None, "DataArray": []} ]} ]
        будет преобразован в
            [{"Id": "2", "Uid": "qwerty"}, {"Id": "5", "Uid": "qwerty"}]

        Все вложенные элементы будут так же преобразованы согласно этим правилам.
        """

        # if data is DataArray
        if isinstance(data, list):
            return [cls.normalize(el) for el in data]

        # if something went wrong with the type
        if not isinstance(data, dict):
            raise TypeError(f"Dict expected, got {type(data)}")

        # if data is Item
        if data.get("Items") is None:
            return cls.normalize({"Items": [data]})

        result = {}
        for item in data["Items"]:
            # copy each item into result
            name = item["Name"]
            result[name] = copy.copy(item)

            # find value of parameter
            if result[name].get("Value", ""):
                result[name] = result[name]["Value"]
            elif result[name].get("Data", None):
                result[name] = cls.normalize(result[name]["Data"])
            elif result[name].get("DataArray", []):
                result[name] = cls.normalize(result[name]["DataArray"])
            else:
                result[name] = None
        return result

    @classmethod
    def uglify(cls, dictionary: Union["Data", "DataArray"]) -> Union["Data", "DataArray"]:
        """
        Процесс, обратный ``normalize``: преобразует обычные словари и списки словарей в типы Data и DataArray.

        Тип Item, так же как и в ``normalize``, не используется в преобразовании напрямую.

        Для примеров возьмем результаты примеров из normalize:
            1.  {"Uid": "token"}
            будет преобразован в
                {"Items": [ {"Name": "Uid", "Value": "token", "Data": None, "DataArray": []} ], "Value": ""}
            2.  {"SubjectRF": {"Id": 10}}
            будет преобразован в
                {"Items": [
                    {"Name": "SubjectRF", "Value": "", "Data": {
                        "Items": [ {"Name": "Id", "Value": 10, "Data": None, "DataArray": []} ], "Value": ""},
                     "DataArray": []
                    }
                ], "Value: ""}
            3.  [{"Id": "2", "Uid": "qwerty"}, {"Id": "5", "Uid": "qwerty"}]
            будет преобразован в
                [ {"Items": [ {"Name": "Id", "Value": "2", "Data": None, "DataArray": []},
                              {"Name": "Uid", "Value": "qwerty", "Data": None, "DataArray": []} ], "Value": ""},
                  {"Items": [ {"Name": "Id", "Value": "5", "Data": None, "DataArray": []},
                              {"Name": "Uid", "Value": "qwerty", "Data": None, "DataArray": []} ], "Value": ""} ]
        """

        if isinstance(dictionary, list):
            return [cls.uglify(el) for el in dictionary]

        if not isinstance(dictionary, dict):
            raise TypeError(f"Dict expected, got {type(dictionary)}")

        result = cls._make_data([])

        for key, value in dictionary.items():
            if isinstance(value, list):  # dataarray
                result["Items"].append(cls._make_item(key, dataarray=cls.uglify(value)))
            elif isinstance(value, dict):  # data
                result["Items"].append(cls._make_item(key, data=cls.uglify(value)))
            else:
                result["Items"].append(cls._make_item(key, value=value))
        return result

    @staticmethod
    def parse(string: str) -> dict[str, Any]:
        """
        Алиас для ``json.loads``.
        """
        return json.loads(string)

    @staticmethod
    def unwrap(seq: Iterable[dict], field: str = "Id", check_last: bool = False) -> "Item":
        """
        Функция преобразовывает список словарей в словарь словарей по какому-либо ключу.

        Примеры, ::

            >>> Parser.unwrap([{"Id": "1", "Value": "one"}, {"Id": "2", "Value": "two"}])
            {"1": {"Value": "one"}, "2": {"Value": "two"}}
            >>> Parser.unwrap([{"Id": "1", "Value": "one"}, {"Id": "2", "Value": "two"}], check_last=True)
            {"1": "one", "2": "two"}
            >>> Parser.unwrap([{"Id": "1", "Value": "one"}, {"Id": "2", "Value": "two"}], field="Value")
            {"one": {"Id": "1"}, "two": {"Id": "2"}}

        Args:
            seq: список словарей с данными
            field: ключевое поле
            check_last: не делать словарь из одного оставшегося элемента.
        """

        def pop(data: dict, key: str, check_if_last: bool) -> Union["Item", "Value"]:
            data.pop(key)
            if check_if_last and len(data) == 1:
                return list(data.values())[0]
            return data

        return {x[field]: pop(x, field, check_last) for x in seq}
