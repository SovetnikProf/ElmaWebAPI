from elmawebapi import Library

import random
import uuid
import unittest


class TestLibrary(unittest.TestCase):
    def test_library_uuid(self):
        uid = str(uuid.uuid4())
        library = Library()
        library.register_uuid("TestObject", uid)
        self.assertEqual(library.uuids.TestObject, uid)

    def test_library_process(self):
        process, token = random.randint(1, 100), str(uuid.uuid4())
        library = Library()
        library.register_process("TestProcessHeader", header=process)
        library.register_process("TestProcessToken", token=token)
        library.register_process("TestProcess", header=process, token=token)
        self.assertEqual(library.process_headers.TestProcessHeader, process)
        self.assertEqual(library.process_tokens.TestProcessToken, token)
        self.assertEqual(library.process_headers.TestProcess, process)
        self.assertEqual(library.process_tokens.TestProcess, token)

    def test_library_load(self):
        host = "http://bpm-demo.elma-bpm.ru/"
        library = Library()
        library.load_from_help(host)

        cl, proc = "3325eab1-fe46-4900-a617-c6fb54ac24c0", "e4f4752a-18e2-40c2-ae52-8113ef316272"
        self.assertEqual(library.uuids.ContractorLegal, cl)
        self.assertEqual(library.uuids.P_DinamicheskieZonyOtvetst, proc)
