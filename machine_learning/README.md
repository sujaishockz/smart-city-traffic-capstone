# Machine Learning and AI: Building an Intelligent Mobility Solution

**Status: not started.** Scaffolded ahead of time so the repository structure
is visible from the first commit.

## Planned Folder Structure

```
machine_learning/
├── notebooks/            # EDA and modelling notebooks
├── models/               # Saved model artifacts (.pkl, .h5, etc.)
├── mlruns/                # MLflow tracking data (gitignored — see .gitignore)
├── deployment/           # FastAPI/Flask deployment mock-up
├── reports/
│   ├── bias_fairness/    # Bias & fairness report
│   └── (final capstone report)
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

## Logging

Every script uses `logging.getLogger(__name__)`; INFO for milestones
(data/model loaded or saved), WARNING for recoverable issues (dropped rows,
capped outliers, monitoring alerts). `print()` is reserved for direct
CLI/user-facing output only.

## How to Run

_To be added once modelling work begins._
