# Supply Chain Policy Lab

A causal inference and simulation framework for evaluating inventory policy
changes in retail supply chains, built on real Walmart sales data from the
M5 Forecasting Competition.

---

## Problem

A retailer wants to know: **does increasing safety stock levels reduce stockouts
enough to justify the additional holding cost — and for which products?**

Simple question. Hard to answer causally because:
- Products in the same category share warehouse space — treating one affects others
- Demand for substitute products is correlated — stockouts cause spillover
- The effect is heterogeneous — works differently across product velocity segments
- Standard A/B testing assumptions break down in supply chains

---

## Results

### Causal Effect of 1.5x Safety Stock Policy
| Method | ATE | p-value | 95% CI |
|---|---|---|---|
| Simple OLS | -0.45pp | 0.056 | [-0.90pp, 0.00pp] |
| OLS with covariates | **-0.79pp** | **0.0001** | [-1.17pp, -0.41pp] |

A 50% increase in safety stock causally reduces stockout rate by **0.79 percentage
points** — statistically significant after controlling for demand, holding cost,
segment and store.

### Heterogeneous Treatment Effects by Segment
| Segment | Baseline Stockout | Reduction | HC Increase | CB Ratio |
|---|---|---|---|---|
| Fast (>10 units/day) | 18.62% | -2.41pp | +50.8% | 4.2x |
| Medium (2-10/day) | 15.69% | -1.86pp | +43.9% | 5.3x |
| Slow (0.5-2/day) | 9.90% | -1.33pp | +35.9% | **6.0x** |
| Dead slow (<0.5/day) | 2.12% | -0.79pp | +26.4% | 4.1x |

### Recommended Policy
| Segment | Recommended Multiplier | Rationale |
|---|---|---|
| Fast | 3.0x | Highest absolute benefit, justifies cost |
| Medium | 2.0x | Good cost-benefit tradeoff |
| Slow | 1.5x | Best CB ratio — modest cost, real benefit |
| Dead slow | No change | Not worth additional holding cost |

### Budget-Constrained Rollout
- Top 20% of products by CB ratio → captures 32% of benefit at $32/day extra cost
- Top 50% → captures 65% of benefit at $88/day
- Full catalog → $943K total benefit at $211/day holding cost increase

---

## Pipeline

| Notebook | Description | Key Output |
|---|---|---|
| `01_data_ingestion` | Load 58M rows, write to Parquet | `daily_sales.parquet` |
| `01b_eda` | 6 findings inform all downstream decisions | 5 report figures |
| `02_demand_forecasting` | LightGBM with price + store features | RMSE 2.28, forecasts |
| `03_inventory_simulation` | Warehouse simulation, calibrated to 9.24% | `simulation_results.parquet` |
| `04_experiment_design` | Cluster RCT, 12 clusters, balanced | `experiment_dataset.parquet` |
| `05_causal_inference` | DiD + EconML CausalForest | ATE -0.79pp |
| `06_policy_recommendation` | Cost-benefit, optimal multiplier per segment | Policy table |

---

## Key Methodological Decisions

**Why cluster randomization:**
Products within the same department are substitutes. Randomizing at department
level keeps substitution spillovers within treatment or control groups rather
than crossing the boundary (SUTVA violation).

**Why EDA before modeling:**
EDA revealed price promotions drive 70x demand spikes invisible to a model
without price features. Notebook 02 was rewritten after EDA findings.

**Why indirect calibration:**
M5 contains sales data not inventory records. Simulation parameters were
calibrated to match the observed 8.4% stockout proxy rate from EDA.

**Positivity violation:**
FOODS_2 clusters were never treated (0% treatment rate). CATE estimates
for fast movers are unreliable — direct simulation comparison used instead.

---

## Dataset

**M5 Forecasting Competition — Walmart Sales Data**
`https://www.kaggle.com/competitions/m5-forecasting-accuracy/data`

- 3,049 products across 10 Walmart stores in 3 states
- 1,941 days of daily sales (2011—2016)
- Scope: FOODS category, California stores, 2013—2016

> Data not included. Download from Kaggle and place in `data/raw/`.
> Run notebooks in order to regenerate all outputs.

---

## Structure

supply-chain-policy-lab/
├── data/
│   ├── raw/                  # M5 CSVs — not tracked
│   ├── processed/            # Intermediate — not tracked
│   └── parquet/              # Parquet files — not tracked
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 01b_eda.ipynb
│   ├── 02_demand_forecasting.ipynb
│   ├── 03_inventory_simulation.ipynb
│   ├── 04_experiment_design.ipynb
│   ├── 05_causal_inference.ipynb
│   └── 06_policy_recommendation.ipynb
├── src/
│   ├── simulation.py         # Inventory simulation engine
│   └── init.py
├── reports/                  # Saved figures
├── outputs/                  # Model artifacts — not tracked
├── environment.yml
└── README.md

---

## Setup

```bash
git clone https://github.com/enny223/supply-chain-policy-lab.git
cd supply-chain-policy-lab

conda env create -f environment.yml
conda activate scpl-env

# Download M5 data from Kaggle → place in data/raw/
# Run notebooks in order: 01 → 01b → 02 → 03 → 04 → 05 → 06

jupyter lab
```

---

## Why This Mirrors Industry Practice

This framework replicates the core infrastructure of Amazon's SCOT Labs team:

| Amazon SCOT Labs | This Project |
|---|---|
| RCT design at supply chain scale | Cluster RCT across 5,667 product-store combinations |
| Interference modeling | Cluster randomization to contain substitution spillovers |
| Supply chain emulation | Inventory simulation calibrated to observed stockout rate |
| Treatment effect estimation | OLS + EconML CausalForest heterogeneous effects |
| Policy evaluation before deployment | Multi-multiplier simulation finds optimal per segment |

---

## References

- Makridakis et al. (2022). M5 accuracy competition. *International Journal of Forecasting*
- Imbens & Rubin (2015). *Causal Inference for Statistics, Social, and Biomedical Sciences*
- Athey & Imbens (2016). Recursive partitioning for heterogeneous causal effects. *PNAS*
- Chernozhukov et al. (2018). Double/debiased machine learning. *Econometrics Journal*
