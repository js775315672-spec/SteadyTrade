import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from archive_batch import collect_months, write_receipt


class Response(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self,*args): self.close()


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.folder=Path(self.temp.name)
        self.payload=b"synthetic archive"
        self.sha=hashlib.sha256(self.payload).hexdigest()

    def tearDown(self):
        self.temp.cleanup()

    def opener(self,url,timeout):
        name=url.rsplit("/",1)[-1].removesuffix(".CHECKSUM")
        if url.endswith(".CHECKSUM"):
            return Response(f"{self.sha}  {name}\n".encode())
        return Response(self.payload)

    def test_two_months_receipts(self):
        result=collect_months("BTCUSDT","1m",2024,12,2025,1,
                             self.folder,opener=self.opener)
        self.assertEqual(result["verified_months"],2)
        self.assertEqual([x["timestamp_unit"] for x in result["receipts"]],
                         ["ms","us"])

    def test_max_months_enforced_before_network(self):
        def forbidden(url,timeout):
            raise AssertionError("unexpected network")
        with self.assertRaises(ValueError):
            collect_months("BTCUSDT","1m",2021,1,2021,5,
                           self.folder,max_months=3,opener=forbidden)

    def test_receipt_exclusive(self):
        target=self.folder/"receipt.json"
        write_receipt({"verified_months":1},target)
        with self.assertRaises(FileExistsError):
            write_receipt({"verified_months":2},target)

    def test_checksum_failure(self):
        def bad(url,timeout):
            if url.endswith(".CHECKSUM"):
                return Response(("0"*64+"  "+url.rsplit("/",1)[-1].removesuffix(".CHECKSUM")).encode())
            return Response(self.payload)
        with self.assertRaises(ValueError):
            collect_months("BTCUSDT","1m",2024,12,2024,12,
                           self.folder,opener=bad)
        self.assertEqual(list(self.folder.glob("*.zip")),[])


if __name__=="__main__":
    unittest.main()
