# Bias, Fairness, Governance, and Sustainability

## Scope and Fairness Assessment

The dataset has no demographic or legally protected-group attributes. The results below are operational subgroup diagnostics for day type, an adverse-weather grouping, and observed weather classes; they are not a formal demographic fairness audit.

The Random Forest was evaluated on a chronological holdout of 9,638 rows. The constructed proxy-positive rate was 21.0%; the predicted-positive rate was 22.8%.

### Day Type

| Group | N | Actual positive rate | Predicted positive rate | TPR/recall | FPR | Precision | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| weekday | 6876 | 0.240 | 0.255 | 0.987 | 0.023 | 0.930 | 0.958 |
| weekend | 2762 | 0.133 | 0.161 | 0.921 | 0.045 | 0.760 | 0.833 |

### Weather Risk

| Group | N | Actual positive rate | Predicted positive rate | TPR/recall | FPR | Precision | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| adverse_or_low_visibility | 4325 | 0.467 | 0.508 | 0.975 | 0.099 | 0.896 | 0.934 |
| other_weather | 5313 | 0.000 | 0.000 | n/a | 0.000 | 0.000 | 0.000 |

### Weather Main

| Group | N | Actual positive rate | Predicted positive rate | TPR/recall | FPR | Precision | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Clear | 2830 | 0.000 | 0.000 | n/a | 0.000 | 0.000 | 0.000 |
| Clouds | 2483 | 0.000 | 0.000 | n/a | 0.000 | 0.000 | 0.000 |
| Drizzle | 339 | 0.575 | 0.587 | 0.979 | 0.056 | 0.960 | 0.970 |
| Fog | 219 | 0.247 | 0.342 | 0.907 | 0.158 | 0.653 | 0.760 |
| Haze | 367 | 0.545 | 0.589 | 0.995 | 0.102 | 0.921 | 0.957 |
| Mist | 1338 | 0.416 | 0.433 | 0.959 | 0.059 | 0.921 | 0.939 |
| Rain | 1032 | 0.525 | 0.563 | 0.993 | 0.088 | 0.926 | 0.958 |
| Snow | 759 | 0.444 | 0.524 | 0.964 | 0.173 | 0.817 | 0.884 |
| Thunderstorm | 269 | 0.494 | 0.550 | 0.992 | 0.118 | 0.892 | 0.940 |

Day type and weather are context variables, not protected attributes. Weather is also part of the proxy-label definition, so performance differences by weather are partly induced by target construction. Small weather groups below the configured support threshold are listed in the JSON and excluded from rate comparison.

The high proxy-model scores do not establish accident-prediction ability. Do not use this model for enforcement, individual risk scoring, or safety-critical decisions. Any future deployment requires an actual incident dataset, stakeholder review, calibration, and fairness testing on appropriate protected-group data collected and governed lawfully.

## Governance Controls

- Intended purpose: educational traffic-pattern analysis and travel-timing exploration on the studied I-94 corridor.
- Data provenance: public Metro Interstate Traffic Volume records, 2012-2018; no person-level or incident-level records were provided.
- Human oversight: treat recommendations and anomaly flags as review aids; verify current traffic and weather before acting.
- Versioning: model artifacts use version 1.0.0 in the model catalog; evaluation data, parameters, metrics, and model signature are recorded in MLflow.
- Change control: retrain only after data-quality checks and chronological evaluation; compare new subgroup metrics and drift status before replacing a model.
- Privacy and security: this dataset contains no direct personal identifiers; keep credentials out of artifacts and restrict writable access to model/report directories in any deployed environment.

## Sustainability

The saved model artifacts total 16,070,612 bytes (15.33 MB). Training and inference were run on CPU; the available AMD GPU was not used. Energy and carbon emissions were not measured, so no environmental impact estimate is claimed.

For a project of roughly 48,000 rows, the compact scikit-learn models avoid a continuously hosted GPU and can be reused rather than retrained for every prediction. Future runs should record wall time, hardware, memory, and energy where available, and retrain only when monitoring or new validated data justifies it.

## Limitations

- One westbound corridor and historical data limit geographic and temporal representativeness.
- Congestion and weather define the proxy target; there is no observed accident outcome or causal evidence.
- No demographic attributes means protected-group fairness remains unmeasurable from the supplied data.
- Weather/day-type subgroup differences are diagnostic only and should not be treated as evidence of discrimination or its absence.
