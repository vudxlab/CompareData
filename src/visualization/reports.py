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
    title: str = "Sensor Comparison Report"
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
