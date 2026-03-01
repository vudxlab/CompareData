# Accelerometer Comparison Project

Project so sanh du lieu gia toc giua:
- `sensor_A`: NI DAQ (Setup5, cac kenh `Channel 1..8`)
- `sensor_B`: ADXL355 (`accX/accY/accZ`)

Hien tai workflow mac dinh dang so sanh:
- `sensor_A`: `channel6(m/s^2)`
- `sensor_B`: `accZ(g)`
- Cua so: `100s` bat dau tu `10:00:00 UTC`
- Resample: `100 Hz`

## Cau truc project (thuc te)

```text
CompareData/
├── configs/
│   └── project.yaml
├── data/
│   ├── raw/
│   │   ├── sensor_A/
│   │   └── sensor_B/
│   └── processed/
├── src/
│   ├── preprocessing/
│   ├── analysis/
│   │   ├── window_compare.py
│   │   └── full_plan_compare.py
│   ├── visualization/
│   └── utils/
├── scripts/
│   └── run.py
├── results/
│   ├── tables/
│   ├── figures/
│   └── reports/
├── docs/
│   ├── methodology.md
│   ├── project_structure.md
│   └── runbook.md
└── README.md
```

## Moi truong chay

Project dang duoc chay bang Python trong env:
- `torch-cuda12.8`

Vi du:

```bash
"/home/nm0610/miniconda3/envs/torch-cuda12.8/bin/python" --version
```

## Quy trinh chay nhanh

### Chay bang 1 file config tong

File config tong:
- `configs/project.yaml`

Chay toan bo bang config:

```bash
"/home/nm0610/miniconda3/envs/torch-cuda12.8/bin/python" scripts/run.py
```

Trong config nay ban co the chon:
- file raw sensor A/B
- file processed output
- hai chuoi du lieu can so sanh (`value_column`)
- cua so thoi gian, align, resampling
- duong dan output metrics/aligned/report/figures

### Chay toan bo pipeline

```bash
"/home/nm0610/miniconda3/envs/torch-cuda12.8/bin/python" scripts/run.py
```

Output chinh:
- `results/tables/comparison_pair_metrics.csv`
- `results/tables/comparison_pair_aligned.csv`
- `results/reports/comparison_pair_report.md`
- `results/tables/comparison_pair_full_metrics.csv`
- `results/figures/comparison_pair/*.png`

## Cac file markdown lien quan

- `docs/project_structure.md`: quy uoc cau truc va naming
- `docs/runbook.md`: huong dan chay end-to-end
- `docs/methodology.md`: phuong phap phan tich
- `results/reports/comparison_pair_report.md`: bao cao ket qua lan chay gan nhat
