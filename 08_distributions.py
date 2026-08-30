"""
08_distributions.py  —  distribution diagnostics for the independent variables:
a histogram (with a normal curve overlaid) and a Q-Q plot side by side per
variable, plus a Shapiro-Wilk table.

Run next to acs_features.csv.
Outputs: distributions_grid.png, qq_grid.png, normality_table.csv
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

HERE = Path(__file__).resolve().parent
FEATURES = ["Population", "Median Household Income", "Poverty Rate", "Median Age",
            "Pct Bachelors Or Higher", "Unemployment Rate", "Pct Renter Occupied"]


def main():
    df = pd.read_csv(HERE / "acs_features.csv")
    feats = [f for f in FEATURES if f in df.columns]

    # ---------- Shapiro-Wilk table ----------
    rows = []
    for f in feats:
        s = df[f].dropna()
        W, p = stats.shapiro(s)
        rows.append({"variable": f, "skew": round(s.skew(), 2),
                     "shapiro_W": round(W, 3), "shapiro_p": round(p, 4),
                     "normal_at_0.05": "yes" if p >= 0.05 else "no"})
    table = pd.DataFrame(rows)
    table.to_csv(HERE / "normality_table.csv", index=False)

    n = len(feats)
    ncols = 3
    nrows = int(np.ceil(n / ncols))

    # ---------- histogram grid (with normal overlay) ----------
    fig, axes = plt.subplots(nrows, ncols, figsize=(4 * ncols, 3.2 * nrows))
    axes = np.array(axes).ravel()
    for ax, f in zip(axes, feats):
        s = df[f].dropna()
        ax.hist(s, bins=15, density=True, color="#4c72b0", edgecolor="white", alpha=0.85)
        xs = np.linspace(s.min(), s.max(), 200)
        ax.plot(xs, stats.norm.pdf(xs, s.mean(), s.std()), "r-", lw=1.8)
        p = table.loc[table["variable"] == f, "shapiro_p"].iloc[0]
        ax.set_title(f"{f}\nShapiro p = {p:.3f}", fontsize=9)
        ax.tick_params(labelsize=7)
    for ax in axes[n:]:
        ax.axis("off")
    fig.suptitle("Distribution of independent variables (red = normal curve)", fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(HERE / "distributions_grid.png", dpi=200, bbox_inches="tight")

    # ---------- Q-Q plot grid ----------
    fig2, axes2 = plt.subplots(nrows, ncols, figsize=(4 * ncols, 3.2 * nrows))
    axes2 = np.array(axes2).ravel()
    for ax, f in zip(axes2, feats):
        s = df[f].dropna()
        stats.probplot(s, dist="norm", plot=ax)
        ax.get_lines()[0].set(marker="o", markersize=4, markerfacecolor="#4c72b0", markeredgecolor="none")
        ax.get_lines()[1].set(color="red", lw=1.5)   # the reference line
        ax.set_title(f, fontsize=9)
        ax.set_xlabel("Theoretical quantiles", fontsize=8)
        ax.set_ylabel("Sample quantiles", fontsize=8)
        ax.tick_params(labelsize=7)
    for ax in axes2[n:]:
        ax.axis("off")
    fig2.suptitle("Q-Q plots vs. normal (points on the line = normal)", fontsize=11)
    fig2.tight_layout(rect=[0, 0, 1, 0.97])
    fig2.savefig(HERE / "qq_grid.png", dpi=200, bbox_inches="tight")

    print("wrote distributions_grid.png, qq_grid.png, normality_table.csv\n")
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()
