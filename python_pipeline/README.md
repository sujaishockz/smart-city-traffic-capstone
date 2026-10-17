# Python Pipeline: Reproducible Traffic Analytics

**Status: complete.** This part cleans the official Metro Interstate Traffic
Volume CSV, engineers analysis-ready features, creates figures, and provides a
command-line traffic analytics application.

## Project Structure

```text
python_pipeline/
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
`data_analytics/data/Metro_Interstate_Traffic_Volume.csv`. Generated datasets
are written under `python_pipeline/data/processed/`.

## Setup

From the repository root, create and activate a virtual environment, then
install the pinned dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r python_pipeline/requirements.txt
```

On Windows, activate with `.venv\\Scripts\\activate` instead.

## Run the Workflow

Run each stage from the repository root, in order:

```bash
python python_pipeline/pipeline.py
python python_pipeline/feature_engineering.py
python python_pipeline/visualizations.py
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
python python_pipeline/mini_app/traffic_cli.py lookup '2017-01-01 08:00:00'
python python_pipeline/mini_app/traffic_cli.py high-traffic --limit 10
python python_pipeline/mini_app/traffic_cli.py compare-days
python python_pipeline/mini_app/traffic_cli.py recommend --day-type weekday --weather Clear
```

The recommendation identifies low-traffic **times** for the single I-94
corridor; it does not select a route. Datetime input must use
`YYYY-MM-DD HH:MM:SS`. Invalid values are reported as logged errors without a
traceback.

## Logging

Every module uses `logging.getLogger(__name__)`. Executable entry points
configure console and file handlers with a formatter containing timestamp,
level, module, and message. A pipeline run starts a fresh
`logs/pipeline.log`; feature engineering, visualization, and CLI runs append to
that log so an end-to-end run preserves the complete event trail.

- `DEBUG`: intermediate values such as scaling ranges and quartile thresholds.
- `INFO`: input/output shapes, successful stages, commands, and saved figures.
- `WARNING`: changed, dropped, or imputed records and recoverable data issues.
- `ERROR`: a failed stage or invalid user request.

`print()` is used only for results returned to the CLI user, not for internal
progress reporting.

## Report and Limitations

See [the Part 2 methodology and findings report](reports/part2_methodology_and_findings.md)
for the cleaning policy, observed patterns, and interpretation limits. The
provided traffic sensor dataset has repeated timestamps and uneven year
coverage; weather averages are descriptive, and the engineered min-max scaling
is computed on this dataset. For predictive evaluation, fit scaling parameters
on training data only to avoid information leakage.
