# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Install

```shell
pip install -e ".[tests]"
```

For GCP/Dataflow support: `pip install -e ".[tests,gcp]"`

## Commands

### Testing

```shell
# Run all weatherbench2 package tests
pytest weatherbench2/

# Run a single test file
pytest weatherbench2/metrics_test.py

# Run all scripts tests (must be separate processes due to flag conflicts)
for test in scripts/*_test.py; do pytest $test; done

# Run a single script test
pytest scripts/evaluate_test.py
```

### Linting / Formatting

```shell
pyink .        # format with pyink (Google-style, 2-space indent)
isort .        # sort imports
pyink --check --diff .   # check without modifying
```

pyink is configured in `pyproject.toml`: 80-char line length, 2-space indent, majority quotes style.

## Architecture

WeatherBench 2 is a weather forecast evaluation framework. It has two layers:

### `weatherbench2/` — Core library

| Module | Role |
|--------|------|
| `config.py` | Dataclasses: `Selection`, `Paths`, `Data`, `Eval`, `Viz`, `Panel` — all evaluation config lives here |
| `evaluation.py` | Orchestrates the full evaluation pipeline; reads forecast + obs, applies metrics, writes results; supports Apache Beam for distributed execution |
| `metrics.py` | All `Metric` subclasses (RMSE, ACC, CRPS, spread/skill, etc.); each implements `compute()` over xarray datasets with latitude weighting |
| `derived_variables.py` | `DerivedVariable` subclasses (wind speed, IVT, etc.) computed on-the-fly during evaluation via `xarray.apply_ufunc` |
| `schema.py` | Time convention helpers; canonical variable names (`ALL_3D_VARIABLES`, `ALL_2D_VARIABLES`); by-init vs. by-valid time indexing |
| `regions.py` | `Region` subclasses for spatial masking (`SliceRegion`, `ExtraTropicalRegion`, `LandRegion`, `CombinedRegion`) |
| `regridding.py` | Regridding utilities wrapping xesmf/scipy |
| `utils.py` | Shared helpers (chunking, time indexing) |
| `thresholds.py` | Threshold definitions for extreme-event metrics |
| `flag_utils.py` | Shared `absl.flags` parsing helpers for scripts |
| `visualization.py` | Plotting utilities consuming eval output |

### `scripts/` — Beam-based CLI pipelines

Each script is a standalone `absl` app runnable locally or on GCP Dataflow:

- `evaluate.py` — main evaluation entry point
- `compute_climatology.py` / `expand_climatology.py` — build and expand climatology baselines
- `regrid.py` — regrid datasets to a target grid
- `resample_in_time.py` / `resample_daily.py` — temporal resampling
- `index_on_valid_time.py` — convert by-init forecasts to by-valid indexing
- `compute_averages.py`, `compute_quantiles.py`, `compute_ensemble_mean.py` — aggregation utilities
- `compute_derived_variables.py` — pre-compute derived variables
- `compute_probabilistic_climatological_forecasts.py` — probabilistic climatology baselines
- `compute_statistical_moments.py`, `compute_zonal_energy_spectrum.py` — diagnostic scripts

### Key design patterns

**Time conventions**: Forecasts follow either *by-init* (`init_time` + `lead_time` → `valid_time`) or *by-valid* (`time` + `lead_time`). `schema.apply_time_conventions()` normalizes both into WB2 convention before evaluation.

**Metrics are stateless dataclasses**: Each `Metric` subclass holds hyperparameters as dataclass fields and exposes a `compute(forecast, truth, ...)` method. Latitude weighting (`metrics.get_lat_weights`) is applied inside metrics.

**Eval config is composable**: Build an `Eval` object with a dict of named metrics and optional dict of named regions; `evaluation.evaluate_in_memory()` or the Beam pipeline iterates all metric × region combinations.

**Scripts run locally or on Dataflow**: Pass `--use_beam=False` (default) for local; `--use_beam=True --runner=DataflowRunner` for GCP. `conftest.py` initializes `absl.app` flags so pytest can import script modules without flag errors.
