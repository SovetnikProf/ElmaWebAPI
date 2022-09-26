import os
import unittest
from datetime import datetime, timedelta, timezone

import pytest

from elmawebapi import ElmaAPI, Library, Parser

HOST = os.environ.get("HOST")
USER = os.environ.get("USER")
PASSWORD = os.environ.get("PASSWORD")
TOKEN = os.environ.get("TOKEN")


def handle_connection_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ConnectionError:
            pytest.skip("Skipping ConnectionError")

    return wrapper


@pytest.fixture(scope="class")
def api_mixin(request):
    if HOST is None:
        pytest.skip("Needs .env filled with HOST, USER, PASSWORD and TOKEN parameters")
    request.cls.API = ElmaAPI(HOST, USER, PASSWORD, TOKEN)
    Library.load_from_help(HOST)


@pytest.mark.usefixtures("api_mixin")
class TestAuth(unittest.TestCase):
    @handle_connection_errors
    def test_reconnect_needs_auth(self):
        # ломаем авторизацию, но так, чтобы декоратор needs_auth обратил на это внимание
        self.API.headers = {}

        self.test_clock()

    @handle_connection_errors
    def test_reconnect_request_decorator(self):
        # ломаем авторизацию, но так, чтобы декоратор needs_auth не обратил на это внимание, а запрос ушел в get
        self.API.headers["AuthToken"] = "12345"
        self.API.headers["SessionToken"] = "12345"

        self.test_clock()

    @handle_connection_errors
    def test_clock(self):
        tz = timezone.utc
        time_a = datetime.now(tz=tz) - timedelta(hours=2)  # расхождение было почти в полчаса с нормальным временем
        time_b = datetime.now(tz=tz) + timedelta(hours=2)
        dt = self.API.AuthService.ServerTimeUTC()
        self.assertTrue(time_a < dt < time_b)

        dt = self.API.AuthService.ServerTime()
        self.assertIsNotNone(dt)  # как это тестировать?

    @handle_connection_errors
    def test_exceptions(self):
        with pytest.raises(ValueError):
            ElmaAPI(HOST, USER, "nopassword", TOKEN)
        with pytest.raises(ConnectionError):
            ElmaAPI("http://a.abcdef/", USER, PASSWORD, TOKEN)


@pytest.mark.usefixtures("api_mixin")
class TestEntity(unittest.TestCase):
    @handle_connection_errors
    def test_load(self):
        contractor = self.API.EntityService.Load(params={"type": Library.uuids.ContractorLegal, "id": "54124"})
        self.assertEqual(contractor["Id"], "54124")

    @handle_connection_errors
    def test_count(self):
        count = self.API.EntityService.Count(params={"type": Library.uuids.ContractorLegal, "q": "Id = 54124"})
        self.assertEqual(count, 1)

    @handle_connection_errors
    def test_query(self):
        query = self.API.EntityService.Query(
            params={"type": Library.uuids.ContractorLegal, "q": "Id in (0, 53849, 54124)", "sort": "Id"}
        )
        self.assertEqual(query[0]["Id"], "53849")
        self.assertEqual(query[1]["Id"], "54124")

    @unittest.skip
    def test_insert(self):
        pk = self.API.EntityService.Insert(Parser.uglify({"Name": "Тест"}), Library.uuids.ContractorLegal)
        self.assertEqual(pk, 7)

    @unittest.skip
    def test_update(self):
        new_name = "Тест update"
        pk = self.API.EntityService.Update(Parser.uglify({"Name": new_name}), Library.uuids.ContractorLegal, 7)
        self.assertEqual(pk, 7)
        obj = self.API.EntityService.Load(params={"type": Library.uuids.ContractorLegal, "id": 7})
        self.assertEqual(obj["Name"], new_name)


@pytest.mark.usefixtures("api_mixin")
class TestWorkflow(unittest.TestCase):
    @handle_connection_errors
    def test_startable(self):
        startable = self.API.WorkflowService.StartableProcesses()
        self.assertTrue(isinstance(startable, dict) and "Groups" in startable and "Processes" in startable)
