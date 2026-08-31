import os
import sys
from pathlib import Path
import pandas as pd
import requests

YEAR = 2023
STATE_FIPS = "12"
API_KEY = "16772b497d6125de3a542cc0313b56e95f0eb4bb"

DETAILED = f"https://api.census.gov/data/{YEAR}/acs/acs5"
SUBJECT = f"https://api.census.gov/data/{YEAR}/acs/acs5/subject"

DETAILED_VARS = ["B19013_001E",
                 "B01002_001E",
                 "B01003_001E",
                 "B25003_001E",
                 "B25003_003E"]
SUBJECT_VARS = ["S1701_C03_001E",
                "S1501_C02_015E",
                "S2301_C04_001E"]


def fetch(base, varlist):
    params = {"get": "NAME," + ",".join(varlist),
              "for": "county:*", "in": f"state:{STATE_FIPS}"}
    if API_KEY:
        params["key"] = API_KEY

    r = requests.get(base, params=params, timeout=30)
    ctype = r.headers.get("content-type", "")

    if r.status_code != 200 or "json" not in ctype.lower():
        safe_url = r.url.replace(API_KEY, "<KEY>") if API_KEY else r.url
        print("\n--- Census API did not return JSON ---", file=sys.stderr)
        print(f"HTTP status : {r.status_code}", file=sys.stderr)
        print(f"Content-Type: {ctype}", file=sys.stderr)
        print(f"URL         : {safe_url}", file=sys.stderr)
        print("Response body (first 600 chars):", file=sys.stderr)
        print(r.text[:600].strip() or "(empty body)", file=sys.stderr)
        print("\nMost common cause: missing/invalid CENSUS_API_KEY. "
              "Check `echo $CENSUS_API_KEY` in this terminal.", file=sys.stderr)
        raise SystemExit(1)

    rows = r.json()
    df = pd.DataFrame(rows[1:], columns=rows[0])
    df["GEO_ID"] = "0500000US" + df["state"] + df["county"]
    for v in varlist:
        df[v] = pd.to_numeric(df[v], errors="coerce")
    return df.drop(columns=["state", "county"])


def main():
    if not API_KEY:
        print("WARNING: CENSUS_API_KEY is not set. The API may reject the request.\n"
              "Get a free key at https://api.census.gov/data/key_signup.html then run:\n"
              "  export CENSUS_API_KEY=your_key_here\n")

    det = fetch(DETAILED, DETAILED_VARS)
    sub = fetch(SUBJECT, SUBJECT_VARS)
    df = det.merge(sub.drop(columns="NAME"), on="GEO_ID")

    df["Pct Renter Occupied"] = df["B25003_003E"] / df["B25003_001E"] * 100
    df = df.rename(columns={
        "B19013_001E": "Median Household Income",
        "B01002_001E": "Median Age",
        "B01003_001E": "Population",
        "S1701_C03_001E": "Poverty Rate",
        "S1501_C02_015E": "Pct Bachelors Or Higher",
        "S2301_C04_001E": "Unemployment Rate",
    })

    cols = ["GEO_ID", "NAME", "Population", "Median Household Income", "Poverty Rate",
            "Median Age", "Pct Bachelors Or Higher", "Unemployment Rate",
            "Pct Renter Occupied"]
    df = df[cols].sort_values("NAME").reset_index(drop=True)

    out = Path(__file__).resolve().parent / "acs_features.csv"
    df.to_csv(out, index=False)

    empty = [c for c in cols[2:] if df[c].isna().all()]
    if empty:
        print(f"WARNING: these columns are entirely empty (check variable codes): {empty}")

    print(f"wrote {out}  ({len(df)} counties)")
    print(df.head().to_string(index=False))


if __name__ == "__main__":
    main()
