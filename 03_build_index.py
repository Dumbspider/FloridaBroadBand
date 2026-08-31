from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
W_GAP, W_NEED = 0.7, 0.3
LOG_POPULATION = False


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

    rows = []
    for wg in [0.9, 0.7, 0.5, 0.3]:
        top10 = score(df, wg, round(1 - wg, 1)).head(10)["NAME"].tolist()
        rows.append({"W_GAP": wg, "W_NEED": round(1 - wg, 1),
                     "top_10": ", ".join(n.replace(" County, FL", "") for n in top10)})
    pd.DataFrame(rows).to_csv(HERE / "weight_sensitivity.csv", index=False)
    print("\nwrote priority_ranking.csv and weight_sensitivity.csv")


if __name__ == "__main__":
    main()
