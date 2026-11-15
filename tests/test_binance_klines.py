import tempfile
import unittest
import zipfile
from datetime import timezone
from pathlib import Path
from binance_klines import parse_klines, read_zip_csv

ROW = ['1609459200000','100','110','90','105','12','1609459259999','1200','5','6','7','0']

class BinanceKlineTests(unittest.TestCase):
    def test_valid_utc(self):
        bar = parse_klines([ROW])[0]
        self.assertEqual(bar.close, 105)
        self.assertEqual(bar.open_time.tzinfo, timezone.utc)

    def test_microseconds(self):
        row = ROW.copy()
        row[0], row[6] = str(int(row[0])*1000), str(int(row[6])*1000)
        self.assertEqual(parse_klines([row], 'us')[0].close, 105)

    def test_invalid_values(self):
        for index, value in ((4, 'nan'), (2, '99'), (5, '-1')):
            row = ROW.copy()
            row[index] = value
            with self.assertRaises(ValueError):
                parse_klines([row])

    def test_duplicate_and_bad_columns(self):
        with self.assertRaises(ValueError):
            parse_klines([ROW, ROW])
        with self.assertRaises(ValueError):
            parse_klines([ROW[:-1]])

    def test_zip_and_size_limit(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'data.zip'
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('BTCUSDT-1m.csv', ','.join(ROW)+'\n')
            self.assertEqual(len(read_zip_csv(path)), 1)
            with self.assertRaises(ValueError):
                read_zip_csv(path, max_uncompressed_bytes=1)

    def test_reject_multiple_members(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'data.zip'
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('a.csv', ','.join(ROW))
                archive.writestr('b.csv', ','.join(ROW))
            with self.assertRaises(ValueError):
                read_zip_csv(path)
