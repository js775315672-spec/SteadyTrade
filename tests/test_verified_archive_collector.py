import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from verified_archive_collector import download_verified_month


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.close()


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self.tmp.name)
        self.name = "BTCUSDT-1m-2024-12.zip"
        self.payload = b"synthetic ZIP bytes for checksum tests"
        self.digest = hashlib.sha256(self.payload).hexdigest()

    def tearDown(self):
        self.tmp.cleanup()

    def opener(self, url, timeout):
        if url.endswith(".CHECKSUM"):
            return FakeResponse((self.digest+"  "+self.name+"\n").encode())
        return FakeResponse(self.payload)

    def test_verified_download(self):
        receipt=download_verified_month("BTCUSDT","1m",2024,12,
                    self.folder,opener=self.opener)
        self.assertTrue(receipt["verified"])
        self.assertEqual((self.folder/self.name).read_bytes(),self.payload)

    def test_no_overwrite(self):
        (self.folder/self.name).write_bytes(b"original")
        with self.assertRaises(FileExistsError):
            download_verified_month("BTCUSDT","1m",2024,12,
                self.folder,opener=self.opener)
        self.assertEqual((self.folder/self.name).read_bytes(),b"original")

    def test_checksum_mismatch_fails_closed(self):
        def bad(url,timeout):
            if url.endswith(".CHECKSUM"):
                return FakeResponse(("0"*64+"  "+self.name).encode())
            return FakeResponse(self.payload)
        with self.assertRaises(ValueError):
            download_verified_month("BTCUSDT","1m",2024,12,self.folder,opener=bad)
        self.assertFalse((self.folder/self.name).exists())

    def test_byte_limit(self):
        with self.assertRaises(ValueError):
            download_verified_month("BTCUSDT","1m",2024,12,
                self.folder,max_zip_bytes=3,opener=self.opener)
        self.assertFalse((self.folder/self.name).exists())

    def test_invalid_symbol_no_network(self):
        def forbidden(url,timeout):
            raise AssertionError("unexpected network")
        with self.assertRaises(ValueError):
            download_verified_month("../BTC","1m",2024,12,self.folder,opener=forbidden)

    def test_invalid_folder(self):
        with self.assertRaises(ValueError):
            download_verified_month("BTCUSDT","1m",2024,12,
                self.folder/"missing",opener=self.opener)


if __name__ == "__main__":
    unittest.main()
