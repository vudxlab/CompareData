# Runbook

## 1) Yeu cau

- Da co du lieu raw:
  - `data/raw/sensor_A/Setup5_*.csv`
  - `data/raw/sensor_B/axdl355_*.csv`
- Python env:
  - `torch-cuda12.8`

## 2) Chuan bi config

Cap nhat `configs/project.yaml`:

- `pipeline.sensor_a.raw_file`
- `pipeline.sensor_b.raw_file`
- `pipeline.comparison.window.start_utc`
- `pipeline.comparison.window.duration_seconds`
- `pipeline.comparison.sensor_a.value_column`
- `pipeline.comparison.sensor_b.value_column`
- `pipeline.comparison.resampling.target_fs_hz`

Mac dinh hien tai:
- So sanh `channel6(m/s^2)` (sensor A) voi `accZ(g)` (sensor B)
- Cua so 100s
- Resample 100Hz

## 3) Chay pipeline

### Chay toan bo bang 1 lenh (khuyen nghi)

```bash
"/home/nm0610/miniconda3/envs/torch-cuda12.8/bin/python" scripts/run.py
```

### Cac stage duoc chay ben trong `scripts/run.py`

- preprocess sensor B
- preprocess sensor A
- compare pair
- full report

## 4) Kiem tra output

- Bang:
  - `results/tables/comparison_pair_metrics.csv`
  - `results/tables/comparison_pair_full_metrics.csv`
- Du lieu aligned:
  - `results/tables/comparison_pair_aligned.csv`
- Hinh:
  - `results/figures/comparison_pair/*.png`
- Bao cao:
  - `results/reports/comparison_pair_report.md`

## 5) Troubleshooting nhanh

- Neu `datetime_utc` parse sai:
  - Chay lai preprocess de tao file processed moi
- Neu thieu cot so sanh (vd `channel6(m/s^2)`):
  - Kiem tra `pipeline.sensor_a.raw_file` va stage preprocess trong `configs/project.yaml`
- Neu output mau qua it:
  - Kiem tra lai `window.start_utc`, `duration_seconds`, va du lieu co nam trong khoang nay hay khong
