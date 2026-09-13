# Smart City Traffic Capstone
**Smart City Traffic Intelligence: From Data Analytics to AI-Powered Mobility**

NUS SOC AMLDS Capstone Project — Week 33

## Project Description

This project transforms ~48,000 hourly records of westbound I-94 traffic volume
(near Minneapolis–St Paul), together with weather and US federal holiday data,
into an end-to-end traffic intelligence solution. The work is split into three
connected parts that build on one another:

| Folder | Focus | Status |
|---|---|---|
| [`data_analytics/`](data_analytics/) | SQL analysis, descriptive statistics, probability, Power BI dashboard | 🟡 In progress (SQL analysis started) |
| [`python_pipeline/`](python_pipeline/) | Reproducible Python pipeline, feature engineering, visualisations, CLI app | ⚪ Not started |
| [`machine_learning/`](machine_learning/) | Supervised/unsupervised ML, deep learning, explainability, MLOps, recommendations | ⚪ Not started |

## Repository Structure

```
smart-city-traffic-capstone/
├── data_analytics/
│   ├── data/                  # Raw CSV dataset
│   ├── db/                    # SQLite database (built from the CSV)
│   ├── sql/                   # SQL scripts for each task
│   ├── reports/               # Insights report(s) and query outputs
│   └── README.md
├── python_pipeline/
│   ├── pipeline.py            # Data pipeline (load, validate, clean)
│   ├── feature_engineering.py # ML-ready feature creation
│   ├── visualizations.py      # Matplotlib charts
│   ├── mini_app/              # CLI analytics application
│   ├── figures/               # Saved charts
│   ├── logs/                  # pipeline.log sample output
│   └── README.md
├── machine_learning/
│   ├── notebooks/             # EDA / modelling notebooks
│   ├── models/                # Saved model artifacts
│   ├── mlruns/                # MLflow experiment tracking (gitignored)
│   ├── deployment/            # FastAPI/Flask deployment mock-up
│   ├── reports/               # Final report + bias & fairness report
│   └── README.md
├── .gitignore
└── README.md
```

## Tools and Technologies

- **Data Analytics**: SQLite, SQL, Power BI, Power Query
- **Python**: pandas, NumPy, Matplotlib, sqlite3, logging, argparse
- **Machine Learning**: scikit-learn, mlxtend (association rules), TensorFlow/PyTorch (deep learning), SHAP/LIME, MLflow, FastAPI/Flask

## How to Run

Each part has its own README with detailed run instructions:
- [Data Analytics](data_analytics/README.md)
- Python Pipeline (added once that work begins)
- Machine Learning (added once that work begins)

## Logging Configuration

Starting in the Python pipeline work, all pipeline and application code uses Python's built-in
`logging` module (never `print()` for internal status):
- Logger created per-module via `logging.getLogger(__name__)`
- Handlers configured only in the entry-point script(s), writing to **console**
  and to a **log file** (`python_pipeline/logs/pipeline.log`)
- Format includes timestamp, log level, module name and message
- **DEBUG** – fine-grained internal values (e.g. quartile thresholds)
- **INFO** – normal milestones (data loaded, figure saved, model saved)
- **WARNING** – recoverable issues (rows dropped/imputed, outliers capped)
- **ERROR** – failures that stop the pipeline, logged with `exc_info=True`

## Assumptions and Limitations

- No accident dataset was provided. The machine learning classification task uses a
  **documented proxy accident-risk label** derived from congestion severity and
  adverse/low-visibility weather — see `machine_learning/README.md` once
  added. This proxy is for demonstrating the ML workflow only and is **not** a
  real accident risk prediction.
- The dataset represents a single corridor (westbound I-94), so travel
  recommendations focus on **timing**, not route selection.

## Commit History

This repository is built with incremental, descriptively named commits
corresponding to each task (see the commit log). Work is not submitted as a
single large commit.

## Author

Capstone submission — NUS SOC AMLDS
