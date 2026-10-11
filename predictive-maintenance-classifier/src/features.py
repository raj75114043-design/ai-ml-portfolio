import numpy as np
import pandas as pd

RAW = ["air_temp_k", "process_temp_k", "rotational_speed_rpm", "torque_nm", "tool_wear_min", "vibration_mm_s"]


def engineer(df: pd.DataFrame) -> pd.DataFrame:
    """Physics-informed features: mechanical power, heat-dissipation margin and wear-strain."""
    out = df[RAW].astype(float).copy()
    out["power_w"] = out["torque_nm"] * out["rotational_speed_rpm"] * 2 * np.pi / 60
    out["temp_diff_k"] = out["process_temp_k"] - out["air_temp_k"]
    out["wear_x_torque"] = out["tool_wear_min"] * out["torque_nm"]
    return out
