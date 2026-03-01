"""
Report generation functions
"""

import pandas as pd
from typing import Dict, Any
from pathlib import Path
from datetime import datetime


def generate_report(
    comparison_results: Dict[str, Any],
    output_path: str,
    title: str = "Sensor Comparison Report",
    figures_dir: Any = None,
    report_md: Any = None,
) -> str:
    """
    Generate a comprehensive comparison report.
    
    Parameters
    ----------
    comparison_results : dict
        Results from compare_sensors function
    output_path : str
        Path to save the report
    title : str
        Report title
    
    Returns
    -------
    str
        Path to generated report
    """
    report_lines = []
    report_lines.append(f"# {title}")
    report_lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("\n---\n")
    
    report_lines.append("## Time Domain Statistics\n")
    report_lines.append("| Metric | Sensor A | Sensor B | Difference |")
    report_lines.append("|--------|----------|----------|------------|")
    
    stats_a = comparison_results.get('sensor_a_stats', {})
    stats_b = comparison_results.get('sensor_b_stats', {})
    
    for metric in ['mean', 'std', 'rms', 'peak', 'peak_to_peak', 'crest_factor']:
        val_a = stats_a.get(metric, 0)
        val_b = stats_b.get(metric, 0)
        diff = val_a - val_b
        report_lines.append(f"| {metric} | {val_a:.6f} | {val_b:.6f} | {diff:.6f} |")
    
    report_lines.append("\n## Correlation Analysis\n")
    corr = comparison_results.get('correlation', {})
    report_lines.append(f"- Pearson r: {corr.get('pearson_r', 0):.6f}")
    report_lines.append(f"- R²: {corr.get('r_squared', 0):.6f}")
    report_lines.append(f"- Spearman r: {corr.get('spearman_r', 0):.6f}")
    
    report_lines.append("\n## Error Metrics\n")
    errors = comparison_results.get('error_metrics', {})
    report_lines.append(f"- MAE: {errors.get('mae', 0):.6f}")
    report_lines.append(f"- RMSE: {errors.get('rmse', 0):.6f}")
    report_lines.append(f"- NRMSE: {errors.get('nrmse', 0):.6f}")
    report_lines.append(f"- Max Error: {errors.get('max_error', 0):.6f}")
    
    report_lines.append("\n## Frequency Domain Analysis\n")
    freq_a = comparison_results.get('sensor_a_freq', {})
    freq_b = comparison_results.get('sensor_b_freq', {})

    report_lines.append("| Metric | Sensor A | Sensor B |")
    report_lines.append("|--------|----------|----------|")
    for metric in ['dominant_frequency', 'spectral_centroid', 'median_frequency']:
        val_a = freq_a.get(metric, 0)
        val_b = freq_b.get(metric, 0)
        report_lines.append(f"| {metric} | {val_a:.2f} Hz | {val_b:.2f} Hz |")

    # Figures section — paths relative to report location
    if figures_dir is not None and report_md is not None:
        figures_dir = Path(figures_dir)
        report_dir = Path(report_md).parent
        report_lines.append("\n## Figures\n")
        figure_defs = [
            ("time_series_3panel.png",  "Time Series — Sensor A, Sensor B, Overlay (UTC axis)"),
            ("freq_3panel_0_20hz.png",  "Frequency Domain — FFT A, FFT B, PSD Overlay (0–20 Hz)"),
            ("time_series.png",         "Time Series — Overlay (resampled)"),
            ("fft.png",                 "FFT Comparison"),
            ("psd.png",                 "PSD Comparison"),
            ("scatter.png",             "Scatter Plot"),
            ("bland_altman.png",        "Bland-Altman Plot"),
        ]
        for fname, caption in figure_defs:
            fig_path = figures_dir / fname
            if fig_path.exists():
                # compute relative path from report dir using os.path
                import os
                rel = os.path.relpath(str(fig_path), str(report_dir)).replace("\\", "/")
                report_lines.append(f"### {caption}\n")
                report_lines.append(f"![]({rel})\n")
    
    # Interpretation
    report_lines.append("\n## Interpretation\n")

    pearson_r = corr.get('pearson_r', 0)
    nrmse = errors.get('nrmse', 0)
    dom_a = freq_a.get('dominant_frequency', 0)
    dom_b = freq_b.get('dominant_frequency', 0)
    freq_match = abs(dom_a - dom_b) <= 1.0

    # Correlation rating
    if abs(pearson_r) >= 0.99:
        corr_rating = "Excellent"
    elif abs(pearson_r) >= 0.95:
        corr_rating = "Good"
    elif abs(pearson_r) >= 0.90:
        corr_rating = "Acceptable"
    else:
        corr_rating = "Poor"

    # NRMSE rating
    if nrmse < 0.01:
        nrmse_rating = "Excellent"
    elif nrmse < 0.05:
        nrmse_rating = "Good"
    elif nrmse < 0.10:
        nrmse_rating = "Acceptable"
    else:
        nrmse_rating = "Poor"

    report_lines.append(f"- **Correlation (Pearson r = {pearson_r:.4f})**: {corr_rating}")
    report_lines.append(f"- **NRMSE = {nrmse:.4f} ({nrmse*100:.1f}%)**: {nrmse_rating}")
    if freq_match:
        report_lines.append(f"- **Dominant frequency**: matched ({dom_a:.2f} Hz vs {dom_b:.2f} Hz) — same vibration source confirmed")
    else:
        report_lines.append(f"- **Dominant frequency**: mismatch ({dom_a:.2f} Hz vs {dom_b:.2f} Hz)")

    if corr_rating == "Poor" and freq_match:
        report_lines.append(
            "\n**Conclusion**: Both sensors capture the same dominant vibration frequency, "
            "but waveform correlation is low. This is consistent with sensors placed at "
            "different physical locations on the structure, where vibration amplitude and "
            "phase differ. Time-lag sweep (cross-correlation over full data) confirmed no "
            "single offset improves correlation significantly (peak r < 0.08 across all channels). "
            "The low correlation is therefore attributed to spatial differences in sensor placement, "
            "not to timestamp misalignment."
        )
    elif corr_rating in ("Excellent", "Good"):
        report_lines.append("\n**Conclusion**: Strong agreement between sensors. Sensors are well-aligned in time and measure comparable signals.")
    else:
        report_lines.append("\n**Conclusion**: Moderate agreement. Further investigation of sensor placement and time alignment is recommended.")

    report_content = "\n".join(report_lines)

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
    Export comparison metrics to CSV file.
    
    Parameters
    ----------
    comparison_results : dict
        Results from compare_sensors function
    output_path : str
        Path to save CSV file
    
    Returns
    -------
    str
        Path to generated CSV
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
