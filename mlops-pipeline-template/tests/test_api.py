from sklearn.datasets import load_breast_cancer
from fastapi.testclient import TestClient
from src.serve import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_predict():
    X, _ = load_breast_cancer(return_X_y=True, as_frame=True)
    r = client.post("/predict", json={"features": X.iloc[0].to_dict()})
    assert r.status_code == 200 and r.json()["prediction"] in (0, 1)


def test_validation():
    assert client.post("/predict", json={"features": {"x": 1.0}}).status_code == 422
