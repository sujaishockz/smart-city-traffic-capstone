# Model-Based Travel-Timing Recommendations

Recommendations use the trained traffic-volume model with June (6) conditions and median weather measurements for each observed weather class.

| Day type | Weather | Historical weather rows | Recommended two-hour window | Mean predicted traffic/hour |
|---|---|---:|---|---:|
| weekday | Clouds | 15158 | 02:00-04:00 | 375 |
| weekday | Clouds | 15158 | 00:00-02:00 | 570 |
| weekday | Clouds | 15158 | 04:00-06:00 | 1841 |
| weekday | Clear | 13384 | 02:00-04:00 | 386 |
| weekday | Clear | 13384 | 00:00-02:00 | 570 |
| weekday | Clear | 13384 | 04:00-06:00 | 1822 |
| weekday | Mist | 5949 | 02:00-04:00 | 352 |
| weekday | Mist | 5949 | 00:00-02:00 | 518 |
| weekday | Mist | 5949 | 22:00-24:00 | 1751 |
| weekend | Clouds | 15158 | 03:00-05:00 | 437 |
| weekend | Clouds | 15158 | 01:00-03:00 | 730 |
| weekend | Clouds | 15158 | 05:00-07:00 | 953 |
| weekend | Clear | 13384 | 03:00-05:00 | 452 |
| weekend | Clear | 13384 | 01:00-03:00 | 750 |
| weekend | Clear | 13384 | 05:00-07:00 | 978 |
| weekend | Mist | 5949 | 03:00-05:00 | 417 |
| weekend | Mist | 5949 | 01:00-03:00 | 703 |
| weekend | Mist | 5949 | 05:00-07:00 | 921 |

These are model estimates, not real-time traffic forecasts. The model reflects the 2012-2018 corridor history, the chosen month, typical observed weather values, and a non-holiday assumption. Verify current conditions before travel.
