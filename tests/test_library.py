from elmawebapi import Library

import random
import uuid
import unittest


class TestLibrary(unittest.TestCase):
    def test_library_uuid(self):
        uid = str(uuid.uuid4())
        Library.register_uuid("TestObject", uid)
        self.assertEqual(Library.uuids.TestObject, uid)

    def test_library_process(self):
        process, token = random.randint(1, 100), str(uuid.uuid4())
        Library.register_process("TestProcessHeader", header=process)
        Library.register_process("TestProcessToken", token=token)
        Library.register_process("TestProcess", header=process, token=token)
        self.assertEqual(Library.process_headers.TestProcessHeader, process)
        self.assertEqual(Library.process_tokens.TestProcessToken, token)
        self.assertEqual(Library.process_headers.TestProcess, process)
        self.assertEqual(Library.process_tokens.TestProcess, token)

    def test_library_load(self):
        host = "http://bpm-demo.elma-bpm.ru/"
        Library.load_from_help(host)

        cl, proc = "3325eab1-fe46-4900-a617-c6fb54ac24c0", "e4f4752a-18e2-40c2-ae52-8113ef316272"
        self.assertEqual(Library.uuids.ContractorLegal, cl)
        self.assertEqual(Library.uuids.P_DinamicheskieZonyOtvetst, proc)
