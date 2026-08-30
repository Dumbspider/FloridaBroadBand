"""
06c_rank_correlation.py — clean weight-sensitivity summary using Spearman rank
correlation. Each bar = how closely that weighting's ranking matches the baseline
(0.7/0.3). Bar near 1.0 = ranking barely changes; lower = bigger reshuffle.

Run next to acs_features.csv and coverage_by_county.csv.
Outputs: rank_correlation.png, rank_correlation.csv
"""
from pathlib import Path
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from scipy import stats

HERE = Path(__file__).resolve().parent
WEIGHTS = [0.3, 0.5, 0.7, 0.9]
BASELINE = 0.7

def mm(s): return (s - s.min()) / (s.max() - s.min())
def priority(df, wg):
    gap = mm(df["coverage_gap"] * df["Population"])
    need = mm(mm(df["Poverty Rate"]) + mm(-df["Median Household Income"]) + mm(df["Median Age"]))
    return wg * gap + (1 - wg) * need

def main():
    acs = pd.read_csv(HERE / "acs_features.csv"); cov = pd.read_csv(HERE / "coverage_by_county.csv")
    df = acs.merge(cov, on="GEO_ID", how="inner")
    base = priority(df, BASELINE)

    labels, rhos, ps = [], [], []
    for w in WEIGHTS:
        rho, p = stats.spearmanr(priority(df, w), base)
        labels.append(f"{w:g}/{round(1-w,1):g}"); rhos.append(rho); ps.append(p)
    out = pd.DataFrame({"weighting": labels, "spearman_rho": np.round(rhos, 3), "p_value": ps})
    out.to_csv(HERE / "rank_correlation.csv", index=False)

    fig, ax = plt.subplots(figsize=(8, 5))
    cmap = plt.colormaps["RdYlGn"]
    bars = ax.bar(labels, rhos, color=[cmap(r) for r in rhos], edgecolor="#333", width=0.6, zorder=3)
    for b, r, p in zip(bars, rhos, ps):
        star = "baseline" if abs(r - 1) < 1e-9 else ("p < .001" if p < .001 else f"p = {p:.3f}")
        ax.text(b.get_x() + b.get_width()/2, r + 0.015, f"\u03C1 = {r:.2f}\n{star}",
                ha="center", va="bottom", fontsize=9)
    ax.axhline(1.0, color="#888", ls="--", lw=1, zorder=1)
    ax.set_ylim(0, 1.18)
    ax.set_ylabel("Rank agreement with baseline\n(Spearman \u03C1)")
    ax.set_xlabel("Weighting  (gap / need)")
    ax.set_title("How much the county ranking changes as the weighting changes")
    ax.text(0.5, -0.16, "Higher bar = ranking stays closer to the 0.7/0.3 baseline.",
            transform=ax.transAxes, ha="center", fontsize=9, color="#555")
    ax.grid(axis="y", alpha=0.25, zorder=0)
    fig.tight_layout()
    fig.savefig(HERE / "rank_correlation.png", dpi=200, bbox_inches="tight")
    print(out.to_string(index=False)); print("wrote rank_correlation.png")

if __name__ == "__main__":
    main()
