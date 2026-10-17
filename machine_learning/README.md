# Machine Learning and AI: Building an Intelligent Mobility Solution

**Status: in progress.** Task 1's supervised benchmark is implemented and
validated; remaining milestone tasks are listed below.

## Planned Folder Structure

```
machine_learning/
├── notebooks/             # EDA and modelling notebooks
├── models/                # Selected Task 1 model artifacts
├── mlruns/                # MLflow tracking data (gitignored — see .gitignore)
├── deployment/            # FastAPI/Flask deployment mock-up
├── reports/
│   ├── bias_fairness/     # Bias & fairness report
│   ├── supervised_metrics.json
│   └── (final capstone report)
├── tests/                 # Focused model-pipeline tests
├── requirements.txt
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

## Logging

Every script uses `logging.getLogger(__name__)`; INFO for milestones
(data/model loaded or saved), WARNING for recoverable issues (dropped rows,
capped outliers, monitoring alerts). `print()` is reserved for direct
CLI/user-facing output only.

## How to Run

_To be added once modelling work begins._
