import unittest
from types import SimpleNamespace
from walkforward_audit import audit_folds, audit_oos_reports
from walk_forward import expanding_folds


def report(a,b,c,d,ret=0.1,mdd=0.02,trades=2):
    return {"train":[a,b],"test":[c,d],"net_return":ret,
            "max_drawdown":mdd,"trade_count":trades}


class WalkForwardAuditTests(unittest.TestCase):
    def test_valid_expanding_folds(self):
        folds=expanding_folds(100,30,20,gap=5)
        self.assertEqual(audit_folds(folds,100)["fold_count"],3)

    def test_reject_overlapping_test_windows(self):
        folds=expanding_folds(100,30,20,step=10)
        with self.assertRaisesRegex(ValueError,"overlapping"):
            audit_folds(folds,100)

    def test_reject_train_test_overlap(self):
        with self.assertRaises(ValueError):
            audit_folds([SimpleNamespace(train_start=0,train_end=30,
                     test_start=29,test_end=40)],100)

    def test_reject_out_of_range(self):
        with self.assertRaises(ValueError):
            audit_folds([SimpleNamespace(train_start=0,train_end=30,
                     test_start=30,test_end=101)],100)

    def test_valid_reports_no_compounding(self):
        result=audit_oos_reports([report(0,30,30,50),
                                  report(0,50,50,70)],n_rows=100)
        self.assertIsNone(result["compounded_return"])

    def test_report_overlap(self):
        with self.assertRaises(ValueError):
            audit_oos_reports([report(0,30,30,50),report(0,40,40,60)],
                              n_rows=100)

    def test_nonfinite_return(self):
        with self.assertRaises(ValueError):
            audit_oos_reports([report(0,30,30,50,float("nan"))],n_rows=100)

    def test_negative_trades(self):
        with self.assertRaises(ValueError):
            audit_oos_reports([report(0,30,30,50,trades=-1)],n_rows=100)

    def test_empty_folds(self):
        with self.assertRaises(ValueError):
            audit_folds([],100)

    def test_boolean_boundary_rejected(self):
        with self.assertRaises(ValueError):
            audit_folds([SimpleNamespace(train_start=False,train_end=30,
                     test_start=30,test_end=50)],100)

if __name__ == "__main__":
    unittest.main()
