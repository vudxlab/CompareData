# Full Comparison Report: Sensor A Channel 3 (g) vs Sensor B accZ(g)

Ngày tạo: 2026-03-02 08:59:35

---

## 1. Thống kê miền thời gian

| Chỉ số | Sensor A | Sensor B | Chênh lệch |
|--------|----------|----------|------------|
| Trung bình (Mean) | -0.000006 | -0.000027 | 0.000020 |
| Độ lệch chuẩn (Std) | 0.036617 | 0.051602 | -0.014985 |
| Giá trị hiệu dụng (RMS) | 0.036617 | 0.051602 | -0.014985 |
| Đỉnh tuyệt đối (Peak) | 0.182414 | 0.402612 | -0.220197 |
| Biên độ đỉnh-đỉnh (Peak-to-peak) | 0.362620 | 0.733550 | -0.370930 |
| Hệ số đỉnh (Crest factor) | 4.981638 | 7.802232 | -2.820594 |

**Nhận xét miền thời gian:**

- Độ lệch chuẩn Sensor B cao hơn Sensor A khoảng 41% (0.0516 g so với 0.0366 g), cho thấy Sensor B ghi nhận rung động mạnh hơn.
- Giá trị đỉnh (peak) của Sensor B gấp 2.2 lần Sensor A (0.4026 g so với 0.1824 g).
- Biên độ đỉnh-đỉnh (peak-to-peak) của Sensor B gấp 2.0 lần Sensor A (0.7336 g so với 0.3626 g).
- Sự chênh lệch biên độ có thể do vị trí đặt cảm biến khác nhau trên kết cấu (mode shape effect) hoặc do đặc tính đáp ứng khác nhau giữa hai loại cảm biến.

## 2. Phân tích tương quan

| Chỉ số | Giá trị | Đánh giá |
|--------|---------|----------|
| Pearson r | 0.007457 | Kém |
| R² | 0.000056 | — |
| Spearman r | -0.003441 | Kém |

**Nhận xét tương quan:**

- Pearson r = 0.0075, gần bằng 0: **không có tương quan tuyến tính** đáng kể giữa hai chuỗi tín hiệu trong miền thời gian.
- R² = 0.000056: Sensor A chỉ giải thích được 0.0056% phương sai của Sensor B — gần như bằng 0.
- Spearman r = -0.0034: tương quan thứ bậc cũng rất thấp, loại trừ khả năng có mối quan hệ đơn điệu phi tuyến.

## 3. Chỉ số sai số và khoảng tin cậy

| Chỉ số | Giá trị | 95% CI | Đánh giá |
|--------|---------|--------|----------|
| Pearson r | 0.007457 | [-0.002972, 0.016835] | Kém |
| MAE | 0.048712 g | [0.048364, 0.049059] | — |
| RMSE | 0.063051 g | [0.062604, 0.063543] | — |
| NRMSE | 0.173876 (17.4%) | — | Kém |
| Sai số cực đại | 0.388504 g | — | — |

**Nhận xét sai số:**

- Khoảng tin cậy 95% của Pearson r [-0.002972, 0.016835] **chứa giá trị 0**, xác nhận tương quan không có ý nghĩa thống kê.
- NRMSE = 17.4% thuộc mức **Kém** (ngưỡng chấp nhận < 10%).
- Sai số cực đại (0.3885 g) gấp 6.2 lần RMSE (0.0631 g), cho thấy phân bố sai số có đuôi nặng (heavy tail).

## 4. Phân tích Coherence

| Chỉ số | Giá trị | Đánh giá |
|--------|---------|----------|
| Coherence trung bình | 0.0481 | Kém |
| Coherence cực tiểu | 0.0000 | — |

**Nhận xét coherence:**

- Coherence trung bình = 0.0481 < 0.80: xếp hạng **Kém**.
- Hai tín hiệu không có mối liên hệ tuyến tính nhất quán tại bất kỳ dải tần nào.
- Kết quả này phù hợp với giả thuyết hai cảm biến đặt tại vị trí khác nhau trên kết cấu, dẫn đến đáp ứng rung khác biệt cả về biên độ lẫn pha.

## 5. Phân tích Bland-Altman

| Chỉ số | Giá trị |
|--------|---------|
| Sai khác trung bình (bias) | 0.000020 g |
| Độ lệch chuẩn sai khác (ddof=1) | 0.063052 g |
| Giới hạn đồng thuận trên (Upper LoA) | +0.123599 g |
| Giới hạn đồng thuận dưới (Lower LoA) | -0.123558 g |

### Kiểm định phân phối chuẩn (Shapiro-Wilk)

- Thống kê kiểm định: 0.995030
- Giá trị p: 0.000000
- Kết quả: Sai khác **không phân phối chuẩn** (p <= 0.05) — giới hạn đồng thuận (LoA) cần thận trọng khi diễn giải.

**Nhận xét Bland-Altman:**

- Bias gần bằng 0 (0.000020 g): **không có sai lệch hệ thống** đáng kể giữa hai cảm biến.
- Giới hạn đồng thuận rộng (±0.1236 g), phản ánh mức độ không đồng thuận đáng kể giữa hai phép đo.
- Hai cảm biến có thể nhận biết cùng thành phần tần số chính, nhưng **chưa đủ điều kiện để thay thế trực tiếp nhau** khi yêu cầu độ chính xác biên độ cao ở miền thời gian.

## 6. Phân tích miền tần số

| Chỉ số | Sensor A | Sensor B | Chênh lệch |
|--------|----------|----------|------------|
| Tần số trội | 5.50 Hz | 5.69 Hz | -0.19 Hz |
| Trọng tâm phổ | 36.45 Hz | 62.73 Hz | -26.28 Hz |
| Tần số trung vị | 15.72 Hz | 42.35 Hz | -26.63 Hz |

**Nhận xét miền tần số:**

- Tần số trội: **khớp nhau** (5.50 Hz so với 5.69 Hz, chênh lệch 0.19 Hz < ngưỡng 1.0 Hz). Cả hai cảm biến cùng bắt được nguồn rung chính.
- Trọng tâm phổ của Sensor B (62.73 Hz) cao hơn đáng kể so với Sensor A (36.45 Hz), cho thấy Sensor B chứa nhiều năng lượng ở dải tần cao hơn.
- FFT được tính với cửa sổ Hann và hệ số bù biên độ (amplitude correction factor).

## 7. Hình ảnh và biểu đồ

### Chuỗi thời gian — Sensor A, Sensor B, chồng lớp (trục UTC)

![](../figures/comparison_pair/time_series_3panel.png)

### Miền tần số — FFT A, FFT B, PSD chồng lớp (0–20 Hz)

![](../figures/comparison_pair/freq_3panel_0_20hz.png)

### Chuỗi thời gian — chồng lớp (đã resample)

![](../figures/comparison_pair/time_series.png)

### So sánh FFT (0–50 Hz)

![](../figures/comparison_pair/fft.png)

### So sánh PSD (0–50 Hz)

![](../figures/comparison_pair/psd.png)

### Biểu đồ tán xạ (Scatter)

![](../figures/comparison_pair/scatter.png)

### Biểu đồ Bland-Altman

![](../figures/comparison_pair/bland_altman.png)

### Phân tích Coherence

![](../figures/comparison_pair/coherence.png)


## 8. Phân tích dải tần 0–20 Hz

### Thống kê theo từng cảm biến

| Chỉ số | Sensor A | Sensor B | Chênh lệch |
|--------|----------|----------|------------|
| Trung bình biên độ | 0.000525 | 0.000778 | -0.000252 |
| Độ lệch chuẩn biên độ | 0.000863 | 0.000866 | -0.000004 |
| RMS biên độ | 0.001010 | 0.001164 | -0.000154 |
| Đỉnh biên độ | 0.010227 | 0.007425 | 0.002802 |
| Tần số đỉnh (Hz) | 5.500000 | 5.690000 | -0.190000 |
| Năng lượng phổ | 0.002042 | 0.002710 | -0.000668 |

- **Tỷ lệ năng lượng (A/B)**: 0.7534
  - Sensor B có năng lượng cao hơn ~33% trong dải 0–20 Hz.

### Chỉ số so sánh phổ tần

| Chỉ số | Giá trị |
|--------|---------|
| Pearson r (phổ) | 0.564525 |
| MAE (biên độ) | 0.000508 |
| RMSE (biên độ) | 0.000845 |
| NRMSE (biên độ) | 0.082640 (8.26%) |

**Nhận xét dải tần 0–20 Hz:**

- Tương quan phổ trong dải 0–20 Hz đạt r = 0.56, **cao hơn đáng kể** so với tương quan miền thời gian (r = 0.0075).
- Điều này cho thấy hình dạng phổ tần hai cảm biến tương đồng trong dải thấp, mặc dù dạng sóng theo thời gian khác biệt.

## 9. Tổng hợp và kết luận

### Bảng tổng hợp đánh giá

| Tiêu chí | Giá trị | Xếp hạng | Ngưỡng tham khảo |
|----------|---------|----------|------------------|
| Tương quan (Pearson r) | 0.0075 | Kém | Xuất sắc > 0.99, Tốt > 0.95, Chấp nhận > 0.90 |
| Sai số chuẩn hóa (NRMSE) | 17.4% | Kém | Xuất sắc < 1%, Tốt < 5%, Chấp nhận < 10% |
| Coherence trung bình | 0.0481 | Kém | Xuất sắc > 0.95, Tốt > 0.90, Chấp nhận > 0.80 |
| Tần số trội | 5.50 vs 5.69 Hz | Khớp | Chênh lệch < 1.0 Hz |

### Kết luận kỹ thuật

1. Tương quan miền thời gian rất thấp (Pearson r = 0.0075), không có ý nghĩa thống kê.
2. Sensor B cho thấy biên độ dao động cao hơn Sensor A (peak gấp ~2.2 lần, std gấp ~1.4 lần).
3. Cả hai cảm biến đều bắt được cùng tần số trội chính (~5.6 Hz), xác nhận cùng nguồn rung.
4. Tương quan phổ trong dải 0–20 Hz (r = 0.56) cao hơn đáng kể so với tương quan miền thời gian, cho thấy hình dạng phổ tương đồng nhưng dạng sóng khác biệt.
5. Coherence trung bình rất thấp (0.0481), cho thấy không có mối liên hệ tuyến tính nhất quán theo tần số giữa hai cảm biến.
6. Bland-Altman: bias gần 0 (0.000020 g) nhưng giới hạn đồng thuận rộng (±0.1236 g).

**Kết luận tổng thể:** Mức đồng thuận trung bình. Cần kiểm tra thêm vị trí đặt cảm biến và canh hàng thời gian.

### Khuyến nghị

Nếu mục tiêu là đối chiếu đáp ứng rung cùng trục:

1. Thực hiện thí nghiệm co-location (đặt hai cảm biến cùng vị trí trên kết cấu)
2. Hiệu chuẩn (calibration) với tín hiệu tham chiếu đã biết
3. Xác nhận lại mapping trục/hướng gắn cảm biến
4. So sánh đa trục (3 trục + vector magnitude)
5. Phân tích nhiều cửa sổ thời gian với các điều kiện kích thích khác nhau