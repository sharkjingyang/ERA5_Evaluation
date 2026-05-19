# WeatherBench2 Evaluation

## 快速开始：64×32 单日评测（2020-01-01）

> 另见：[240×121 高分辨率评测](#240121-单日评测2020-01-01)

### 1. 安装依赖

```bash
pip install -e ".[tests]"
```

### 2. 下载数据

```bash
python download_eval_oneday.py
```

下载内容（共约 1 GB）：

| 数据集 | 内容 | 大小 |
|--------|------|------|
| HRES 预报 | 2020-01-01 00:00 和 12:00 两个初始化时刻，各 40 个 lead time | 57 MB |
| ERA5 观测 | 2020-01-01 ~ 2020-01-12（覆盖预报最长 10 天有效时刻） | 33 MB |
| ERA5 气候态 | 1990-2019 全年（用于 ACC 计算，无法按日期切片） | 852 MB |

### 3. 运行评测

```bash
python scripts/evaluate.py \
  --forecast_path=./local_data_minimal/hres_20200101_64x32.zarr \
  --obs_path=./local_data_minimal/era5_20200101_64x32.zarr \
  --climatology_path=./local_data_minimal/climatology_1990-2019_64x32.zarr \
  --output_dir=./output_minimal/ \
  --output_file_prefix=hres_20200101_ \
  --input_chunks=init_time=1 \
  --eval_configs=deterministic \
  --time_start=2020-01-01 \
  --time_stop=2020-01-01 \
  --variables=geopotential,temperature,u_component_of_wind,v_component_of_wind,specific_humidity,2m_temperature,10m_u_component_of_wind,10m_v_component_of_wind,mean_sea_level_pressure
```

结果保存至 `./output_minimal/hres_20200101_deterministic.nc`。

### 参数说明

| 参数 | 说明 |
|------|------|
| `--forecast_path` | 预报模型数据路径（zarr 格式） |
| `--obs_path` | 观测/真值数据路径（ERA5） |
| `--climatology_path` | 气候态路径，用于计算 ACC |
| `--output_dir` | 结果输出目录 |
| `--output_file_prefix` | 输出文件名前缀 |
| `--input_chunks` | 数据读取分块大小，控制内存用量 |
| `--eval_configs` | 评测配置，`deterministic` 包含 MSE/ACC/Bias/MAE |
| `--time_start/stop` | 初始化时刻的筛选范围 |
| `--variables` | 待评测变量列表，逗号分隔 |

### 变量名对照

| 常用缩写 | WeatherBench2 变量名 |
|---------|---------------------|
| z | `geopotential` |
| t | `temperature` |
| u | `u_component_of_wind` |
| v | `v_component_of_wind` |
| q | `specific_humidity` |
| t2m | `2m_temperature` |
| u10m | `10m_u_component_of_wind` |
| v10m | `10m_v_component_of_wind` |
| msl | `mean_sea_level_pressure` |

---

## 240×121 单日评测（2020-01-01）

### 1. 下载数据

```bash
python download_eval_oneday.py 240x121
```

下载内容（共约 1.3 GB）：

| 数据集 | 内容 | 大小 |
|--------|------|------|
| HRES 预报 | 2020-01-01 00:00 和 12:00 两个初始化时刻，各 40 个 lead time | ~200 MB |
| ERA5 观测 | 2020-01-01 ~ 2020-01-12（覆盖预报最长 10 天有效时刻） | ~120 MB |
| ERA5 气候态 | 1990-2019，dayofyear 1-30（chunk 宽度为 30 天，`slice(1,12)` 会加载完整第一个 chunk） | ~1.2 GB |

> **注**：与 64×32 不同，240×121 气候态文件名含 `_jan1-12`，表示仅含 dayofyear 1-30 的数据，已足够评测 10 天预报。

### 2. 运行评测

```bash
python scripts/evaluate.py \
  --forecast_path=./local_data_minimal/hres_20200101_240x121.zarr \
  --obs_path=./local_data_minimal/era5_20200101_240x121.zarr \
  --climatology_path=./local_data_minimal/climatology_1990-2019_240x121_jan1-12.zarr \
  --output_dir=./output_minimal/ \
  --output_file_prefix=hres_20200101_240x121_ \
  --input_chunks=init_time=1 \
  --eval_configs=deterministic \
  --time_start=2020-01-01 \
  --time_stop=2020-01-01 \
  --variables=geopotential,temperature,u_component_of_wind,v_component_of_wind,specific_humidity,2m_temperature,10m_u_component_of_wind,10m_v_component_of_wind,mean_sea_level_pressure
```

结果保存至 `./output_minimal/hres_20200101_240x121_deterministic.nc`。
