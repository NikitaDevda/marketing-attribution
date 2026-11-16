import os
import sqlite3
import pandas as pd
from statsmodels.stats.proportion import proportions_ztest, proportion_confint
from scipy.stats import chisquare

os.makedirs("outputs", exist_ok=True)
con = sqlite3.connect("data/marketing.db")

df = pd.read_sql("""
  SELECT u.variant,
         COUNT(DISTINCT u.user_id) AS users,
         COUNT(DISTINCT o.user_id) AS conv
  FROM users u
  LEFT JOIN orders o ON o.user_id = u.user_id
  GROUP BY u.variant
  ORDER BY u.variant
""", con)

df["conv_rate"] = (df.conv / df.users).round(4)
print("--- A/B TEST CONVERSION SUMMARY ---")
print(df)

a, b = df.iloc[0], df.iloc[1]
z, p = proportions_ztest([b.conv, a.conv], [b.users, a.users])
lift = ((b.conv / b.users - a.conv / a.users) / (a.conv / a.users)) * 100
lo, hi = proportion_confint(b.conv, b.users, alpha=0.05)

# Sample Ratio Mismatch (SRM) check (50/50 split expectation)
srm_p = chisquare([a.users, b.users]).pvalue

print(f"\nLift (B vs A): {lift:.2f}%")
print(f"z = {z:.2f}, p-value = {p:.4f} ->", "SIGNIFICANT" if p < 0.05 else "NOT significant")
print(f"B conversion 95% CI: [{lo:.4f}, {hi:.4f}]")
print(f"SRM check p-value = {srm_p:.3f}", "(OK - Balanced Split)" if srm_p > 0.01 else "(SPLIT GADBAD HAI)")

# Power BI ke liye summary + statistical metrics export karein
df["lift_vs_a_pct"] = [0.0, round(lift, 2)]
df["p_value"]       = round(p, 4)
df["srm_p_value"]   = round(srm_p, 4)
df["status"]        = "Significant" if p < 0.05 else "Not Significant"

df.to_csv("outputs/mart_ab_test.csv", index=False)
con.close()
print("\nExported 'outputs/mart_ab_test.csv' successfully!")