"""
06_weight_sensitivity_fig.py  —  heatmap of county priority RANK across a sweep
of gap/equity weightings. Stable counties show a smooth horizontal color band;
weight-sensitive counties show abrupt jumps across their row.

Run next to acs_features.csv and coverage_by_county.csv.
Outputs: weight_sensitivity_heatmap.png, weight_rank_matrix.csv
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

HERE = Path(__file__).resolve().parent
WEIGHTS = [0.3, 0.5, 0.7, 0.9]   # gap weight; need weight = 1 - this
BASELINE = 0.7                    # the default weighting to sort by
TOP_N = 25                        # show the top N counties; set None to show all 67


def minmax(s):
    return (s - s.min()) / (s.max() - s.min())


def priority(df, w_gap):
    d = df.copy()
    d["unserved_people"] = d["coverage_gap"] * d["Population"]
    gap = minmax(d["unserved_people"])
    need = minmax(minmax(d["Poverty Rate"]) + minmax(-d["Median Household Income"]) + minmax(d["Median Age"]))
    return w_gap * gap + (1 - w_gap) * need


def main():
    acs = pd.read_csv(HERE / "acs_features.csv")
    cov = pd.read_csv(HERE / "coverage_by_county.csv")
    df = acs.merge(cov, on="GEO_ID", how="inner")
    df["name"] = (df["NAME"].str.replace(" County, FL", "", regex=False)
                            .str.replace(r",.*$", "", regex=True))

    # rank matrix: rows = counties, cols = weightings (1 = highest priority)
    ranks = pd.DataFrame({"name": df["name"].values})
    for w in WEIGHTS:
        ranks[w] = priority(df, w).rank(ascending=False, method="first").astype(int).values
    ranks = ranks.sort_values(BASELINE).reset_index(drop=True)
    ranks.to_csv(HERE / "weight_rank_matrix.csv", index=False)

    show = ranks if TOP_N is None else ranks.head(TOP_N)
    mat = show[WEIGHTS].values

    # dark = better rank (1). reverse so rank 1 is darkest.
    cmap = LinearSegmentedColormap.from_list("need", ["#7f0000", "#fdd49e", "#fff7ec"])

    fig, ax = plt.subplots(figsize=(6.5, max(5, 0.32 * len(show))))
    im = ax.imshow(mat, cmap=cmap, aspect="auto",
                   vmin=1, vmax=len(ranks))

    # annotate each cell with the rank number
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            r = mat[i, j]
            ax.text(j, i, str(r), ha="center", va="center", fontsize=7,
                    color="white" if r <= len(ranks) * 0.25 else "#333333")

    ax.set_xticks(range(len(WEIGHTS)))
    ax.set_xticklabels([f"{w:g}/{round(1-w,1):g}" for w in WEIGHTS])
    ax.set_xlabel("Weighting  (gap / need)")
    ax.set_yticks(range(len(show)))
    ax.set_yticklabels(show["name"], fontsize=8)
    ax.set_title(f"Priority rank across weightings (sorted by {BASELINE:g}/{round(1-BASELINE,1):g})")

    cbar = fig.colorbar(im, ax=ax, shrink=0.6)
    cbar.set_label("Priority rank (1 = highest need)")
    fig.tight_layout()
    fig.savefig(HERE / "weight_sensitivity_heatmap.png", dpi=200, bbox_inches="tight")

    print("wrote weight_sensitivity_heatmap.png and weight_rank_matrix.csv")
    print(f"\nTop {min(TOP_N or len(ranks), len(ranks))} counties, rank by weighting:")
    print(show.to_string(index=False))


if __name__ == "__main__":
    main()