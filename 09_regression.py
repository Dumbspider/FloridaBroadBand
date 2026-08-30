"""
09_regression.py  —  Multiple linear regression: what county characteristics
predict the mobile coverage gap?

DV  = coverage_gap (observed; from 02_process_coverage.py)
IVs = log10(population) + income + poverty + median age + % bachelor's +
      unemployment + % renter   (predictors standardized for comparable betas)

NOTE: the priority score is NOT used as the DV — it is built from these inputs,
so regressing it on them would be circular. The coverage gap is the observed
outcome, making this a legitimate supporting analysis of the gap's drivers.

Requires statsmodels:  pip install statsmodels
Run next to acs_features.csv and coverage_by_county.csv.
Outputs: regression_table.csv, regression_diagnostics.png
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

HERE = Path(__file__).resolve().parent
PREDS = ["log_pop", "Median Household Income", "Poverty Rate", "Median Age",
         "Pct Bachelors Or Higher", "Unemployment Rate", "Pct Renter Occupied"]


def main():
    acs = pd.read_csv(HERE / "acs_features.csv")
    cov = pd.read_csv(HERE / "coverage_by_county.csv")
    df = acs.merge(cov, on="GEO_ID", how="inner").dropna(subset=["coverage_gap"])
    df["log_pop"] = np.log10(df["Population"])

    # standardize predictors so coefficients are directly comparable in size
    Xz = (df[PREDS] - df[PREDS].mean()) / df[PREDS].std(ddof=1)
    X = sm.add_constant(Xz)
    y = df["coverage_gap"]

    model = sm.OLS(y, X).fit()
    print(model.summary())

    # regression table -> CSV
    tbl = pd.DataFrame({
        "term": model.params.index,
        "beta": model.params.values.round(4),
        "std_err": model.bse.values.round(4),
        "t": model.tvalues.values.round(2),
        "p": model.pvalues.values.round(3),
    })
    # VIF (multicollinearity) for each predictor
    vif = {PREDS[i]: round(variance_inflation_factor(Xz.values, i), 2) for i in range(len(PREDS))}
    tbl["VIF"] = tbl["term"].map(vif).fillna("")
    tbl.to_csv(HERE / "regression_table.csv", index=False)

    print(f"\nR2 = {model.rsquared:.3f}   adjR2 = {model.rsquared_adj:.3f}   "
          f"F = {model.fvalue:.2f}   p = {model.f_pvalue:.4f}")
    W, p = stats.shapiro(model.resid)
    print(f"Residual Shapiro-Wilk: W = {W:.3f}, p = {p:.4f}")

    # diagnostics figure
    fig, ax = plt.subplots(1, 2, figsize=(10, 4.2))
    ax[0].scatter(model.fittedvalues, model.resid, s=30, color="#4c72b0",
                  edgecolor="#333", linewidth=0.4, alpha=0.85)
    ax[0].axhline(0, color="red", lw=1.2)
    ax[0].set(xlabel="Fitted coverage gap", ylabel="Residual", title="Residuals vs. Fitted")
    ax[0].grid(alpha=0.2)
    stats.probplot(model.resid, dist="norm", plot=ax[1])
    ax[1].set_title("Normal Q-Q of Residuals")
    ax[1].grid(alpha=0.2)
    fig.suptitle("Regression Residual Diagnostics", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(HERE / "regression_diagnostics.png", dpi=200, bbox_inches="tight")
    print("wrote regression_table.csv and regression_diagnostics.png")


if __name__ == "__main__":
    main()
