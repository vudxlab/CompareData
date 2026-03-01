# Runbook

## 1) Yeu cau

- Da co du lieu raw:
  - `data/raw/sensor_A/<ten_file>.csv`
  - `data/raw/sensor_B/<ten_file>.csv`
- Python env (Windows):
  - `C:\Users\NHAT MINH\miniconda3\envs\torch2.2`

## 2) Chuan bi config

Cap nhat `configs/project.yaml`:

- `pipeline.sensor_a.raw_file` — duong dan file CSV sensor A
- `pipeline.sensor_a.processed_file` — duong dan file processed sensor A
- `pipeline.sensor_b.raw_file` — duong dan file CSV sensor B
- `pipeline.sensor_b.processed_file` — duong dan file processed sensor B
- `pipeline.comparison.window.start_utc` — thoi diem bat dau cua so (UTC)
- `pipeline.comparison.window.duration_seconds` — do dai cua so (giay)
- `pipeline.comparison.sensor_a.value_column` — ten cot gia tri sensor A
- `pipeline.comparison.sensor_b.value_column` — ten cot gia tri sensor B
- `pipeline.comparison.resampling.target_fs_hz` — tan so resample muc tieu

Mac dinh hien tai:
- So sanh `Channel 3 (g)` (sensor A) voi `accZ(g)` (sensor B)
- Cua so 120s bat dau `2026-02-28T09:23:15Z`
- Resample 500 Hz

### Luu y dinh dang sensor A moi

Neu file sensor A dung timestamp Unix epoch theo dong ho UTC+7 (khong phai UTC),
can dat them:

```yaml
pipeline:
  sensor_a:
    preprocess:
      timezone_offset_hours: 7
```

Gia tri nay se duoc cong vao epoch truoc khi chuyen sang `datetime_utc`.

## 3) Chay pipeline

### Chay toan bo bang 1 lenh (khuyen nghi)

```bash
"C:\Users\NHAT MINH\miniconda3\envs\torch2.2\python.exe" scripts/run.py
```

### Cac stage duoc chay ben trong `scripts/run.py`

- preprocess sensor B (ADXL355)
- preprocess sensor A (NI DAQ)
- compare pair
- full report

## 4) Kiem tra output

- Bang:
  - `results/tables/comparison_pair_metrics.csv`
  - `results/tables/comparison_pair_full_metrics.csv`
  - `results/tables/comparison_pair_fft_peaks_0_50hz.csv`
- Du lieu aligned:
  - `results/tables/comparison_pair_aligned.csv`
- Hinh:
  - `results/figures/comparison_pair/*.png`
- Bao cao:
  - `results/reports/comparison_pair_report.md`
  - `results/reports/comparison_pair_detailed_report.md`

## 5) Troubleshooting nhanh

- Neu `FileNotFoundError` khi doc raw file:
  - Kiem tra `pipeline.sensor_a.raw_file` / `pipeline.sensor_b.raw_file` trong config
  - Dam bao file da duoc copy vao dung thu muc `data/raw/`
- Neu `datetime_utc` parse sai / hai sensor khong overlap:
  - Kiem tra `timezone_offset_hours` cho sensor A (neu dung dong ho UTC+7)
  - Xac nhan lai `window.start_utc` nam trong khoang ca hai sensor co du lieu
- Neu `Missing required column` / `No channel columns detected`:
  - Kiem tra ten cot trong file raw khop voi config (`value_column`)
- Neu output mau qua it:
  - Kiem tra lai `window.start_utc`, `duration_seconds`, va du lieu co nam trong khoang nay hay khong
- Neu `convert_to_g: true` nhung du lieu da o don vi `g`:
  - Dat `convert_to_g: false` de tranh chia nham cho 9.80665
