import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

df = pd.read_csv("acs_features.csv")
features = ["Population", "Median Household Income", "Poverty Rate", "Median Age",
            "Pct Bachelors Or Higher", "Unemployment Rate", "Pct Renter Occupied"]

df[features].hist(bins=15, figsize=(12, 8))
plt.tight_layout()
plt.savefig("feature_distributions.png", dpi=150)
plt.show()   # <-- this opens the interactive window

for f in features:                       
    s = df[f].dropna()
    W, p = stats.shapiro(s)
    print(f"{f:28s} skew={s.skew():+.2f}  shapiro_p={p:.3f}")