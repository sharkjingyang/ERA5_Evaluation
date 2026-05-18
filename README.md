# WeatherBench2 Evaluation

## 快速开始：64×32 单日评测

### 1. 安装依赖

```bash
pip install -e ".[tests]"
```

### 2. 下载数据

运行以下脚本，下载 2020-01-01 所需的最小数据集（约 1 GB）：

```bash
python download_minimal.py
```

下载内容：
- HRES 预报：2020-01-01 00:00 和 12:00 两个初始化时刻（57 MB）
- ERA5 观测：2020-01-01 ~ 2020-01-12（33 MB）
- ERA5 气候态：1990-2019 全年（852 MB，用于 ACC 计算）

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
