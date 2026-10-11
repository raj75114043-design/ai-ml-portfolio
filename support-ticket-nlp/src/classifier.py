"""TF-IDF (word + character n-grams) with logistic regression for ticket categorisation."""
import json
from pathlib import Path
import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline, make_union
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "artifacts"
TEAMS = {"Billing": "Finance Operations", "Network": "Network Operations Centre", "Access": "Identity & Access Management",
         "Hardware": "Field Support", "Software": "Application Support"}


def build_model():
    features = make_union(TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=2),
                          TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True, min_df=2))
    return make_pipeline(features, LogisticRegression(max_iter=3000, C=4, class_weight="balanced"))


def train():
    df = pd.read_csv(ROOT / "data" / "tickets.csv")
    X_tr, X_te, y_tr, y_te = train_test_split(df["text"], df["category"], test_size=0.2,
                                              stratify=df["category"], random_state=42)
    model = build_model().fit(X_tr, y_tr)
    pred = model.predict(X_te)
    report = classification_report(y_te, pred, output_dict=True)
    meta = {"macro_f1": round(f1_score(y_te, pred, average="macro"), 3), "n_train": len(X_tr), "n_test": len(X_te),
            "report": {k: {m: round(v, 3) for m, v in d.items()} for k, d in report.items() if isinstance(d, dict)}}
    ARTIFACTS.mkdir(exist_ok=True)
    joblib.dump(model, ARTIFACTS / "model.joblib")
    (ARTIFACTS / "metadata.json").write_text(json.dumps(meta, indent=2))
    return model, meta


def load():
    if not (ARTIFACTS / "model.joblib").exists():
        return train()
    return joblib.load(ARTIFACTS / "model.joblib"), json.loads((ARTIFACTS / "metadata.json").read_text())
