import numpy as np, pandas as pd, random
from datetime import datetime, timedelta

np.random.seed(42); random.seed(42)

N_USERS = 10000
START   = datetime(2025, 1, 1)

# ---------- CHANNEL + UTM ----------
CHANNELS = ["Google Ads", "Facebook", "LinkedIn", "Organic", "Email"]
# pehli visit: awareness channels zyada | baad ki visits: Email/Organic/Google zyada
W_FIRST = [0.30, 0.30, 0.12, 0.22, 0.06]
W_LATER = [0.25, 0.12, 0.08, 0.25, 0.30]

UTM = {  # channel: (source, medium, [campaigns])
    "Google Ads": ("google",     "cpc",         ["summer_sale", "brand_search", "competitor_kw", "retargeting"]),
    "Facebook":   ("facebook",   "paid_social", ["summer_sale", "lookalike_audience", "video_ads", "retargeting"]),
    "LinkedIn":   ("linkedin",   "paid_social", ["b2b_leads", "webinar_promo", "thought_leadership"]),
    "Organic":    ("google",     "organic",     ["(not set)"]),
    "Email":      ("newsletter", "email",       ["weekly_digest", "cart_reminder", "winback"]),
}
SPEND_BASE = {"Google Ads": 1500, "Facebook": 1200, "LinkedIn": 800, "Email": 200, "Organic": 0}

# ---------- LANDING PAGE ----------
LANDING = ["/home", "/product", "/pricing", "/blog"]
LP_W = {   # channel ke hisab se landing page mix
    "Google Ads": [0.25, 0.40, 0.25, 0.10],
    "Facebook":   [0.35, 0.20, 0.10, 0.35],
    "LinkedIn":   [0.20, 0.15, 0.30, 0.35],
    "Organic":    [0.20, 0.20, 0.15, 0.45],
    "Email":      [0.15, 0.50, 0.30, 0.05],
}
# landing page ka product_view tak pahunchne pe asar
LP_MOD = {"/home": 1.0, "/product": 1.25, "/pricing": 0.6, "/blog": 0.7}

# ---------- DEVICE ----------
DEVICES = ["mobile", "desktop", "tablet"]
DEV_W   = [0.60, 0.30, 0.10]
DEV_MOD = {"mobile": 0.85, "desktop": 1.10, "tablet": 1.0}

# ---------- GEO ----------
CITIES = [("Mumbai", "Maharashtra"), ("Delhi", "Delhi"), ("Bangalore", "Karnataka"),
          ("Pune", "Maharashtra"), ("Hyderabad", "Telangana"),
          ("Indore", "Madhya Pradesh"), ("Chennai", "Tamil Nadu")]
CITY_W = [0.20, 0.20, 0.20, 0.12, 0.12, 0.08, 0.08]

# ---------- FUNNEL ----------
STAGES = ["session_start", "product_view", "add_to_cart", "checkout", "purchase"]
BASE = {  # view, cart, checkout, purchase
    "Google Ads": [0.70, 0.35, 0.60, 0.65],
    "Facebook":   [0.60, 0.25, 0.50, 0.55],
    "LinkedIn":   [0.75, 0.30, 0.65, 0.70],
    "Organic":    [0.80, 0.40, 0.70, 0.75],
    "Email":      [0.85, 0.45, 0.75, 0.80],
}

def funnel_probs(ch, lp, dev, variant, s_idx, allow_purchase):
    p = BASE[ch][:]
    p[0] *= LP_MOD[lp]                          # landing page effect
    for k in (1, 2, 3):
        p[k] *= 1 + 0.10 * s_idx                # returning user = zyada intent
    for k in (2, 3):
        p[k] *= DEV_MOD[dev]                    # device effect (checkout side)
        if variant == "B":                      # A/B: B me checkout flow better
            p[k] *= 1.12 if k == 2 else 1.15
    p = [min(x, 0.95) for x in p]
    if not allow_purchase:                      # purchase ke baad wale sessions
        p[3] = 0
    return p

# ---------- GENERATE ----------
users, sessions, events, orders = [], [], [], []
sid = eid = oid = 0

for uid in range(1, N_USERS + 1):
    city, state = random.choices(CITIES, CITY_W)[0]
    pref_dev    = random.choices(DEVICES, DEV_W)[0]
    variant     = random.choice(["A", "B"])         # USER level assignment
    signup      = START + timedelta(days=int(np.random.randint(0, 180)))

    users.append(dict(user_id=uid, signup_date=signup.date(), country="India",
                      state=state, city=city, variant=variant))

    n_planned = int(np.random.choice([1, 2, 3, 4, 5, 6],
                                     p=[0.20, 0.25, 0.25, 0.15, 0.10, 0.05]))
    ts = signup + timedelta(hours=int(np.random.randint(0, 24)))
    purchased, s_idx = False, 0

    while s_idx < n_planned:
        ch = str(np.random.choice(CHANNELS, p=W_FIRST if s_idx == 0 else W_LATER))
        src, med, camps = UTM[ch]
        camp = random.choice(camps)
        lp   = random.choices(LANDING, LP_W[ch])[0]
        # 70% time apna preferred device, 30% kuch aur
        dev  = pref_dev if random.random() < 0.7 else random.choice(DEVICES)

        if s_idx > 0:
            ts += timedelta(days=int(np.random.randint(0, 6)),
                            hours=int(np.random.randint(1, 24)))
        sid += 1
        sessions.append(dict(session_id=sid, user_id=uid, session_number=s_idx + 1,
                             session_ts=ts, channel=ch, source=src, medium=med,
                             campaign=camp, landing_page=lp, device=dev,
                             city=city, state=state, variant=variant,
                             is_post_purchase=int(purchased)))
        eid += 1
        events.append(dict(event_id=eid, session_id=sid, user_id=uid,
                           event_ts=ts, event_type="session_start"))

        probs = funnel_probs(ch, lp, dev, variant, s_idx, allow_purchase=not purchased)
        last_ts, bought = ts, False
        for i, pr in enumerate(probs):
            if np.random.rand() < pr:
                eid += 1
                last_ts += timedelta(minutes=int(np.random.randint(1, 15)))
                events.append(dict(event_id=eid, session_id=sid, user_id=uid,
                                   event_ts=last_ts, event_type=STAGES[i + 1]))
                if STAGES[i + 1] == "purchase":
                    bought = True
            else:
                break

        if bought:
            oid += 1
            orders.append(dict(order_id=oid, user_id=uid, session_id=sid, order_ts=last_ts,
                               revenue=round(float(np.random.lognormal(7, 0.5)), 2)))
            purchased = True
            # purchase ke baad 0/1/2 aur sessions (repeat visits)
            n_planned = s_idx + 1 + int(np.random.choice([0, 1, 2], p=[0.7, 0.2, 0.1]))
        s_idx += 1

# ---------- AD SPEND (campaign level) ----------
spend = []
for d in pd.date_range("2025-01-01", "2025-08-15"):
    for ch, (src, med, camps) in UTM.items():
        shares = np.random.dirichlet(np.ones(len(camps)))
        for camp, sh in zip(camps, shares):
            amt = SPEND_BASE[ch] * np.random.uniform(0.7, 1.3) * sh
            spend.append(dict(date=d.date(), channel=ch, source=src, medium=med,
                              campaign=camp, spend=round(amt, 2)))

pd.DataFrame(users).to_csv("data/users.csv", index=False)
pd.DataFrame(sessions).to_csv("data/sessions.csv", index=False)
pd.DataFrame(events).to_csv("data/events.csv", index=False)
pd.DataFrame(orders).to_csv("data/orders.csv", index=False)
pd.DataFrame(spend).to_csv("data/ad_spend.csv", index=False)

u, o = pd.DataFrame(users), pd.DataFrame(orders)
u["converted"] = u.user_id.isin(o.user_id)
print(f"{len(sessions)} sessions | {len(events)} events | {len(orders)} orders")
print(u.groupby("variant").converted.mean().round(4))