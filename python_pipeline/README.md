# Python Pipeline: Building a Reproducible Traffic Analytics Pipeline

**Status: not started.** This folder is scaffolded so the structure exists
from the first commit; files will be filled in one piece at a time, each as
its own commit.

## Planned Folder Structure

```
python_pipeline/
├── pipeline.py               # load, validate, clean (with logging)
├── feature_engineering.py    # NumPy/Pandas feature creation
├── visualizations.py         # Matplotlib charts
├── mini_app/                 # CLI analytics application
├── figures/                  # Output charts from visualizations.py
├── logs/
│   └── pipeline_sample.log   # Sample log output for graders
└── README.md
```

## Planned Work

1. **Data Pipeline (`pipeline.py`)** — load CSV, validate schema, standardise
   categorical values, parse/validate datetimes, remove duplicates, detect
   and impute outliers (e.g. 0K temperature readings, implausible rain
   values) using conditionals/loops where group-by-group logic is needed
   (e.g. monthly medians). Every step logged separately via
   `logging.getLogger(__name__)`.
2. **Feature Engineering (`feature_engineering.py`)** — hour, day-of-week,
   weekend flag, cyclical encodings, weather encodings, scaled numeric
   features, data-driven congestion category. Shape logged before/after;
   intermediate thresholds logged at DEBUG.
3. **Visualisations (`visualizations.py`)** — at least 3 Matplotlib charts
   with interpretations, each save logged at INFO with its file path.
4. **Mini CLI App (`mini_app/`)** — at least 3 query commands over the
   processed dataset, with INFO logs of command+args and ERROR logs (not raw
   tracebacks) for invalid input.
5. **GitHub & Reproducibility** — incremental commits per piece of work, this
   README kept up to date with how to run everything and the logging
   configuration.

## Logging Configuration (to be implemented)

- `logging.getLogger(__name__)` in every module — no bare root logger.
- Handler configured only in the entry-point script(s): writes to console
  **and** `logs/pipeline.log`.
- Formatter: timestamp, level, module name, message.
- DEBUG = internal-only values · INFO = milestones · WARNING = recoverable
  data issues · ERROR = pipeline-stopping failures (`exc_info=True`).

## How to Run

_To be added once `pipeline.py` exists._
