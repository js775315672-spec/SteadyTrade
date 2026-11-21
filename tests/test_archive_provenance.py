import hashlib
import tempfile
import unittest
from pathlib import Path
from archive_provenance import monthly_spot_manifest, manifests, verify_checksum


class ProvenanceTests(unittest.TestCase):
    def test_2024_milliseconds(self):
        x=monthly_spot_manifest("BTCUSDT","1m",2024,12)
        self.assertEqual(x["timestamp_unit"],"ms")
        self.assertTrue(x["url"].endswith("BTCUSDT-1m-2024-12.zip"))

    def test_2025_microseconds(self):
        x=monthly_spot_manifest("BTCUSDT","1m",2025,1)
        self.assertEqual(x["timestamp_unit"],"us")

    def test_checksum_url(self):
        x=monthly_spot_manifest("ETHUSDT","1h",2026,1)
        self.assertEqual(x["checksum_url"],x["url"]+".CHECKSUM")

    def test_cross_year_manifest(self):
        x=manifests("BTCUSDT","1m",2024,12,2025,2)
        self.assertEqual([i["timestamp_unit"] for i in x],["ms","us","us"])

    def test_invalid_symbol(self):
        with self.assertRaises(ValueError):
            monthly_spot_manifest("../BTC","1m",2024,1)

    def test_invalid_interval(self):
        with self.assertRaises(ValueError):
            monthly_spot_manifest("BTCUSDT","2s",2024,1)

    def test_reversed_dates(self):
        with self.assertRaises(ValueError):
            manifests("BTCUSDT","1m",2025,2,2025,1)

    def test_checksum_success(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"BTCUSDT-1m-2024-12.zip"
            p.write_bytes(b"offline synthetic archive")
            sha=hashlib.sha256(p.read_bytes()).hexdigest()
            self.assertTrue(verify_checksum(p,f"{sha}  {p.name}")["verified"])

    def test_checksum_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"test.zip"
            p.write_bytes(b"abc")
            with self.assertRaises(ValueError):
                verify_checksum(p,"0"*64+"  test.zip")

    def test_checksum_filename_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"test.zip"
            p.write_bytes(b"abc")
            sha=hashlib.sha256(p.read_bytes()).hexdigest()
            with self.assertRaises(ValueError):
                verify_checksum(p,sha+"  other.zip")


if __name__=="__main__":
    unittest.main()
