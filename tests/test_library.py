import random
import unittest
import uuid

import pytest

from elmawebapi import Library


class TestLibrary(unittest.TestCase):
    def test_uuid(self):
        uid = str(uuid.uuid4())
        Library.register_uuid("TestObject", uid)
        self.assertEqual(Library.uuids.TestObject, uid)

    def test_process(self):
        process, token = random.randint(1, 100), str(uuid.uuid4())
        Library.register_process("TestProcessHeader", header=process)
        Library.register_process("TestProcessToken", token=token)
        Library.register_process("TestProcess", header=process, token=token)
        self.assertEqual(Library.processes.TestProcessHeader.header, process)
        self.assertEqual(Library.processes.TestProcessToken.token, token)
        self.assertEqual(Library.processes.TestProcess.header, process)
        self.assertEqual(Library.processes.TestProcess.token, token)

    def test_load(self):
        host = "http://bpm-demo.elma-bpm.ru/"
        Library.load_from_help(host)

        cl, proc = "3325eab1-fe46-4900-a617-c6fb54ac24c0", "e4f4752a-18e2-40c2-ae52-8113ef316272"
        self.assertEqual(Library.uuids.ContractorLegal, cl)
        self.assertEqual(Library.uuids.P_DinamicheskieZonyOtvetst, proc)

    def test_process_exception(self):
        with pytest.raises(ValueError):
            Library.register_process("TestException")

    def test_load_exception(self):
        with pytest.raises(ConnectionError):
            Library.load_from_help("http://a.abcdef/")
