# Part 2: Methodology and Findings

## Methodology

The workflow uses the provided Metro Interstate Traffic Volume CSV, preserving the raw source file and writing processed datasets separately. The pipeline first verifies that all nine expected columns exist, then parses timestamps and numeric sensor fields, standardizes categorical labels, and removes rows duplicated across every source column. It retains repeated timestamps when their observations differ because those rows may contain distinct weather labels. Sensor checks flag temperatures at or below 0 K, rainfall outside 0–9,000 mm, negative snowfall, and cloud coverage outside 0–100. Invalid sensor readings are imputed using the median for the corresponding calendar month; a global median is only a fallback if a month has no valid values. Invalid or negative traffic targets are not imputed.

The raw file contains 48,204 rows. Cleaning removes 17 exact duplicate records and imputes 10 zero-K temperature readings and one rainfall reading above 9,000 mm, yielding 48,187 rows. The original data has 7,629 repeated timestamps, which are retained unless the complete rows are identical. The holiday field uses the source value `None` to mean no holiday; this is preserved as a no-holiday category rather than treated as a missing record.

Feature engineering adds hour, day of week, weekend and holiday flags, sine/cosine encodings for hour and weekday, one-hot weather categories, low-visibility/adverse-weather/precipitation indicators, and min-max scaled temperature, rain, snow, and cloud coverage. Congestion is categorized using traffic-volume quartiles: Low at or below Q1 (1,192.5), Medium through Q2 (3,379), High through Q3 (4,933), and Severe above Q3. These are descriptive full-dataset scaling values for this pipeline; future model evaluation must fit scaling parameters on training folds only.

Four Matplotlib figures are saved: hourly traffic by weekday/weekend, average traffic by weather, temperature versus traffic, and the traffic-volume distribution. The CLI supports exact timestamp lookup, top-volume observations, weekday/weekend comparison, and a two-hour travel-timing recommendation.

## Findings

Mean traffic volume is 3,259.6 vehicles per hour, the median is 3,379, and the standard deviation is 1,987.0. The range is 0–7,280, reflecting both low-volume overnight observations and busy periods. The Pearson correlation between temperature and traffic is weak and positive (0.132).

Weekday traffic peaks at 16:00, averaging 6,189.5 vehicles per hour; weekend traffic peaks at 12:00, averaging 4,372.5. Across the full dataset, weekday and weekend means are 3,533.3 and 2,570.7 vehicles per hour, respectively. The weather-group averages range from 2,061.8 for Squall to 3,618.0 for Clouds, but the Squall mean is based on only four records, compared with 15,158 Clouds observations. The large difference should therefore not be read as a controlled estimate of weather's effect.

The CLI's timing recommendations use historical observations, not a traffic forecast. For example, the lowest weekday two-hour average in this sample is 02:00–04:00; this may not be a practical commuter recommendation even though its measured volume is low. Recommendations should be evaluated for relevance and user needs before operational use.

## Limitations

This dataset represents one westbound I-94 corridor and has incomplete, uneven coverage across years, duplicate timestamps, and very small counts for some weather conditions. Traffic and weather associations are descriptive, not causal. The data contains no accident outcomes, so traffic volume must not be presented as actual accident likelihood. Data-derived categories and full-dataset scaling are useful for this analytics workflow but require leakage-safe recomputation and time-aware validation before predictive modelling or deployment.
