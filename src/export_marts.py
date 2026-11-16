import os
import sqlite3
import pandas as pd

os.makedirs("outputs", exist_ok=True)
con = sqlite3.connect("data/marketing.db")

# 1. Core Funnel & Attribution Marts
pd.read_sql(open("sql/01_funnel.sql").read(), con).to_csv("outputs/mart_funnel.csv", index=False)
pd.read_sql(open("sql/02_funnel_by_channel.sql").read(), con).to_csv("outputs/mart_funnel_channel.csv", index=False)
pd.read_sql(open("sql/04_roas_cac.sql").read(), con).to_csv("outputs/mart_roas_cac.csv", index=False)

# 2. Dimension-wise Funnels (Landing Page, Device, City, State, Variant)
for dim in ["landing_page", "device", "city", "state", "variant"]:
    q = open("sql/05_dimension_funnel.sql").read().replace("s.landing_page", f"s.{dim}")
    pd.read_sql(q, con).to_csv(f"outputs/mart_funnel_{dim}.csv", index=False)

# 3. Top Multi-Touch Journey Paths
pd.read_sql(open("sql/06_journey_paths.sql").read(), con).to_csv("outputs/mart_journey_paths.csv", index=False)

# 4. Daily Trends (Sessions & Ad Spend)
pd.read_sql("""
  SELECT DATE(s.session_ts) AS date,
         s.channel,
         s.is_post_purchase,
         COUNT(*) AS sessions
  FROM sessions s
  GROUP BY 1, 2, 3
""", con).to_csv("outputs/mart_daily_sessions.csv", index=False)

pd.read_sql("SELECT * FROM ad_spend", con).to_csv("outputs/mart_daily_spend.csv", index=False)

con.close()
print("Marts exported successfully to 'outputs/'!")