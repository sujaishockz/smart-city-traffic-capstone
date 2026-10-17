# Neural Network and LIME Analysis

The MLPClassifier uses hidden layers of 64 and 32 units. Its target is the constructed `high_risk_proxy`, not observed accidents.

## Chronological Holdout Metrics

| Accuracy | Precision | Recall | F1 | ROC-AUC |
|---:|---:|---:|---:|---:|
| 0.972 | 0.912 | 0.959 | 0.935 | 0.992 |

## Local Explanations

LIME weights below approximate the model around selected holdout examples. Positive weights increase support for the high-risk proxy class; negative weights decrease it.

### 2017-11-02T06:00:00 (actual proxy=1, predicted probability=0.887)
- `weather_main_Haze <= 0.00`: -0.369
- `weather_main_Snow <= 0.00`: -0.368
- `weather_main_Drizzle <= 0.00`: -0.298
- `weather_main_Mist > 0.00`: +0.246
- `weather_main_Thunderstorm <= 0.00`: -0.242
- `weather_main_Rain <= 0.00`: -0.240
- `weather_main_Fog <= 0.00`: -0.142
- `weather_main_Clear <= 0.00`: +0.129
- `weather_main_Clouds <= 0.00`: +0.118
- `is_weekend <= 0.00`: +0.060

### 2017-11-02T06:00:00 (actual proxy=1, predicted probability=0.872)
- `weather_main_Thunderstorm <= 0.00`: -0.290
- `weather_main_Drizzle <= 0.00`: -0.282
- `weather_main_Fog > 0.00`: +0.256
- `weather_main_Rain <= 0.00`: -0.255
- `weather_main_Snow <= 0.00`: -0.246
- `weather_main_Mist <= 0.00`: -0.234
- `weather_main_Clouds <= 0.00`: +0.180
- `weather_main_Clear <= 0.00`: +0.146
- `holiday_flag <= 0.00`: +0.146
- `snow_1h <= 0.00`: +0.051

### 2017-11-02T07:00:00 (actual proxy=1, predicted probability=0.946)
- `weather_main_Haze <= 0.00`: -0.330
- `weather_main_Rain <= 0.00`: -0.299
- `weather_main_Mist > 0.00`: +0.208
- `holiday_flag <= 0.00`: +0.204
- `weather_main_Drizzle <= 0.00`: -0.189
- `weather_main_Thunderstorm <= 0.00`: -0.189
- `weather_main_Clouds <= 0.00`: +0.131
- `weather_main_Snow <= 0.00`: -0.118
- `weather_main_Fog <= 0.00`: -0.105
- `snow_1h <= 0.00`: +0.056

### 2017-11-02T07:00:00 (actual proxy=1, predicted probability=0.987)
- `weather_main_Drizzle > 0.00`: +0.372
- `weather_main_Thunderstorm <= 0.00`: -0.356
- `weather_main_Mist <= 0.00`: -0.281
- `weather_main_Snow <= 0.00`: -0.252
- `weather_main_Fog <= 0.00`: -0.199
- `weather_main_Haze <= 0.00`: -0.146
- `weather_main_Rain <= 0.00`: -0.136
- `weather_main_Clouds <= 0.00`: +0.119
- `weather_main_Clear <= 0.00`: +0.106
- `weather_main_Smoke <= 0.00`: -0.062

### 2017-11-02T08:00:00 (actual proxy=1, predicted probability=0.951)
- `weather_main_Fog <= 0.00`: -0.364
- `weather_main_Mist > 0.00`: +0.326
- `weather_main_Rain <= 0.00`: -0.301
- `weather_main_Haze <= 0.00`: -0.280
- `weather_main_Snow <= 0.00`: -0.212
- `weather_main_Thunderstorm <= 0.00`: -0.166
- `weather_main_Clear <= 0.00`: +0.135
- `weather_main_Clouds <= 0.00`: +0.120
- `weather_main_Drizzle <= 0.00`: -0.079
- `5.00 < hour <= 11.00`: +0.075

### 2017-11-01T20:00:00 (actual proxy=0, predicted probability=0.086)
- `weather_main_Rain <= 0.00`: -0.360
- `weather_main_Thunderstorm <= 0.00`: -0.353
- `weather_main_Fog <= 0.00`: -0.344
- `weather_main_Haze <= 0.00`: -0.252
- `weather_main_Drizzle > 0.00`: +0.244
- `weather_main_Mist <= 0.00`: -0.243
- `weather_main_Snow <= 0.00`: -0.165
- `weather_main_Clouds <= 0.00`: +0.159
- `weather_main_Clear <= 0.00`: +0.123
- `weather_main_Smoke <= 0.00`: +0.042

### 2017-11-01T20:00:00 (actual proxy=0, predicted probability=0.122)
- `weather_main_Thunderstorm <= 0.00`: -0.399
- `weather_main_Haze <= 0.00`: -0.257
- `weather_main_Rain <= 0.00`: -0.239
- `weather_main_Snow <= 0.00`: -0.206
- `weather_main_Mist > 0.00`: +0.189
- `weather_main_Drizzle <= 0.00`: -0.151
- `weather_main_Fog <= 0.00`: -0.147
- `weather_main_Clouds <= 0.00`: +0.134
- `weather_main_Clear <= 0.00`: +0.129
- `snow_1h <= 0.00`: -0.103

### 2017-11-01T20:00:00 (actual proxy=0, predicted probability=0.083)
- `weather_main_Drizzle <= 0.00`: -0.386
- `weather_main_Fog <= 0.00`: -0.308
- `weather_main_Snow <= 0.00`: -0.301
- `weather_main_Haze <= 0.00`: -0.287
- `weather_main_Mist <= 0.00`: -0.183
- `weather_main_Rain > 0.00`: +0.134
- `weather_main_Clouds <= 0.00`: +0.129
- `weather_main_Thunderstorm <= 0.00`: -0.123
- `weather_main_Clear <= 0.00`: +0.110
- `hour > 17.00`: -0.050

### 2017-11-01T21:00:00 (actual proxy=0, predicted probability=0.033)
- `weather_main_Mist > 0.00`: +0.215
- `weather_main_Snow <= 0.00`: -0.212
- `weather_main_Rain <= 0.00`: -0.194
- `weather_main_Drizzle <= 0.00`: -0.188
- `weather_main_Haze <= 0.00`: -0.187
- `weather_main_Thunderstorm <= 0.00`: -0.174
- `weather_main_Clouds <= 0.00`: +0.125
- `weather_main_Fog <= 0.00`: -0.114
- `weather_main_Clear <= 0.00`: +0.107
- `snow_1h <= 0.00`: -0.018

### 2017-11-01T21:00:00 (actual proxy=0, predicted probability=0.017)
- `weather_main_Rain <= 0.00`: -0.316
- `weather_main_Fog <= 0.00`: -0.281
- `weather_main_Mist <= 0.00`: -0.264
- `weather_main_Drizzle > 0.00`: +0.208
- `weather_main_Haze <= 0.00`: -0.192
- `weather_main_Snow <= 0.00`: -0.184
- `weather_main_Clouds <= 0.00`: +0.155
- `weather_main_Thunderstorm <= 0.00`: -0.143
- `weather_main_Clear <= 0.00`: +0.108
- `hour > 17.00`: -0.082

LIME is a local surrogate rather than a causal explanation. Since observed weather is part of the proxy-label definition, weather-related weights partly explain label construction. This is not evidence about real accident risk.
