import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .spc import SPECS, control_limits, oos_flags, oot_flags, cpk


def analyse(df, col, baseline=30):
    df = df.copy().reset_index(drop=True)
    mean, sigma = control_limits(df[col], baseline)
    df["OOS"] = oos_flags(df, col)
    rules = oot_flags(df[col], mean, sigma)
    df["OOT"] = rules.any(axis=1) & ~df["OOS"]
    df["OOT_rules"] = rules.apply(lambda r: ", ".join(r.index[r]), axis=1)
    lo, hi = SPECS[col]
    return df, {"mean": mean, "sigma": sigma, "cpk": cpk(df[col], lo, hi), "lsl": lo, "usl": hi}


def control_chart(df, col, stats):
    m, s = stats["mean"], stats["sigma"]
    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.plot(df.index, df[col], marker="o", ms=3, color="#444", lw=1)
    ax.axhline(m, color="#1f77b4", lw=1, label="Mean")
    for k, ls in [(2, ":"), (3, "--")]:
        ax.axhline(m + k * s, color="#1f77b4", ls=ls, lw=0.8)
        ax.axhline(m - k * s, color="#1f77b4", ls=ls, lw=0.8)
    for lim in (stats["lsl"], stats["usl"]):
        if lim is not None:
            ax.axhline(lim, color="red", lw=1.2)
    ax.scatter(df.index[df.OOT], df[col][df.OOT], color="orange", s=45, zorder=3, label="OOT")
    ax.scatter(df.index[df.OOS], df[col][df.OOS], color="red", s=65, zorder=3, label="OOS")
    ax.set_xlabel("Batch sequence")
    ax.set_ylabel(col)
    ax.set_title(f"{col} — Individuals Control Chart (dotted ±2σ, dashed ±3σ, red = specification)")
    ax.legend(loc="lower left")
    fig.tight_layout()
    return fig
