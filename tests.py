from elma import ElmaAPI, Parser, Library

import unittest
from datetime import datetime, timezone, timedelta


TEST_LABEL_UUID = "325e686a-fbfd-4c6e-88b7-b6e8c8c8b7ca"  # TODO: найти другой объект, этот нельзя создавать из WebAPI


class TestLibrary(unittest.TestCase):
    def test_library_uuid(self):
        Library.register_uuid("TestLabel", TEST_LABEL_UUID)
        self.assertEqual(Library.uuids.TestLabel, TEST_LABEL_UUID)


class SetUpMixin:
    def setUp(self) -> None:
        self.API = ElmaAPI(
            "http://192.168.1.19:8000",
            "Artificer",
            "fAy#L6k_Hs$EdiA*mAa",
            "02969CDAAB144BFA301FE1B5BFD69A44638D46002421054478E0B2B76D5D6004"
            "053B451672EBDCCE6B8523ACBFD4BFB6F1C5C7339954E85F94409CA916493F04",
        )


class TestAuth(SetUpMixin, unittest.TestCase):
    def test_clock(self):
        tz = timezone(timedelta(hours=3))
        time_a = datetime.now(tz=tz)
        dt = self.API.AuthService.ServerTime()
        time_b = datetime.now(tz=tz)

        self.assertTrue(time_a < dt < time_b)


class TestEntity(SetUpMixin, unittest.TestCase):
    def test_load(self):
        contractor = self.API.EntityService.Load(params={"type": Library.uuids.ContractorLegal, "id": "53827"})
        self.assertEqual(contractor["Id"], "53827")

    def test_count(self):
        count = self.API.EntityService.Count(params={"type": Library.uuids.ContractorLegal, "q": "Id = 53827"})
        self.assertEqual(count, 1)

    def test_query(self):
        query = self.API.EntityService.Query(
            params={"type": Library.uuids.ContractorLegal, "q": "Id in (147716, 53827)", "sort": "Id"}
        )
        self.assertEqual(query[0]["Id"], "53827")
        self.assertEqual(query[1]["Id"], "147716")

    @unittest.skip
    def test_insert(self):
        id = self.API.EntityService.Insert(
            Parser.uglify({"NaimenovanieMetki": "Тест создания из ElmaAPI"}), TEST_LABEL_UUID
        )
        self.assertEqual(id, 3)

    @unittest.skip
    def test_update(self):
        new_name = "Тест обновления из ElmaAPI"
        id = self.API.EntityService.Update(Parser.uglify({"NaimenovanieMetki": new_name}), TEST_LABEL_UUID, 3)
        self.assertEqual(id, 3)
        obj = self.API.EntityService.Load(params={"type": TEST_LABEL_UUID, "id": 3})
        self.assertEqual(obj["NaimenovanieMetki"], new_name)


if __name__ == "__main__":
    unittest.main()
