"""
02_process_coverage.py  —  FCC mobile coverage -> coverage gap per FL county.

Reads the FCC "Mobile Broadband Summary by Geography Type" (County) file and
produces the project's DEPENDENT VARIABLE inputs, one row per county.

Output: coverage_by_county.csv  with
  GEO_ID            0500000US12XXX  (matches acs_features.csv)
  covered_share     primary coverage definition (5G-NR 7/1 Mbps, outdoor)
  covered_share_4g  sensitivity definition (4G LTE 5/1 Mbps, outdoor)
  coverage_gap      1 - covered_share   (DV; multiply by Population in step 03)

Coverage-definition decision (LOG THIS in RESEARCH_LOG.md):
  primary  = mobilebb_5g_spd1_area_st_pct  (5G-NR 7/1 Mbps, stationary/outdoor)
  sensitivity = mobilebb_4g_area_st_pct    (4G LTE 5/1 Mbps, stationary/outdoor)
  st = stationary (outdoor); iv = in-vehicle (moving). We use stationary.
LIMITATION: these are AREA-based coverage %, not population-based. unserved_people
  = coverage_gap * population assumes residents are spread evenly across county
  area. Defensible at county grain; state it explicitly in methods.
"""
from pathlib import Path
import pandas as pd

RAW = Path(__file__).resolve().parent / "bdc_us_mobile_broadband_summary_by_geography_D25_23jun2026.csv"

PRIMARY = "mobilebb_5g_spd1_area_st_pct"   # 5G-NR 7/1 Mbps, outdoor
SENSITIVITY = "mobilebb_4g_area_st_pct"    # 4G LTE 5/1 Mbps, outdoor


def main():
    df = pd.read_csv(RAW, dtype=str)

    # Florida counties, whole-county figure only (area_data_type == 'Total').
    # Filter on FIPS 12 — NOT the name 'Florida' (which would catch PR's Florida Municipio).
    m = ((df["geography_type"] == "County")
         & (df["geography_id"].str.startswith("12"))
         & (df["area_data_type"] == "Total"))
    fl = df[m].copy()

    for c in (PRIMARY, SENSITIVITY):
        fl[c] = pd.to_numeric(fl[c], errors="coerce")

    fl["GEO_ID"] = "0500000US" + fl["geography_id"]
    fl["covered_share"] = fl[PRIMARY]
    fl["covered_share_4g"] = fl[SENSITIVITY]
    fl["coverage_gap"] = 1 - fl["covered_share"]

    out = fl[["GEO_ID", "covered_share", "covered_share_4g", "coverage_gap"]] \
        .drop_duplicates("GEO_ID").reset_index(drop=True)
    assert len(out) == 67, f"expected 67 counties, got {len(out)}"

    path = Path(__file__).resolve().parent / "coverage_by_county.csv"
    out.to_csv(path, index=False)
    print(f"wrote {path}  ({len(out)} counties)")
    print("\nLargest coverage gaps (5G 7/1, outdoor):")
    show = out.merge(fl[["GEO_ID", "geography_desc"]], on="GEO_ID")
    print(show.sort_values("coverage_gap", ascending=False)
          [["geography_desc", "covered_share", "coverage_gap"]].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
