import copy
import json
from typing import AnyStr


AnyBasic = AnyStr | int | float | bool


class Parser:
    @staticmethod
    def _make_item(
        name: AnyStr, value: AnyBasic | None = None, data: dict | None = None, dataarray: list | None = None
    ) -> dict:
        """Return dictionary that represents json Item structure"""
        result = {"Name": name}
        if value is not None:
            result["Value"] = value
        if data is not None:
            result["Data"] = data
        if dataarray is not None:
            result["DataArray"] = dataarray
        return result

    @staticmethod
    def _make_data(items: list) -> dict:
        """Return dictionary that represents json Data structure"""
        return {"Items": items}

    @classmethod
    def normalize(cls, data: list | dict) -> list | dict:
        """Transforms Data dictionary into a user-friendly dictionary.
        In short, it takes key from item's name and values from item's value or data(array).

        E.g., Data dictionary
            {'Items': [ {'Name': 'Uid', 'Value': 'token', 'Data': {}, 'DataArray': []} ]}
        will be transformed into
            {'Uid': 'token'}

        Item dictionary is handled as Data dictionary with one element in 'Items' entry.
        So this item
            {'Name': 'SubjectRF', 'Value': '',
             'Data': {'Items': [ {'Name': 'Id', 'Value': 10, 'Data': {}, 'DataArray': []} ]}
            }
        will be transformed into
            {'SubjectRF': {'Id': 10}}

        DataArray is handled as list of Data dictionaries, and this array
            [ {'Items': [ {'Name': 'Id', 'Value': 2, 'Data': {}, 'DataArray': []},
                          {'Name': 'Uid', 'Value': 'qwerty', 'Data': {}, 'DataArray': []} ]},
              {'Items': [ {'Name': 'Id', 'Value': 5, 'Data': {}, 'DataArray': []},
                          {'Name': 'Uid', 'Value': 'qwerty', 'Data': {}, 'DataArray': []} ]} ]
        will be transformed into
            [{'Id': 2, 'Uid': 'qwerty'}, {'Id': 5, 'Uid': 'qwerty'}]

        All nested elements will be handled in accordance with these rules.
        """

        # if data is DataArray
        if type(data) == list:
            return [cls.normalize(el) for el in data]

        # if something went wrong with the type
        if type(data) != dict:
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
            elif result[name].get("Data", {}):
                result[name] = cls.normalize(result[name]["Data"])
            elif result[name].get("DataArray", []):
                result[name] = cls.normalize(result[name]["DataArray"])
            else:
                result[name] = None
        return result

    @classmethod
    def uglify(cls, dictionary: list | dict) -> list | dict:
        """Reverse process of normalize: transforms simple dictionaries into humongous json dictionaries.

        Because in normalize Item structure is treated as Data structure with one item in Items array, this method
        cannot build the Item structure. It will return data in either Data or DataArray structures.

        Using the results from normalize method's examples:
            1.  {'Uid': 'token'}
            will be transformed into
                {'Items': [ {'Name': 'Uid', 'Value': 'token', 'Data': {}, 'DataArray': []} ]}
            2.  {'SubjectRF': {'Id': 10}}
            will be transformed into
                {'Items': [ {'Name': 'SubjectRF', 'Value': '', 'DataArray': [],
                 'Data': {'Items': [ {'Name': 'Id', 'Value': 10, 'Data': {}, 'DataArray': []} ]}
                } ]}
            3.  [{'Id': 2, 'Uid': 'qwerty'}, {'Id': 5, 'Uid': 'qwerty'}]
            will be transformed into
                [ {'Items': [ {'Name': 'Id', 'Value': 2, 'Data': {}, 'DataArray': []},
                              {'Name': 'Uid', 'Value': 'qwerty', 'Data': {}, 'DataArray': []} ]},
                  {'Items': [ {'Name': 'Id', 'Value': 5, 'Data': {}, 'DataArray': []},
                              {'Name': 'Uid', 'Value': 'qwerty', 'Data': {}, 'DataArray': []} ]} ]
        """

        if type(dictionary) == list:
            return [cls.uglify(el) for el in dictionary]

        if type(dictionary) != dict:
            raise TypeError(f"Dict expected, got {type(dictionary)}")

        result = cls._make_data([])

        for k, v in dictionary.items():
            if type(v) == list:  # dataarray
                result["Items"].append(cls._make_item(k, dataarray=cls.uglify(v)))
            elif type(v) == dict:  # data
                result["Items"].append(cls._make_item(k, data=cls.uglify(v)))
            else:
                result["Items"].append(cls._make_item(k, value=v))
        return result

    @staticmethod
    def parse(string: str) -> dict:
        return json.loads(string)


{
    "Items": [
        {"Name": "ProcessHeaderId", "Value": 174},
        {"Name": "ProcessName", "Value": "Generation X"},
        {"Name": "Context", "Data": {"Items": [{"Name": "answer", "Value": "{}"}, {"Name": "processid"}]}},
    ]
}
