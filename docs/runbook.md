# Runbook

## 1) Yêu cầu

- Đã có dữ liệu raw:
  - `data/raw/sensor_A/<tên_file>.csv`
  - `data/raw/sensor_B/<tên_file>.csv`
- Python env (Windows):
  - `C:\Users\NHAT MINH\miniconda3\envs\torch2.2`

## 2) Chuẩn bị config

Cập nhật `configs/project.yaml`:

### Pipeline (bắt buộc)

- `pipeline.sensor_a.raw_file` — đường dẫn file CSV sensor A
- `pipeline.sensor_a.processed_file` — đường dẫn file processed sensor A
- `pipeline.sensor_b.raw_file` — đường dẫn file CSV sensor B
- `pipeline.sensor_b.processed_file` — đường dẫn file processed sensor B
- `pipeline.comparison.window.start_utc` — thời điểm bắt đầu cửa sổ (UTC)
- `pipeline.comparison.window.duration_seconds` — độ dài cửa sổ (giây)
- `pipeline.comparison.sensor_a.value_column` — tên cột giá trị sensor A
- `pipeline.comparison.sensor_b.value_column` — tên cột giá trị sensor B
- `pipeline.comparison.resampling.target_fs_hz` — tần số resample mục tiêu

### Preprocessing (tùy chọn)

- `preprocessing.filtering.highpass_hz` — tần số cắt high-pass (mặc định: 0.5)
- `preprocessing.filtering.highpass_order` — bậc bộ lọc high-pass (mặc định: 2)
- `preprocessing.filtering.lowpass_hz` — tần số cắt low-pass (mặc định: 500)
- `preprocessing.filtering.lowpass_order` — bậc bộ lọc low-pass (mặc định: 4)

### Analysis (tùy chọn)

- `preprocessing.analysis.fft_window` — window function cho FFT (mặc định: "hann")
- `preprocessing.analysis.freq_band_min_hz` — giới hạn dưới dải tần phân tích (mặc định: 0.0)
- `preprocessing.analysis.freq_band_max_hz` — giới hạn trên dải tần phân tích (mặc định: 20.0)
- `preprocessing.analysis.dominant_freq_tolerance_hz` — ngưỡng khớp tần số trội (mặc định: 1.0)

### Mặc định hiện tại

- So sánh `Channel 3 (g)` (sensor A) với `accZ(g)` (sensor B)
- Cửa sổ 100s bắt đầu `2026-02-28T02:23:30Z` (UTC thật)
- Resample 500 Hz
- Alignment: tắt (dùng timestamp UTC tuyệt đối trực tiếp)

### Lưu ý timezone

- **Sensor A**: epoch UTC chuẩn → `timezone_offset_hours: 0`
- **Sensor B**: epoch theo đồng hồ UTC+7 → `timezone_offset_hours: -7`

## 3) Chạy pipeline

### Chạy toàn bộ bằng 1 lệnh (khuyến nghị)

```bash
"C:\Users\NHAT MINH\miniconda3\envs\torch2.2\python.exe" scripts/run.py
```

### Các stage được chạy bên trong `scripts/run.py`

- Preprocess sensor B (ADXL355) — với filter params từ config
- Preprocess sensor A (NI DAQ) — với filter params từ config
- Compare pair (bao gồm anti-aliasing trước resampling)
- Full report (bao gồm coherence, bootstrap CI, normality test)

## 4) Chạy unit tests

```bash
python -m pytest tests/ -v
```

26 unit tests bao gồm:
- `test_filtering.py` — lowpass/highpass filter (5 tests)
- `test_frequency.py` — FFT peak detection, window function (4 tests)
- `test_resampling.py` — bảo toàn tần số, anti-aliasing (4 tests)
- `test_correlation.py` — Pearson r, coherence (5 tests)
- `test_error_metrics.py` — RMSE, MAE, Bland-Altman ddof, bootstrap CI (8 tests)

## 5) Kiểm tra output

- Bảng:
  - `results/tables/comparison_pair_metrics.csv`
  - `results/tables/comparison_pair_full_metrics.csv`
  - `results/tables/comparison_pair_fft_peaks_0_50hz.csv`
- Dữ liệu aligned:
  - `results/tables/comparison_pair_aligned.csv`
- Hình:
  - `results/figures/comparison_pair/time_series.png`
  - `results/figures/comparison_pair/time_series_3panel.png`
  - `results/figures/comparison_pair/fft.png`
  - `results/figures/comparison_pair/freq_3panel_0_20hz.png`
  - `results/figures/comparison_pair/psd.png`
  - `results/figures/comparison_pair/scatter.png`
  - `results/figures/comparison_pair/bland_altman.png`
  - `results/figures/comparison_pair/coherence.png`
- Báo cáo:
  - `results/reports/comparison_pair_report.md`
  - `results/reports/comparison_pair_detailed_report.md`

## 6) Xử lý sự cố nhanh

- Nếu `FileNotFoundError` khi đọc raw file:
  - Kiểm tra `pipeline.sensor_a.raw_file` / `pipeline.sensor_b.raw_file` trong config
  - Đảm bảo file đã được copy vào đúng thư mục `data/raw/`
- Nếu `datetime_utc` parse sai / hai sensor không overlap:
  - Kiểm tra `timezone_offset_hours`: sensor A = 0, sensor B = -7
  - Xác nhận lại `window.start_utc` nằm trong khoảng cả hai sensor có dữ liệu (UTC thật)
- Nếu `Missing required column` / `No channel columns detected`:
  - Kiểm tra tên cột trong file raw khớp với config (`value_column`)
- Nếu output mẫu quá ít:
  - Kiểm tra lại `window.start_utc`, `duration_seconds`, và dữ liệu có nằm trong khoảng này hay không
- Nếu `convert_to_g: true` nhưng dữ liệu đã ở đơn vị `g`:
  - Đặt `convert_to_g: false` để tránh chia nhầm cho 9.80665
- Nếu unit test fail:
  - Kiểm tra scipy, numpy đã được cài đặt đúng version
  - Chạy `python -m pytest tests/ -v --tb=short` để xem chi tiết lỗi
