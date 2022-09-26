import unittest

import pytest

from elmawebapi import Parser


class TestNormalize(unittest.TestCase):
    def test_data_single(self):
        x = Parser.normalize({"Items": [{"Name": "Uid", "Value": "token", "Data": None, "DataArray": []}], "Value": ""})
        self.assertDictEqual(x, {"Uid": "token"})

    def test_data_multiple(self):
        x = Parser.normalize(
            {
                "Items": [
                    {"Name": "Uid", "Value": "token", "Data": None, "DataArray": []},
                    {"Name": "Id", "Value": "10", "Data": None, "DataArray": []},
                ],
                "Value": "",
            }
        )
        self.assertDictEqual(x, {"Uid": "token", "Id": "10"})

    def test_data_simplified(self):
        x = Parser.normalize({"Items": [{"Name": "Uid", "Value": "token"}]})
        self.assertDictEqual(x, {"Uid": "token"})

    def test_datalist(self):
        x = Parser.normalize(
            [
                {"Items": [{"Name": "Uid", "Value": "token", "Data": None, "DataArray": []}], "Value": ""},
                {"Items": [{"Name": "Id", "Value": "10", "Data": None, "DataArray": []}], "Value": ""},
            ]
        )
        self.assertListEqual(x, [{"Uid": "token"}, {"Id": "10"}])

    def test_item(self):
        x = Parser.normalize(
            {
                "Name": "SubjectRF",
                "Value": "",
                "Data": {"Items": [{"Name": "Id", "Value": "10", "Data": None, "DataArray": []}]},
                "DataArray": [],
            }
        )
        self.assertDictEqual(x, {"SubjectRF": {"Id": "10"}})

    def test_exception(self):
        with pytest.raises(TypeError):
            Parser.normalize("")


class TestUglify(unittest.TestCase):
    def test_data_single(self):
        x = Parser.uglify({"Uid": "token"})
        self.assertDictEqual(
            x, {"Items": [{"Name": "Uid", "Value": "token", "Data": None, "DataArray": []}], "Value": ""}
        )

    def test_data_multiple(self):
        x = Parser.uglify({"Uid": "token", "Id": "10"})
        self.assertDictEqual(
            x,
            {
                "Items": [
                    {"Name": "Uid", "Value": "token", "Data": None, "DataArray": []},
                    {"Name": "Id", "Value": "10", "Data": None, "DataArray": []},
                ],
                "Value": "",
            },
        )

    def test_datalist(self):
        x = Parser.uglify([{"Uid": "token"}, {"Id": "10"}])
        self.assertListEqual(
            x,
            [
                {"Items": [{"Name": "Uid", "Value": "token", "Data": None, "DataArray": []}], "Value": ""},
                {"Items": [{"Name": "Id", "Value": "10", "Data": None, "DataArray": []}], "Value": ""},
            ],
        )

    def test_nested(self):
        x = Parser.uglify({"SubjectRF": {"Id": "10"}})
        self.assertDictEqual(
            x,
            {
                "Items": [
                    {
                        "Name": "SubjectRF",
                        "Value": "",
                        "Data": {"Items": [{"Name": "Id", "Value": "10", "Data": None, "DataArray": []}], "Value": ""},
                        "DataArray": [],
                    }
                ],
                "Value": "",
            },
        )

    def test_data_dataarray(self):
        x = Parser.uglify({"SubjectRF": [{"Id": "1"}, {"Id": "2"}]})
        self.assertDictEqual(
            x,
            {
                "Items": [
                    {
                        "Name": "SubjectRF",
                        "Value": "",
                        "Data": None,
                        "DataArray": [
                            {"Items": [{"Name": "Id", "Value": "1", "Data": None, "DataArray": []}], "Value": ""},
                            {"Items": [{"Name": "Id", "Value": "2", "Data": None, "DataArray": []}], "Value": ""},
                        ],
                    }
                ],
                "Value": "",
            },
        )

    def test_exception(self):
        with pytest.raises(TypeError):
            Parser.uglify("")


class TestUtils(unittest.TestCase):
    def test_parse(self):
        x = Parser.parse('{"bool": true, "int": 10, "string": "string", "list": [1, 2, 3], "dict": {"key": "value"}}')
        self.assertDictEqual(
            x, {"bool": True, "int": 10, "string": "string", "list": [1, 2, 3], "dict": {"key": "value"}}
        )

    def test_unwrap_simple(self):
        x = Parser.unwrap([{"Id": "1", "Value": "value", "Key": "key"}, {"Id": "2", "Value": "s", "Name": "name"}])
        self.assertDictEqual(x, {"1": {"Value": "value", "Key": "key"}, "2": {"Value": "s", "Name": "name"}})

    def test_unwrap_field(self):
        x = Parser.unwrap(
            [{"Id": "1", "Value": "value", "Key": "key"}, {"Id": "2", "Value": "s", "Name": "name"}], field="Value"
        )
        self.assertDictEqual(x, {"value": {"Id": "1", "Key": "key"}, "s": {"Id": "2", "Name": "name"}})

    def test_unwrap_last(self):
        x = Parser.unwrap([{"Id": "1", "Value": "value"}, {"Id": "2", "Value": "s"}], check_last=True)
        self.assertDictEqual(x, {"1": "value", "2": "s"})
