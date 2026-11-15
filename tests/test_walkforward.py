import unittest
from walkforward import walk_forward_windows

class WalkForwardTests(unittest.TestCase):
    def test_nonoverlap_with_purge_gap(self):
        windows = walk_forward_windows(30, 10, 5, gap=2)
        self.assertEqual(len(windows), 3)
        for w in windows:
            self.assertEqual(w.test_start - w.train_end, 2)
            self.assertLessEqual(w.test_end, 30)
            self.assertLessEqual(w.train_end, w.test_start)

    def test_exact_boundary(self):
        windows = walk_forward_windows(17, 10, 5, gap=2)
        self.assertEqual([(w.train_start,w.train_end,w.test_start,w.test_end)
                          for w in windows], [(0,10,12,17)])

    def test_short_series(self):
        self.assertEqual(walk_forward_windows(5, 10, 5), [])

    def test_bad_parameters(self):
        for args in [(10,0,2), (10,5,0), (-1,2,2), (10,5,2,-1)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                walk_forward_windows(*args)
        with self.assertRaises(TypeError):
            walk_forward_windows(True, 2, 2)
        with self.assertRaises(ValueError):
            walk_forward_windows(10, 5, 2, step=0)

    def test_test_windows_do_not_overlap_with_default_step(self):
        windows = walk_forward_windows(40, 10, 5)
        for previous, current in zip(windows, windows[1:]):
            self.assertEqual(previous.test_end, current.test_start)
