"""
07_scatter.py  —  the "core story" scatter: coverage gap vs. median income,
point size = population, color = priority score.

Shows whether coverage gaps concentrate in lower-income counties (the thesis),
while size keeps the demand dimension visible and color ties back to the index.

Run next to acs_features.csv and coverage_by_county.csv.
Output: scatter_gap_vs_income.png
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent


def minmax(s):
    return (s - s.min()) / (s.max() - s.min())


def main():
    acs = pd.read_csv(HERE / "acs_features.csv")
    cov = pd.read_csv(HERE / "coverage_by_county.csv")
    df = acs.merge(cov, on="GEO_ID", how="inner")
    df["name"] = (df["NAME"].str.replace(" County, FL", "", regex=False)
                            .str.replace(r",.*$", "", regex=True))

    # priority (so color matches your index)
    df["unserved_people"] = df["coverage_gap"] * df["Population"]
    gap = minmax(df["unserved_people"])
    need = minmax(minmax(df["Poverty Rate"]) + minmax(-df["Median Household Income"]) + minmax(df["Median Age"]))
    df["priority"] = 0.7 * gap + 0.3 * need

    x = df["coverage_gap"] * 100          # % of county area uncovered
    y = df["Median Household Income"]
    sizes = minmax(df["Population"]) * 900 + 30   # scale pop -> marker area

    fig, ax = plt.subplots(figsize=(9, 6.5))
    sc = ax.scatter(x, y, s=sizes, c=df["priority"], cmap="OrRd",
                    edgecolor="#444", linewidth=0.5, alpha=0.85)

    # label the highest-priority counties so the story is legible
    for _, r in df.nlargest(8, "priority").iterrows():
        ax.annotate(r["name"], (r["coverage_gap"] * 100, r["Median Household Income"]),
                    xytext=(5, 4), textcoords="offset points", fontsize=8)

    ax.set_xlabel("Mobile coverage gap  (% of county area without 5G)")
    ax.set_ylabel("Median household income ($)")
    ax.set_title("Coverage gaps vs. income across Florida counties")
    ax.grid(alpha=0.2)
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label("Priority score (higher = greater need)")
    # note explaining bubble size
    ax.text(0.99, 0.02, "bubble size = population", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=8, color="#666")
    fig.tight_layout()
    fig.savefig(HERE / "scatter_gap_vs_income.png", dpi=200, bbox_inches="tight")
    print("wrote scatter_gap_vs_income.png")

    # quick correlation to report in the caption
    r = np.corrcoef(df["coverage_gap"], df["Median Household Income"])[0, 1]
    print(f"correlation(coverage gap, median income) = {r:+.2f}")


if __name__ == "__main__":
    main()
