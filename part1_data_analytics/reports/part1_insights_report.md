# Smart City Traffic Intelligence: Part 1 Insights Report

## Scope and data quality

This analysis uses 48,204 hourly records of westbound I-94 traffic volume with
weather and holiday fields. The SQLite load was verified against the source CSV:
all 48,204 rows are present, covering 2012-10-02 through 2018-09-30. The source
contains 40,575 distinct timestamps, so duplicate timestamps and uneven yearly
coverage must be considered when interpreting totals.

## SQL traffic trends

Total yearly traffic is not directly comparable because the number of recorded
hours varies substantially. The more useful average hourly volumes range from
3,169.4 vehicles in 2016 to 3,340.7 in 2017. Total volume increased in 2013,
decreased in 2014 and 2015, and increased again in 2016 and 2017; these swings
largely reflect missing coverage rather than abrupt changes in demand.

Holiday temperatures also vary by year. New Year's Day averaged -6.12°C in 2016
and -3.06°C in 2017, while Labor Day averaged 22.17°C in 2015, 21.60°C in 2016,
and 17.48°C in 2017. New Year's Day 2017 was warmer and had higher average
traffic than 2016. Labor Day 2017 was cooler but had higher traffic than 2016,
showing that weekday and holiday travel patterns can be more important than
temperature alone.

## Descriptive statistics and correlation

Across all records, mean traffic volume is 3,259.82 and median traffic volume is
3,380.00. The standard deviation is 1,986.86, with a variance of 3,947,615.32 and
a range from 0 to 7,280 vehicles. The wide spread is consistent with the mix of
quiet overnight periods and busy commuting periods. The median above the mean
indicates that low-volume observations pull the average downward.

The Pearson correlation between temperature and traffic volume is 0.1303, a weak
positive relationship. Temperature by itself is therefore not a strong linear
predictor of traffic. This is an association rather than a causal conclusion;
time of day, weekday, season, weather category and duplicate timestamps are
important confounding factors.

## Probability and congestion

Using traffic volume greater than 5,500 as congestion, the probability of
congestion is 0.1473. Clear weather occurs in 0.2778 of records, and congestion
and clear weather occur together in 0.0366 of records. The conditional probability
of clear weather given congestion is 0.2483, while the probability of high
temperature given congestion is 0.2630.

The independence estimate P(Congestion) x P(Clear Weather) is 0.0409, compared
with the observed joint probability of 0.0366. The difference indicates that the
two events are not exactly independent in this sample. Comparing only clear and
cloudy weather, the clear-to-cloudy congestion odds ratio is 0.7354. Congestion
odds are therefore lower during clear weather than cloudy weather under these
definitions, although weather is not sufficient to explain congestion on its own.

## Mobility implications

1. Use average hourly traffic and hour-of-day patterns instead of raw annual
   totals when comparing this dataset, because coverage is incomplete and uneven.
2. Plan congestion messaging around commute periods and calendar patterns, not
   temperature alone.
3. Treat weather as a supporting signal for traffic operations. Cloudy or adverse
   conditions may coincide with different congestion odds, but time and weekday
   effects need to be included in later models.
4. De-duplicate timestamps and document coverage before building predictive models
   or presenting year-over-year claims.

## Dashboard handoff

The Power BI preparation view and dashboard specification are in
`sql/06_powerbi_queries.sql` and `reports/powerbi_dashboard_spec.md`. They provide
fields for date, hour, Celsius temperature and traffic category, plus the required
trend, weather and KPI queries. The remaining manual deliverable is the `.pbix`
file, which must be created in Power BI Desktop.
