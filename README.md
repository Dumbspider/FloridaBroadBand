# Florida County-Level Mobile Broadband Prioritization

A transparent, reproducible index that ranks Florida's 67 counties by **need for
mobile broadband (cell tower) investment**, combining a demand-weighted coverage
gap with a socioeconomic equity score.

## Research question

> In Florida, are mobile coverage gaps concentrated in lower-income, more rural
> counties? Does a need-based prioritization that weights the coverage gap by
> socioeconomic vulnerability rank different counties than coverage gap alone?

**Hypothesis:** coverage gaps fall disproportionately on poorer, more rural
counties, so the equity-weighted ranking will diverge meaningfully from a
ranking based on unserved population alone.

This is a *prioritization* (a scoring/ranking problem), **not** a tower-siting
optimization and **not** a prediction of subscription rate. See RESEARCH_LOG.md
for why those framings were rejected.

## Pipeline

```
01_pull_acs.py          Census ACS demographics  -> data/processed/acs_features.csv
02_process_coverage.py  FCC mobile coverage       -> data/processed/coverage_by_county.csv
03_build_index.py       merge + score + rank      -> outputs/tables/priority_ranking.csv
04_explore_importance.py  coverage-gap drivers (supporting analysis)
05_visualize.py         choropleth + sensitivity  -> outputs/figures/
```

Run them in order. Steps 01 runs today; 02 needs the FCC mobile file downloaded
into data/raw/ first (see data/README.md).

## The scoring model
            
```
coverage_gap     = 1 - covered_share                 # from FCC mobile data
unserved_people  = coverage_gap * population          # demand-weighted backbone
gap_score        = minmax(unserved_people)            # 0..1 across the 67 counties
need_score       = minmax( minmax(poverty)
                         + minmax(-income)
                         + minmax(median_age) )       # equity tilt
priority         = W_GAP * gap_score + W_NEED * need_score
```

Weights (`W_GAP`, `W_NEED`) are explicit assumptions, not learned. They are
swept in 03_build_index.py and 05_visualize.py as a sensitivity check.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export CENSUS_API_KEY=your_key_here   # free: https://api.census.gov/data/key_signup.html
python src/01_pull_acs.py
```

## Data vintages (keep these fixed for reproducibility)

- Census ACS 5-Year Estimates: **2019–2023 (vintage 2023)**
- FCC mobile broadband coverage (BDC): **as-of 2025-06-30**
- County boundaries: Census Cartographic Boundary file, **2023**

Record the exact file names and download dates in data/README.md.
