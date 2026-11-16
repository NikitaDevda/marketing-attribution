import os
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

os.makedirs("outputs", exist_ok=True)
con = sqlite3.connect("data/marketing.db")

# Sirf pre-purchase valid touches fetch karein
t = pd.read_sql("""
  SELECT o.order_id, o.revenue, o.order_ts, s.channel, s.campaign, s.session_ts
  FROM orders o
  JOIN sessions s ON s.user_id = o.user_id 
   AND s.session_ts <= o.order_ts
   AND s.is_post_purchase = 0
""", con, parse_dates=["order_ts", "session_ts"])

t = t.sort_values(["order_id", "session_ts"])
t["n"]   = t.groupby("order_id")["channel"].transform("size")
t["pos"] = t.groupby("order_id").cumcount() + 1

# --- Attribution Weights ---
t["w_first"]  = (t.pos == 1).astype(float)
t["w_last"]   = (t.pos == t.n).astype(float)
t["w_linear"] = 1.0 / t.n

days = (t.order_ts - t.session_ts).dt.total_seconds() / 86400
raw  = 0.5 ** (days / 7)  # 7-day half-life
t["w_decay"] = raw / raw.groupby(t.order_id).transform("sum")

t["w_pos"] = np.where(
    t.n == 1, 1.0,
    np.where(
        t.n == 2, 0.5,
        np.where((t.pos == 1) | (t.pos == t.n), 0.4, 0.2 / (t.n - 2).clip(lower=1))
    )
)

models = ["first", "last", "linear", "decay", "pos"]
for m in models:
    t[f"rev_{m}"] = t.revenue * t[f"w_{m}"]

# 1. Channel-Level Attribution & ROAS
result = t.groupby("channel")[[f"rev_{m}" for m in models]].sum().round(2)
result.columns = ["First Touch", "Last Touch", "Linear", "Time Decay", "Position Based"]
print("\n--- CHANNEL ATTRIBUTION REVENUE ---")
print(result)

spend = pd.read_sql("SELECT channel, SUM(spend) AS spend FROM ad_spend GROUP BY channel", con)
summary = result.reset_index().merge(spend, on="channel", how="left")

for col in ["First Touch", "Last Touch", "Linear", "Time Decay", "Position Based"]:
    summary[f"ROAS_{col}"] = (summary[col] / summary.spend.replace(0, np.nan)).round(2)

# 2. Campaign-Level Attribution & ROAS
camp_res = t.groupby(["channel", "campaign"])[[f"rev_{m}" for m in models]].sum().round(2)
camp_res.columns = ["First Touch", "Last Touch", "Linear", "Time Decay", "Position Based"]
camp_spend = pd.read_sql("SELECT channel, campaign, SUM(spend) AS spend FROM ad_spend GROUP BY channel, campaign", con)
camp_summary = camp_res.reset_index().merge(camp_spend, on=["channel", "campaign"], how="right").fillna(0)
camp_summary["ROAS_Linear"] = (camp_summary["Linear"] / camp_summary.spend.replace(0, np.nan)).round(2)

# --- Visualization ---
ax = result.plot(kind="bar", figsize=(11, 5.5))
plt.title("Revenue by Channel across Attribution Models (Pre-Purchase Journeys)")
plt.ylabel("Attributed Revenue (INR)")
plt.xlabel("Marketing Channel")
plt.xticks(rotation=0)
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig("outputs/attribution_comparison.png", dpi=150)

# --- Dashboard Exports ---
summary.to_csv("outputs/mart_attribution.csv", index=False)
camp_summary.to_csv("outputs/mart_campaign_attribution.csv", index=False)
con.close()
print("\nSaved attribution charts and CSV marts in 'outputs/'.")