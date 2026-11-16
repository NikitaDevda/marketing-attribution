# Marketing Attribution & Funnel Intelligence Platform

An end-to-end data analytics and multi-touch attribution platform built to process user behavioral journeys, evaluate marketing channel performance, optimize ad spend (ROAS/CAC), and execute rigorous statistical A/B testing.

---

## Tech Stack & Architecture
* **Data Engineering & Modeling:** Python, Pandas, NumPy, Scikit-learn
* **Database & Warehouse:** SQLite (`marketing.db`)
* **Statistical Testing:** Z-tests, P-values, Sample Ratio Mismatch (SRM) validation
* **Visualization & BI:** Power BI (`.pbix`), Streamlit (for prototyping)

---

## Key Features & Analytical Models

### 1. Multi-Touch Attribution (MTA) Models
Credits revenue across customer touchpoints using 5 distinct attribution models implemented from scratch in Python:
* **First-Touch Attribution:** Credits 100% of conversion to the initial discovery channel.
* **Last-Touch Attribution:** Credits the final interaction before purchase.
* **Linear Attribution:** Distributes credit equally across all touchpoints.
* **Time-Decay Attribution:** Gives heavier weight to touchpoints closer in time to the conversion.
* **Position-Based (U-Shaped) Attribution:** Allocates 40% to First touch, 40% to Last touch, and 20% split among middle interactions.

### 2. Funnel Diagnostics & Drop-Off Analysis
* Tracks user progression across key milestones: `session_start` -> `product_view` -> `add_to_cart` -> `checkout` -> `purchase`.
* Pinpoints exact drop-off bottlenecks by channel, device type, geographic location (state/city), and landing page.

### 3. Rigorous A/B Testing & Experimentation
* Evaluated a new checkout flow (Variant B vs. Control Variant A).
* Executed **Z-tests** confirming a **+12.95% conversion lift** with high statistical significance ($p < 0.001$).
* Conducted **Sample Ratio Mismatch (SRM)** checks ($p = 0.749$) to ensure data integrity and unbiased traffic splits.

---

## Power BI Dashboard Overview (`dashboard/marketing_attribution.pbix`)
The accompanying interactive Power BI dashboard features 5 specialized reporting pages:
1. **Executive Overview:** High-level KPI cards (Revenue, Spend, Orders) and daily session/spend trends.
2. **Funnel Diagnostics:** Visual funnel progression and channel conversion tables.
3. **Multi-Touch Attribution:** Comparative bar charts evaluating channel weightings across attribution algorithms.
4. **CRO & Geo Insights:** Landing page bounce rates, device performance, and campaign-level ROAS/CAC matrices.
5. **A/B Test Results:** Variant conversion lift comparisons and statistical validation metrics.

---

## Repository Structure
```text
marketing-attribution/
│
├── dashboard/
│   └── marketing_attribution.pbix   # Power BI Dashboard file
├── outputs/
│   └── all_marts.xlsx               # Processed analytical data marts
├── src/
│   ├── generate_data.py             # Synthetic data generation pipeline
│   ├── load_db.py                   # SQLite database loader
│   ├── attribution.py               # MTA attribution modeling script
│   └── ab_test.py                   # Z-test and SRM statistical calculator
├── marketing.db                     # SQLite data warehouse
├── requirements.txt                 # Project dependencies
└── README.md                        # Project documentation