"""
Visualize HRES 2020-01-01 evaluation results for both resolutions.

Usage:
  python visual_oneday.py

Output (saved to ./output_minimal/):
  acc_oneday.png      — ACC for 3D variables at key pressure levels
  mse_oneday.png      — MSE for 3D variables at key pressure levels
  surface_oneday.png  — ACC / MSE / Bias for surface variables
"""
import matplotlib.pyplot as plt
from weatherbench2.visualization import load_results, plot_timeseries, set_wb2_style

RESULTS_PATHS = {
    'HRES 64x32':   './output_minimal/hres_20200101_64x32_deterministic.nc',
    'HRES 240x121': './output_minimal/hres_20200101_240x121_deterministic.nc',
}
OUT_DIR = './output_minimal'

set_wb2_style()
results = load_results(RESULTS_PATHS)


def save_fig(fig, filename):
    path = f'{OUT_DIR}/{filename}'
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'Saved -> {path}')


# ── Figure 1: ACC ─────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
fig.suptitle('ACC — HRES 2020-01-01', fontsize=14)

panels = [
    ('geopotential',        500, axes[0, 0]),
    ('geopotential',        850, axes[0, 1]),
    ('temperature',         500, axes[0, 2]),
    ('temperature',         850, axes[1, 0]),
    ('u_component_of_wind', 500, axes[1, 1]),
    ('specific_humidity',   850, axes[1, 2]),
]
for i, (var, level, ax) in enumerate(panels):
    plot_timeseries(results, metric='acc', variable=var, level=level, ax=ax,
                    title=f'{var} @{level} hPa', add_legend=(i == 0))

save_fig(fig, 'acc_oneday.png')

# ── Figure 2: MSE ─────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
fig.suptitle('MSE — HRES 2020-01-01', fontsize=14)

for i, (var, level, ax) in enumerate(
    [
        ('geopotential',        500, axes[0, 0]),
        ('geopotential',        850, axes[0, 1]),
        ('temperature',         500, axes[0, 2]),
        ('temperature',         850, axes[1, 0]),
        ('u_component_of_wind', 500, axes[1, 1]),
        ('specific_humidity',   850, axes[1, 2]),
    ]
):
    plot_timeseries(results, metric='mse', variable=var, level=level, ax=ax,
                    title=f'{var} @{level} hPa', add_legend=(i == 0))

save_fig(fig, 'mse_oneday.png')

# ── Figure 3: Surface variables ───────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
fig.suptitle('Surface Variables — HRES 2020-01-01', fontsize=14)

for i, (metric, var, ax) in enumerate(
    [
        ('acc',  '2m_temperature',          axes[0, 0]),
        ('mse',  '2m_temperature',          axes[0, 1]),
        ('bias', '2m_temperature',          axes[0, 2]),
        ('acc',  'mean_sea_level_pressure', axes[1, 0]),
        ('mse',  'mean_sea_level_pressure', axes[1, 1]),
        ('bias', 'mean_sea_level_pressure', axes[1, 2]),
    ]
):
    plot_timeseries(results, metric=metric, variable=var, ax=ax,
                    title=f'{var} — {metric.upper()}', add_legend=(i == 0))

save_fig(fig, 'surface_oneday.png')

print('\nDone.')
