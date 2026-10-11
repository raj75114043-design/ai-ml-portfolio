import pandas as pd
from src.analysis import analyse

df = pd.read_csv("data/batch_results.csv")


def test_oos_batch_detected():
    res, _ = analyse(df, "assay_pct")
    assert "B2026052" in set(res.loc[res.OOS, "batch_id"])


def test_drift_flagged_as_oot():
    res, _ = analyse(df, "assay_pct")
    assert res.OOT.sum() >= 1 and not (res.OOT & res.OOS).any()


def test_cpk_reported():
    _, stats = analyse(df, "assay_pct")
    assert stats["cpk"] > 0


def test_dissolution_one_sided_spec():
    _, stats = analyse(df, "dissolution_pct")
    assert stats["usl"] is None and stats["cpk"] > 0
