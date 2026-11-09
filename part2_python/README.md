# Python Pipeline: Reproducible Traffic Analytics

**Status: complete.** This part cleans the official Metro Interstate Traffic
Volume CSV, engineers analysis-ready features, creates figures, and provides a
command-line traffic analytics application.

## Project Structure

```text
part2_python/
├── data/processed/
│   ├── traffic_cleaned.csv
│   └── traffic_features.csv
├── figures/                         # Four generated Matplotlib figures
├── logs/pipeline.log                # Successful end-to-end sample log
├── mini_app/traffic_cli.py          # Four query commands
├── reports/
│   ├── part2_methodology_and_findings.md
│   └── visualization_interpretations.md
├── feature_engineering.py
├── pipeline.py
├── requirements.txt
└── visualizations.py
```

The original CSV remains unchanged at
`part1_data_analytics/data/Metro_Interstate_Traffic_Volume.csv`. Generated datasets
are written under `part2_python/data/processed/`.

## Setup

From the repository root, create and activate a virtual environment, then
install the pinned dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r part2_python/requirements.txt
```

On Windows, activate with `.venv\\Scripts\\activate` instead.

## Run the Workflow

Run each stage from the repository root, in order:

```bash
python part2_python/pipeline.py
python part2_python/feature_engineering.py
python part2_python/visualizations.py
```

Optional `--input` and `--output` arguments are available on the pipeline and
feature-engineering scripts. The visualization script accepts `--input`,
`--output-dir`, and `--report`. Each script also accepts `--debug` to include
intermediate calculations where applicable.

The pipeline validates the required schema before transformations, standardizes
categories, parses timestamps, removes exact duplicate rows, validates physical
sensor ranges, and imputes invalid sensor readings with calendar-month medians.
Repeated timestamps with differing observations are retained. The raw CSV is
never overwritten.

Feature engineering adds hour, weekday, weekend and holiday flags, cyclical time
encodings, one-hot weather categories, weather indicators, min-max scaled
continuous fields, and a four-level congestion category derived from traffic
volume quartiles.

The visualization step creates four PNGs in `figures/` and writes their
interpretations to `reports/visualization_interpretations.md`.

## Mini-App

Run commands from the repository root:

```bash
python part2_python/mini_app/traffic_cli.py lookup '2017-01-01 08:00:00'
python part2_python/mini_app/traffic_cli.py high-traffic --limit 10
python part2_python/mini_app/traffic_cli.py compare-days
python part2_python/mini_app/traffic_cli.py recommend --day-type weekday --weather Clear
```

The recommendation identifies low-traffic **times** for the single I-94
corridor; it does not select a route. Datetime input must use
`YYYY-MM-DD HH:MM:SS`. Invalid values are reported as logged errors without a
traceback.

## End-to-End Verification

From the repository root, run the three workflow commands in order under
[Run the Workflow](#run-the-workflow), then check that both processed CSVs have
48,187 records and that four PNG files and the interpretation report were
generated. Exercise all four CLI commands above. To confirm invalid input is
handled without a traceback, run:

```bash
python part2_python/mini_app/traffic_cli.py lookup invalid
```

This command should log the expected timestamp-format error and return exit
code 2. Part 2 currently has no separate unit-test package; the root README
contains the full three-milestone smoke-test sequence.

## Logging

Every module uses `logging.getLogger(__name__)`. Executable entry points
configure console and file handlers with a formatter containing timestamp,
level, module, and message. A pipeline run starts a fresh
`logs/pipeline.log`; feature engineering, visualization, and CLI runs append to
that log so an end-to-end run preserves the complete event trail.

- `DEBUG`: intermediate values such as scaling ranges and quartile thresholds.
- `INFO`: input/output shapes, successful stages, routine category normalization,
  commands, and saved figures.
- `WARNING`: data-quality issues that affect records, such as dropped rows,
  invalid readings, or imputed values.
- `ERROR`: a failed stage or invalid user request. The explicitly handled
  pipeline failures are logged with tracebacks and return a nonzero status;
  other exceptions propagate rather than being caught generically.

`print()` is used only for results returned to the CLI user, not for internal
progress reporting.

## Report and Limitations

See [the Part 2 methodology and findings report](reports/part2_methodology_and_findings.md)
for the cleaning policy, observed patterns, and interpretation limits. The
provided traffic sensor dataset has repeated timestamps and uneven year
coverage; weather averages are descriptive, and the engineered min-max scaling
is computed on this dataset. For predictive evaluation, fit scaling parameters
on training data only to avoid information leakage.
