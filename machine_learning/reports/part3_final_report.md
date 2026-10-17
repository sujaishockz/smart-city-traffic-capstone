# Part 3 Final Report: Machine Learning and AI

## Executive Summary

Part 3 adds supervised models, descriptive clustering and association rules, a neural network with LIME explanations, Isolation Forest anomaly scoring, model-based travel timing, and an MLOps simulation to the Part 2 I-94 traffic pipeline. All modeling was run locally on CPU; no CUDA GPU was available or required.

The results demonstrate a reproducible workflow on approximately 48,000 historical hourly observations. They do not demonstrate actual accident prediction: the risk target is a constructed proxy, and the dataset contains no accident outcomes.

## Results by Task

### Task 1: Supervised Models

A chronological 80/20 split used 38,549 training and 9,638 test rows. The best proxy classifier was Random Forest (F1 0.934, ROC-AUC 0.992). Histogram Gradient Boosting was the best traffic regressor (MAE 287.4, RMSE 509.1 vehicles/hour, R-squared 0.933).

The proxy is positive for upper-half congestion combined with adverse or low-visibility weather, using congestion thresholds calculated from training data. Since observed weather is part of the target rule, the classifier metrics must be read as performance on that proxy only.

### Task 2: Unsupervised Patterns

K-means formed four condition clusters. The largest contains 18,505 observations (high-volume; mean volume 5232). The strongest association rule has lift 3.83 and support 0.098. These are descriptive co-occurrences, not causal rules.

### Task 3: Neural Network and Explainability

The MLP classifier reached F1 0.935 and ROC-AUC 0.992 on the same chronological proxy task. LIME explanations are local approximations; they do not provide causal explanations or real accident-risk drivers.

### Task 4: Advanced Anomaly Detection

An Isolation Forest trained on the earlier period flagged 243 of 9,638 later-period records (2.5%) using a 2% contamination assumption. Flags indicate unusual feature combinations, not incidents.

### Task 5: Travel Recommendations

The traffic regressor ranks two-hour windows by day type, month, and observed weather class. For a June weekend with Clear weather, the model's first choice is 03:00-05:00 (estimated 452 vehicles/hour). This reflects typical historical weather measurements and is not a real-time forecast.

### Task 6: MLOps

Five artifacts are catalogued at version 1.0.0. MLflow run `d1451d4661544709b26080a4ca775308` tracks the traffic regressor and its chronological holdout metrics. A FastAPI simulation serves the regression model. PSI monitoring reports **ALERT/Requires investigation** for the recent holdout; `clouds_all_scaled` PSI is 0.390 against a 0.2 threshold. A controlled +50% traffic shift also exercises the ALERT path.

### Task 7: Responsible AI

Subgroup diagnostics compare weekday/weekend and weather segments. There are no demographic attributes, so a formal protected-group fairness audit is not possible. Combined model artifact size is 15.33 MB; training ran on CPU. Energy and carbon were not measured.

## Limitations and Use Boundaries

- The source covers one westbound I-94 corridor and the 2012-2018 period; external validity is limited.
- No accident, incident, or demographic data were provided. Proxy classification, fairness, and safety claims must remain constrained accordingly.
- Distribution drift is not predictive error. The observed PSI ALERT is driven by feature shifts and needs investigation; it does not establish model failure or traffic danger.
- Recommendations use historical averages/medians, assume no holiday, and do not include live traffic feeds.
- No energy or carbon measurements were available, so sustainability discussion is qualitative except for artifact sizes and CPU-only execution.

## Reproduction

Install pinned packages with `python -m pip install -r machine_learning/requirements.txt`, then run the scripts documented in `machine_learning/README.md`. Run tests with `python -m unittest discover -s machine_learning/tests -v`. For local serving, use `uvicorn machine_learning.deployment.app:app --host 127.0.0.1 --port 8000`.

Supporting metrics, models, configurations, and reports are stored under `machine_learning/models/` and `machine_learning/reports/`; the local MLflow run store is ignored by Git, with its run ID retained in the evidence JSON.
