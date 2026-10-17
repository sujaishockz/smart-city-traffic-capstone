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
| [`data_analytics/`](data_analytics/) | SQL analysis, descriptive statistics, probability, Power BI dashboard | ✅ Complete |
| [`python_pipeline/`](python_pipeline/) | Reproducible Python pipeline, feature engineering, visualisations, CLI app | ✅ Complete |
| [`machine_learning/`](machine_learning/) | Supervised/unsupervised ML, deep learning, explainability, MLOps, recommendations | ⚪ Not started |

## Capstone Progress Checklist

Update this checklist after each task is validated, committed, and pushed. Complete the milestones in order: Data Analytics, Python Pipeline, then Machine Learning and AI.

### Milestone 1: Data Analytics — Complete

- [x] Task 1.1: Load the CSV into SQLite and verify the loaded data.
- [x] Task 1.2: Analyze 2012–2017 annual traffic trends, year-over-year changes, and observations.
- [x] Task 1.3: Compare New Year's Day and Labor Day temperatures for 2015–2017 and discuss traffic context.
- [x] Task 2.1: Calculate and interpret traffic mean, median, standard deviation, variance, and range.
- [x] Task 2.2: Calculate and interpret temperature/traffic correlation; explain correlation versus causation.
- [x] Task 3: Calculate congestion/weather probabilities, conditional probabilities, independence comparison, and odds ratio.
- [x] Task 4.1: Prepare Power Query fields, check data quality/types, and create hour, Celsius temperature, and traffic category.
- [x] Task 4.2: Build daily, hourly, weather, and temperature/traffic dashboard visuals.
- [x] Task 4.3: Add KPI cards and hour, weather, and traffic-category slicers.
- [x] Deliver the SQLite/SQL work, Power BI dashboard, and 1–2 page insights report.

### Milestone 2: Python Data Pipeline — Complete

- [x] Task 1: Load and schema-validate the raw CSV; clean categories, timestamps, duplicates, and impossible values with logged handling.
- [x] Task 2: Engineer time/weather features, cyclical encodings, scaled numeric features, and quartile-based congestion categories.
- [x] Task 3: Save at least three Matplotlib visualizations with written interpretations.
- [x] Task 4: Provide at least three CLI queries, command/argument logging, and graceful invalid-input handling.
- [x] Task 5: Document setup, run steps, logging, and reproducibility; include pinned dependencies, sample log, and methodology/findings report.

### Milestone 3: Machine Learning and AI — In Progress

- [x] Create the quartile-based congestion category and documented proxy accident-risk label; state that it is not actual accident prediction.
- [x] Task 1: Train at least two classification and two regression algorithms; compare with the specified metrics.
- [x] Task 2: Apply K-means clustering and association-rule mining; interpret clusters and high-lift rules.
- [x] Task 3: Implement a neural network, LSTM, or CNN and apply SHAP or LIME explainability.
- [x] Task 4: Apply an advanced AI technique and document its rationale, implementation, value, and limitations.
- [x] Task 5: Build a travel-timing recommendation using day type and, where useful, weather.
- [ ] Task 6.1: Document model versions and performance.
- [ ] Task 6.2: Track experiments, parameters, metrics, and model versions with MLflow.
- [ ] Task 6.3: Create a FastAPI or Flask deployment simulation serving at least one model.
- [ ] Task 6.4: Simulate prediction-error or feature-distribution drift monitoring.
- [ ] Task 6.5: Report monitoring status as PASS/Normal or ALERT/Requires investigation.
- [ ] Task 7: Complete bias/fairness, governance, and sustainability analysis.
- [ ] Final deliverables: models, notebooks/scripts, MLflow evidence, deployment and recommendation components, final report, fairness report, and README.

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
│   ├── data/processed/        # Cleaned and engineered CSV outputs
│   ├── figures/               # Four saved charts
│   ├── logs/                  # End-to-end pipeline.log sample output
│   ├── reports/               # Part 2 findings and figure interpretations
│   └── requirements.txt       # Pinned Python dependencies
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
- [Python Pipeline](python_pipeline/README.md)
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
