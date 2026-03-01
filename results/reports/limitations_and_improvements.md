# Báo cáo Hạn chế và Đề xuất Cải thiện

**Dự án:** So sánh dữ liệu gia tốc giữa hai hệ thống cảm biến (NI DAQ Setup5 vs ADXL355)
**Ngày:** 2026-03-02 (cập nhật)
**Mục đích:** Phục vụ viết bài báo khoa học — đánh giá khách quan các hạn chế kỹ thuật và phương pháp luận

> **Ghi chú cập nhật (2026-03-02):** Nhiều hạn chế kỹ thuật và phương pháp luận đã được khắc phục. Các mục đã giải quyết được đánh dấu [ĐÃ KHẮC PHỤC].

---

## 1. Tổng quan kết quả hiện tại

| Chỉ số | Giá trị | Đánh giá |
|--------|---------|----------|
| Pearson r | 0.0064 | Kém (ngưỡng chấp nhận > 0.90) |
| R² | 0.00004 | Gần như bằng 0 |
| NRMSE | 17.7% | Kém (ngưỡng chấp nhận < 10%) |
| Tần số trội Sensor A | 11.64 Hz | Khớp nhau |
| Tần số trội Sensor B | 11.72 Hz | Khớp nhau |
| Pearson r phổ tần (0–20 Hz) | 0.594 | Trung bình |
| Tỷ lệ năng lượng A/B (0–20 Hz) | 0.66 | Sensor B năng lượng cao hơn ~50% |

**Nhận xét tổng quát:** Hai cảm biến nhận diện đúng cùng tần số rung trội (~11.7 Hz), nhưng tương quan miền thời gian gần bằng 0. Điều này cho thấy phương pháp hiện tại chỉ đủ để xác nhận nguồn rung chung, chưa đủ để kết luận hai cảm biến có thể thay thế nhau.

---

## 2. Hạn chế về Phương pháp luận (Methodology)

### 2.1. Nguy cơ aliasing khi resampling [ĐÃ KHẮC PHỤC]

**Vấn đề:** Pipeline downsample từ ~1651 Hz xuống 500 Hz bằng nội suy tuyến tính (`np.interp`), không sử dụng bộ lọc anti-aliasing trước khi resampling.

- Tần số Nyquist tại 500 Hz là 250 Hz
- Bộ lọc lowpass trong tiền xử lý đặt tại 500 Hz, nghĩa là tín hiệu vẫn chứa năng lượng trong dải 250–500 Hz
- Năng lượng trong dải 250–500 Hz sẽ bị gập (alias) vào dải 0–250 Hz sau khi resampling
- Nội suy tuyến tính bản thân nó cũng tạo hiệu ứng lowpass nhưng không đảm bảo triệt tiêu hoàn toàn aliasing

**Mức độ ảnh hưởng:** Trung bình đến cao. Aliasing có thể tạo ra các thành phần tần số giả trong dải phân tích, ảnh hưởng đến độ tin cậy của các chỉ số miền tần số trên tín hiệu đã resampled. Tuy nhiên, pipeline hiện tại tính FFT/PSD trên tín hiệu gốc (trước resampling) nên phần phân tích tần số ít bị ảnh hưởng. Phần bị ảnh hưởng chính là các chỉ số miền thời gian (correlation, error metrics) được tính trên dữ liệu đã resampled.

**Đề xuất:** Thêm bộ lọc lowpass anti-aliasing tại `0.45 × fs_target` (225 Hz) trước khi resampling, hoặc sử dụng `scipy.signal.resample` (FFT-based) hoặc `scipy.signal.resample_poly` (polyphase filter) thay cho `np.interp`.

**Giải pháp đã thực hiện:** Thêm lowpass Butterworth order 8 tại `0.9 × Nyquist_target` (225 Hz) trong `_resample_linear()` trước khi `np.interp`. Hàm nhận thêm param `fs_source` để xác định khi nào cần anti-aliasing (chỉ khi `fs_target < fs_source`).

### 2.2. FFT không áp dụng window function [ĐÃ KHẮC PHỤC]

**Vấn đề:** Hàm `compute_fft()` sử dụng FFT trực tiếp trên tín hiệu mà không áp dụng hàm cửa sổ (window function), tương đương với rectangular window.

- Rectangular window gây spectral leakage nghiêm trọng, làm năng lượng từ một tần số "rò" sang các tần số lân cận
- Điều này ảnh hưởng đến độ chính xác của việc xác định dominant frequency và các FFT peaks
- Phổ PSD (Welch) có sử dụng Hann window nên kết quả PSD đáng tin cậy hơn

**Mức độ ảnh hưởng:** Trung bình. Ảnh hưởng chủ yếu đến biểu đồ FFT và bảng FFT peaks. Các kết quả PSD không bị ảnh hưởng.

**Đề xuất:** Áp dụng Hann window (hoặc Hamming, Blackman-Harris) trước khi tính FFT. Cần nhân với hệ số bù biên độ (amplitude correction factor) tương ứng.

**Giải pháp đã thực hiện:** `compute_fft()` trong `frequency.py` giờ nhận param `window="hann"` (cấu hình qua `preprocessing.analysis.fft_window`). Áp dụng amplitude correction factor `acf = N / sum(win)` để bù biên độ.

### 2.3. Chuẩn hóa biên độ FFT tại DC

**Vấn đề:** Công thức chuẩn hóa `|FFT| × 2 / N` áp dụng cho tất cả tần số, bao gồm cả thành phần DC (0 Hz) và Nyquist. Theo lý thuyết, thành phần DC và Nyquist không nên nhân 2 vì chúng không có phần đối xứng âm.

**Mức độ ảnh hưởng:** Thấp. DC đã bị loại bỏ bởi bước tiền xử lý (remove offset + highpass filter), nên sai số 2× tại DC không ảnh hưởng thực tế.

### 2.4. Bland-Altman sử dụng population standard deviation [ĐÃ KHẮC PHỤC]

**Vấn đề:** Hàm `bland_altman_analysis()` sử dụng `np.std` với `ddof=0` (population std) thay vì `ddof=1` (sample std). Phương pháp Bland-Altman chuẩn (Bland & Altman, 1986) sử dụng sample standard deviation.

**Mức độ ảnh hưởng:** Rất thấp với kích thước mẫu hiện tại (~50,000 điểm). Sự khác biệt giữa `ddof=0` và `ddof=1` là không đáng kể khi N lớn. Tuy nhiên, nếu áp dụng cho cửa sổ ngắn (N nhỏ), hạn chế này sẽ trở nên quan trọng.

**Đề xuất:** Đổi thành `np.std(differences, ddof=1)` để tuân thủ đúng phương pháp gốc.

**Giải pháp đã thực hiện:** Đã đổi thành `np.std(differences, ddof=1)` trong `bland_altman_analysis()`. Thêm Shapiro-Wilk normality test cho differences.

### 2.5. Ước lượng tần số lấy mẫu thiếu robust

**Vấn đề:** Tần số lấy mẫu được ước lượng bằng `1 / mean(diff(timestamps))`. Phương pháp này nhạy cảm với:
- Jitter trong timestamp (đặc biệt với ADXL355 ghi timestamp qua phần mềm)
- Khoảng cách lấy mẫu không đều (missing samples, buffer overflow)
- Outlier trong timestamp (một giá trị bất thường có thể kéo lệch mean)

**Đề xuất:** Sử dụng phương pháp robust hơn: `fs = (N - 1) / (t_last - t_first)` hoặc `1 / median(diff(timestamps))`.

---

## 3. Hạn chế về Thiết kế thí nghiệm

### 3.1. Không đồng vị trí (co-location) cảm biến

**Vấn đề:** Đây là hạn chế lớn nhất của nghiên cứu. Hai cảm biến được đặt tại các vị trí khác nhau trên kết cấu, dẫn đến:
- Biên độ rung khác nhau tại mỗi vị trí (mode shape effect)
- Pha tín hiệu khác nhau (phase shift do truyền sóng)
- Tỷ lệ năng lượng A/B = 0.66, cho thấy Sensor B nhận rung mạnh hơn ~50%
- Pearson r ≈ 0 không thể kết luận được là do sai lệch cảm biến hay do vị trí đặt khác nhau

**Hệ quả:** Không thể tách biệt được hai nguồn sai lệch: (1) sai lệch bản thân cảm biến (accuracy, linearity, noise) và (2) sai lệch do vị trí đặt (mode shape, wave propagation). Đây là confounding variable nghiêm trọng.

**Đề xuất cho nghiên cứu tiếp theo:**
- Thực hiện thí nghiệm co-location: đặt cả hai cảm biến tại cùng một điểm (hoặc càng gần càng tốt, < 5 cm)
- Sử dụng bàn rung (vibration shaker/exciter) với tín hiệu kích thích đã biết (sine sweep, white noise) để đánh giá transfer function của từng cảm biến
- Tham chiếu tiêu chuẩn ISO 16063 (calibration of vibration transducers)

### 3.2. Chưa hiệu chuẩn (calibration) cảm biến

**Vấn đề:** Không có bước hiệu chuẩn nào được thực hiện trước khi so sánh:
- Không có calibration certificate hoặc sensitivity verification cho cả hai cảm biến
- Không kiểm tra gain/sensitivity match giữa NI DAQ và ADXL355
- Không kiểm tra cross-axis sensitivity (ADXL355 có thể có ~1% cross-axis)
- Không xác nhận hướng trục đo (axis orientation) của hai cảm biến có cùng chiều hay không

**Đề xuất:**
- Sử dụng tín hiệu tham chiếu đã biết (known reference signal) để hiệu chuẩn cả hai cảm biến
- Ghi lại orientation matrix của từng cảm biến so với hệ tọa độ chung
- Kiểm tra cross-axis sensitivity bằng thí nghiệm kích thích đơn trục

### 3.3. Cửa sổ phân tích hạn chế

**Vấn đề:** Chỉ phân tích một cửa sổ 100 giây duy nhất. Kết quả phụ thuộc hoàn toàn vào đặc tính rung trong khoảng thời gian cụ thể này.

**Đề xuất:**
- Phân tích nhiều cửa sổ thời gian với các điều kiện kích thích khác nhau
- Tính toán confidence interval cho các chỉ số thống kê
- Phân tích time-varying coherence (spectrogram, STFT) để đánh giá sự ổn định theo thời gian

### 3.4. Chỉ so sánh một trục

**Vấn đề:** Pipeline hiện tại chỉ so sánh một cặp kênh (Channel 3 vs accZ). ADXL355 là cảm biến 3 trục, NI DAQ có thể có nhiều kênh. Việc chỉ so sánh một trục không cho bức tranh toàn diện.

**Đề xuất:**
- So sánh tất cả các trục tương ứng (X, Y, Z)
- So sánh vector magnitude để loại bỏ ảnh hưởng của sai lệch hướng trục
- Phân tích cross-axis correlation matrix

---

## 4. Hạn chế về Kỹ thuật phần mềm

### 4.1. Không có unit test [ĐÃ KHẮC PHỤC]

**Vấn đề:** Project không có bất kỳ test nào. Không có thư mục `tests/`, không có cấu hình pytest, không có test function. Việc xác nhận pipeline đúng chỉ dựa trên "chạy không có exception".

- Không thể phát hiện regression khi sửa code
- Không thể xác nhận tính đúng đắn của từng hàm xử lý (ví dụ: lọc, FFT, resampling)
- Không có test với synthetic data (tín hiệu đã biết kết quả mong đợi)

**Đề xuất:**
- Viết unit test cho các hàm core: filtering, FFT, resampling, correlation, error metrics
- Test với synthetic signals (sine wave đã biết tần số, biên độ) để xác nhận pipeline cho kết quả đúng
- Integration test chạy pipeline end-to-end với dữ liệu mẫu

**Giải pháp đã thực hiện:** Đã tạo 5 file test với 26 unit tests sử dụng synthetic signals: `test_filtering.py` (5), `test_frequency.py` (4), `test_resampling.py` (4), `test_correlation.py` (5), `test_error_metrics.py` (8). Tất cả tests pass.

### 4.2. Code thừa không được sử dụng [ĐÃ KHẮC PHỤC MỘT PHẦN]

**Vấn đề:** Nhiều hàm được viết nhưng không bao giờ được gọi trong pipeline:

| Hàm | File |
|-----|------|
| `remove_outliers()` | `cleaning.py` |
| `fill_missing_values()` | `cleaning.py` |
| `bandpass_filter()` | `filtering.py` |
| `moving_average()` | `filtering.py` |
| `resample_to_common_rate()` | `synchronization.py` |
| `cross_correlation()` | `correlation.py` |
| `coherence()` | `correlation.py` |
| `compare_sensors()` | `comparison.py` |
| `compute_rms_over_windows()` | `statistics.py` |
| `compute_vector_magnitude()` | `statistics.py` |

**Hệ quả:** Tăng complexity không cần thiết, gây nhầm lẫn cho người đọc code, khó bảo trì.

**Đề xuất:** Loại bỏ hoặc đánh dấu rõ ràng các hàm utility chưa được tích hợp vào pipeline.

**Giải pháp đã thực hiện:** Các hàm utility không dùng trong pipeline đã được đánh dấu docstring rõ ràng: `"Utility function — not used in the main pipeline. Available for ad-hoc analysis."`. Hàm `coherence()` giờ đã được tích hợp vào pipeline.

### 4.3. Trùng lặp code (code duplication) [ĐÃ KHẮC PHỤC]

**Vấn đề:** Các hàm `_to_utc()`, `_to_g()`, `_estimate_fs()` được viết lại trong cả `window_compare.py` và `full_plan_compare.py` thay vì tái sử dụng.

**Đề xuất:** Tách các hàm tiện ích chung vào module `src/utils/` và import từ đó.

**Giải pháp đã thực hiện:** Đã tạo `src/analysis/_helpers.py` chứa `to_utc`, `to_g`, `estimate_fs`, `load_window_raw`. Cả `window_compare.py` và `full_plan_compare.py` đều import từ `_helpers.py`.

### 4.4. Giá trị hardcode không qua config [ĐÃ KHẮC PHỤC MỘT PHẦN]

**Vấn đề:** Nhiều tham số quan trọng bị hardcode trực tiếp trong source code thay vì đọc từ config:

| Tham số | Giá trị hardcode | Vị trí |
|---------|-------------------|--------|
| Filter cutoffs | 0.5 Hz, 500 Hz | `load_data.py` |
| Filter orders | 2, 4 | `load_data.py` |
| Dải tần phân tích | 0–20 Hz | `full_plan_compare.py` |
| Peak detection threshold | mean + 1×std | `frequency.py` |
| Dominant freq match tolerance | 1.0 Hz | `reports.py` |
| Skip rows sensor A | 5 | `load_data.py` |
| Chunk size | 200,000 rows | `window_compare.py` |

**Đề xuất:** Đưa tất cả tham số này vào `project.yaml` để dễ điều chỉnh và tái lập kết quả.

**Giải pháp đã thực hiện:** Đã đưa vào config: filter cutoffs (`highpass_hz`, `lowpass_hz`), filter orders (`highpass_order`, `lowpass_order`), dải tần phân tích (`freq_band_min_hz`, `freq_band_max_hz`), FFT window (`fft_window`), dominant freq tolerance (`dominant_freq_tolerance_hz`). Các tham số còn lại (skip_rows, chunk_size) vẫn hardcode do ít ảnh hưởng.

### 4.5. Không có error handling trong pipeline chính

**Vấn đề:** `scripts/run.py` không có try/except cho bất kỳ stage nào. Nếu một stage thất bại, toàn bộ pipeline crash mà không có thông báo lỗi hữu ích hoặc partial results.

**Đề xuất:** Thêm error handling với logging cấu trúc, cho phép các stage độc lập tiếp tục chạy khi một stage thất bại.

### 4.6. Rủi ro rò rỉ bộ nhớ (memory leak) matplotlib

**Vấn đề:** Các hàm plot trong `plots.py` tạo matplotlib figure nhưng không đóng (`plt.close(fig)`). Trong pipeline chạy dài hoặc nhiều cửa sổ, số lượng figure tích lũy sẽ tiêu tốn bộ nhớ.

**Đề xuất:** Luôn gọi `plt.close(fig)` sau khi lưu figure.

---

## 5. Hạn chế về Phân tích thống kê

### 5.1. Không có phân tích coherence [ĐÃ KHẮC PHỤC]

**Vấn đề:** Mặc dù hàm `coherence()` đã được viết (sử dụng `scipy.signal.coherence`), nó không được tích hợp vào pipeline. Coherence là chỉ số quan trọng nhất để đánh giá mức độ tương quan tuyến tính theo tần số giữa hai tín hiệu, đặc biệt phù hợp cho bài toán so sánh cảm biến rung.

- Coherence > 0.95 tại một tần số → hai cảm biến nhất quán tại tần số đó
- Coherence < 0.5 → tín hiệu tại tần số đó về cơ bản không tương quan

**Đề xuất:** Tích hợp coherence analysis vào báo cáo, vẽ biểu đồ coherence vs frequency, và sử dụng coherence thresholds từ `methodology.md` (Excellent > 0.95, Good > 0.90, Acceptable > 0.80).

**Giải pháp đã thực hiện:** Coherence analysis đã được tích hợp đầy đủ vào pipeline: tính `scipy.signal.coherence`, vẽ biểu đồ `coherence.png` với đường ngưỡng 0.95/0.80, hiển thị mean/min coherence và đánh giá trong report.

### 5.2. Thiếu confidence interval và uncertainty quantification [ĐÃ KHẮC PHỤC]

**Vấn đề:** Tất cả các chỉ số (Pearson r, RMSE, MAE, etc.) đều được báo cáo dưới dạng giá trị điểm (point estimate) mà không có khoảng tin cậy (confidence interval).

**Đề xuất:**
- Bootstrap confidence interval cho Pearson r, RMSE, MAE
- Fisher z-transformation cho confidence interval của correlation
- Confidence interval cho Bland-Altman limits of agreement (theo Bland & Altman, 1999)

**Giải pháp đã thực hiện:** Đã thêm `compute_bootstrap_ci()` tính 95% CI cho Pearson r, RMSE, MAE (n_bootstrap=1000, seed=42). CI được hiển thị trong report.

### 5.3. Không kiểm tra giả định phân phối chuẩn [ĐÃ KHẮC PHỤC]

**Vấn đề:** Bland-Altman limits of agreement giả định differences có phân phối chuẩn. Pipeline không kiểm tra giả định này.

**Đề xuất:**
- Thêm normality test (Shapiro-Wilk hoặc Anderson-Darling) cho phần Bland-Altman
- Nếu không phân phối chuẩn, sử dụng non-parametric limits of agreement (percentile-based)
- Vẽ histogram/Q-Q plot của differences

**Giải pháp đã thực hiện:** Đã thêm Shapiro-Wilk normality test trong `bland_altman_analysis()`. Kết quả (statistic, p-value, is_normal) được hiển thị trong report. Nếu p <= 0.05, cảnh báo LoA cần thận trọng khi diễn giải.

### 5.4. Chưa phân tích stationarity

**Vấn đề:** Các phương pháp phân tích tần số (FFT, PSD) giả định tín hiệu là stationary. Pipeline không kiểm tra giả định này.

**Đề xuất:**
- Augmented Dickey-Fuller test hoặc KPSS test cho stationarity
- Nếu tín hiệu non-stationary, cân nhắc sử dụng Short-Time Fourier Transform (STFT) hoặc Wavelet analysis
- Phân chia tín hiệu thành các segment và kiểm tra tính nhất quán giữa các segment

### 5.5. R² được tính là Pearson r²

**Vấn đề:** `R² = pearson_r²` chỉ đúng khi so sánh mô hình hồi quy giữa hai biến. Khi so sánh hai phép đo độc lập (sensor comparison), R² nên được tính từ regression line fit, không phải bình phương hệ số tương quan. Khi có systematic bias giữa hai cảm biến, `pearson_r²` sẽ cao hơn R² thực tế từ regression.

**Mức độ ảnh hưởng:** Thấp trong trường hợp hiện tại vì cả hai đều gần 0.

---

## 6. Hạn chế cần nêu trong bài báo (Limitations section)

Khi viết bài báo, phần **Limitations** nên bao gồm các điểm sau (sắp xếp theo mức độ quan trọng):

### Mức độ quan trọng cao (phải nêu)

1. **Vị trí đặt cảm biến không đồng nhất** — Hai cảm biến không được co-locate, nên không thể tách biệt sai lệch do cảm biến và sai lệch do vị trí. Đây là confounding variable chính.

2. **Thiếu hiệu chuẩn tham chiếu** — Không có calibrated reference sensor hoặc known excitation signal để xác nhận độ chính xác tuyệt đối của từng cảm biến.

3. **Cửa sổ phân tích đơn** — Chỉ phân tích 100 giây, chưa đánh giá tính ổn định và reproducibility của kết quả trên nhiều cửa sổ/điều kiện khác nhau.

### Mức độ quan trọng trung bình (nên nêu)

4. ~~**Resampling không có anti-aliasing filter**~~ — [ĐÃ KHẮC PHỤC] Đã thêm lowpass anti-aliasing filter trước resampling.

5. ~~**Chưa phân tích coherence function**~~ — [ĐÃ KHẮC PHỤC] Coherence analysis đã được tích hợp đầy đủ vào pipeline và report.

6. **Chỉ so sánh một trục đo** — Chưa phân tích đầy đủ 3 trục và vector magnitude.

### Mức độ quan trọng thấp (có thể nêu)

7. ~~**FFT không sử dụng window function**~~ — [ĐÃ KHẮC PHỤC] FFT giờ áp dụng Hann window với amplitude correction factor.

8. ~~**Không có uncertainty quantification**~~ — [ĐÃ KHẮC PHỤC] Bootstrap 95% CI cho Pearson r, RMSE, MAE đã được thêm.

---

## 7. Đề xuất cho nghiên cứu tiếp theo (Future Work)

| STT | Đề xuất | Mục đích |
|-----|---------|----------|
| 1 | Thí nghiệm co-location trên bàn rung | Loại bỏ confounding variable vị trí |
| 2 | Calibration với reference accelerometer | Xác nhận sensitivity/gain của từng cảm biến |
| 3 | ~~Tích hợp coherence analysis~~ | [ĐÃ KHẮC PHỤC] |
| 4 | ~~Phân tích nhiều cửa sổ + bootstrap CI~~ | [ĐÃ KHẮC PHỤC] Bootstrap CI đã thêm; nhiều cửa sổ chưa |
| 5 | So sánh đa trục (3-axis + magnitude) | Bức tranh toàn diện hơn |
| 6 | Transfer function estimation (H1/H2) | Xác định frequency response giữa hai vị trí |
| 7 | Time-frequency analysis (STFT/Wavelet) | Phân tích tín hiệu non-stationary |
| 8 | ~~Unit test với synthetic signals~~ | [ĐÃ KHẮC PHỤC] 26 tests |
| 9 | ~~Anti-aliasing filter trước resampling~~ | [ĐÃ KHẮC PHỤC] |
| 10 | ~~Thêm normality test cho Bland-Altman~~ | [ĐÃ KHẮC PHỤC] Shapiro-Wilk |

---

## 8. Tóm tắt đánh giá tổng thể

### Điểm mạnh của project

- Pipeline tự động, tái lập được (reproducible) với config duy nhất
- Sử dụng phương pháp Bland-Altman chuẩn (tham chiếu đúng Bland & Altman, 1986) với ddof=1 và normality test
- Phân tích đa miền: thời gian, tần số, tương quan, sai số, coherence
- FFT áp dụng Hann window với amplitude correction factor
- Anti-aliasing filter trước khi resampling
- Bootstrap 95% CI cho các chỉ số chính (Pearson r, RMSE, MAE)
- FFT/PSD được tính trên tín hiệu gốc (không qua resampling) — best practice
- Bộ chỉ số phong phú (16 time-domain, 5 correlation, 6 error, 5 frequency metrics)
- Report tự động với biểu đồ và nhận định
- 26 unit tests với synthetic signals
- Tham số phân tích cấu hình được qua config (không hardcode)
- Code không trùng lặp (shared helpers module)

### Điểm yếu còn lại

- **Thiết kế thí nghiệm:** Thiếu co-location và calibration — không thể kết luận mạnh về sự nhất quán giữa hai loại cảm biến
- **Phương pháp:** Thiếu stationarity check, chưa phân tích nhiều cửa sổ
- **Phạm vi:** Chỉ so sánh một trục đo, chưa phân tích đa trục

### Kết luận

Project đã xây dựng được một pipeline phân tích có cấu trúc tốt và áp dụng nhiều phương pháp thống kê phù hợp. Tuy nhiên, **hạn chế lớn nhất nằm ở thiết kế thí nghiệm** (không co-locate cảm biến), khiến kết quả tương quan thấp không thể giải thích rõ ràng là do cảm biến hay do vị trí. Để bài báo có sức thuyết phục, cần bổ sung thí nghiệm co-location và calibration, đồng thời tích hợp coherence analysis và uncertainty quantification vào pipeline.

---

*Báo cáo được tạo tự động phục vụ đánh giá nội bộ trước khi viết bài báo khoa học.*
