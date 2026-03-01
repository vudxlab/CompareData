# Phuong phap so sanh cam bien gia toc

## 1. Muc tieu

So sanh do tuong dong va sai khac giua hai chuoi gia toc do boi hai he cam bien khac nhau.

## 2. Thiet lap thi nghiem

### 2.1 Cam bien

- **Sensor A**: NI DAQ Setup5 (`Channel 1..8`, don vi `m/s^2`)
- **Sensor B**: ADXL355 (`accX/accY/accZ`, don vi `g`)

### 2.2 Cau hinh so sanh hien tai

- Chuoi A: `channel6(m/s^2)` -> quy doi sang `g`
- Chuoi B: `accZ(g)`
- Cua so thoi gian: 100 giay tu `10:00:00 UTC`
- Tan so phan tich muc tieu: `100 Hz` (resample)
- Canh hang: cross-correlation, `max_lag_seconds = 2.0`

## 3. Quy trinh xu ly du lieu

### 3.1 Tien xu ly
1. Doc du lieu raw theo dinh dang rieng tung sensor
2. Chuyen doi ve timestamp UTC
3. Loai bo DC offset
4. Loc high-pass va low-pass
5. Luu vao `data/processed`

### 3.2 Chuan hoa truoc so sanh
1. Cat du lieu theo cua so UTC
2. Quy doi don vi ve `g`
3. Resample ve tan so chung (100 Hz)
4. Canh hang theo do tre toi uu

## 4. Tap chi so bao cao

### 4.1 Mien thoi gian
- Mean, Std, RMS, Peak, Peak-to-peak, Crest factor

### 4.2 Mien tan so
- FFT
- PSD
- Dominant frequency
- Spectral centroid
- Median frequency

### 4.3 So sanh truc tiep
- Pearson/Spearman
- RMSE, MAE, NRMSE, Max error
- Bland-Altman

## 5. Dau ra

- Bang tong hop: `results/tables/*metrics*.csv`
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
