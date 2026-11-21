import csv
import tempfile
import unittest
import zipfile
from pathlib import Path

from offline_walkforward import evaluate_archive


class ArchiveWalkforwardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name)/"klines.zip"
        rows = []
        for i in range(90):
            t = 1609459200000 + i*60000
            price = 100 + i*0.1
            rows.append([t,price,price+1,price-1,price,10,
                         t+59999,1000,10,5,500,0])
        with zipfile.ZipFile(self.path,"w") as z:
            z.writestr("klines.csv","\n".join(",".join(map(str,row)) for row in rows))

    def tearDown(self):
        self.temp.cleanup()

    def test_three_nonoverlapping_oos_folds(self):
        r = evaluate_archive(self.path,train_size=30,test_size=20,
                             strategy="ema",fast=2,slow=5)
        self.assertEqual(r["fold_count"],3)
        self.assertEqual([f["test"] for f in r["folds"]],
                         [[30,50],[50,70],[70,90]])
        self.assertIsNone(r["aggregate_equity"])

    def test_gap_purges_boundary(self):
        r = evaluate_archive(self.path,train_size=30,test_size=20,gap=5)
        self.assertEqual(r["folds"][0]["train"],[0,30])
        self.assertEqual(r["folds"][0]["test"],[35,55])

    def test_insufficient_history(self):
        with self.assertRaises(ValueError):
            evaluate_archive(self.path,train_size=90,test_size=20)

    def test_all_three_strategies(self):
        for s in ("ema","rsi","macd"):
            with self.subTest(strategy=s):
                r = evaluate_archive(self.path,train_size=40,test_size=20,
                                     strategy=s)
                self.assertEqual(r["fold_count"],2)

    def test_bad_archive_rejected(self):
        with zipfile.ZipFile(self.path,"w") as z:
            z.writestr("other.txt","broken")
        with self.assertRaises(ValueError):
            evaluate_archive(self.path,train_size=30,test_size=20)


if __name__ == "__main__":
    unittest.main()
