from elmawebapi import ElmaAPI, Parser, Library

import pytest
import unittest
from datetime import datetime, timezone, timedelta

HOST = "http://bpm-demo.elma-bpm.ru/"
TOKEN = (
    "0145B63A7C45B1408E9C983A2756E0EF7C3079EBA24E34D39047E8745383146B"
    "3515B112CF50B0D393077031585DE076FADEE11C44459EFB5AE89D91C4A1604E"
)
USER = "bpm_portal_execution"
PASSWORD = "bpm_portal_execution"


def handle_connection_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ConnectionError:
            pytest.skip("Skipping ConnectionError")
    return wrapper


class SetUpMixin:
    def setUp(self) -> None:
        self.API = ElmaAPI(HOST, USER, PASSWORD, TOKEN)
        Library.load_from_help(HOST)


class TestAuth(SetUpMixin, unittest.TestCase):
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


class TestEntity(SetUpMixin, unittest.TestCase):
    @handle_connection_errors
    def test_load(self):
        contractor = self.API.EntityService.Load(params={"type": Library.uuids.ContractorLegal, "id": "3"})
        self.assertEqual(contractor["Id"], "3")

    @handle_connection_errors
    def test_count(self):
        count = self.API.EntityService.Count(params={"type": Library.uuids.ContractorLegal, "q": "Id = 3"})
        self.assertEqual(count, 1)

    @handle_connection_errors
    def test_query(self):
        query = self.API.EntityService.Query(
            params={"type": Library.uuids.ContractorLegal, "q": "Id in (0, 2, 3)", "sort": "Id"}
        )
        self.assertEqual(query[0]["Id"], "2")
        self.assertEqual(query[1]["Id"], "3")

    @unittest.skip
    def test_insert(self):
        pk = self.API.EntityService.Insert(
            Parser.uglify({"Name": "Тест"}), Library.uuids.ContractorLegal
        )
        self.assertEqual(pk, 7)

    @unittest.skip
    def test_update(self):
        new_name = "Тест update"
        pk = self.API.EntityService.Update(Parser.uglify({"Name": new_name}), Library.uuids.ContractorLegal, 7)
        self.assertEqual(pk, 7)
        obj = self.API.EntityService.Load(params={"type": Library.uuids.ContractorLegal, "id": 7})
        self.assertEqual(obj["Name"], new_name)


class TestWorkflow(SetUpMixin, unittest.TestCase):
    @handle_connection_errors
    def test_startable(self):
        startable = self.API.WorkflowService.StartableProcesses()
        self.assertTrue(isinstance(startable, dict) and "Groups" in startable and "Processes" in startable)
