import os
import sqlite3
import pandas as pd

os.makedirs("data", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

con = sqlite3.connect("data/marketing.db")

for t in ["users", "sessions", "events", "orders", "ad_spend"]:
    df = pd.read_csv(f"data/{t}.csv")
    df.to_sql(t, con, if_exists="replace", index=False)
    print(f"Loaded {t}: {len(df)} rows")

con.executescript("""
CREATE INDEX IF NOT EXISTS idx_sess_user      ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sess_post_pur  ON sessions(is_post_purchase);
CREATE INDEX IF NOT EXISTS idx_sess_chan_camp ON sessions(channel, campaign);
CREATE INDEX IF NOT EXISTS idx_ev_sess        ON events(session_id);
CREATE INDEX IF NOT EXISTS idx_ord_user       ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_spend_ch_camp  ON ad_spend(channel, campaign);
""")

con.close()
print("Database setup complete: data/marketing.db")