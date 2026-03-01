# Báo Cáo Chi Tiết So Sánh Dữ Liệu Cảm Biến Gia Tốc

## 1) Tổng quan

Báo cáo này tổng hợp kết quả so sánh giữa 2 chuỗi dữ liệu gia tốc:

- **Sensor A**: `NI DAQ - Setup5`, kênh `Channel 3 (g)`
- **Sensor B**: `ADXL355`, kênh `accZ(g)`

Dữ liệu được xử lý và so sánh theo cấu hình trong `configs/project.yaml`.

## 2) Cấu hình chạy và phạm vi phân tích

- Cửa sổ thời gian: `2026-02-28T02:23:30Z` -> `+100s` (đến `02:25:10Z`)
- Căn chỉnh độ trễ: tắt (dùng timestamp UTC tuyệt đối trực tiếp)
- Resampling: `target_fs_hz=500` (có anti-aliasing filter trước downsample)
- Anti-aliasing: lowpass Butterworth order 8 tại 225 Hz trước nội suy
- FFT window: Hann (với amplitude correction factor)
- Dải phân tích tần số: `0–20 Hz` (cấu hình qua config)
- Dải hiển thị FFT/PSD: `0–50 Hz`

## 3) Kết quả tổng hợp (Key Metrics)

Nguồn: `results/tables/comparison_pair_metrics.csv`

| Chỉ số | Giá trị |
|--------|--------:|
| Số mẫu sau đồng bộ | 49,999 |
| Tần số phân tích | 500.0 Hz |
| Độ trễ căn hàng (lag) | 0.0 s |
| Pearson r | 0.00746 |
| R² | 0.00006 |
| MAE | 0.04871 g |
| RMSE | 0.06305 g |
| NRMSE | 0.17388 |

Nhận xét nhanh:
- Tương quan tuyến tính giữa 2 chuỗi rất thấp (`r` gần 0).
- Sai số RMS ở mức ~`0.063 g`.
- Không áp dụng căn hàng theo lag — hai sensor đã có timestamp UTC tuyệt đối.

## 4) Phân tích miền thời gian

Nguồn: `results/tables/comparison_pair_full_metrics.csv`

| Chỉ số | Sensor A | Sensor B |
|--------|----------|----------|
| Mean | -6.42e-06 g | -2.69e-05 g |
| Std | 0.03662 g | 0.05160 g |
| RMS | 0.03662 g | 0.05160 g |
| Peak (abs) | 0.18241 g | 0.40261 g |
| Peak-to-peak | 0.36262 g | 0.73355 g |
| Crest factor | 4.98 | 7.80 |
| Kurtosis | 0.68 | 2.24 |
| Skewness | -0.05 | 0.16 |

Nhận xét:
- Biên độ dao động của Sensor B lớn hơn rõ rệt so với Sensor A (peak gấp ~2.2 lần).
- Độ lệch chuẩn Sensor B cao hơn ~41%, cho thấy đáp ứng mạnh hơn hoặc vị trí đặt nhận rung nhiều hơn.
- Kurtosis của Sensor B cao hơn (2.24 vs 0.68), cho thấy phân phối có đuôi nặng hơn.

## 5) Phân tích miền tần số

Nguồn: `results/tables/comparison_pair_full_metrics.csv`

| Chỉ số | Sensor A | Sensor B |
|--------|----------|----------|
| Tần số trội | 5.50 Hz | 5.69 Hz |
| Trọng tâm phổ | 36.45 Hz | 62.73 Hz |
| Tần số trung vị | 15.72 Hz | 42.35 Hz |

Lưu ý:
- FFT được tính với Hann window và amplitude correction factor (`acf = N / sum(win)`).
- Trọng tâm phổ và tần số trung vị của Sensor B cao hơn đáng kể, cho thấy Sensor B có nhiều năng lượng ở dải tần cao hơn.

### Peak trong dải 0–50 Hz

Nguồn: `results/tables/comparison_pair_fft_peaks_0_50hz.csv`

| Sensor | Tần số peak (Hz) | Biên độ |
|--------|------------------:|--------:|
| Sensor A | 5.50 | 0.01023 |
| Sensor A | 5.42 | 0.00777 |
| Sensor A | 11.64 | 0.00750 |
| Sensor A | 14.41 | 0.00719 |
| Sensor A | 11.68 | 0.00669 |
| Sensor B | 5.69 | 0.00743 |
| Sensor B | 5.49 | 0.00716 |
| Sensor B | 14.70 | 0.00710 |
| Sensor B | 11.72 | 0.00613 |
| Sensor B | 14.68 | 0.00565 |

### Diễn giải chi tiết kết quả miền tần số

1. **Mức độ trùng khớp tần số**
   - Hai sensor đều xuất hiện cụm peak gần nhau tại:
     - `~5.5 Hz` (tần số trội chính — chênh 0.19 Hz)
     - `~11.6–11.7 Hz` (bội hài bậc 2)
     - `~14.4–14.7 Hz`
   - Sai khác tần số giữa hai sensor ở từng cụm rất nhỏ (< 0.3 Hz), cho thấy cả hai cùng bắt được các thành phần dao động chính.

2. **Ý nghĩa vật lý của việc trùng peak**
   - Việc trùng peak trong dải `0–20 Hz` cho thấy nguồn kích động có các tần số đặc trưng rõ ràng, và hai hệ đo đều ghi nhận cùng một "chu kỳ rung" chính.
   - Ở góc nhìn miền tần số, hai chuỗi **nhất quán về vị trí tần số ưu thế**.

3. **Vì sao vẫn có Pearson thấp dù tần số trùng**
   - Pearson/Spearman thấp vì các chỉ số này nhạy với:
     - sai lệch biên độ (Sensor B peak-to-peak gấp 2× Sensor A),
     - sai lệch pha theo thời gian (do vị trí đặt khác nhau),
     - thành phần nhiễu ngoài cụm tần số chính.
   - Do đó có thể xảy ra trường hợp:
     - **vị trí peak giống nhau (miền tần số phù hợp)**,
     - nhưng **dạng sóng theo thời gian không giống nhau hoàn toàn** -> hệ số tương quan tổng thể vẫn thấp.

4. **Đánh giá theo mục tiêu ứng dụng**
   - Nếu mục tiêu là phát hiện tần số đặc trưng trong dải thấp (`0–20 Hz`) thì kết quả hiện tại là tích cực, vì các peak chính giữa hai sensor trùng khớp tốt.
   - Nếu mục tiêu là thay thế trực tiếp giá trị biên độ theo thời gian (time-domain equivalence), cần tiếp tục cải thiện gain calibration và kiểm soát hướng gắn trục.

## 6) Phân tích dải tần 0–20 Hz

Nguồn: `results/tables/comparison_pair_full_metrics.csv` (mục `freq_band_metrics`)

### Thống kê theo từng sensor

| Chỉ số | Sensor A | Sensor B | Chênh lệch |
|--------|----------|----------|-------------|
| Mean (biên độ) | 0.000525 | 0.000778 | -0.000252 |
| Std (biên độ) | 0.000863 | 0.000866 | -0.000004 |
| RMS (biên độ) | 0.001010 | 0.001164 | -0.000154 |
| Peak (biên độ) | 0.010227 | 0.007425 | 0.002802 |
| Tần số peak (Hz) | 5.50 | 5.69 | -0.19 |
| Năng lượng phổ | 0.002042 | 0.002710 | -0.000668 |

- **Tỷ lệ năng lượng (A/B)**: 0.7534 — Sensor B có năng lượng cao hơn ~33% trong dải 0–20 Hz.

### Chỉ số so sánh phổ tần

| Chỉ số | Giá trị |
|--------|---------|
| Pearson r (phổ) | 0.5645 |
| MAE (biên độ) | 0.000508 |
| RMSE (biên độ) | 0.000845 |
| NRMSE (biên độ) | 8.26% |

Nhận xét:
- Tương quan phổ trong dải 0–20 Hz đạt `r = 0.56`, cao hơn đáng kể so với tương quan miền thời gian (`r = 0.007`).
- NRMSE phổ chỉ 8.26%, cho thấy hình dạng phổ tần hai sensor khá tương đồng trong dải thấp.

## 7) Phân tích tương quan và sai số

Nguồn: `results/tables/comparison_pair_full_metrics.csv`

- Pearson r: `0.00746` [95% CI: -0.00297, 0.01684]
- Spearman r: `-0.00344`
- R²: `0.00006`
- RMSE: `0.06305 g` [95% CI: 0.06260, 0.06354]
- MAE: `0.04871 g` [95% CI: 0.04836, 0.04906]
- NRMSE: `0.17388` (17.4%)
- Sai số cực đại: `0.38850 g`

Diễn giải:
- Cả Pearson và Spearman đều gần 0 -> mối liên hệ tuyến tính giữa 2 chuỗi yếu.
- 95% CI cho Pearson r chứa 0, xác nhận tương quan không có ý nghĩa thống kê.
- NRMSE 17.4% thuộc mức "Kém" (ngưỡng chấp nhận < 10%).
- Phân bố sai số có đuôi rộng (sai số cực đại 0.39 g so với RMSE 0.063 g).

## 8) Phân tích Coherence

Nguồn: `results/tables/comparison_pair_full_metrics.csv`

- Coherence trung bình: `0.0481` (Kém)
- Coherence cực tiểu: `0.0000`

Diễn giải:
- Coherence trung bình rất thấp (< 0.80), xếp hạng "Kém" theo tiêu chí đánh giá.
- Điều này cho thấy hai tín hiệu không có mối liên hệ tuyến tính nhất quán tại bất kỳ tần số nào.
- Kết quả phù hợp với việc hai sensor đặt tại vị trí khác nhau trên kết cấu.

## 9) Phân tích Bland-Altman

Nguồn: `results/tables/comparison_pair_full_metrics.csv`

- Sai khác trung bình (bias): `0.000020 g`
- Độ lệch chuẩn sai khác (ddof=1): `0.063052 g`
- Giới hạn đồng thuận trên (Upper LoA): `+0.123599 g`
- Giới hạn đồng thuận dưới (Lower LoA): `-0.123558 g`

### Kiểm định phân phối chuẩn (Shapiro-Wilk)

- p-value: `0.000000`
- Kết quả: Sai khác **không phân phối chuẩn** (p <= 0.05) — LoA cần thận trọng khi diễn giải.

Diễn giải:
- Bias gần 0 cho thấy không có sai lệch hệ thống đáng kể giữa hai sensor.
- LoA rộng (±0.124 g) phản ánh mức độ không đồng thuận đáng kể.
- Phân phối sai khác không chuẩn, nên giới hạn đồng thuận dựa trên mean ± 1.96×std chỉ mang tính tham khảo.

## 10) Hình ảnh và biểu đồ

### 10.1 Chuỗi thời gian — 3 panel (Sensor A, Sensor B, chồng lớp)

![Chuỗi thời gian 3 panel](../figures/comparison_pair/time_series_3panel.png)

### 10.2 Miền tần số — 3 panel (FFT A, FFT B, PSD chồng lớp, 0–20 Hz)

![Miền tần số 3 panel](../figures/comparison_pair/freq_3panel_0_20hz.png)

### 10.3 Chuỗi thời gian — chồng lớp (đã resample)

![Chuỗi thời gian](../figures/comparison_pair/time_series.png)

### 10.4 So sánh FFT (0–50 Hz)

![FFT](../figures/comparison_pair/fft.png)

### 10.5 So sánh PSD (0–50 Hz)

![PSD](../figures/comparison_pair/psd.png)

### 10.6 Biểu đồ tán xạ (Scatter)

![Tán xạ](../figures/comparison_pair/scatter.png)

**Nhận xét chi tiết:**
- Các điểm phân bố khá rộng, không tạo thành dải hẹp bám sát đường đồng nhất `y=x`.
- Mật độ điểm tập trung quanh vùng biên độ nhỏ, nhưng khi biên độ tăng thì độ phân tán tăng rõ.
- Có hiện tượng "kéo giãn" theo trục Sensor B, phù hợp với quan sát Sensor B có biên độ/độ lệch chuẩn cao hơn.
- Tổng thể, scatter xác nhận mức tương quan tuyến tính thấp trong cửa sổ phân tích.

### 10.7 Biểu đồ Bland-Altman

![Bland-Altman](../figures/comparison_pair/bland_altman.png)

**Nhận xét chi tiết:**
- Đám mây sai khác phân bố quanh đường bias trung bình nhưng có độ rộng lớn.
- Nhiều điểm nằm xa đường trung bình sai khác, cho thấy sai số tức thời không ổn định.
- Giới hạn đồng thuận (LoA) rộng (±0.124 g), phản ánh mức độ không đồng thuận đáng kể.
- Hai sensor có thể cùng nhận biết thành phần tần số chính, nhưng chưa đủ điều kiện để thay thế trực tiếp nhau khi cần độ chính xác biên độ cao ở miền thời gian.

### 10.8 Phân tích Coherence

![Coherence](../figures/comparison_pair/coherence.png)

## 11) Kết luận kỹ thuật

1. Trong cửa sổ 100s được chọn, 2 chuỗi dữ liệu (`Channel 3 (g)` vs `accZ(g)`) có mức tương quan miền thời gian rất thấp (Pearson r = 0.007, không có ý nghĩa thống kê).
2. Sensor B cho thấy biên độ dao động cao hơn Sensor A (peak gấp ~2.2 lần, std gấp ~1.4 lần).
3. Cả hai sensor đều bắt được cùng tần số trội chính (~5.5 Hz), xác nhận cùng nguồn rung.
4. Tương quan phổ trong dải 0–20 Hz (r = 0.56) cao hơn đáng kể so với tương quan miền thời gian, cho thấy hình dạng phổ tương đồng nhưng dạng sóng khác biệt.
5. Coherence trung bình rất thấp (0.048), cho thấy không có mối liên hệ tuyến tính nhất quán theo tần số.
6. Bland-Altman: bias gần 0 nhưng LoA rộng (±0.124 g); sai khác không phân phối chuẩn.
7. Kết quả phù hợp với giả thuyết hai sensor đặt tại vị trí khác nhau trên kết cấu (mode shape effect, phase shift do truyền sóng).

### Khuyến nghị

Nếu mục tiêu là đối chiếu đáp ứng rung cùng trục:
- Thực hiện thí nghiệm co-location (đặt hai sensor cùng vị trí)
- Hiệu chuẩn (calibration) với tín hiệu tham chiếu đã biết
- Xác nhận lại mapping trục/hướng gắn sensor
- So sánh đa trục (3-axis + vector magnitude)

## 12) Tài liệu đầu vào kết quả

- `results/tables/comparison_pair_metrics.csv`
- `results/tables/comparison_pair_full_metrics.csv`
- `results/tables/comparison_pair_full_metrics_summary.csv`
- `results/tables/comparison_pair_fft_peaks_0_50hz.csv`
- `results/tables/comparison_pair_aligned.csv`
- `results/figures/comparison_pair/*.png`
