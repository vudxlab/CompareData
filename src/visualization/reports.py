"""
Report generation functions — Xuất báo cáo so sánh cảm biến bằng tiếng Việt có dấu.
"""

import pandas as pd
from typing import Dict, Any
from pathlib import Path
from datetime import datetime


def generate_report(
    comparison_results: Dict[str, Any],
    output_path: str,
    title: str = "Báo Cáo So Sánh Cảm Biến",
    figures_dir: Any = None,
    report_md: Any = None,
    dominant_freq_tolerance_hz: float = 1.0,
) -> str:
    """
    Sinh báo cáo so sánh chi tiết bằng tiếng Việt có dấu.

    Parameters
    ----------
    comparison_results : dict
        Kết quả từ pipeline so sánh
    output_path : str
        Đường dẫn lưu file báo cáo
    title : str
        Tiêu đề báo cáo
    figures_dir : Path or None
        Thư mục chứa hình
    report_md : Path or None
        Đường dẫn file report (dùng để tính relative path cho hình)
    dominant_freq_tolerance_hz : float
        Ngưỡng chênh lệch tần số trội để coi là khớp (Hz)

    Returns
    -------
    str
        Đường dẫn file báo cáo đã tạo
    """
    L = []  # report lines

    # --- Header ---
    L.append(f"# {title}")
    L.append(f"\nNgày tạo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    L.append("\n---\n")

    # --- Extract data ---
    stats_a = comparison_results.get('sensor_a_stats', {})
    stats_b = comparison_results.get('sensor_b_stats', {})
    corr = comparison_results.get('correlation', {})
    errors = comparison_results.get('error_metrics', {})
    bootstrap_ci = comparison_results.get('bootstrap_ci', {})
    coh = comparison_results.get('coherence', {})
    bland = comparison_results.get('bland_altman', {})
    freq_a = comparison_results.get('sensor_a_freq', {})
    freq_b = comparison_results.get('sensor_b_freq', {})
    fb_metrics = comparison_results.get('freq_band_metrics', {})

    pearson_r = corr.get('pearson_r', 0)
    spearman_r = corr.get('spearman_r', 0)
    r_squared = corr.get('r_squared', 0)
    mae_val = errors.get('mae', 0)
    rmse_val = errors.get('rmse', 0)
    nrmse = errors.get('nrmse', 0)
    max_error = errors.get('max_error', 0)
    dom_a = freq_a.get('dominant_frequency', 0)
    dom_b = freq_b.get('dominant_frequency', 0)
    freq_match = abs(dom_a - dom_b) <= dominant_freq_tolerance_hz

    # =====================================================================
    # 1. THỐNG KÊ MIỀN THỜI GIAN
    # =====================================================================
    L.append("## 1. Thống kê miền thời gian\n")
    metric_labels = {
        'mean': 'Trung bình (Mean)',
        'std': 'Độ lệch chuẩn (Std)',
        'rms': 'Giá trị hiệu dụng (RMS)',
        'peak': 'Đỉnh tuyệt đối (Peak)',
        'peak_to_peak': 'Biên độ đỉnh-đỉnh (Peak-to-peak)',
        'crest_factor': 'Hệ số đỉnh (Crest factor)',
    }
    L.append("| Chỉ số | Sensor A | Sensor B | Chênh lệch |")
    L.append("|--------|----------|----------|------------|")
    for key, label in metric_labels.items():
        va = stats_a.get(key, 0)
        vb = stats_b.get(key, 0)
        diff = va - vb
        L.append(f"| {label} | {va:.6f} | {vb:.6f} | {diff:.6f} |")

    # Nhận xét miền thời gian
    std_a = stats_a.get('std', 0)
    std_b = stats_b.get('std', 0)
    peak_a = stats_a.get('peak', 0)
    peak_b = stats_b.get('peak', 0)
    ptp_a = stats_a.get('peak_to_peak', 0)
    ptp_b = stats_b.get('peak_to_peak', 0)

    L.append("\n**Nhận xét miền thời gian:**\n")
    if std_b > 0 and std_a > 0:
        ratio_std = std_b / std_a
        L.append(f"- Độ lệch chuẩn Sensor B cao hơn Sensor A khoảng {(ratio_std - 1)*100:.0f}% "
                 f"({std_b:.4f} g so với {std_a:.4f} g), cho thấy Sensor B ghi nhận rung động mạnh hơn.")
    if peak_b > 0 and peak_a > 0:
        ratio_peak = peak_b / peak_a
        L.append(f"- Giá trị đỉnh (peak) của Sensor B gấp {ratio_peak:.1f} lần Sensor A "
                 f"({peak_b:.4f} g so với {peak_a:.4f} g).")
    if ptp_b > 0 and ptp_a > 0:
        ratio_ptp = ptp_b / ptp_a
        L.append(f"- Biên độ đỉnh-đỉnh (peak-to-peak) của Sensor B gấp {ratio_ptp:.1f} lần Sensor A "
                 f"({ptp_b:.4f} g so với {ptp_a:.4f} g).")
    L.append("- Sự chênh lệch biên độ có thể do vị trí đặt cảm biến khác nhau trên kết cấu "
             "(mode shape effect) hoặc do đặc tính đáp ứng khác nhau giữa hai loại cảm biến.")

    # =====================================================================
    # 2. PHÂN TÍCH TƯƠNG QUAN
    # =====================================================================
    L.append("\n## 2. Phân tích tương quan\n")
    L.append("| Chỉ số | Giá trị | Đánh giá |")
    L.append("|--------|---------|----------|")

    def _corr_rating(r: float) -> str:
        ar = abs(r)
        if ar >= 0.99: return "Xuất sắc"
        if ar >= 0.95: return "Tốt"
        if ar >= 0.90: return "Chấp nhận được"
        return "Kém"

    L.append(f"| Pearson r | {pearson_r:.6f} | {_corr_rating(pearson_r)} |")
    L.append(f"| R² | {r_squared:.6f} | — |")
    L.append(f"| Spearman r | {spearman_r:.6f} | {_corr_rating(spearman_r)} |")

    L.append("\n**Nhận xét tương quan:**\n")
    if abs(pearson_r) < 0.10:
        L.append(f"- Pearson r = {pearson_r:.4f}, gần bằng 0: **không có tương quan tuyến tính** "
                 "đáng kể giữa hai chuỗi tín hiệu trong miền thời gian.")
        L.append(f"- R² = {r_squared:.6f}: Sensor A chỉ giải thích được {r_squared*100:.4f}% "
                 "phương sai của Sensor B — gần như bằng 0.")
        L.append(f"- Spearman r = {spearman_r:.4f}: tương quan thứ bậc cũng rất thấp, "
                 "loại trừ khả năng có mối quan hệ đơn điệu phi tuyến.")
    elif abs(pearson_r) >= 0.90:
        L.append(f"- Pearson r = {pearson_r:.4f}: tương quan mạnh, hai chuỗi tín hiệu nhất quán tốt.")
    else:
        L.append(f"- Pearson r = {pearson_r:.4f}: tương quan ở mức trung bình.")

    # =====================================================================
    # 3. CHỈ SỐ SAI SỐ VÀ KHOẢNG TIN CẬY
    # =====================================================================
    L.append("\n## 3. Chỉ số sai số và khoảng tin cậy\n")

    if bootstrap_ci:
        r_ci = bootstrap_ci.get('pearson_r_ci', (None, None))
        rmse_ci = bootstrap_ci.get('rmse_ci', (None, None))
        mae_ci = bootstrap_ci.get('mae_ci', (None, None))
        L.append("| Chỉ số | Giá trị | 95% CI | Đánh giá |")
        L.append("|--------|---------|--------|----------|")
        L.append(f"| Pearson r | {pearson_r:.6f} | [{r_ci[0]:.6f}, {r_ci[1]:.6f}] | {_corr_rating(pearson_r)} |")
        L.append(f"| MAE | {mae_val:.6f} g | [{mae_ci[0]:.6f}, {mae_ci[1]:.6f}] | — |")
        L.append(f"| RMSE | {rmse_val:.6f} g | [{rmse_ci[0]:.6f}, {rmse_ci[1]:.6f}] | — |")

        def _nrmse_rating(n: float) -> str:
            if n < 0.01: return "Xuất sắc"
            if n < 0.05: return "Tốt"
            if n < 0.10: return "Chấp nhận được"
            return "Kém"

        L.append(f"| NRMSE | {nrmse:.6f} ({nrmse*100:.1f}%) | — | {_nrmse_rating(nrmse)} |")
        L.append(f"| Sai số cực đại | {max_error:.6f} g | — | — |")
    else:
        L.append(f"- MAE: {mae_val:.6f} g")
        L.append(f"- RMSE: {rmse_val:.6f} g")
        L.append(f"- NRMSE: {nrmse:.6f} ({nrmse*100:.1f}%)")
        L.append(f"- Sai số cực đại: {max_error:.6f} g")

    L.append("\n**Nhận xét sai số:**\n")
    if bootstrap_ci:
        r_ci = bootstrap_ci.get('pearson_r_ci', (0, 0))
        if r_ci[0] <= 0 <= r_ci[1]:
            L.append(f"- Khoảng tin cậy 95% của Pearson r [{r_ci[0]:.6f}, {r_ci[1]:.6f}] **chứa giá trị 0**, "
                     "xác nhận tương quan không có ý nghĩa thống kê.")
        else:
            L.append(f"- Khoảng tin cậy 95% của Pearson r [{r_ci[0]:.6f}, {r_ci[1]:.6f}] "
                     "không chứa giá trị 0, cho thấy tương quan có ý nghĩa thống kê.")
    if nrmse >= 0.10:
        L.append(f"- NRMSE = {nrmse*100:.1f}% thuộc mức **Kém** (ngưỡng chấp nhận < 10%).")
    elif nrmse >= 0.05:
        L.append(f"- NRMSE = {nrmse*100:.1f}% thuộc mức **Chấp nhận được** (< 10%).")
    else:
        L.append(f"- NRMSE = {nrmse*100:.1f}% thuộc mức **Tốt** (< 5%).")
    if max_error > 0 and rmse_val > 0:
        L.append(f"- Sai số cực đại ({max_error:.4f} g) gấp {max_error/rmse_val:.1f} lần RMSE ({rmse_val:.4f} g), "
                 "cho thấy phân bố sai số có đuôi nặng (heavy tail).")

    # =====================================================================
    # 4. PHÂN TÍCH COHERENCE
    # =====================================================================
    if coh:
        mean_coh = coh.get('mean', 0)
        min_coh = coh.get('min', 0)

        def _coh_rating(c: float) -> str:
            if c >= 0.95: return "Xuất sắc"
            if c >= 0.90: return "Tốt"
            if c >= 0.80: return "Chấp nhận được"
            return "Kém"

        L.append("\n## 4. Phân tích Coherence\n")
        L.append("| Chỉ số | Giá trị | Đánh giá |")
        L.append("|--------|---------|----------|")
        L.append(f"| Coherence trung bình | {mean_coh:.4f} | {_coh_rating(mean_coh)} |")
        L.append(f"| Coherence cực tiểu | {min_coh:.4f} | — |")

        L.append("\n**Nhận xét coherence:**\n")
        if mean_coh < 0.80:
            L.append(f"- Coherence trung bình = {mean_coh:.4f} < 0.80: xếp hạng **Kém**.")
            L.append("- Hai tín hiệu không có mối liên hệ tuyến tính nhất quán tại bất kỳ dải tần nào.")
            L.append("- Kết quả này phù hợp với giả thuyết hai cảm biến đặt tại vị trí khác nhau "
                     "trên kết cấu, dẫn đến đáp ứng rung khác biệt cả về biên độ lẫn pha.")
        elif mean_coh >= 0.95:
            L.append(f"- Coherence trung bình = {mean_coh:.4f} >= 0.95: xếp hạng **Xuất sắc**.")
            L.append("- Hai tín hiệu có mối liên hệ tuyến tính mạnh và nhất quán theo tần số.")
        else:
            L.append(f"- Coherence trung bình = {mean_coh:.4f}: mức trung bình.")

    # =====================================================================
    # 5. PHÂN TÍCH BLAND-ALTMAN
    # =====================================================================
    if bland:
        L.append("\n## 5. Phân tích Bland-Altman\n")
        mean_diff = bland.get('mean_difference', 0)
        std_diff = bland.get('std_difference', 0)
        upper_loa = bland.get('upper_loa', 0)
        lower_loa = bland.get('lower_loa', 0)

        L.append("| Chỉ số | Giá trị |")
        L.append("|--------|---------|")
        L.append(f"| Sai khác trung bình (bias) | {mean_diff:.6f} g |")
        L.append(f"| Độ lệch chuẩn sai khác (ddof=1) | {std_diff:.6f} g |")
        L.append(f"| Giới hạn đồng thuận trên (Upper LoA) | +{upper_loa:.6f} g |")
        L.append(f"| Giới hạn đồng thuận dưới (Lower LoA) | {lower_loa:.6f} g |")

        normality = bland.get('normality_test', {})
        if normality:
            L.append(f"\n### Kiểm định phân phối chuẩn (Shapiro-Wilk)\n")
            p_val = normality.get('p_value', 0)
            stat_val = normality.get('statistic', 0)
            is_normal = normality.get('is_normal', False)
            L.append(f"- Thống kê kiểm định: {stat_val:.6f}")
            L.append(f"- Giá trị p: {p_val:.6f}")
            if is_normal:
                L.append("- Kết quả: Sai khác **phân phối chuẩn** (p > 0.05) — giới hạn đồng thuận (LoA) đáng tin cậy.")
            else:
                L.append("- Kết quả: Sai khác **không phân phối chuẩn** (p <= 0.05) — "
                         "giới hạn đồng thuận (LoA) cần thận trọng khi diễn giải.")

        L.append("\n**Nhận xét Bland-Altman:**\n")
        if abs(mean_diff) < 0.001:
            L.append(f"- Bias gần bằng 0 ({mean_diff:.6f} g): **không có sai lệch hệ thống** đáng kể giữa hai cảm biến.")
        else:
            L.append(f"- Bias = {mean_diff:.6f} g: có sai lệch hệ thống giữa hai cảm biến.")
        L.append(f"- Giới hạn đồng thuận rộng (±{abs(upper_loa):.4f} g), phản ánh mức độ "
                 "không đồng thuận đáng kể giữa hai phép đo.")
        L.append("- Hai cảm biến có thể nhận biết cùng thành phần tần số chính, nhưng **chưa đủ điều kiện "
                 "để thay thế trực tiếp nhau** khi yêu cầu độ chính xác biên độ cao ở miền thời gian.")

    # =====================================================================
    # 6. PHÂN TÍCH MIỀN TẦN SỐ
    # =====================================================================
    L.append("\n## 6. Phân tích miền tần số\n")

    freq_metric_labels = {
        'dominant_frequency': 'Tần số trội',
        'spectral_centroid': 'Trọng tâm phổ',
        'median_frequency': 'Tần số trung vị',
    }
    L.append("| Chỉ số | Sensor A | Sensor B | Chênh lệch |")
    L.append("|--------|----------|----------|------------|")
    for key, label in freq_metric_labels.items():
        va = freq_a.get(key, 0)
        vb = freq_b.get(key, 0)
        diff = va - vb
        L.append(f"| {label} | {va:.2f} Hz | {vb:.2f} Hz | {diff:.2f} Hz |")

    L.append("\n**Nhận xét miền tần số:**\n")
    if freq_match:
        L.append(f"- Tần số trội: **khớp nhau** ({dom_a:.2f} Hz so với {dom_b:.2f} Hz, "
                 f"chênh lệch {abs(dom_a - dom_b):.2f} Hz < ngưỡng {dominant_freq_tolerance_hz:.1f} Hz). "
                 "Cả hai cảm biến cùng bắt được nguồn rung chính.")
    else:
        L.append(f"- Tần số trội: **không khớp** ({dom_a:.2f} Hz so với {dom_b:.2f} Hz, "
                 f"chênh lệch {abs(dom_a - dom_b):.2f} Hz > ngưỡng {dominant_freq_tolerance_hz:.1f} Hz).")

    sc_a = freq_a.get('spectral_centroid', 0)
    sc_b = freq_b.get('spectral_centroid', 0)
    if sc_b > sc_a * 1.2:
        L.append(f"- Trọng tâm phổ của Sensor B ({sc_b:.2f} Hz) cao hơn đáng kể so với Sensor A ({sc_a:.2f} Hz), "
                 "cho thấy Sensor B chứa nhiều năng lượng ở dải tần cao hơn.")
    elif sc_a > sc_b * 1.2:
        L.append(f"- Trọng tâm phổ của Sensor A ({sc_a:.2f} Hz) cao hơn Sensor B ({sc_b:.2f} Hz).")

    L.append("- FFT được tính với cửa sổ Hann và hệ số bù biên độ (amplitude correction factor).")

    # =====================================================================
    # 7. HÌNH ẢNH VÀ BIỂU ĐỒ
    # =====================================================================
    if figures_dir is not None and report_md is not None:
        figures_dir = Path(figures_dir)
        report_dir = Path(report_md).parent
        L.append("\n## 7. Hình ảnh và biểu đồ\n")
        figure_defs = [
            ("time_series_3panel.png",  "Chuỗi thời gian — Sensor A, Sensor B, chồng lớp (trục UTC)"),
            ("freq_3panel_0_20hz.png",  "Miền tần số — FFT A, FFT B, PSD chồng lớp (0–20 Hz)"),
            ("time_series.png",         "Chuỗi thời gian — chồng lớp (đã resample)"),
            ("fft.png",                 "So sánh FFT (0–50 Hz)"),
            ("psd.png",                 "So sánh PSD (0–50 Hz)"),
            ("scatter.png",             "Biểu đồ tán xạ (Scatter)"),
            ("bland_altman.png",        "Biểu đồ Bland-Altman"),
            ("coherence.png",           "Phân tích Coherence"),
        ]
        import os
        for fname, caption in figure_defs:
            fig_path = figures_dir / fname
            if fig_path.exists():
                rel = os.path.relpath(str(fig_path), str(report_dir)).replace("\\", "/")
                L.append(f"### {caption}\n")
                L.append(f"![]({rel})\n")

    # =====================================================================
    # 8. PHÂN TÍCH DẢI TẦN 0–20 Hz
    # =====================================================================
    L.append("\n## 8. Phân tích dải tần 0–20 Hz\n")
    if fb_metrics:
        L.append("### Thống kê theo từng cảm biến\n")
        L.append("| Chỉ số | Sensor A | Sensor B | Chênh lệch |")
        L.append("|--------|----------|----------|------------|")
        stat_rows = [
            ("Trung bình biên độ", "mean_a", "mean_b"),
            ("Độ lệch chuẩn biên độ", "std_a", "std_b"),
            ("RMS biên độ", "rms_a", "rms_b"),
            ("Đỉnh biên độ", "peak_a", "peak_b"),
            ("Tần số đỉnh (Hz)", "peak_freq_a", "peak_freq_b"),
            ("Năng lượng phổ", "spectral_energy_a", "spectral_energy_b"),
        ]
        for label, key_a, key_b in stat_rows:
            va = fb_metrics.get(key_a, float("nan"))
            vb = fb_metrics.get(key_b, float("nan"))
            diff = va - vb
            L.append(f"| {label} | {va:.6f} | {vb:.6f} | {diff:.6f} |")

        energy_ratio = fb_metrics.get('energy_ratio', float('nan'))
        L.append(f"\n- **Tỷ lệ năng lượng (A/B)**: {energy_ratio:.4f}")
        if energy_ratio < 1.0:
            L.append(f"  - Sensor B có năng lượng cao hơn ~{(1/energy_ratio - 1)*100:.0f}% trong dải 0–20 Hz.")
        else:
            L.append(f"  - Sensor A có năng lượng cao hơn ~{(energy_ratio - 1)*100:.0f}% trong dải 0–20 Hz.")

        L.append("\n### Chỉ số so sánh phổ tần\n")
        L.append("| Chỉ số | Giá trị |")
        L.append("|--------|---------|")
        fb_pearson = fb_metrics.get('pearson_r', float('nan'))
        fb_mae = fb_metrics.get('mae', float('nan'))
        fb_rmse = fb_metrics.get('rmse', float('nan'))
        fb_nrmse = fb_metrics.get('nrmse', float('nan'))
        L.append(f"| Pearson r (phổ) | {fb_pearson:.6f} |")
        L.append(f"| MAE (biên độ) | {fb_mae:.6f} |")
        L.append(f"| RMSE (biên độ) | {fb_rmse:.6f} |")
        L.append(f"| NRMSE (biên độ) | {fb_nrmse:.6f} ({fb_nrmse*100:.2f}%) |")

        L.append("\n**Nhận xét dải tần 0–20 Hz:**\n")
        if fb_pearson > 0.5:
            L.append(f"- Tương quan phổ trong dải 0–20 Hz đạt r = {fb_pearson:.2f}, "
                     f"**cao hơn đáng kể** so với tương quan miền thời gian (r = {pearson_r:.4f}).")
            L.append("- Điều này cho thấy hình dạng phổ tần hai cảm biến tương đồng trong dải thấp, "
                     "mặc dù dạng sóng theo thời gian khác biệt.")
        elif fb_pearson > 0.3:
            L.append(f"- Tương quan phổ trong dải 0–20 Hz ở mức trung bình (r = {fb_pearson:.2f}).")
        else:
            L.append(f"- Tương quan phổ trong dải 0–20 Hz thấp (r = {fb_pearson:.2f}).")

    # =====================================================================
    # 9. TỔNG HỢP VÀ KẾT LUẬN
    # =====================================================================
    L.append("\n## 9. Tổng hợp và kết luận\n")

    # Rating summary table
    corr_rating = _corr_rating(pearson_r)
    def _nrmse_r(n: float) -> str:
        if n < 0.01: return "Xuất sắc"
        if n < 0.05: return "Tốt"
        if n < 0.10: return "Chấp nhận được"
        return "Kém"
    nrmse_rating = _nrmse_r(nrmse)

    L.append("### Bảng tổng hợp đánh giá\n")
    L.append("| Tiêu chí | Giá trị | Xếp hạng | Ngưỡng tham khảo |")
    L.append("|----------|---------|----------|------------------|")
    L.append(f"| Tương quan (Pearson r) | {pearson_r:.4f} | {corr_rating} | Xuất sắc > 0.99, Tốt > 0.95, Chấp nhận > 0.90 |")
    L.append(f"| Sai số chuẩn hóa (NRMSE) | {nrmse*100:.1f}% | {nrmse_rating} | Xuất sắc < 1%, Tốt < 5%, Chấp nhận < 10% |")
    if coh:
        mean_coh = coh.get('mean', 0)
        coh_r = _coh_rating(mean_coh) if '_coh_rating' not in dir() else ("Xuất sắc" if mean_coh >= 0.95 else "Tốt" if mean_coh >= 0.90 else "Chấp nhận được" if mean_coh >= 0.80 else "Kém")
        L.append(f"| Coherence trung bình | {mean_coh:.4f} | {coh_r} | Xuất sắc > 0.95, Tốt > 0.90, Chấp nhận > 0.80 |")
    if freq_match:
        L.append(f"| Tần số trội | {dom_a:.2f} vs {dom_b:.2f} Hz | Khớp | Chênh lệch < {dominant_freq_tolerance_hz:.1f} Hz |")
    else:
        L.append(f"| Tần số trội | {dom_a:.2f} vs {dom_b:.2f} Hz | Không khớp | Chênh lệch < {dominant_freq_tolerance_hz:.1f} Hz |")

    L.append("\n### Kết luận kỹ thuật\n")

    # Build numbered conclusions
    conclusions = []
    conclusions.append(f"Tương quan miền thời gian rất thấp (Pearson r = {pearson_r:.4f}), "
                       "không có ý nghĩa thống kê.")
    if std_b > std_a:
        conclusions.append(f"Sensor B cho thấy biên độ dao động cao hơn Sensor A "
                           f"(peak gấp ~{peak_b/peak_a:.1f} lần, std gấp ~{std_b/std_a:.1f} lần).")
    if freq_match:
        conclusions.append(f"Cả hai cảm biến đều bắt được cùng tần số trội chính "
                           f"(~{(dom_a + dom_b)/2:.1f} Hz), xác nhận cùng nguồn rung.")
    if fb_metrics and fb_pearson > 0.3:
        conclusions.append(f"Tương quan phổ trong dải 0–20 Hz (r = {fb_pearson:.2f}) cao hơn đáng kể "
                           "so với tương quan miền thời gian, cho thấy hình dạng phổ tương đồng "
                           "nhưng dạng sóng khác biệt.")
    if coh and mean_coh < 0.80:
        conclusions.append(f"Coherence trung bình rất thấp ({mean_coh:.4f}), cho thấy không có "
                           "mối liên hệ tuyến tính nhất quán theo tần số giữa hai cảm biến.")
    if bland:
        mean_diff = bland.get('mean_difference', 0)
        upper_loa = bland.get('upper_loa', 0)
        conclusions.append(f"Bland-Altman: bias gần 0 ({mean_diff:.6f} g) nhưng giới hạn đồng thuận rộng "
                           f"(±{abs(upper_loa):.4f} g).")

    for i, c in enumerate(conclusions, 1):
        L.append(f"{i}. {c}")

    # Overall conclusion
    L.append("")
    if corr_rating == "Poor" and freq_match:
        L.append("**Kết luận tổng thể:** Cả hai cảm biến bắt được cùng tần số rung trội, "
                 "nhưng tương quan dạng sóng theo thời gian rất thấp. "
                 "Kết quả phù hợp với giả thuyết hai cảm biến đặt tại **vị trí khác nhau** trên kết cấu, "
                 "nơi biên độ và pha rung khác nhau do hiệu ứng mode shape và truyền sóng. "
                 "Tương quan thấp được quy cho sự khác biệt về vị trí đặt cảm biến, "
                 "không phải do lệch timestamp.")
    elif corr_rating in ("Xuất sắc", "Excellent", "Tốt", "Good"):
        L.append("**Kết luận tổng thể:** Hai cảm biến có sự đồng thuận mạnh. "
                 "Tín hiệu đo được nhất quán cả về biên độ và pha.")
    else:
        L.append("**Kết luận tổng thể:** Mức đồng thuận trung bình. "
                 "Cần kiểm tra thêm vị trí đặt cảm biến và canh hàng thời gian.")

    # Recommendations
    L.append("\n### Khuyến nghị\n")
    L.append("Nếu mục tiêu là đối chiếu đáp ứng rung cùng trục:\n")
    L.append("1. Thực hiện thí nghiệm co-location (đặt hai cảm biến cùng vị trí trên kết cấu)")
    L.append("2. Hiệu chuẩn (calibration) với tín hiệu tham chiếu đã biết")
    L.append("3. Xác nhận lại mapping trục/hướng gắn cảm biến")
    L.append("4. So sánh đa trục (3 trục + vector magnitude)")
    L.append("5. Phân tích nhiều cửa sổ thời gian với các điều kiện kích thích khác nhau")

    # --- Write output ---
    report_content = "\n".join(L)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)

    return str(output_path)


def export_metrics_to_csv(
    comparison_results: Dict[str, Any],
    output_path: str
) -> str:
    """
    Xuất chỉ số so sánh ra file CSV.

    Parameters
    ----------
    comparison_results : dict
        Kết quả từ pipeline so sánh
    output_path : str
        Đường dẫn lưu file CSV

    Returns
    -------
    str
        Đường dẫn file CSV đã tạo
    """
    rows = []

    for category, metrics in comparison_results.items():
        if isinstance(metrics, dict):
            for metric_name, value in metrics.items():
                if isinstance(value, (int, float)):
                    rows.append({
                        'category': category,
                        'metric': metric_name,
                        'value': value
                    })

    df = pd.DataFrame(rows)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    return str(output_path)
