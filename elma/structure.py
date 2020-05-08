import copy
from typing import AnyStr, Any, Union


def make_item(name: AnyStr, value: Any = '', data: dict = {}, dataarray: list = []) -> dict:
    """ Return dictionary that represents json Item structure """
    return {'Name': name, 'Value': value, 'Data': data, 'DataArray': dataarray}


def make_data(items: list) -> dict:
    """ Return dictionary that represents json Data structure """
    return {'Items': items}


def normalize(data: Union[list, dict]) -> Union[list, dict]:
    """ Transforms Data dictionary into a user-friendly dictionary.
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

        All nested elements will be handled in accordance with this rules.
    """

    # if data is DataArray
    if type(data) == list:
        return [normalize(el) for el in data]

    # if something went wrong with the type
    if type(data) != dict:
        raise TypeError(f'Dict expected, got {type(data)}')

    # if data is Item
    if data.get('Items') is None:
        return normalize({'Items': [data]})

    result = {}
    for item in data['Items']:
        # copy each item into result
        name = item['Name']
        result[name] = copy.copy(item)

        # find value of parameter
        if result[name].get('Value', ''):
            result[name] = result[name]['Value']
        elif result[name].get('Data', {}):
            result[name] = normalize(result[name]['Data'])
        elif result[name].get('DataArray', []):
            result[name] = normalize(result[name]['DataArray'])
        else:
            result[name] = None
    return result


def jsonify(dictionary: Union[list, dict]) -> Union[list, dict]:
    """ Reverse process of normalize: transforms simple dictionaries into humongous json dictionaries.

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
        return [jsonify(el) for el in dictionary]

    if type(dictionary) != dict:
        raise TypeError(f'Dict expected, got {type(dictionary)}')

    result = make_data([])

    for k, v in dictionary.items():
        if type(v) == list:  # dataarray
            result['Items'].append(make_item(k, dataarray=jsonify(v)))
        elif type(v) == dict:  # data
            result['Items'].append(make_item(k, data=jsonify(v)))
        else:
            result['Items'].append(make_item(k, value=v))
    return result