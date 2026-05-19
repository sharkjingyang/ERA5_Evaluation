"""
Download data for evaluating HRES on 2020-01-01.

Usage:
  python download_eval_oneday.py           # default: 64x32
  python download_eval_oneday.py 240x121
  python download_eval_oneday.py 64x32

Downloads:
  - HRES forecast: 2 init times (00:00 and 12:00 UTC), 40 lead steps x 6h = 10 days
  - ERA5 obs: 2020-01-01 ~ 2020-01-12, covers all forecast valid times
  - ERA5 climatology: 1990-2019, required for ACC
    - 64x32:   full year (~852 MB, chunk is full year, cannot slice)
    - 240x121: ~1.2 GB, chunk is (4, 30, 240, 121) so slice(1,12) loads full dayofyear 1-30
"""
import os
import sys
import warnings
warnings.filterwarnings('ignore', category=FutureWarning, module='google')
import xarray as xr
from dask.diagnostics import ProgressBar

# ── Resolution hyperparameter ──────────────────────────────────────────────────
RESOLUTION = sys.argv[1] if len(sys.argv) > 1 else '64x32'

GCS_CONFIGS = {
    '64x32': {
        'forecast': (
            'gs://weatherbench2/datasets/hres/'
            '2016-2022-0012-64x32_equiangular_conservative.zarr'
        ),
        'obs': (
            'gs://weatherbench2/datasets/era5/'
            '1959-2022-6h-64x32_equiangular_conservative.zarr'
        ),
        'clim': (
            'gs://weatherbench2/datasets/era5-hourly-climatology/'
            '1990-2019_6h_64x32_equiangular_conservative.zarr'
        ),
        'clim_can_slice': False,  # chunk is (4, 366, 64, 32), full year = 1 chunk
    },
    '240x121': {
        'forecast': (
            'gs://weatherbench2/datasets/hres/'
            '2016-2022-0012-240x121_equiangular_with_poles_conservative.zarr'
        ),
        'obs': (
            'gs://weatherbench2/datasets/era5/'
            '1959-2022-6h-240x121_equiangular_with_poles_conservative.zarr'
        ),
        'clim': (
            'gs://weatherbench2/datasets/era5-hourly-climatology/'
            '1990-2019_6h_240x121_equiangular_with_poles_conservative.zarr'
        ),
        'clim_can_slice': True,  # chunk is (4, 30, 240, 121), can slice by dayofyear
    },
}

if RESOLUTION not in GCS_CONFIGS:
    raise ValueError(f'Unknown resolution {RESOLUTION!r}. Choose from: {list(GCS_CONFIGS)}')

cfg = GCS_CONFIGS[RESOLUTION]
STORAGE_OPTS = {'token': 'anon'}
OUT_DIR = './local_data_minimal'
os.makedirs(OUT_DIR, exist_ok=True)

VARIABLES = [
    'geopotential',
    'temperature',
    'u_component_of_wind',
    'v_component_of_wind',
    'specific_humidity',
    'wind_speed',
    '2m_temperature',
    '10m_u_component_of_wind',
    '10m_v_component_of_wind',
    '10m_wind_speed',
    'mean_sea_level_pressure',
    'total_precipitation_6hr',
    'total_precipitation_24hr',
]


def select_vars(ds, variables):
    avail = [v for v in variables if v in ds]
    missing = set(variables) - set(avail)
    if missing:
        print(f'  skipping missing vars: {sorted(missing)}')
    return ds[avail]


def load_with_progress(ds):
    with ProgressBar():
        return ds.compute()


def report_size(ds, label):
    mb = sum(v.nbytes for v in ds.values()) / 1e6
    print(f'  {label}: {mb:.1f} MB (uncompressed in memory, disk may differ)')


print(f'=== Downloading {RESOLUTION} data ===')

# ── 1. HRES: only 2020-01-01 00:00 and 12:00 ─────────────────────────────────
print(f'=== [{RESOLUTION}] HRES forecast ===')
fc = xr.open_zarr(cfg['forecast'], storage_options=STORAGE_OPTS, chunks='auto')
fc = select_vars(fc, VARIABLES)
time_dim = 'time' if 'time' in fc.dims else 'init_time'
fc_slice = fc.sel({time_dim: ['2020-01-01T00:00', '2020-01-01T12:00']})
fc_slice = load_with_progress(fc_slice)
report_size(fc_slice, 'downloaded')
out_fc = f'{OUT_DIR}/hres_20200101_{RESOLUTION}.zarr'
fc_slice.to_zarr(out_fc, mode='w')
print(f'  Saved → {out_fc}')

# ── 2. ERA5 obs: valid time range ─────────────────────────────────────────────
print(f'=== [{RESOLUTION}] ERA5 observations ===')
obs = xr.open_zarr(cfg['obs'], storage_options=STORAGE_OPTS, chunks='auto')
obs = select_vars(obs, VARIABLES)
obs_slice = obs.sel(time=slice('2020-01-01', '2020-01-12'))
obs_slice = load_with_progress(obs_slice)
report_size(obs_slice, 'downloaded')
out_obs = f'{OUT_DIR}/era5_20200101_{RESOLUTION}.zarr'
obs_slice.to_zarr(out_obs, mode='w')
print(f'  Saved → {out_obs}')

# ── 3. Climatology ────────────────────────────────────────────────────────────
print(f'=== [{RESOLUTION}] Climatology ===')
clim = xr.open_zarr(cfg['clim'], storage_options=STORAGE_OPTS, chunks='auto')
clim = select_vars(clim, VARIABLES)
if cfg['clim_can_slice']:
    # 10-day forecast from 2020-01-01 covers valid times up to 2020-01-11 (dayofyear 1-11).
    clim = clim.sel(dayofyear=slice(1, 12))
    out_clim = f'{OUT_DIR}/climatology_1990-2019_{RESOLUTION}_jan1-12.zarr'
else:
    out_clim = f'{OUT_DIR}/climatology_1990-2019_{RESOLUTION}.zarr'
clim = load_with_progress(clim)
report_size(clim, 'downloaded')
clim.to_zarr(out_clim, mode='w')
print(f'  Saved → {out_clim}')

print('\n=== Done. Run evaluation with: ===')
print(f'  --forecast_path={out_fc}')
print(f'  --obs_path={out_obs}')
print(f'  --climatology_path={out_clim}')
print(f'  --time_start=2020-01-01 --time_stop=2020-01-01')
