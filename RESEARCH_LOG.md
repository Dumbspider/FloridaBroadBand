# Research Log

Every decision and *why*. This file becomes your Methods and Limitations
sections. Add an entry whenever you choose a variable, a weight, a threshold, or
drop a row. Newest entries at the bottom.

---

## Project framing (decisions already made)

**Goal = prioritization, not optimization.** Ranking the 67 counties by investment
need, not choosing specific tower coordinates. County granularity is therefore
acceptable; acknowledged limitation = Modifiable Areal Unit Problem (gaps within a
county are masked).

**Dependent variable for the importance analysis = mobile coverage gap**
(`unserved_people`), NOT cellular subscription rate. Reason: subscription rate
measures adoption/affordability (who *buys* a plan), not where coverage is
missing. A model predicting subscription from demographics just relearns "richer
counties subscribe more" — circular, and useless for siting.

**No coverage-derived variable on the predictor side** when coverage gap is the
outcome — that would be target leakage.

**Equity variables = poverty rate, median household income, median age.**
Rationale: a coverage gap is more urgent where residents are least able to
self-remedy. Income and poverty are strongly collinear (treat as one economic
axis); median age captures Florida's retiree geography as a distinct dimension.

**Initial weights: W_GAP = 0.7, W_NEED = 0.3.** Arbitrary starting point. To be
sweep-tested (0.5/0.5, 0.9/0.1) — robustness of the top-10 ranking is the real
test.

**"Adequate coverage" threshold = TODO.** FCC publishes 4G LTE (5/1 Mbps) and
5G-NR (7/1 and 35/3 Mbps). Decide which defines the gap; report both as
sensitivity. [Fill in once decided.]

---

## Daily entries

### YYYY-MM-DD — <session title>
- What I did:
- Decisions + why:
- What broke / surprised me:
- Next:
