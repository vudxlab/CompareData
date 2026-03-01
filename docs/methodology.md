# Phuong phap so sanh cam bien gia toc

## 1. Muc tieu

So sanh do tuong dong va sai khac giua hai chuoi gia toc do boi hai he cam bien khac nhau.

## 2. Thiet lap thi nghiem

### 2.1 Cam bien

- **Sensor A**: NI DAQ Setup5
  - Cac kenh: `Channel 1 (g)`, `Channel 2 (g)`, `Channel 3 (g)`
  - Don vi goc: `g` (du lieu moi) hoac `m/s^2` (du lieu cu, can `convert_to_g: true`)
  - Tan so lay mau: 1651 Hz (co the khac tuy file)
  - Dinh dang timestamp: Unix epoch theo dong ho UTC chuan (`timezone_offset_hours: 0`)

- **Sensor B**: ADXL355
  - Cac kenh: `accX(g)`, `accY(g)`, `accZ(g)`
  - Don vi: `g`
  - Tan so lay mau: ~1651 Hz
  - Dinh dang timestamp: Unix epoch theo dong ho UTC+7 (can `timezone_offset_hours: -7` de chinh ve UTC)

### 2.2 Cau hinh so sanh hien tai

- Chuoi A: `Channel 3 (g)` (sensor A)
- Chuoi B: `accZ(g)` (sensor B)
- Cua so thoi gian: 100 giay bat dau `2026-02-28T02:23:30Z` (UTC)
- Tan so resample muc tieu: `500 Hz`
- Canh hang theo thoi gian: **khong dung cross-correlation** — hai sensor da co timestamp UTC tuyet doi, cat dung window theo UTC roi so sanh truc tiep

## 3. Quy trinh xu ly du lieu

### 3.1 Tien xu ly

1. Doc du lieu raw theo dinh dang rieng tung sensor
2. Chuyen doi ve timestamp UTC
   - Sensor A: epoch UTC chuan, `timezone_offset_hours: 0`
   - Sensor B: epoch theo dong ho UTC+7, can `timezone_offset_hours: -7` (tru 7h de ra UTC that)
3. Loai bo DC offset (mean subtraction)
4. Loc high-pass (0.5 Hz) va low-pass (500 Hz)
5. Luu vao `data/processed/`

### 3.2 Chuan hoa truoc so sanh

1. Cat du lieu theo cua so UTC da khai bao (diem bat dau gan nhat trong file)
2. Resample ve tan so chung (`target_fs_hz`)
3. So sanh truc tiep theo timestamp UTC — khong dung cross-correlation alignment
4. Tinh toan metrics

## 4. Tap chi so bao cao

### 4.1 Mien thoi gian

- Mean, Std, RMS, Peak, Peak-to-peak, Crest factor

### 4.2 Mien tan so

- FFT
- PSD
- Dominant frequency
- Spectral centroid
- Median frequency
- FFT peaks (top N trong dai 0–50 Hz)

### 4.3 So sanh truc tiep

- Pearson r, Spearman r, R²
- RMSE, MAE, NRMSE, Max error
- Bland-Altman plot

## 5. Dau ra

- Bang tong hop: `results/tables/*metrics*.csv`
- FFT peaks: `results/tables/*fft_peaks*.csv`
- Du lieu da canh hang: `results/tables/*aligned*.csv`
- Hinh phan tich: `results/figures/.../*.png`
- Bao cao markdown: `results/reports/..._report.md`

## 6. Tieu chi danh gia tham khao

| Metric | Excellent | Good | Acceptable | Poor |
|--------|-----------|------|------------|------|
| Pearson r | > 0.99 | > 0.95 | > 0.90 | < 0.90 |
| NRMSE | < 1% | < 5% | < 10% | > 10% |
| Coherence | > 0.95 | > 0.90 | > 0.80 | < 0.80 |

## 7. Tai lieu tham khao

1. Bland, J.M. & Altman, D.G. (1986). Statistical methods for assessing agreement between two methods of clinical measurement.
2. ISO 16063 - Methods for the calibration of vibration and shock transducers
