"""
03_build_index.py  —  Build the county mobile-broadband priority index.

Inputs (both next to this script):
  acs_features.csv        from 01_pull_acs.py
  coverage_by_county.csv  from 02_process_coverage.py

Output:
  priority_ranking.csv    ranked 67 counties
  weight_sensitivity.csv  top-10 under different weight choices

Formula:
  coverage_gap    = 1 - covered_share
  unserved_people = coverage_gap * population            (demand-weighted backbone)
  gap_score       = minmax(unserved_people)
  need_score      = minmax( minmax(poverty) + minmax(-income) + minmax(age) )   (equity tilt)
  priority        = W_GAP * gap_score + W_NEED * need_score
Weights are explicit assumptions, swept below as a robustness check.
"""
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
W_GAP, W_NEED = 0.7, 0.3
LOG_POPULATION = False   # set True to log-compress metro population skew (log the choice!)


def minmax(s):
    return (s - s.min()) / (s.max() - s.min())


def score(df, w_gap, w_need):
    d = df.copy()
    pop = d["Population"]
    if LOG_POPULATION:
        import numpy as np
        pop = np.log10(pop)
    d["unserved_people"] = d["coverage_gap"] * pop
    d["gap_score"] = minmax(d["unserved_people"])
    need = (minmax(d["Poverty Rate"])
            + minmax(-d["Median Household Income"])
            + minmax(d["Median Age"]))
    d["need_score"] = minmax(need)
    d["priority"] = w_gap * d["gap_score"] + w_need * d["need_score"]
    return d.sort_values("priority", ascending=False).reset_index(drop=True)


def main():
    acs = pd.read_csv(HERE / "acs_features.csv")
    cov = pd.read_csv(HERE / "coverage_by_county.csv")
    df = acs.merge(cov, on="GEO_ID", how="inner")
    assert len(df) == 67, f"merge produced {len(df)} rows, expected 67 — check GEO_ID match"

    ranked = score(df, W_GAP, W_NEED)
    ranked["rank"] = range(1, len(ranked) + 1)

    keep = ["rank", "NAME", "priority", "gap_score", "need_score",
            "unserved_people", "coverage_gap", "Population",
            "Median Household Income", "Poverty Rate", "Median Age"]
    ranked[keep].to_csv(HERE / "priority_ranking.csv", index=False)

    print(f"Priority ranking (W_GAP={W_GAP}, W_NEED={W_NEED}) — top 15:")
    print(ranked[["rank", "NAME", "priority", "unserved_people", "coverage_gap"]]
          .head(15).to_string(index=False))

    # --- weight sensitivity: does the top-10 hold up? ---
    rows = []
    for wg in [0.9, 0.7, 0.5, 0.3]:
        top10 = score(df, wg, round(1 - wg, 1)).head(10)["NAME"].tolist()
        rows.append({"W_GAP": wg, "W_NEED": round(1 - wg, 1),
                     "top_10": ", ".join(n.replace(" County, FL", "") for n in top10)})
    pd.DataFrame(rows).to_csv(HERE / "weight_sensitivity.csv", index=False)
    print("\nwrote priority_ranking.csv and weight_sensitivity.csv")


if __name__ == "__main__":
    main()