# Machine Learning and AI: Building an Intelligent Mobility Solution

**Status: complete.** Tasks 1 through 7 are implemented and validated; the
final Part 3 report and fairness/governance report are included.

## Planned Folder Structure

```
machine_learning/
├── notebooks/             # Reserved scaffold; current workflows are scripts
├── models/                # Trained classifiers, regressors, clusterers and detector
├── mlruns/                # MLflow tracking data (gitignored — see .gitignore)
├── deployment/
│   └── app.py              # FastAPI model-serving simulation
├── reports/
│   ├── bias_fairness/
│   │   ├── bias_fairness_governance_sustainability.md
│   │   └── bias_fairness_metrics.json
│   ├── cluster_assignments.csv
│   ├── pattern_analysis.md
│   ├── pattern_analysis.json
│   ├── neural_explainability.md
│   ├── neural_explainability.json
│   ├── anomaly_detection.md
│   ├── anomaly_monitoring.json
│   ├── anomaly_scores.csv
│   ├── travel_recommendations.md
│   ├── travel_recommendations.json
│   ├── model_versions.json
│   ├── mlflow_evidence.json
│   ├── drift_monitoring.md
│   ├── drift_monitoring.json
│   ├── supervised_metrics.json
│   └── part3_final_report.md
├── tests/                 # Focused model-pipeline tests
├── requirements.txt
├── analyze_patterns.py
├── analyze_responsible_ai.py
├── detect_anomalies.py
├── monitor_drift.py
├── recommend_travel_time.py
├── run_mlops.py
├── train_neural_explainer.py
├── train_supervised.py
└── README.md
```

## Important Note — No Accident Dataset

No accident dataset was provided for this capstone. The classification task
uses the documented `high_risk_proxy`: a record is positive when its
training-threshold congestion category is High/Severe (the upper half of
traffic volumes) and observed weather is adverse or low-visibility. The label
demonstrates an ML workflow only; it is not a real accident-risk prediction.
See the completed Part 3 final report for the definition and limitations.

## Milestone Tasks

1. Supervised ML — classification (proxy accident risk) + regression
   (traffic volume), 2 algorithms each, compared on standard metrics.
2. Unsupervised ML — K-means clustering of traffic conditions + association
   rule mining over discretised time/weekday/weather features.
3. Deep learning (NN or LSTM) with SHAP/LIME explainability.
4. One advanced technique (MLflow recommended, or quantisation / GAN /
   self-supervised anomaly detection).
5. Traffic recommendation system (best travel windows by day type/weather).
6. MLOps simulation — model versioning, MLflow experiment tracking, a
   FastAPI/Flask deployment mock-up, drift monitoring, PASS/ALERT reporting.
7. Responsible & sustainable AI — bias & fairness report, governance and
   sustainability discussion.

## Supervised Learning (Task 1)

Run from the repository root after installing `machine_learning/requirements.txt`:

```bash
python machine_learning/train_supervised.py
```

The benchmark sorts records by timestamp and reserves the latest 20% for
testing. Numeric preprocessing is fitted inside each model pipeline using only
the training period. It compares logistic regression and random forest for
classification, and random forest and histogram gradient boosting for traffic
volume regression. Classification metrics are accuracy, precision, recall,
F1, and ROC-AUC; regression metrics are MAE, RMSE, and R-squared.

The script derives Low/Medium/High/Severe congestion from training-period
traffic-volume quartiles. `high_risk_proxy` is true when traffic is in the
training-defined upper half (High or Severe) and observed weather is adverse
or low-visibility. This is a constructed teaching label, not an accident
observation or actual accident-risk prediction. Weather is part of the proxy
definition, so classification scores measure prediction of this proxy only.
The supplied dataset is retrospective and does not establish causal effects
or guarantee future performance.

Metrics are written to `machine_learning/reports/supervised_metrics.json` and
the best-F1 classifier and lowest-RMSE regressor are serialized under
`machine_learning/models/`. Training and unit tests run on CPU; the available
AMD Radeon GPU is not used by scikit-learn's estimators.

The 20% time-based holdout contains 9,638 records (2017-11-01 through
2018-09-30). Random Forest classified the proxy label with F1 0.934 and
ROC-AUC 0.992. Histogram Gradient Boosting predicted traffic volume with
MAE 287.4 vehicles/hour, RMSE 509.1, and R-squared 0.933. These scores describe
only this historical split; the strong proxy-label result is not evidence of
real-world accident prediction.

Run the focused tests with:

```bash
python -m unittest discover -s machine_learning/tests -v
```

## Unsupervised Pattern Analysis (Task 2)

Run from the repository root:

```bash
python machine_learning/analyze_patterns.py
```

The script standardizes time, calendar, weather, and traffic-volume features
before fitting four K-means clusters. It mines up to 20 association rules from
hour band, weekday/weekend, weather group, and congestion category; defaults
are minimum support 0.03 and minimum lift 1.2. The cluster model and row-level
assignments are saved under `machine_learning/models/` and
`machine_learning/reports/`; JSON and Markdown reports include the profiles,
rules, thresholds, and limitations.

Across 48,187 records, the largest cluster contained 18,505 weekday records
with high-volume conditions (mean 5,232 vehicles/hour) and dominant Severe
congestion. A separate 13,700-record cluster consisted entirely of weekend
observations with mean traffic volume 2,571. The strongest reported rule links
weekday Medium congestion with late evening (support 0.098, confidence 0.636,
lift 3.83). Weekend overnight conditions linked to Low congestion with
confidence 0.886 and lift 3.54. These describe historical co-occurrences on
one corridor; neither clusters nor rules imply causation or generalize
automatically to other roads.

## Neural Network and LIME (Task 3)

Run the CPU MLP and local LIME explanations with:

```bash
python machine_learning/train_neural_explainer.py
```

The two-hidden-layer MLP uses the Task 1 chronological split and its
training-derived `high_risk_proxy` target. On the latest 20% holdout it reached
accuracy 0.972, precision 0.912, recall 0.959, F1 0.935, and ROC-AUC 0.992.
LIME explains five positive and five negative holdout examples using original
numeric units and binary weather indicators. The model is saved as
`machine_learning/models/traffic_risk_neural_network.joblib`; the metrics and
per-example explanations are saved in `machine_learning/reports/`.

LIME explanations are local surrogate approximations, not causal explanations.
Observed weather contributes to the proxy-label definition, so weather
features partly explain the constructed label. Neither the model nor its
explanations predict observed accidents.

## Advanced Technique: Isolation Forest (Task 4)

Run the chronological anomaly-scoring simulation with:

```bash
python machine_learning/detect_anomalies.py
```

Isolation Forest was selected to find unusual combinations of traffic,
calendar, and weather features without accident labels. It fits on the first
80% of records and scores the latest 20%, using a documented 2% contamination
assumption. The 9,638-row holdout contained 243 flagged records (2.5%). The
saved model, per-record scores, weekly rates, and highest-scoring examples are
under `machine_learning/models/` and `machine_learning/reports/`.

This technique's value is prioritizing unusual records for review. There are
no incident labels to validate those flags: an anomaly is not an accident, and
the holdout rate may reflect seasonality, concept drift, sensor changes, or
the contamination assumption rather than an operational event rate.

## Travel-Timing Recommendations (Task 5)

Generate the report for weekday/weekend and the three most common weather
conditions, or request a specific recommendation:

```bash
python machine_learning/recommend_travel_time.py --report
python machine_learning/recommend_travel_time.py --day-type weekend --weather Clear --month 6
```

The recommender loads the Task 1 traffic-volume regressor, supplies median
historical numeric weather measurements for the requested weather class, and
ranks non-overlapping two-hour windows. For a June weekend with Clear weather,
the top estimated window is 03:00-05:00 at about 452 vehicles/hour. The report
includes the historical support count and can be regenerated for a different
month. Results are based on 2012-2018 corridor data, assume a non-holiday, and
are not real-time forecasts or route recommendations.

## MLOps Simulation (Task 6)

### Model Versions and MLflow

The version/performance catalog in `machine_learning/reports/model_versions.json`
lists the five persisted models as version `1.0.0`, their artifact paths,
algorithms, scikit-learn version, and task-specific metrics. Log the selected
traffic-volume model to the local MLflow experiment store with:

```bash
python machine_learning/run_mlops.py
```

The run records parameters, holdout metrics, model signature, input example,
and artifact under the `traffic-volume-regression` experiment. The local
`machine_learning/mlruns/` store is gitignored; the run ID and metric summary
are preserved in `machine_learning/reports/mlflow_evidence.json`.

### Model Serving

Start the FastAPI simulation from the repository root:

```bash
uvicorn machine_learning.deployment.app:app --host 127.0.0.1 --port 8000
```

`GET /health` reports the served version. `POST /predict` serves the saved
traffic-volume regressor and validates hour, calendar, weather, and month
inputs. This is a local demonstration, not a production deployment.

In another terminal, check the health response and submit a sample prediction:

```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/predict \
   -H 'Content-Type: application/json' \
   -d '{"hour":8,"day_of_week":1,"is_weekend":0,"holiday_flag":0,"month":6,"temp":290,"rain_1h":0,"snow_1h":0,"clouds_all":25,"weather_main":"Clear"}'
```

### Drift Monitoring

Run the PSI feature-distribution monitor with:

```bash
python machine_learning/monitor_drift.py
```

The baseline is the first 80% of the chronological dataset; the recent sample
is the final 20%. PSI 0.2 triggers `ALERT/Requires investigation`. The current
holdout status is **ALERT/Requires investigation** because
`clouds_all_scaled` PSI is 0.390. A controlled +50% traffic-volume shift also
alerts (traffic PSI 0.878), demonstrating the alert path. PSI indicates
distribution change, not predictive error; inspect seasonality and data
quality before taking operational action.

## Responsible AI and Final Report (Task 7)

Generate the subgroup diagnostics, governance/sustainability report, and
integrated Part 3 report with:

```bash
python machine_learning/analyze_responsible_ai.py
```

The report compares proxy-classifier TPR, FPR, precision, and F1 across
weekday/weekend and observed-weather groups on the chronological holdout. The
dataset has no demographic attributes, so these operational segments do not
constitute a protected-group fairness audit. Weather is part of the proxy-label
definition, which creates expected differences between weather groups.

See `machine_learning/reports/bias_fairness/` for subgroup metrics and
governance/sustainability findings, and
`machine_learning/reports/part3_final_report.md` for the integrated summary of
all Part 3 tasks, results, limitations, and reproduction steps.

## Logging

Every script uses `logging.getLogger(__name__)`; INFO for milestones
(data/model loaded or saved), WARNING for recoverable issues (dropped rows,
capped outliers, monitoring alerts). `print()` is reserved for direct
CLI/user-facing output only.

## How to Run

From the repository root, install the pinned dependencies and run the complete
test suite:

```bash
python -m pip install -r machine_learning/requirements.txt
python -m unittest discover -s machine_learning/tests -v
```

Run each task script from the repository root using the commands in its section
above. The final synthesis is in
`machine_learning/reports/part3_final_report.md`.
