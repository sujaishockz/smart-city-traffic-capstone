# Traffic Pattern Analysis

## K-means Clusters

| Cluster | Records | Traffic level | Mean volume | Mean hour | Weekend share | Dominant weather | Dominant congestion |
|---:|---:|---|---:|---:|---:|---|---|
| 0 | 13700 | moderate-volume | 2570.7 | 11.4 | 100.0% | Clouds | High |

moderate-volume conditions centered near hour 11.4, most often High congestion with Clouds weather.

| 1 | 15921 | moderate-volume | 1568.9 | 10.8 | 0.0% | Clear | Low |

moderate-volume conditions centered near hour 10.8, most often Low congestion with Clear weather.

| 2 | 61 | low-volume | 865.4 | 0.0 | 0.0% | Clear | Low |

low-volume conditions centered near hour 0.0, most often Low congestion with Clear weather.

| 3 | 18505 | high-volume | 5232.2 | 12.0 | 0.0% | Clouds | Severe |

high-volume conditions centered near hour 12.0, most often Severe congestion with Clouds weather.

## Highest-Lift Association Rules

| If these conditions occur | Then this condition occurs | Support | Confidence | Lift |
|---|---|---:|---:|---:|
| congestion_category_Medium + day_type_weekday | hour_band_late_evening | 0.098 | 0.636 | 3.83 |
| hour_band_late_evening | congestion_category_Medium + day_type_weekday | 0.098 | 0.591 | 3.83 |
| congestion_category_Medium + weather_category_clear | hour_band_late_evening | 0.044 | 0.595 | 3.58 |
| hour_band_late_evening | congestion_category_Medium + weather_category_clear | 0.044 | 0.267 | 3.58 |
| day_type_weekend + hour_band_overnight | congestion_category_Low | 0.064 | 0.886 | 3.54 |
| congestion_category_Low | day_type_weekend + hour_band_overnight | 0.064 | 0.258 | 3.54 |
| congestion_category_Medium + weather_category_cloudy | hour_band_late_evening | 0.044 | 0.586 | 3.53 |
| hour_band_late_evening | congestion_category_Medium + weather_category_cloudy | 0.044 | 0.262 | 3.53 |
| congestion_category_Low + day_type_weekday | hour_band_overnight | 0.152 | 0.899 | 3.53 |
| hour_band_overnight | congestion_category_Low + day_type_weekday | 0.152 | 0.596 | 3.53 |
| congestion_category_Low + weather_category_clear | hour_band_overnight | 0.070 | 0.882 | 3.46 |
| hour_band_overnight | congestion_category_Low + weather_category_clear | 0.070 | 0.273 | 3.46 |
| hour_band_overnight + weather_category_cloudy | congestion_category_Low | 0.049 | 0.853 | 3.41 |
| congestion_category_Low | hour_band_overnight + weather_category_cloudy | 0.049 | 0.197 | 3.41 |
| hour_band_overnight + weather_category_clear | congestion_category_Low | 0.070 | 0.851 | 3.40 |
| congestion_category_Low | hour_band_overnight + weather_category_clear | 0.070 | 0.278 | 3.40 |
| congestion_category_Low | hour_band_overnight | 0.216 | 0.865 | 3.40 |
| hour_band_overnight | congestion_category_Low | 0.216 | 0.849 | 3.40 |
| congestion_category_Low | hour_band_overnight + weather_category_adverse | 0.098 | 0.390 | 3.38 |
| hour_band_overnight + weather_category_adverse | congestion_category_Low | 0.098 | 0.845 | 3.38 |

These clusters and rules are descriptive, not causal. The dataset covers one traffic corridor, and its congestion bands are dataset-derived.
