# Hướng dẫn cấu trúc Project

## Mục tiêu

Tài liệu này mô tả cấu trúc thư mục chuẩn cho project so sánh dữ liệu gia tốc.

## Nguyên tắc tổ chức

- `data/raw`: dữ liệu gốc, không sửa trực tiếp
- `data/processed`: dữ liệu đã tiền xử lý, sẵn sàng phân tích
- `configs`: tất cả tham số cho pipeline (bao gồm filter params và analysis params)
- `src`: toàn bộ logic Python có thể tái sử dụng
- `scripts`: entry-point để chạy nhanh workflow
- `results`: output sau mỗi lần chạy (tables, figures, reports)
- `docs`: tài liệu hướng dẫn và phương pháp
- `tests`: unit tests với synthetic signals

## Các file config quan trọng

- `configs/project.yaml`
  - Config duy nhất cho toàn bộ project
  - Khai báo sensor metadata + preprocess + comparison + output
  - Khai báo cặp chuỗi cần so sánh, cửa sổ thời gian, tần số resample
  - Tham số `timezone_offset_hours` để chỉnh lệch giờ UTC cho từng sensor
    (sensor A = 0, sensor B = -7)
  - Section `preprocessing.filtering`: highpass_hz, highpass_order, lowpass_hz, lowpass_order
  - Section `preprocessing.analysis`: fft_window, freq_band_min_hz, freq_band_max_hz, dominant_freq_tolerance_hz

## Các module phân tích chính trong src

- `src/preprocessing/load_data.py`
  - `preprocess_adxl355`: tiền xử lý sensor B (ADXL355)
  - `preprocess_353B34_keep_channels`: tiền xử lý sensor A (NI DAQ)
    - Hỗ trợ 2 định dạng timestamp: `Time (s)` (relative) và `Time (UTC epoch s)` (unix)
    - Tham số `timezone_offset_hours` để chỉnh epoch UTC+7 sang UTC
  - Nhận filter params từ config (highpass_hz, highpass_order, lowpass_hz, lowpass_order)

- `src/preprocessing/time_conversion.py`
  - Các hàm tiện ích chuyển đổi timestamp: unix <-> UTC, relative time

- `src/analysis/_helpers.py`
  - Các hàm tiện ích dùng chung: `to_utc`, `to_g`, `estimate_fs`, `load_window_raw`
  - Được import bởi `window_compare.py` và `full_plan_compare.py` để tránh trùng lặp code

- `src/analysis/window_compare.py`
  - So sánh 1 cặp chuỗi theo config
  - Cắt window theo timestamp UTC tuyệt đối, resample (có anti-aliasing), tính metrics
  - Không dùng cross-correlation alignment (đã có timestamp UTC chính xác)

- `src/analysis/full_plan_compare.py`
  - Chạy full workflow theo plan
  - Bao gồm: coherence analysis, bootstrap CI, Bland-Altman với normality test
  - Sinh bảng kết quả + hình + report markdown

- `src/analysis/frequency.py`
  - `compute_fft`: FFT với Hann window (cấu hình được) và amplitude correction factor
  - `compute_frequency_metrics`: dominant frequency, spectral centroid, median frequency

- `src/analysis/comparison.py`
  - `compute_error_metrics`: RMSE, MAE, NRMSE, Max error
  - `compute_bootstrap_ci`: bootstrap 95% CI cho Pearson r, RMSE, MAE
  - `bland_altman_analysis`: ddof=1, Shapiro-Wilk normality test, proportional bias

- `src/analysis/correlation.py`
  - `compute_correlation`: Pearson r, Spearman r, R²
  - `coherence`: coherence vs frequency bằng `scipy.signal.coherence`

- `src/visualization/plots.py`
  - Các hàm vẽ biểu đồ: time_series, fft, psd, scatter, bland_altman, coherence, 3-panel

- `src/visualization/reports.py`
  - `generate_report`: sinh báo cáo markdown với tất cả sections (bao gồm coherence, CI, normality)

## Các script chạy

- `scripts/run.py`: script duy nhất chạy end-to-end (preprocess + compare + full report)
  - Truyền filter params từ config vào preprocessing functions

## Unit tests

- `tests/test_filtering.py`: lowpass/highpass filter (5 tests)
- `tests/test_frequency.py`: FFT peak detection, window function (4 tests)
- `tests/test_resampling.py`: bảo toàn tần số, anti-aliasing (4 tests)
- `tests/test_correlation.py`: Pearson r, coherence (5 tests)
- `tests/test_error_metrics.py`: RMSE, MAE, Bland-Altman ddof, bootstrap CI (8 tests)

Chạy tests: `python -m pytest tests/ -v`

## Quy ước đặt tên output

- Bảng kết quả:
  - `results/tables/*metrics*.csv`
  - `results/tables/*aligned*.csv`
  - `results/tables/*fft_peaks*.csv`
- Hình ảnh:
  - `results/figures/<run_name>/*.png`
  - Bao gồm: time_series, time_series_3panel, fft, freq_3panel_0_20hz, psd, scatter, bland_altman, coherence
- Báo cáo:
  - `results/reports/<run_name>_report.md`
