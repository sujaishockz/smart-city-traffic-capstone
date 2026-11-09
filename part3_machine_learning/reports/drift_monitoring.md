# Feature-Distribution Drift Monitoring

- PSI threshold: 0.20
- Observed holdout status: **ALERT/Requires investigation**
- Controlled +50% traffic shift status: **ALERT/Requires investigation**

## Observed PSI by Feature

| Feature | PSI | Status |
|---|---:|---|
| traffic_volume | 0.008 | PASS |
| temp_scaled | 0.123 | PASS |
| rain_1h_scaled | 0.000 | PASS |
| clouds_all_scaled | 0.390 | ALERT |
| hour_sin | 0.000 | PASS |

The controlled scenario multiplies recent traffic volume by 1.5 to exercise the alert path. PSI is a distribution monitor, not a performance or incident metric; review alerts for seasonality and data-quality changes.
