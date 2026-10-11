from fastapi.testclient import TestClient
from src.train import main as train
from src.api import app

meta = train()
client = TestClient(app)
NORMAL = {"air_temp_k": 300, "process_temp_k": 310, "rotational_speed_rpm": 1540, "torque_nm": 40,
          "tool_wear_min": 50, "vibration_mm_s": 3}
RISKY = {"air_temp_k": 302, "process_temp_k": 310.5, "rotational_speed_rpm": 1300, "torque_nm": 62,
         "tool_wear_min": 230, "vibration_mm_s": 5}


def test_model_beats_no_skill_baseline():
    best = meta["comparison"][meta["model"]]
    assert best["pr_auc"] > 5 * meta["failure_rate"]


def test_risky_machine_scores_higher():
    a = client.post("/predict", json=NORMAL).json()["failure_probability"]
    b = client.post("/predict", json=RISKY).json()["failure_probability"]
    assert b > a


def test_input_validation():
    assert client.post("/predict", json={**NORMAL, "torque_nm": -5}).status_code == 422


def test_health():
    assert client.get("/health").json()["status"] == "ok"
