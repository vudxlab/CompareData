# Báo Cáo So Sánh Thông Số Kỹ Thuật Cảm Biến

## PCB Piezotronics 353B34 vs Analog Devices ADXL355

**Ngày:** 2026-03-02
**Mục đích:** So sánh datasheet hai loại cảm biến gia tốc sử dụng trong dự án

---

## 1. Tổng quan

| Tiêu chí | PCB 353B34 | ADXL355 |
|----------|------------|---------|
| **Nhà sản xuất** | PCB Piezotronics (USA) | Analog Devices (USA) |
| **Loại cảm biến** | Piezoelectric (ICP/IEPE) | MEMS (Micro-Electro-Mechanical) |
| **Cấu trúc cảm biến** | Ceramic Shear | Silicon MEMS hermetically sealed |
| **Số trục đo** | 1 trục (uniaxial) | 3 trục (triaxial: X, Y, Z) |
| **Ngõ ra** | Analog (ICP/IEPE) | Digital (SPI / I2C) |
| **Phân khúc** | Công nghiệp / phòng thí nghiệm | Embedded / IoT / nghiên cứu |

---

## 2. Thông số kỹ thuật chi tiết

### 2.1 Dải đo và độ nhạy

| Thông số | PCB 353B34 | ADXL355 |
|----------|------------|---------|
| **Dải đo** | ±50 g peak | ±2.048 g / ±4.096 g / ±8.192 g (chọn được) |
| **Độ nhạy** | 100 mV/g (±10%) | 3.9 ug/LSB (ở ±2g, 20-bit) |
| **Độ phân giải ADC** | Phụ thuộc DAQ card | 20-bit tích hợp |
| **Broadband Resolution** | 0.0005 g rms (0.5 mg rms) | ~25 ug/sqrt(Hz) × sqrt(BW) |

### 2.2 Đáp ứng tần số

| Thông số | PCB 353B34 | ADXL355 |
|----------|------------|---------|
| **Dải tần (±5%)** | 2 Hz - 10,000 Hz | DC - 1,500 Hz (programmable) |
| **Dải tần mở rộng** | 0.5 Hz - 10,000 Hz (±10%) | Tùy ODR setting |
| **Tần số cộng hưởng** | >= 50 kHz | N/A (MEMS) |
| **Output Data Rate (ODR)** | Liên tục (analog) | 3.906 Hz - 4,000 Hz (chọn được) |
| **Đo DC (0 Hz)** | Không (AC-coupled qua ICP) | Có (DC-coupled) |

### 2.3 Nhiễu (Noise)

| Thông số | PCB 353B34 | ADXL355 |
|----------|------------|---------|
| **Noise Density** | ~10 ug/sqrt(Hz) (typical) | 25 ug/sqrt(Hz) (typical, ±2g) |
| **Broadband Noise (1-10kHz)** | 0.5 mg rms | ~1.5 mg rms (tại BW 1500 Hz) |

> **Ghi chú:** PCB 353B34 có mật độ nhiễu thấp hơn, nhưng ADXL355 thuộc hàng rất thấp cho MEMS (25 ug/sqrt(Hz) so với >100 ug/sqrt(Hz) của nhiều MEMS thông thường).

### 2.4 Điện và giao tiếp

| Thông số | PCB 353B34 | ADXL355 |
|----------|------------|---------|
| **Nguồn cấp** | 18 - 30 VDC (qua ICP/IEPE) | 2.25 - 3.6 VDC |
| **Dòng tiêu thụ** | 2 - 20 mA (constant current) | ~200 uA |
| **Trở kháng ngõ ra** | <= 100 Ohm | Digital (SPI/I2C) |
| **Giao tiếp** | Analog signal qua cáp coaxial | SPI (4-wire) hoặc I2C |
| **Cần DAQ card** | Có (NI DAQ, Bruel & Kjaer, etc.) | Không (kết nối trực tiếp MCU) |

### 2.5 Vật lý và môi trường

| Thông số | PCB 353B34 | ADXL355 |
|----------|------------|---------|
| **Khối lượng** | 5.8 g (0.20 oz) | < 0.5 g (chip level) |
| **Vỏ** | Titanium | 14-lead LGA (6mm x 6mm) |
| **Đầu nối** | 10-32 coaxial | Hàn trực tiếp lên PCB |
| **Gắn kết** | Stud / Adhesive / Magnetic base | Hàn SMD trên board |
| **Dải nhiệt hoạt động** | -54 to +121 C | -40 to +125 C |
| **Drift nhiệt độ (offset)** | Thấp (shear design) | ±0.15 mg/C (typical) |
| **Cảm biến nhiệt tích hợp** | Không | Có |

### 2.6 Độ chính xác

| Thông số | PCB 353B34 | ADXL355 |
|----------|------------|---------|
| **Nonlinearity** | <= 1% (full scale) | ±0.1% (full scale) |
| **Cross-axis Sensitivity** | <= 5% (typical) | ±1% (typical) |
| **Offset drift (nhiệt)** | Rất thấp (shear mode) | ±0.15 mg/C |
| **Long-term stability** | Tốt (ceramic element) | Tốt (hermetically sealed) |

---

## 3. So sánh ưu nhược điểm

### 3.1 PCB 353B34

**Ưu điểm:**
- Dải tần rộng (2 - 10,000 Hz), phù hợp đo rung tần số cao
- Dải đo lớn (±50 g), chịu được va đập mạnh
- Mật độ nhiễu thấp (~10 ug/sqrt(Hz))
- Vỏ titanium bền, phù hợp môi trường công nghiệp khắc nghiệt
- Chuẩn ICP/IEPE phổ biến, tương thích nhiều hệ DAQ
- Thiết kế shear mode giảm ảnh hưởng nhiệt và biến dạng đế

**Nhược điểm:**
- Chỉ đo 1 trục, cần 3 cảm biến cho 3 trục
- Cần hệ thống DAQ card đắt tiền (NI, B&K)
- Không đo được thành phần DC (AC-coupled)
- Giá thành cao (~200-500 USD/unit)
- Cần cáp coaxial, hệ thống cồng kềnh

### 3.2 ADXL355

**Ưu điểm:**
- 3 trục tích hợp trong 1 chip nhỏ gọn
- Đo được DC (tilt, inclination, gravity)
- Tiêu thụ điện cực thấp (~200 uA), phù hợp IoT/battery
- Giao tiếp digital (SPI/I2C), kết nối trực tiếp MCU
- Giá thành thấp (~15-30 USD/unit)
- Nonlinearity rất tốt (±0.1%)
- Có cảm biến nhiệt tích hợp
- ADC 20-bit tích hợp, không cần DAQ card

**Nhược điểm:**
- Dải tần hẹp hơn (DC - 1,500 Hz)
- Dải đo nhỏ (max ±8.192 g)
- Mật độ nhiễu cao hơn (25 ug/sqrt(Hz))
- Cần thiết kế PCB/board riêng
- Timestamp phụ thuộc phần mềm (jitter cao hơn)

---

## 4. Bảng tóm tắt so sánh theo tiêu chí ứng dụng

| Tiêu chí | PCB 353B34 | ADXL355 | Ghi chú |
|----------|:----------:|:-------:|---------|
| Đo rung tần số cao (>1 kHz) | ★★★★★ | ★★☆☆☆ | 353B34 vượt trội |
| Đo rung tần số thấp (<20 Hz) | ★★★☆☆ | ★★★★★ | ADXL355 đo được DC |
| Đo va đập / shock | ★★★★★ | ★★☆☆☆ | 353B34: ±50g vs ADXL355: ±8g |
| Monitoring dài hạn / IoT | ★★☆☆☆ | ★★★★★ | ADXL355 tiết kiệm điện |
| Độ chính xác biên độ | ★★★★★ | ★★★★☆ | 353B34 noise thấp hơn |
| Dễ triển khai | ★★★☆☆ | ★★★★★ | ADXL355 không cần DAQ |
| Chi phí hệ thống | ★★☆☆☆ | ★★★★★ | ADXL355 rẻ hơn nhiều |
| Đo đa trục | ★★☆☆☆ | ★★★★★ | ADXL355 tích hợp 3 trục |
| Môi trường khắc nghiệt | ★★★★★ | ★★★☆☆ | 353B34 vỏ titanium |

---

## 5. Ý nghĩa đối với dự án so sánh

### 5.1 Tại sao kết quả tương quan thấp?

Dựa trên thông số kỹ thuật, các yếu tố sau góp phần vào Pearson r thấp (~0.007):

1. **Vị trí đặt khác nhau** (confounding variable chính — không liên quan đến datasheet)
2. **Dải tần đáp ứng khác nhau**: 353B34 có năng lượng trong dải 1,500-10,000 Hz mà ADXL355 không ghi nhận được
3. **Đặc tính nhiễu khác nhau**: noise floor khác nhau ảnh hưởng đến SNR
4. **Timestamp precision**: 353B34 qua NI DAQ có timestamp chính xác (hardware-timed), ADXL355 timestamp qua phần mềm (jitter cao hơn)
5. **Cross-axis sensitivity**: 353B34 (5%) vs ADXL355 (1%) — ảnh hưởng khi trục gắn không hoàn toàn thẳng hàng

### 5.2 Dải tần phù hợp để so sánh

| Dải tần | So sánh được? | Ghi chú |
|---------|:-------------:|---------|
| 0 - 20 Hz | Tốt | Cả hai hoạt động tốt |
| 20 - 500 Hz | Khá | Cả hai trong dải, nhưng noise khác nhau |
| 500 - 1,500 Hz | Hạn chế | ADXL355 gần giới hạn, suy giảm biên độ |
| > 1,500 Hz | Không | ADXL355 không đo được |

### 5.3 Khuyến nghị

- Dải so sánh tin cậy nhất: **0 - 500 Hz** (cả hai cảm biến hoạt động trong spec)
- Pipeline hiện tại resample về 500 Hz (Nyquist = 250 Hz) — phù hợp
- Nên tập trung phân tích trong dải **0 - 200 Hz** để đảm bảo cả hai cảm biến có đáp ứng phẳng

---

## 6. Tài liệu tham khảo

1. PCB Piezotronics — Model 353B34 Product Page: https://www.pcb.com/products?m=353B34
2. Analog Devices — ADXL355 Product Page: https://www.analog.com/en/products/adxl355.html
3. PCB Piezotronics — ICP/IEPE Accelerometer Handbook
4. Analog Devices — ADXL355 Datasheet (Rev. C)
5. ISO 16063 — Methods for the calibration of vibration and shock transducers

---

*Báo cáo được tổng hợp từ datasheet chính thức của nhà sản xuất. Các giá trị mang tính tham khảo — luôn kiểm tra phiên bản datasheet mới nhất.*
