# Accelerometer Comparison Project

Project so sánh dữ liệu gia tốc giữa:
- `sensor_A`: NI DAQ (353B34, các kênh `Channel 1..8`)
- `sensor_B`: ADXL355 (`accX/accY/accZ`)

Hiện tại workflow mặc định đang so sánh:
- `sensor_A`: `Channel 3 (g)`
- `sensor_B`: `accZ(g)`
- Cửa sổ: `100s` bắt đầu từ `2026-02-28T02:23:30Z` (UTC)
- Resample: `500 Hz`

## Cấu trúc project (thực tế)

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
│   │   ├── _helpers.py
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
├── tests/
│   ├── test_filtering.py
│   ├── test_frequency.py
│   ├── test_resampling.py
│   ├── test_correlation.py
│   └── test_error_metrics.py
├── docs/
│   ├── methodology.md
│   ├── project_structure.md
│   └── runbook.md
└── README.md
```

## Môi trường chạy

Project đang được chạy bằng Python trong env:
- `torch-cuda12.8`

Ví dụ:

```bash
"/home/nm0610/miniconda3/envs/torch-cuda12.8/bin/python" --version
```

## Quy trình chạy nhanh

### Chạy bằng 1 file config tổng

File config tổng:
- `configs/project.yaml`

Chạy toàn bộ bằng config:

```bash
"/home/nm0610/miniconda3/envs/torch-cuda12.8/bin/python" scripts/run.py
```

Trong config này bạn có thể chọn:
- file raw sensor A/B
- file processed output
- hai chuỗi dữ liệu cần so sánh (`value_column`)
- cửa sổ thời gian, align, resampling
- tham số lọc (highpass/lowpass Hz, order)
- tham số phân tích (freq_band, fft_window, dominant_freq_tolerance)
- đường dẫn output metrics/aligned/report/figures

### Chạy toàn bộ pipeline

```bash
"/home/nm0610/miniconda3/envs/torch-cuda12.8/bin/python" scripts/run.py
```

Output chính:
- `results/tables/comparison_pair_metrics.csv`
- `results/tables/comparison_pair_aligned.csv`
- `results/reports/comparison_pair_report.md`
- `results/tables/comparison_pair_full_metrics.csv`
- `results/figures/comparison_pair/*.png` (bao gồm `coherence.png`)

### Chạy unit tests

```bash
python -m pytest tests/ -v
```

## Các tính năng phân tích

- Miền thời gian: Mean, Std, RMS, Peak, Peak-to-peak, Crest factor
- Miền tần số: FFT (với Hann window), PSD (Welch), dominant frequency, spectral centroid
- Tương quan: Pearson r, Spearman r, R² với 95% bootstrap confidence intervals
- Sai số: RMSE, MAE, NRMSE, Max error với 95% bootstrap CI
- Coherence analysis: coherence vs frequency, đánh giá Excellent/Good/Acceptable/Poor
- Bland-Altman: ddof=1, Shapiro-Wilk normality test, limits of agreement
- Anti-aliasing: lowpass filter trước khi downsample
- 26 unit tests với synthetic signals

## Các file markdown liên quan

- `docs/project_structure.md`: quy ước cấu trúc và naming
- `docs/runbook.md`: hướng dẫn chạy end-to-end
- `docs/methodology.md`: phương pháp phân tích
- `results/reports/comparison_pair_report.md`: báo cáo kết quả lần chạy gần nhất
- `results/reports/limitations_and_improvements.md`: báo cáo hạn chế và đề xuất
