# Báo cáo So sánh Đầy đủ: Sensor A Channel 3 (g) vs Sensor B accZ(g)

Ngày tạo: 2026-03-02 00:27:03

---

## Thống kê Miền Thời gian

| Chỉ số | Sensor A | Sensor B | Chênh lệch |
|--------|----------|----------|-------------|
| mean | -0.000006 | -0.000027 | 0.000020 |
| std | 0.036617 | 0.051602 | -0.014985 |
| rms | 0.036617 | 0.051602 | -0.014985 |
| peak | 0.182414 | 0.402612 | -0.220197 |
| peak_to_peak | 0.362620 | 0.733550 | -0.370930 |
| crest_factor | 4.981638 | 7.802232 | -2.820594 |

## Phân tích Tương quan

- Pearson r: 0.007457
- R²: 0.000056
- Spearman r: -0.003441

## Chỉ số Sai số

- Pearson r: 0.007457 [95% CI: -0.002972, 0.016835]
- MAE: 0.048712 [95% CI: 0.048364, 0.049059]
- RMSE: 0.063051 [95% CI: 0.062604, 0.063543]
- NRMSE: 0.173876
- Sai số cực đại: 0.388504

## Phân tích Coherence

- Coherence trung bình: 0.0481 (Kém)
- Coherence cực tiểu: 0.0000

## Phân tích Bland-Altman

- Sai khác trung bình: 0.000020
- Độ lệch chuẩn sai khác (ddof=1): 0.063052
- Giới hạn đồng thuận trên (Upper LoA): 0.123599
- Giới hạn đồng thuận dưới (Lower LoA): -0.123558

### Kiểm định Phân phối chuẩn (Shapiro-Wilk)

- Thống kê: 0.995030
- p-value: 0.000000
- Kết quả: Sai khác **không phân phối chuẩn** (p <= 0.05) — LoA cần thận trọng khi diễn giải

## Phân tích Miền Tần số

| Chỉ số | Sensor A | Sensor B |
|--------|----------|----------|
| Tần số trội | 5.50 Hz | 5.69 Hz |
| Trọng tâm phổ | 36.45 Hz | 62.73 Hz |
| Tần số trung vị | 15.72 Hz | 42.35 Hz |

## Biểu đồ

### Chuỗi thời gian — Sensor A, Sensor B, Chồng lớp (trục UTC)

![](../figures/comparison_pair/time_series_3panel.png)

### Miền tần số — FFT A, FFT B, PSD chồng lớp (0–20 Hz)

![](../figures/comparison_pair/freq_3panel_0_20hz.png)

### Chuỗi thời gian — Chồng lớp (đã resample)

![](../figures/comparison_pair/time_series.png)

### So sánh FFT

![](../figures/comparison_pair/fft.png)

### So sánh PSD

![](../figures/comparison_pair/psd.png)

### Biểu đồ tán xạ (Scatter)

![](../figures/comparison_pair/scatter.png)

### Biểu đồ Bland-Altman

![](../figures/comparison_pair/bland_altman.png)

### Phân tích Coherence

![](../figures/comparison_pair/coherence.png)


## Phân tích Dải tần (0–20 Hz)

### Thống kê theo từng sensor

| Chỉ số | Sensor A | Sensor B | Chênh lệch |
|--------|----------|----------|-------------|
| mean (biên độ) | 0.000525 | 0.000778 | -0.000252 |
| std (biên độ) | 0.000863 | 0.000866 | -0.000004 |
| rms (biên độ) | 0.001010 | 0.001164 | -0.000154 |
| peak (biên độ) | 0.010227 | 0.007425 | 0.002802 |
| tần số peak (Hz) | 5.500000 | 5.690000 | -0.190000 |
| năng lượng phổ | 0.002042 | 0.002710 | -0.000668 |

- **Tỷ lệ năng lượng (A/B)**: 0.7534

### Chỉ số So sánh Phổ tần

| Chỉ số | Giá trị |
|--------|---------|
| Pearson r (phổ) | 0.564525 |
| MAE (biên độ) | 0.000508 |
| RMSE (biên độ) | 0.000845 |
| NRMSE (biên độ) | 0.082640 |

## Diễn giải

- **Tương quan (Pearson r = 0.0075)**: Kém
- **NRMSE = 0.1739 (17.4%)**: Kém
- **Tần số trội**: khớp nhau (5.50 Hz vs 5.69 Hz) — xác nhận cùng nguồn rung

**Kết luận**: Cả hai sensor đều bắt được cùng tần số rung trội, nhưng tương quan dạng sóng thấp. Điều này phù hợp với việc hai sensor được đặt tại các vị trí vật lý khác nhau trên kết cấu, nơi biên độ và pha rung khác nhau. Quét độ trễ thời gian (cross-correlation trên toàn bộ dữ liệu) xác nhận không có offset đơn lẻ nào cải thiện đáng kể tương quan (peak r < 0.08 trên tất cả các kênh). Tương quan thấp do đó được quy cho sự khác biệt về vị trí đặt sensor, không phải do lệch timestamp.
