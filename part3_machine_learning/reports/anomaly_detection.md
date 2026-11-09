# Traffic Anomaly Detection

## Method

Isolation Forest was fit on the first 80% of the time-ordered data and applied to the latest 20%. The contamination value of 0.02 is an explicit modeling assumption.

## Holdout Result

- Records scored: 9638
- Anomalies: 243 (2.5%)
- Training period ends: 2017-11-01 19:00:00
- Holdout period begins: 2017-11-01 20:00:00

The highest-scoring observations are in `anomaly_scores.csv`; weekly flag rates are in `anomaly_monitoring.json`.

## Value and Limitations

This unsupervised score can prioritize unusual records for data-quality or operations review without requiring labels. It does not identify accidents. A shift from the earlier period can also reflect seasonality, concept drift, or sensor changes, and the configured contamination is not an observed event rate.
