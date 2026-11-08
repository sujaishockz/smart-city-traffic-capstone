# Power BI Dashboard Results

## Weather Impact

This analysis compares the average hourly traffic volume across weather conditions in the Power BI dashboard data.

| Weather condition | Recorded observations | Average traffic volume |
|---|---:|---:|
| Clouds | 15,164 | 3,618.4 |
| Haze | 1,360 | 3,502.1 |
| Rain | 5,672 | 3,317.9 |
| Drizzle | 1,821 | 3,290.7 |
| Smoke | 20 | 3,237.7 |
| Clear | 13,391 | 3,055.9 |
| Snow | 2,876 | 3,016.8 |
| Thunderstorm | 1,034 | 3,001.6 |
| Mist | 5,950 | 2,933.0 |
| Fog | 912 | 2,703.7 |
| Squall | 4 | 2,061.8 |

### Answers

- **Which weather condition has the highest average traffic?**
  **Clouds**, with an average traffic volume of **3,618.4 vehicles per hourly observation**.

- **Which weather condition has the lowest average traffic?**
  **Squall**, with an average traffic volume of **2,061.8 vehicles per hourly observation**.

- **What is the difference between the highest and lowest average traffic?**
  The difference is **1,556.7 vehicles**.

The difference is calculated as:

**3,618.4 (Clouds) - 2,061.8 (Squall) = 1,556.6** when subtracting the rounded averages shown above. The underlying unrounded values produce **1,556.7**, which is the precise calculation used in the dashboard analysis.

## Interpretation

Weather conditions associated with the highest recorded traffic are cloudy conditions, while Squall has the lowest average in the available data. Because some weather categories contain comparatively few observations—particularly Squall and Smoke—their averages may be less reliable indicators of broader weather patterns. Weather should therefore be treated as one contributing factor alongside time, season, location, and road conditions rather than as a sole explanation for traffic volume.

## Calculation Method

Average traffic volume was calculated by grouping observations by the `weather_main` field and calculating the mean of `traffic_volume` for each weather category. The highest and lowest averages were then compared to obtain the difference.
