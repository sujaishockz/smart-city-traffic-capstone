# Machine Learning and AI: Building an Intelligent Mobility Solution

**Status: in progress.** Tasks 1 through 5 are implemented and validated; remaining
milestone tasks are listed below.

## Planned Folder Structure

```
machine_learning/
├── notebooks/             # EDA and modelling notebooks
├── models/                # Selected Task 1 model artifacts
├── mlruns/                # MLflow tracking data (gitignored — see .gitignore)
├── deployment/            # FastAPI/Flask deployment mock-up
├── reports/
│   ├── bias_fairness/     # Bias & fairness report
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
│   ├── supervised_metrics.json
│   └── (final capstone report)
├── tests/                 # Focused model-pipeline tests
├── requirements.txt
├── analyze_patterns.py
├── detect_anomalies.py
├── recommend_travel_time.py
├── train_neural_explainer.py
├── train_supervised.py
└── README.md
```

## Important Note — No Accident Dataset

No accident dataset was provided for this capstone. The classification task
uses a **documented proxy accident-risk label**: a record is flagged
`high_risk` when High/Severe congestion (top 2 quartiles of `traffic_volume`)
coincides with severe or low-visibility weather. This proxy demonstrates the
ML classification workflow only and must not be interpreted as a real
accident-risk prediction — this will be stated explicitly in the final report.

## Planned Tasks

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

## Logging

Every script uses `logging.getLogger(__name__)`; INFO for milestones
(data/model loaded or saved), WARNING for recoverable issues (dropped rows,
capped outliers, monitoring alerts). `print()` is reserved for direct
CLI/user-facing output only.

## How to Run

_To be added once modelling work begins._
