"""
Download data for evaluating HRES on 2020-01-01 at 64x32 resolution.

Downloads:
  - HRES forecast: 2 init times (00:00 and 12:00 UTC), 40 lead steps x 6h = 10 days (~57 MB)
  - ERA5 obs: 2020-01-01 ~ 2020-01-12, covers all forecast valid times (~33 MB)
  - ERA5 climatology: 1990-2019 full year, required for ACC (~852 MB, cannot be sliced)
Total: ~1 GB
"""
import os
import xarray as xr

STORAGE_OPTS = {'token': 'anon'}
OUT_DIR = './local_data_minimal'
os.makedirs(OUT_DIR, exist_ok=True)

# Change to a shorter list to reduce download size further
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

GCS_FORECAST = (
    'gs://weatherbench2/datasets/hres/'
    '2016-2022-0012-64x32_equiangular_conservative.zarr'
)
GCS_OBS = (
    'gs://weatherbench2/datasets/era5/'
    '1959-2022-6h-64x32_equiangular_conservative.zarr'
)
GCS_CLIM = (
    'gs://weatherbench2/datasets/era5-hourly-climatology/'
    '1990-2019_6h_64x32_equiangular_conservative.zarr'
)


def select_vars(ds, variables):
    avail = [v for v in variables if v in ds]
    missing = set(variables) - set(avail)
    if missing:
        print(f'  skipping missing vars: {sorted(missing)}')
    return ds[avail]


def report_size(ds, label):
    mb = sum(v.nbytes for v in ds.values()) / 1e6
    print(f'  {label}: {mb:.1f} MB (uncompressed in memory, disk may differ)')


# ── 1. HRES: only 2020-01-01 00:00 and 12:00 ─────────────────────────────────
print('=== HRES forecast ===')
fc = xr.open_zarr(GCS_FORECAST, storage_options=STORAGE_OPTS)
fc = select_vars(fc, VARIABLES)
# time dim is init_time in by-init datasets
time_dim = 'time' if 'time' in fc.dims else 'init_time'
fc_slice = fc.sel({time_dim: ['2020-01-01T00:00', '2020-01-01T12:00']})
fc_slice.load()  # trigger actual download
report_size(fc_slice, 'downloaded')
out_fc = f'{OUT_DIR}/hres_20200101_64x32.zarr'
fc_slice.to_zarr(out_fc, mode='w')
print(f'  Saved → {out_fc}')

# ── 2. ERA5 obs: valid time range + small buffer ──────────────────────────────
print('=== ERA5 observations ===')
obs = xr.open_zarr(GCS_OBS, storage_options=STORAGE_OPTS)
obs = select_vars(obs, VARIABLES)
obs_slice = obs.sel(time=slice('2020-01-01', '2020-01-12'))
obs_slice.load()
report_size(obs_slice, 'downloaded')
out_obs = f'{OUT_DIR}/era5_20200101_64x32.zarr'
obs_slice.to_zarr(out_obs, mode='w')
print(f'  Saved → {out_obs}')

# ── 3. Climatology (dims: hour x dayofyear, must download full year) ─────────
# Chunks are (4, 366, ...) — one chunk per variable, can't slice by date.
print('=== Climatology (full year required) ===')
clim = xr.open_zarr(GCS_CLIM, storage_options=STORAGE_OPTS)
clim = select_vars(clim, VARIABLES)
clim.load()
report_size(clim, 'downloaded')
out_clim = f'{OUT_DIR}/climatology_1990-2019_64x32.zarr'
clim.to_zarr(out_clim, mode='w')
print(f'  Saved → {out_clim}')

print('\n=== Done. Run evaluation with: ===')
print(f'  --forecast_path={out_fc}')
print(f'  --obs_path={out_obs}')
print(f'  --climatology_path={out_clim}')
print(f'  --time_start=2020-01-01 --time_stop=2020-01-01')
