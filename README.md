# Supply Chain Policy Lab

A causal inference and simulation framework for evaluating inventory policy changes
in retail supply chains — built on real Walmart sales data from the M5 Forecasting
Competition.

---

## Problem

A retailer wants to know: **does increasing safety stock levels reduce stockouts enough
to justify the additional holding cost?**

Simple question. Hard to answer causally because:
- Products in the same category share warehouse space — treating one affects others
- Demand for substitute products is correlated — stockouts cause spillover to competitors
- The effect is heterogeneous — works differently for fast vs slow moving products

Standard A/B testing assumptions break down in supply chains. This project implements
the correct causal machinery to answer the question honestly.

---

## Approach

| Stage | Description |
|---|---|
| 01 — Data Ingestion | Load M5 data in chunks, write to Parquet on disk |
| 02 — Demand Forecasting | Train LightGBM on historical sales to forecast demand |
| 03 — Inventory Simulation | Simulate warehouse dynamics using real demand signal |
| 04 — Experiment Design | Cluster randomized trial — randomize at category level |
| 05 — Causal Inference | Difference-in-differences + heterogeneous treatment effects |
| 06 — Policy Recommendation | Optimal safety stock multiplier per product segment |

---

## Key Concepts

- **Safety stock** — buffer inventory held beyond expected demand to prevent stockouts
- **Stockout** — demand exceeds available inventory, sale is lost
- **Holding cost** — cost of storing unsold inventory
- **Interference** — treating one product affects outcomes of substitute products
- **Cluster randomization** — randomize at category level to reduce spillover
- **Difference-in-Differences** — causal estimator that removes confounding time trends
- **Heterogeneous treatment effects** — policy impact varies by product type

---

## Dataset

**M5 Forecasting Competition — Walmart Sales Data**
Available free on Kaggle: `https://www.kaggle.com/competitions/m5-forecasting-accuracy/data`

- 3,049 products across 10 Walmart stores in 3 states
- 1,941 days of daily sales history (2011—2016)
- 3 product categories: FOODS, HOBBIES, HOUSEHOLD
- Hierarchical structure: product → department → category → store → state

> Data is not included in this repo. Download from Kaggle and place in `data/raw/`.

---

## Structure

supply-chain-policy-lab/
├── data/
│   ├── raw/                  # M5 raw CSVs — not tracked by git
│   ├── processed/            # Cleaned long-format data — not tracked
│   └── parquet/              # Parquet files for efficient disk access — not tracked
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 02_demand_forecasting.ipynb
│   ├── 03_inventory_simulation.ipynb
│   ├── 04_experiment_design.ipynb
│   ├── 05_causal_inference.ipynb
│   └── 06_policy_recommendation.ipynb
├── src/
│   ├── ingestion.py          # Chunked data loading and Parquet writing
│   ├── simulation.py         # Inventory simulation engine
│   ├── causal.py             # Causal inference utilities
│   └── policy.py             # Policy recommendation logic
├── reports/                  # Saved figures and result summaries
├── outputs/                  # Model artifacts — not tracked by git
├── environment.yml
└── README.md

---

## Setup

```bash
# Clone the repo
git clone https://github.com/enny223/supply-chain-policy-lab.git
cd supply-chain-policy-lab

# Create and activate environment
conda env create -f environment.yml
conda activate scpl-env

# Download M5 data from Kaggle
# Place these files in data/raw/:
#   sales_train_validation.csv
#   calendar.csv
#   sell_prices.csv

# Launch notebooks
jupyter lab
```

---

## Why This Matters

This framework mirrors the infrastructure built by Amazon's SCOT Labs team for
evaluating supply chain policy changes across millions of products. The core
challenges — interference between units, heterogeneous treatment effects, and
offline policy evaluation before live deployment — are active research problems
in causal inference for operations.

---

## References

- Makridakis et al. (2022). M5 accuracy competition. *International Journal of
  Forecasting*.
- Imbens & Rubin (2015). *Causal Inference for Statistics, Social, and Biomedical
  Sciences*. Cambridge University Press.
- Athey & Imbens (2016). Recursive partitioning for heterogeneous causal effects.
  *PNAS*.