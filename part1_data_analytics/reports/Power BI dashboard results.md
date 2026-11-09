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

## Temperature and Traffic

This analysis compares the temperature Celsius field with hourly traffic volume. The Pearson correlation between temperature and traffic is **0.1303**, which indicates a **weak positive relationship**. As temperature increases, traffic volume tends to increase slightly, but temperature alone explains very little of the variation in traffic.

### Answers

- **Whether a visible relationship exists:** A weak visible relationship exists in the scatter chart. The points are widely dispersed, showing that traffic volume varies substantially at almost every temperature. The weak upward trend is consistent with the 0.1303 positive correlation, but it is not strong enough for temperature alone to predict traffic accurately.
- **The temperature range associated with higher traffic:** Traffic is generally highest around **25°C to 35°C**. The average traffic bins were approximately 4,402 vehicles from 25–30°C and 4,770 vehicles from 30–35°C, compared with 3,260 vehicles across the valid-temperature dataset. The small 35–40°C bin averaged about 5,074 vehicles, but contains only 7 observations and should therefore be interpreted cautiously.
- **Any notable outliers:** The dataset contains traffic values from **0 to 7,280 vehicles**, but traffic volume itself has no IQR outliers at the statistical threshold of 10,541 vehicles. The highest traffic observation, 7,280 vehicles, occurred at approximately **-2.4°C** on 2017-03-09 at 16:00, showing that high traffic can also occur in cold conditions. The scatter also contains **10 invalid temperature records at approximately -273.15°C** (converted from 0 kelvin in the source), which are data-quality errors rather than real temperatures. Several observations have very low or zero traffic, often outside peak travel periods.

## Temperature Interpretation

The temperature/traffic pattern is influenced by time of day, commute periods, weekday patterns, season, weather category and historical data coverage. Temperatures around 25–35°C coinciding with higher average traffic do not prove that warmer weather causes congestion. The wide scatter and weak correlation show that temperature is best used as a supporting factor alongside operational variables such as hour of day.

## Calculation Method for Temperature and Traffic

Temperature was converted from Kelvin to Celsius using `temp - 273.15`. The Pearson correlation coefficient was calculated between the Celsius temperature and `traffic_volume` values. Temperature bins of 5°C were also used to compare average traffic volumes and identify ranges with comparatively higher traffic.
