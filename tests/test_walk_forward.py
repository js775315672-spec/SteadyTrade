import unittest
from walk_forward import Fold, expanding_folds


class WalkForwardTests(unittest.TestCase):
    def test_expanding_nonoverlapping(self):
        self.assertEqual(expanding_folds(20, 8, 4), [
            Fold(0, 8, 8, 12), Fold(0, 12, 12, 16), Fold(0, 16, 16, 20)])

    def test_embargo_gap(self):
        folds = expanding_folds(20, 8, 4, gap=2)
        self.assertEqual(folds[0], Fold(0, 8, 10, 14))
        self.assertTrue(all(f.train_end + 2 == f.test_start for f in folds))

    def test_no_partial_final_fold(self):
        self.assertEqual(expanding_folds(10, 8, 4), [])

    def test_custom_step(self):
        self.assertEqual([f.test_start for f in expanding_folds(20, 8, 4, step=2)], [8, 10, 12, 14, 16])

    def test_invalid_params(self):
        for args in [(20, 0, 4), (20, 8, 0), (-1, 8, 4), (20, 8, 4)]:
            if args == (20, 8, 4):
                with self.assertRaises(ValueError):
                    expanding_folds(*args, gap=-1)
            else:
                with self.assertRaises(ValueError):
                    expanding_folds(*args)
        with self.assertRaises(ValueError):
            expanding_folds(20, 8, 4, step=0)
        with self.assertRaises(ValueError):
            expanding_folds(20, True, 4)

    def test_boundaries_never_leak(self):
        for f in expanding_folds(100, 30, 10, gap=3):
            self.assertLessEqual(f.train_end, f.test_start)
            self.assertLessEqual(f.test_end, 100)
