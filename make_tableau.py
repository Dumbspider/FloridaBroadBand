from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
df = pd.read_csv(HERE / "priority_ranking.csv")

df["county_name"] = (df["NAME"].str.replace(r",.*$", "", regex=True)
                                .str.replace(" County", "", regex=False)
                                .str.strip())
df["state"] = "Florida"

if "GEO_ID" in df.columns:
    df["county_fips"] = df["GEO_ID"].str[-5:]
else:
    acs_path = HERE / "acs_features.csv"
    if acs_path.exists():
        acs = pd.read_csv(acs_path)
        if {"GEO_ID", "NAME"}.issubset(acs.columns):
            lut = acs.assign(county_fips=acs["GEO_ID"].str[-5:])[["NAME", "county_fips"]]
            df = df.merge(lut, on="NAME", how="left")
    if "county_fips" not in df.columns:
        df["county_fips"] = ""
        print("NOTE: no GEO_ID found; using county_name + state for mapping.")

cols = ["county_fips", "county_name", "state", "rank", "priority",
        "gap_score", "need_score", "unserved_people", "coverage_gap",
        "Population", "Median Household Income", "Poverty Rate", "Median Age"]
cols = [c for c in cols if c in df.columns]
df[cols].to_csv(HERE / "priority_tableau.csv", index=False)
print("wrote priority_tableau.csv")
print(df[[c for c in ["county_fips", "county_name", "rank", "priority"] if c in df.columns]].head().to_string(index=False))
