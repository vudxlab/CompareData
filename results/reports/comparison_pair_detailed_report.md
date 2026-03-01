# Báo Cáo Chi Tiết So Sánh Dữ Liệu Cảm Biến Gia Tốc

## 1) Tổng quan

Báo cáo này tổng hợp kết quả so sánh giữa 2 chuỗi dữ liệu gia tốc:

- **Sensor A**: `NI DAQ - Setup5`, kênh `Channel 6 (g)`
- **Sensor B**: `ADXL355`, kênh `accZ(g)`

Dữ liệu được xử lý và so sánh theo cấu hình trong `configs/project.yaml`.

## 2) Cấu hình chạy và phạm vi phân tích

- Cửa sổ thời gian: `2026-02-03T10:00:00Z` -> `+100s`
- Căn chỉnh độ trễ: `enabled=true`, `max_lag_seconds=2.0`
- Resampling: `enabled=true`, `target_fs_hz=500`
- Dải hiển thị FFT/PSD: `0-50 Hz`

## 3) Kết quả tổng hợp (Key Metrics)

Nguồn: `results/tables/comparison_pair_metrics.csv`

| Chỉ số | Giá trị |
|---|---:|
| Số mẫu sau đồng bộ | 49,356 |
| Tần số phân tích | 500.0 Hz |
| Độ trễ căn hàng (lag) | 1.286 s |
| Pearson r | 0.01957 |
| R^2 | 0.00038 |
| MAE | 0.09292 g |
| RMSE | 0.12961 g |
| NRMSE | 0.14545 |

Nhận xét nhanh:
- Tương quan tuyến tính giữa 2 chuỗi rất thấp (`r` gần 0).
- Sai số RMS ở mức ~`0.13 g`.
- Độ trễ căn hàng lớn (`1.286 s`) cho thấy 2 nguồn có sai lệch đồng bộ đáng kể.

## 4) Phân tích miền thời gian

Nguồn: `results/tables/comparison_pair_full_metrics.csv`

| Metric | Sensor A | Sensor B |
|---|---:|---:|
| Mean | -1.45e-05 g | -7.30e-05 g |
| Std | 0.03607 g | 0.12520 g |
| RMS | 0.03607 g | 0.12520 g |
| Peak (abs) | 0.55788 g | 1.18485 g |
| Peak-to-peak | 0.89112 g | 2.22870 g |

Nhận xét:
- Biên độ dao động của Sensor B lớn hơn rõ rệt so với Sensor A.
- Độ lệch chuẩn và peak của Sensor B cao hơn, cho thấy đáp ứng mạnh hơn hoặc nhiều thành phần rung hơn.

## 5) Phân tích miền tần số

Nguồn: `results/tables/comparison_pair_full_metrics.csv`

| Metric | Sensor A | Sensor B |
|---|---:|---:|
| Dominant frequency | 222.61 Hz | 64.18 Hz |
| Spectral centroid | 227.73 Hz | 114.02 Hz |
| Median frequency | 221.51 Hz | 73.33 Hz |

Lưu ý:
- Các giá trị dominant/centroid/median phía trên được tính trên phổ FFT đầy đủ (dữ liệu gốc trong window).
- Hình FFT/PSD bên dưới chỉ hiển thị đến 50 Hz để quan sát chi tiết vùng tần số thấp.

### Peak trong 0-20 Hz

Nguồn: `results/tables/comparison_pair_fft_peaks_0_50hz.csv`

| Sensor | Peak frequency (Hz) |
|---|---:|
| Sensor B | 8.56 |
| Sensor B | 9.49 |
| Sensor B | 16.94 |
| Sensor A | 8.57 |
| Sensor A | 9.45 |
| Sensor A | 16.86 |

### Diễn giải chi tiết kết quả miền tần số (dựa trên 3 peak đầu tiên)

1. **Mức độ trùng khớp tần số**
   - Hai sensor đều xuất hiện cụm peak gần nhau tại:
     - `~8.56-8.57 Hz`
     - `~9.45-9.49 Hz`
     - `~16.86-16.94 Hz`
   - Sai khác tần số giữa hai sensor ở từng cụm rất nhỏ, cho thấy cả hai cùng bắt được các thành phần dao động chính trong dải tần thấp.

2. **Ý nghĩa vật lý của việc trùng peak**
   - Việc trùng peak trong dải `0-20 Hz` cho thấy nguồn kích động có các tần số đặc trưng rõ ràng, và hai hệ đo đều ghi nhận cùng một “chu kỳ rung” chính.
   - Ở góc nhìn miền tần số, hai chuỗi **nhất quán về vị trí tần số ưu thế**.

3. **Vì sao vẫn có Pearson thấp dù tần số trùng**
   - Pearson/Spearman thấp vì các chỉ số này nhạy với:
     - sai lệch biên độ,
     - sai lệch pha theo thời gian,
     - thành phần nhiễu ngoài cụm tần số chính.
   - Do đó có thể xảy ra trường hợp:
     - **vị trí peak giống nhau (miền tần số phù hợp)**,
     - nhưng **dạng sóng theo thời gian không giống nhau hoàn toàn** -> hệ số tương quan tổng thể vẫn thấp.

4. **Đánh giá theo mục tiêu ứng dụng**
   - Nếu mục tiêu là phát hiện tần số đặc trưng trong dải thấp (`0-20 Hz`) thì kết quả hiện tại là tích cực, vì các peak chính giữa hai sensor trùng khớp tốt.
   - Nếu mục tiêu là thay thế trực tiếp giá trị biên độ theo thời gian (time-domain equivalence), cần tiếp tục cải thiện đồng bộ, gain calibration và kiểm soát hướng gắn trục.

## 6) Phân tích tương quan và sai số

Nguồn: `results/tables/comparison_pair_full_metrics.csv`

- Pearson r: `0.01957`
- Spearman r: `0.01948`
- RMSE: `0.12961 g`
- MAE: `0.09292 g`
- Max error: `1.18179 g`

Diễn giải:
- Cả Pearson và Spearman đều thấp -> mối liên hệ đồng biến giữa 2 chuỗi yếu.
- Phân bố sai số có đuôi rộng (Max error cao), phù hợp với quan sát trên biểu đồ Bland-Altman.

## 7) Hình ảnh và biểu đồ

### 7.1 Time Series

![Time Series](../figures/comparison_pair/time_series.png)

### 7.2 FFT (0-50 Hz, auto y-scale)

![FFT](../figures/comparison_pair/fft.png)

### 7.3 PSD (0-50 Hz)

![PSD](../figures/comparison_pair/psd.png)

### 7.4 Scatter Plot

![Scatter](../figures/comparison_pair/scatter.png)

**Nhận xét chi tiết ảnh 7.4 (Scatter):**
- Các điểm phân bố khá rộng, không tạo thành dải hẹp bám sát đường đồng nhất `y=x`.
- Mật độ điểm tập trung quanh vùng biên độ nhỏ, nhưng khi biên độ tăng thì độ phân tán theo trục dọc tăng rõ, cho thấy sai khác biên độ giữa hai sensor lớn hơn ở các đoạn dao động mạnh.
- Có hiện tượng “kéo giãn” theo trục Sensor B, phù hợp với quan sát rằng Sensor B có biên độ/độ lệch chuẩn cao hơn.
- Tổng thể, scatter xác nhận mức tương quan tuyến tính thấp của cặp dữ liệu trong cửa sổ phân tích.

### 7.5 Bland-Altman

![Bland Altman](../figures/comparison_pair/bland_altman.png)

**Nhận xét chi tiết ảnh 7.5 (Bland-Altman):**
- Đám mây sai khác phân bố quanh đường bias trung bình nhưng có độ rộng lớn, phản ánh mức độ không đồng thuận đáng kể giữa hai phương pháp đo.
- Nhiều điểm nằm xa đường trung bình sai khác, cho thấy sai số tức thời không ổn định theo thời gian.
- Khi giá trị trung bình của hai phép đo tăng, độ phân tán sai khác vẫn còn đáng kể; điều này hàm ý giới hạn đồng thuận (LoA) rộng.
- Về thực tế ứng dụng, hai sensor có thể cùng nhận biết thành phần tần số chính, nhưng chưa đủ điều kiện để thay thế trực tiếp nhau khi cần độ chính xác biên độ cao ở miền thời gian.

## 8) Kết luận kỹ thuật

1. Trong cửa sổ 100s được chọn, 2 chuỗi dữ liệu (`Channel 6 (g)` vs `accZ(g)`) có mức tương quan thấp.
2. Sensor B cho thấy biên độ dao động và năng lượng tín hiệu cao hơn Sensor A.
3. Độ trễ căn hàng đáng kể (`~1.286 s`) ảnh hưởng đến mức độ tương đồng theo thời gian.
4. Nếu mục tiêu là đối chiếu đáp ứng rung cùng trục, cần:
   - xác nhận lại mapping trục/hướng gắn sensor,
   - xác nhận mốc đồng bộ thời gian (trigger chung),
   - xem xét lọc bổ sung theo dải tần mục tiêu trước khi so sánh.

## 9) Tài liệu đầu vào kết quả

- `results/tables/comparison_pair_metrics.csv`
- `results/tables/comparison_pair_full_metrics.csv`
- `results/tables/comparison_pair_full_metrics_summary.csv`
- `results/tables/comparison_pair_fft_peaks_0_50hz.csv`
- `results/tables/comparison_pair_aligned.csv`
- `results/figures/comparison_pair/*.png`
