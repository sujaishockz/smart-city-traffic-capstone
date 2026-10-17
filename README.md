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
| [`machine_learning/`](machine_learning/) | Supervised/unsupervised ML, neural network, explainability, MLOps, recommendations | Complete |

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

### Milestone 3: Machine Learning and AI — Complete

- [x] Create the quartile-based congestion category and documented proxy accident-risk label; state that it is not actual accident prediction.
- [x] Task 1: Train at least two classification and two regression algorithms; compare with the specified metrics.
- [x] Task 2: Apply K-means clustering and association-rule mining; interpret clusters and high-lift rules.
- [x] Task 3: Implement a neural network, LSTM, or CNN and apply SHAP or LIME explainability.
- [x] Task 4: Apply an advanced AI technique and document its rationale, implementation, value, and limitations.
- [x] Task 5: Build a travel-timing recommendation using day type and, where useful, weather.
- [x] Task 6.1: Document model versions and performance.
- [x] Task 6.2: Track experiments, parameters, metrics, and model versions with MLflow.
- [x] Task 6.3: Create a FastAPI or Flask deployment simulation serving at least one model.
- [x] Task 6.4: Simulate prediction-error or feature-distribution drift monitoring.
- [x] Task 6.5: Report monitoring status as PASS/Normal or ALERT/Requires investigation.
- [x] Task 7: Complete bias/fairness, governance, and sustainability analysis.
- [x] Final deliverables: models, notebooks/scripts, MLflow evidence, deployment and recommendation components, final report, fairness report, and README.

## Repository Structure

```
smart-city-traffic-capstone/
├── data_analytics/
│   ├── data/                  # Raw CSV dataset
│   ├── db/traffic.db          # SQLite database
│   ├── reports/               # Findings, dashboard specification and .pbix
│   ├── sql/                   # SQL and statistics/probability scripts
│   └── README.md
├── python_pipeline/
│   ├── data/processed/        # Cleaned and engineered CSV outputs
│   ├── figures/               # Four generated charts
│   ├── mini_app/traffic_cli.py
│   ├── reports/               # Methodology and chart interpretations
│   ├── pipeline.py
│   ├── feature_engineering.py
│   ├── visualizations.py
│   ├── requirements.txt
│   └── README.md
├── machine_learning/
│   ├── deployment/app.py      # FastAPI model-serving simulation
│   ├── models/                # Versioned model artifacts
│   ├── mlruns/                # Local MLflow store (gitignored)
│   ├── reports/               # Task metrics, final report and fairness review
│   ├── tests/                 # 14 unit tests
│   ├── requirements.txt
│   └── README.md
├── .gitignore
└── README.md
```

## Tools and Technologies

- **Data Analytics**: SQLite, SQL, Power BI, Power Query
- **Python**: pandas, NumPy, Matplotlib, sqlite3, logging, argparse
- **Machine Learning**: scikit-learn, mlxtend (association rules), MLPClassifier, LIME, MLflow, FastAPI and Uvicorn

## How to Run

### Get Started

From the repository root, create a virtual environment and install the Python
dependencies. The data-analytics scripts use only Python's standard library;
the ML dependency set also includes the packages needed for the API and MLflow.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r python_pipeline/requirements.txt
python -m pip install -r machine_learning/requirements.txt
```

On Windows, activate the environment with `.venv\Scripts\activate`.

### End-to-End Verification

Run these commands from the repository root. They rebuild the SQLite database,
execute the analytics, regenerate the Python outputs, retrain the ML artifacts,
and run the unit suite.

```bash
# Milestone 1: database, SQL, statistics and probabilities
python data_analytics/sql/load_csv_to_sqlite.py
sqlite3 -bail data_analytics/db/traffic.db < data_analytics/sql/02_annual_traffic_trends.sql
sqlite3 -bail data_analytics/db/traffic.db < data_analytics/sql/03_holiday_temperature.sql
python data_analytics/sql/04_descriptive_statistics.py
python data_analytics/sql/05_probability_congestion.py
sqlite3 -bail data_analytics/db/traffic.db < data_analytics/sql/06_powerbi_queries.sql

# Milestone 2: clean, engineer, visualize and query
python python_pipeline/pipeline.py
python python_pipeline/feature_engineering.py
python python_pipeline/visualizations.py
python python_pipeline/mini_app/traffic_cli.py lookup '2017-01-01 08:00:00'
python python_pipeline/mini_app/traffic_cli.py high-traffic --limit 3
python python_pipeline/mini_app/traffic_cli.py compare-days
python python_pipeline/mini_app/traffic_cli.py recommend --day-type weekday --weather Clear

# Milestone 3: train, analyze, serve/report and test
python machine_learning/train_supervised.py
python machine_learning/analyze_patterns.py
python machine_learning/train_neural_explainer.py
python machine_learning/detect_anomalies.py
python machine_learning/recommend_travel_time.py --report
python machine_learning/run_mlops.py
python machine_learning/monitor_drift.py
python machine_learning/analyze_responsible_ai.py
python -m unittest discover -s machine_learning/tests -v
python -m pip check
```

The automated `unittest` suite covers the ML components (14 tests). Milestones
1 and 2 are checked by running their database/analysis scripts and CLI smoke
commands above; they do not currently have separate unit-test packages.

The invalid-input path can be checked with
`python python_pipeline/mini_app/traffic_cli.py lookup invalid`; it should log
the format error, return exit code 2, and not print a traceback. Confirm the
database has 48,204 rows, the cleaned/features CSVs have 48,187 rows, and four
PNG files exist under `python_pipeline/figures/`.

The verification commands regenerate tracked databases, logs, models, and
reports. Review `git status` afterward before committing; MLflow run files under
`machine_learning/mlruns/` are local and gitignored.

For the local model API, start
`uvicorn machine_learning.deployment.app:app --host 127.0.0.1 --port 8000`,
then check `GET /health` and `POST /predict`; the payload and expected response
are documented in [the ML guide](machine_learning/README.md).

The Power BI deliverable is
[`data_analytics/reports/smart-city-traffic-dashboard.pbix`](data_analytics/reports/smart-city-traffic-dashboard.pbix).
`unzip -t` checks package integrity. For the actual visual interaction check,
open it in Power BI Desktop on Windows and verify the KPI cards, four visuals,
and hour/weather/traffic-category slicers; Power BI Desktop's visual UI could
not be exercised on this macOS environment.

Detailed instructions and results are in the [Data Analytics](data_analytics/README.md),
[Python Pipeline](python_pipeline/README.md), and [Machine Learning](machine_learning/README.md)
guides.

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
  **documented proxy accident-risk label** derived from training-period upper-half
  congestion and adverse/low-visibility weather. See the completed Part 3 report
  and `machine_learning/README.md`. This proxy demonstrates the ML workflow only
  and is **not** a real accident-risk prediction.
- The dataset represents a single corridor (westbound I-94), so travel
  recommendations focus on **timing**, not route selection.

## Commit History

This repository is built with incremental, descriptively named commits
corresponding to each task (see the commit log). Work is not submitted as a
single large commit.

## Author

Capstone submission — NUS SOC AMLDS
