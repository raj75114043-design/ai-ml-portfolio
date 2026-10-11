"""Train and compare models for imbalanced failure prediction, then pick a cost-optimal threshold."""
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score, precision_recall_curve
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from .features import engineer

ARTIFACTS = Path(__file__).resolve().parent.parent / "artifacts"
DATA = Path(__file__).resolve().parent.parent / "data" / "sensor_data.csv"
COST_FN, COST_FP = 5000, 400  # unplanned breakdown vs unnecessary inspection (illustrative)


def load_split():
    df = pd.read_csv(DATA)
    X, y = engineer(df), df["failure"]
    return train_test_split(X, y, test_size=0.25, stratify=y, random_state=42)


def expected_cost(y, proba, threshold):
    pred = proba >= threshold
    fn = int(((y == 1) & ~pred).sum())
    fp = int(((y == 0) & pred).sum())
    return fn * COST_FN + fp * COST_FP, fn, fp


def best_threshold(y, proba):
    grid = np.round(np.arange(0.02, 0.96, 0.01), 2)
    costs = [expected_cost(y, proba, t)[0] for t in grid]
    return float(grid[int(np.argmin(costs))])


def main():
    X_tr, X_te, y_tr, y_te = load_split()
    candidates = {
        "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(class_weight="balanced", max_iter=2000)),
        "Random Forest": RandomForestClassifier(n_estimators=300, min_samples_leaf=3, class_weight="balanced_subsample",
                                                random_state=42, n_jobs=-1),
    }
    report = {}
    for name, model in candidates.items():
        proba = model.fit(X_tr, y_tr).predict_proba(X_te)[:, 1]
        t = best_threshold(y_te, proba)
        cost, fn, fp = expected_cost(y_te, proba, t)
        report[name] = {"pr_auc": round(average_precision_score(y_te, proba), 3),
                        "roc_auc": round(roc_auc_score(y_te, proba), 3), "threshold": t,
                        "missed_failures": fn, "false_alarms": fp, "expected_cost": cost}
    best = max(report, key=lambda k: report[k]["pr_auc"])
    ARTIFACTS.mkdir(exist_ok=True)
    joblib.dump(candidates[best], ARTIFACTS / "model.joblib")
    meta = {"model": best, "threshold": report[best]["threshold"], "features": list(X_tr.columns),
            "failure_rate": round(float(y_tr.mean()), 4), "comparison": report}
    (ARTIFACTS / "metadata.json").write_text(json.dumps(meta, indent=2))
    return meta


if __name__ == "__main__":
    meta = main()
    print(f"Failure rate: {meta['failure_rate']:.1%}. Selected model: {meta['model']}")
    print(pd.DataFrame(meta["comparison"]).T.to_string())
