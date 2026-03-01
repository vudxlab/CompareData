# Project Structure Guide

## Muc tieu

Tai lieu nay mo ta cau truc thu muc chuan cho project so sanh du lieu gia toc.

## Nguyen tac to chuc

- `data/raw`: du lieu goc, khong sua truc tiep
- `data/processed`: du lieu da tien xu ly, san sang phan tich
- `configs`: tat ca tham so cho pipeline
- `src`: toan bo logic python co the tai su dung
- `scripts`: entry-point de chay nhanh workflow
- `results`: output sau moi lan chay (tables, figures, reports)
- `docs`: tai lieu huong dan va phuong phap

## Cac file config quan trong

- `configs/project.yaml`
  - config duy nhat cho toan bo project
  - khai bao sensor metadata + preprocess + comparison + output
  - khai bao cap chuoi can so sanh, cua so thoi gian, tan so resample
  - tham so `timezone_offset_hours` de chinh lech gio UTC cho sensor A

## Cac module phan tich chinh trong src

- `src/preprocessing/load_data.py`
  - `preprocess_adxl355`: tien xu ly sensor B (ADXL355)
  - `preprocess_setup5_keep_channels`: tien xu ly sensor A (NI DAQ)
    - Ho tro 2 dinh dang timestamp: `Time (s)` (relative) va `Time (UTC epoch s)` (unix)
    - Tham so `timezone_offset_hours` de chinh epoch UTC+7 sang UTC

- `src/preprocessing/time_conversion.py`
  - Cac ham tien ich chuyen doi timestamp: unix <-> UTC, relative time

- `src/analysis/window_compare.py`
  - So sanh 1 cap chuoi theo config
  - Chuan hoa don vi, canh hang, tinh metrics co ban

- `src/analysis/full_plan_compare.py`
  - Chay full workflow theo plan
  - Sinh bang ket qua + hinh + report markdown

## Cac script chay

- `scripts/run.py`: script duy nhat chay end-to-end (preprocess + compare + full report)

## Quy uoc dat ten output

- Bang ket qua:
  - `results/tables/*metrics*.csv`
  - `results/tables/*aligned*.csv`
  - `results/tables/*fft_peaks*.csv`
- Hinh anh:
  - `results/figures/<run_name>/*.png`
- Bao cao:
  - `results/reports/<run_name>_report.md`
