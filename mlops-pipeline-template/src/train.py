"""Train, evaluate and version a model. Logs to MLflow when it is installed."""
import json
from pathlib import Path
import joblib
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import train_test_split

ARTIFACTS = Path("artifacts")
PARAMS = {"n_estimators": 200, "max_depth": 6, "random_state": 42}
QUALITY_GATE = {"f1": 0.90}


def main():
    X, y = load_breast_cancer(return_X_y=True, as_frame=True)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    model = RandomForestClassifier(**PARAMS).fit(X_tr, y_tr)
    metrics = {"f1": round(f1_score(y_te, model.predict(X_te)), 4),
               "roc_auc": round(roc_auc_score(y_te, model.predict_proba(X_te)[:, 1]), 4)}
    if metrics["f1"] < QUALITY_GATE["f1"]:
        raise SystemExit(f"Quality gate failed: {metrics}")
    ARTIFACTS.mkdir(exist_ok=True)
    joblib.dump(model, ARTIFACTS / "model.joblib")
    (ARTIFACTS / "metadata.json").write_text(json.dumps(
        {"params": PARAMS, "metrics": metrics, "features": list(X.columns)}, indent=2))
    try:
        import mlflow
        with mlflow.start_run():
            mlflow.log_params(PARAMS)
            mlflow.log_metrics(metrics)
            mlflow.log_artifact(str(ARTIFACTS / "model.joblib"))
    except ImportError:
        pass
    print(f"Model trained and saved. Metrics: {metrics}")


if __name__ == "__main__":
    main()
