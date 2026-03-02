# Phương pháp so sánh cảm biến gia tốc

## 1. Mục tiêu

So sánh độ tương đồng và sai khác giữa hai chuỗi gia tốc đo bởi hai hệ cảm biến khác nhau.

## 2. Thiết lập thí nghiệm

### 2.1 Cảm biến

- **Sensor A**: NI DAQ 353B34
  - Các kênh: `Channel 1 (g)`, `Channel 2 (g)`, `Channel 3 (g)`
  - Đơn vị gốc: `g` (dữ liệu mới) hoặc `m/s^2` (dữ liệu cũ, cần `convert_to_g: true`)
  - Tần số lấy mẫu: 1651 Hz (có thể khác tùy file)
  - Định dạng timestamp: Unix epoch theo đồng hồ UTC chuẩn (`timezone_offset_hours: 0`)

- **Sensor B**: ADXL355
  - Các kênh: `accX(g)`, `accY(g)`, `accZ(g)`
  - Đơn vị: `g`
  - Tần số lấy mẫu: ~1651 Hz
  - Định dạng timestamp: Unix epoch theo đồng hồ UTC+7 (cần `timezone_offset_hours: -7` để chỉnh về UTC)

### 2.2 Cấu hình so sánh hiện tại

- Chuỗi A: `Channel 3 (g)` (sensor A)
- Chuỗi B: `accZ(g)` (sensor B)
- Cửa sổ thời gian: 100 giây bắt đầu `2026-02-28T02:23:30Z` (UTC)
- Tần số resample mục tiêu: `500 Hz`
- Canh hàng theo thời gian: **không dùng cross-correlation** — hai sensor đã có timestamp UTC tuyệt đối, cắt đúng window theo UTC rồi so sánh trực tiếp

## 3. Quy trình xử lý dữ liệu

### 3.1 Tiền xử lý

1. Đọc dữ liệu raw theo định dạng riêng từng sensor
2. Chuyển đổi về timestamp UTC
   - Sensor A: epoch UTC chuẩn, `timezone_offset_hours: 0`
   - Sensor B: epoch theo đồng hồ UTC+7, cần `timezone_offset_hours: -7` (trừ 7h để ra UTC thật)
3. Loại bỏ DC offset (mean subtraction)
4. Lọc high-pass và low-pass (tham số đọc từ config)
   - `preprocessing.filtering.highpass_hz` (mặc định: 0.5 Hz)
   - `preprocessing.filtering.highpass_order` (mặc định: 2)
   - `preprocessing.filtering.lowpass_hz` (mặc định: 500 Hz)
   - `preprocessing.filtering.lowpass_order` (mặc định: 4)
5. Lưu vào `data/processed/`

### 3.2 Chuẩn hóa trước so sánh

1. Cắt dữ liệu theo cửa sổ UTC đã khai báo (điểm bắt đầu gần nhất trong file)
2. Áp dụng anti-aliasing filter trước khi resample (lowpass tại 0.9 × Nyquist mục tiêu)
3. Resample về tần số chung (`target_fs_hz`)
4. So sánh trực tiếp theo timestamp UTC — không dùng cross-correlation alignment
5. Tính toán metrics

### 3.3 Anti-aliasing khi resampling

Khi downsample từ fs_source xuống fs_target (ví dụ 1651 Hz → 500 Hz):
- Nyquist mục tiêu = fs_target / 2 = 250 Hz
- Áp dụng lowpass Butterworth order 8 tại cutoff = 0.9 × Nyquist = 225 Hz trước khi nội suy
- Điều này ngăn chặn năng lượng trong dải 225–826 Hz bị gập (alias) vào dải 0–250 Hz
- Sau đó mới thực hiện nội suy tuyến tính (`np.interp`) về tần số mục tiêu

## 4. Tập chỉ số báo cáo

### 4.1 Miền thời gian

- Mean, Std, RMS, Peak, Peak-to-peak, Crest factor

### 4.2 Miền tần số

- FFT (áp dụng Hann window với amplitude correction factor)
- PSD (Welch method)
- Dominant frequency
- Spectral centroid
- Median frequency
- FFT peaks (top N trong dải 0–50 Hz)
- Frequency band analysis (dải cấu hình được, mặc định 0–20 Hz)

#### 4.2.1 FFT với window function

FFT được tính với Hann window (mặc định, cấu hình được qua `preprocessing.analysis.fft_window`):

```
win = scipy.signal.get_window("hann", N)
data_windowed = data * win
acf = N / sum(win)                   # amplitude correction factor
magnitude = |FFT(data_windowed)| * 2 / N * acf
```

Hann window giảm spectral leakage so với rectangular window (FFT trực tiếp không window).

### 4.3 So sánh trực tiếp

- Pearson r, Spearman r, R² với 95% bootstrap confidence intervals
- RMSE, MAE, NRMSE, Max error với 95% bootstrap CI
- Bland-Altman analysis (ddof=1, Shapiro-Wilk normality test)
- Coherence analysis (mean coherence, đánh giá theo tiêu chí)

### 4.4 Coherence analysis

Coherence được tính bằng `scipy.signal.coherence` giữa hai tín hiệu đã resample:
- Biểu đồ coherence vs frequency (0–50 Hz)
- Mean coherence và min coherence
- Đánh giá theo tiêu chí: Excellent (> 0.95), Good (> 0.90), Acceptable (> 0.80), Poor (< 0.80)
- Đường ngưỡng tại 0.95 và 0.80 trên biểu đồ

### 4.5 Bootstrap confidence interval

Các chỉ số chính được báo cáo kèm 95% CI bằng phương pháp bootstrap (n=1000, seed=42):
- Pearson r: ví dụ `0.007 [95% CI: -0.003, 0.017]`
- RMSE: ví dụ `0.063 [95% CI: 0.063, 0.064]`
- MAE: ví dụ `0.049 [95% CI: 0.048, 0.049]`

### 4.6 Bland-Altman analysis

- Sử dụng sample standard deviation (`ddof=1`) theo Bland & Altman (1986)
- Limits of agreement: mean ± z × std (z = 1.96 cho 95% CI)
- Kiểm tra phân phối chuẩn của differences bằng Shapiro-Wilk test
  - Nếu p > 0.05: differences phân phối chuẩn, LoA có thể tin cậy
  - Nếu p <= 0.05: differences không phân phối chuẩn, LoA cần thận trọng khi diễn giải
- Proportional bias (linear regression của differences vs means)

## 5. Đầu ra

- Bảng tổng hợp: `results/tables/*metrics*.csv`
- FFT peaks: `results/tables/*fft_peaks*.csv`
- Dữ liệu đã canh hàng: `results/tables/*aligned*.csv`
- Hình phân tích: `results/figures/.../*.png`
  - `time_series.png`, `time_series_3panel.png`
  - `fft.png`, `freq_3panel_0_20hz.png`
  - `psd.png`
  - `scatter.png`
  - `bland_altman.png`
  - `coherence.png`
- Báo cáo markdown: `results/reports/..._report.md`

## 6. Tiêu chí đánh giá tham khảo

| Metric | Excellent | Good | Acceptable | Poor |
|--------|-----------|------|------------|------|
| Pearson r | > 0.99 | > 0.95 | > 0.90 | < 0.90 |
| NRMSE | < 1% | < 5% | < 10% | > 10% |
| Coherence | > 0.95 | > 0.90 | > 0.80 | < 0.80 |

## 7. Cấu hình tham số phân tích

Tất cả tham số phân tích được đọc từ `configs/project.yaml`:

| Tham số | Key trong config | Mặc định |
|---------|-----------------|----------|
| Highpass cutoff | `preprocessing.filtering.highpass_hz` | 0.5 Hz |
| Highpass order | `preprocessing.filtering.highpass_order` | 2 |
| Lowpass cutoff | `preprocessing.filtering.lowpass_hz` | 500 Hz |
| Lowpass order | `preprocessing.filtering.lowpass_order` | 4 |
| FFT window | `preprocessing.analysis.fft_window` | "hann" |
| Freq band min | `preprocessing.analysis.freq_band_min_hz` | 0.0 Hz |
| Freq band max | `preprocessing.analysis.freq_band_max_hz` | 20.0 Hz |
| Dominant freq tolerance | `preprocessing.analysis.dominant_freq_tolerance_hz` | 1.0 Hz |

## 8. Tài liệu tham khảo

1. Bland, J.M. & Altman, D.G. (1986). Statistical methods for assessing agreement between two methods of clinical measurement.
2. ISO 16063 - Methods for the calibration of vibration and shock transducers
3. Harris, F.J. (1978). On the use of windows for harmonic analysis with the discrete Fourier transform. Proceedings of the IEEE.
