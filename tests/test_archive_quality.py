import unittest
from datetime import datetime, timezone, timedelta
from binance_klines import Kline
from archive_quality import validate_klines


def sample(n=4):
    start = datetime(2021,1,1,tzinfo=timezone.utc)
    return [Kline(start+timedelta(minutes=i),100,101,99,100,1) for i in range(n)]


class ArchiveQualityTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate_klines(sample())["gaps"],0)

    def test_missing_candle(self):
        rows = sample()
        del rows[1]
        with self.assertRaisesRegex(ValueError,"missing candle"):
            validate_klines(rows)

    def test_duplicate_candle(self):
        rows = sample()
        rows[2] = rows[1]
        with self.assertRaises(ValueError):
            validate_klines(rows)

    def test_unordered_candle(self):
        rows = sample()
        rows[1],rows[2] = rows[2],rows[1]
        with self.assertRaises(ValueError):
            validate_klines(rows)

    def test_wrong_interval(self):
        with self.assertRaises(ValueError):
            validate_klines(sample(),interval="1h")

    def test_invalid_ohlc(self):
        rows = sample()
        rows[2] = Kline(rows[2].open_time,100,90,99,100,1)
        with self.assertRaises(ValueError):
            validate_klines(rows)

    def test_nonfinite(self):
        rows = sample()
        rows[1] = Kline(rows[1].open_time,100,101,99,100,float("nan"))
        with self.assertRaises(ValueError):
            validate_klines(rows)

    def test_negative_volume(self):
        rows = sample()
        rows[1] = Kline(rows[1].open_time,100,101,99,100,-1)
        with self.assertRaises(ValueError):
            validate_klines(rows)

    def test_unsupported_calendar_interval(self):
        with self.assertRaises(ValueError):
            validate_klines(sample(),interval="1M")

    def test_short_history(self):
        with self.assertRaises(ValueError):
            validate_klines(sample(1))

if __name__ == "__main__":
    unittest.main()
