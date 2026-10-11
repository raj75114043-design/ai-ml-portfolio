from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.spc import SPECS, control_limits, oos_flags, oot_flags, cpk

df = pd.read_csv("data/batch_results.csv")
col = "assay_pct"
mean, sigma = control_limits(df[col])
df["OOS"] = oos_flags(df, col)
rules = oot_flags(df[col], mean, sigma)
df["OOT"] = rules.any(axis=1) & ~df["OOS"]
df["OOT_rules"] = rules.apply(lambda r: ", ".join(r.index[r]), axis=1)

lo, hi = SPECS[col]
print(f"Batches analysed: {len(df)}")
print(f"Baseline mean {mean:.2f}%, sigma {sigma:.2f}; Cpk (all batches) = {cpk(df[col], lo, hi)}")
print(f"\nOOS batches ({df['OOS'].sum()}) — formal investigation required:")
print(df.loc[df.OOS, ["batch_id", "release_date", col]].to_string(index=False))
print(f"\nOOT batches ({df['OOT'].sum()}) — trend review required:")
print(df.loc[df.OOT, ["batch_id", col, "OOT_rules"]].to_string(index=False))

Path("outputs").mkdir(exist_ok=True)
df.to_csv("outputs/flagged_batches.csv", index=False)
fig, ax = plt.subplots(figsize=(11, 4.5))
ax.plot(df.index, df[col], marker="o", ms=3, color="#444")
for k, ls in [(0, "-"), (2, ":"), (3, "--")]:
    for s in ([1, -1] if k else [1]):
        ax.axhline(mean + s * k * sigma, color="#1f77b4", ls=ls, lw=0.8)
ax.axhline(lo, color="red", lw=1.2, label="Specification limit")
ax.scatter(df.index[df.OOT], df[col][df.OOT], color="orange", s=40, zorder=3, label="OOT")
ax.scatter(df.index[df.OOS], df[col][df.OOS], color="red", s=60, zorder=3, label="OOS")
ax.set_title("Assay (%) — Individuals Control Chart")
ax.set_xlabel("Batch sequence"); ax.set_ylabel("Assay (%)"); ax.legend()
fig.tight_layout(); fig.savefig("outputs/assay_control_chart.png", dpi=130)
print("\nSaved outputs/flagged_batches.csv and outputs/assay_control_chart.png")
