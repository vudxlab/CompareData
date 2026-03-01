"""
Full report workflow driven by compare_pair config.
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict

import numpy as np
import pandas as pd

from src.analysis.comparison import bland_altman_analysis
from src.analysis.frequency import compute_fft, compute_frequency_metrics, compute_psd
from src.analysis.statistics import compute_time_domain_metrics
from src.analysis.window_compare import compare_single_pair_from_config
from src.utils.config import get_project_root, load_config
from src.visualization.plots import (
    plot_bland_altman,
    plot_comparison,
    plot_fft,
    plot_psd,
    plot_time_series,
)
from src.visualization.reports import export_metrics_to_csv, generate_report


def _plot_3panel_utc(
    raw_a: "pd.DataFrame",
    raw_b: "pd.DataFrame",
    time_col_a: str,
    time_col_b: str,
    val_col_a: str,
    val_col_b: str,
    start_utc: datetime,
    duration_s: int,
    save_path: str,
) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    t_a = raw_a[time_col_a].values
    t_b = raw_b[time_col_b].values
    sig_a = raw_a[val_col_a].to_numpy(dtype=float)
    sig_b = raw_b[val_col_b].to_numpy(dtype=float)

    fmt = mdates.DateFormatter("%H:%M:%S")
    end_utc = start_utc + timedelta(seconds=duration_s)
    title = (
        f"Time Series Comparison\n"
        f"Window: {start_utc.strftime('%Y-%m-%d %H:%M:%S')} UTC, {duration_s}s"
    )

    fig, axes = plt.subplots(3, 1, figsize=(12, 9))
    fig.suptitle(title, fontsize=13, fontweight="bold")

    axes[0].plot(t_a, sig_a, color="#1f77b4", linewidth=0.6, label=f"Sensor A – {val_col_a}")
    axes[0].set_ylabel("Acceleration (g)")
    axes[0].set_title(f"Sensor A – NI DAQ ({val_col_a})")
    axes[0].legend(loc="upper right", fontsize=8)
    axes[0].grid(True, alpha=0.3)
    axes[0].xaxis.set_major_formatter(fmt)
    axes[0].set_xlabel("Time (UTC)")
    axes[0].set_xlim(t_a[0], t_a[-1])

    axes[1].plot(t_b, sig_b, color="#ff7f0e", linewidth=0.6, label=f"Sensor B – {val_col_b}")
    axes[1].set_ylabel("Acceleration (g)")
    axes[1].set_title(f"Sensor B – ADXL355 ({val_col_b})")
    axes[1].legend(loc="upper right", fontsize=8)
    axes[1].grid(True, alpha=0.3)
    axes[1].xaxis.set_major_formatter(fmt)
    axes[1].set_xlabel("Time (UTC)")
    axes[1].set_xlim(t_b[0], t_b[-1])

    axes[2].plot(t_a, sig_a, color="#1f77b4", linewidth=0.6, alpha=0.8, label=f"Sensor A – {val_col_a}")
    axes[2].plot(t_b, sig_b, color="#ff7f0e", linewidth=0.6, alpha=0.8, label=f"Sensor B – {val_col_b}")
    axes[2].set_ylabel("Acceleration (g)")
    axes[2].set_xlabel("Time (UTC)")
    axes[2].set_title("Sensor A vs Sensor B – Overlay")
    axes[2].legend(loc="upper right", fontsize=8)
    axes[2].grid(True, alpha=0.3)
    axes[2].xaxis.set_major_formatter(fmt)
    axes[2].set_xlim(max(t_a[0], t_b[0]), min(t_a[-1], t_b[-1]))

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _to_utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _to_g(values: np.ndarray, unit: str) -> np.ndarray:
    u = unit.lower()
    if u in {"g", "g-force"}:
        return values
    if u in {"m/s^2", "m/s2"}:
        return values / 9.80665
    raise ValueError(f"Unsupported unit: {unit}")


def _estimate_fs(t: np.ndarray) -> float:
    dt = np.diff(t)
    dt = dt[dt > 0]
    if len(dt) == 0:
        return 0.0
    return float(1.0 / np.mean(dt))


def _load_window_raw(
    file_path: Path,
    time_col: str,
    value_col: str,
    start_utc: datetime,
    end_utc: datetime,
    chunksize: int = 200000,
) -> pd.DataFrame:
    parts = []
    for chunk in pd.read_csv(file_path, usecols=[time_col, value_col], chunksize=chunksize):
        raw_t = chunk[time_col]
        if pd.api.types.is_numeric_dtype(raw_t):
            t = pd.to_datetime(raw_t, unit="s", utc=True, errors="coerce")
        else:
            t = pd.to_datetime(raw_t, utc=True, errors="coerce", format="mixed")
        m = (t >= start_utc) & (t < end_utc)
        if m.any():
            out = chunk.loc[m].copy()
            out[time_col] = t.loc[m]
            parts.append(out)
    if not parts:
        return pd.DataFrame(columns=[time_col, value_col])
    return pd.concat(parts, ignore_index=True)


def run_full_report_from_config(config_path: str = "configs/project.yaml") -> Dict[str, str]:
    """
    Run complete analysis and export report artifacts.
    """
    project_root = get_project_root()
    root_cfg = load_config(config_path)
    if "comparison" in root_cfg:
        cfg = root_cfg.get("comparison", {})
    else:
        cfg = root_cfg.get("pipeline", {}).get("comparison", {})

    pair_result = compare_single_pair_from_config(config_path)
    aligned = pd.read_csv(pair_result["aligned_path"])
    fs = float(pair_result["metrics"]["fs_target_hz"])

    sensor_a = aligned["sensor_a_g"].to_numpy(dtype=float)
    sensor_b = aligned["sensor_b_g"].to_numpy(dtype=float)
    t = aligned["time_s"].to_numpy(dtype=float)

    sensor_a_stats = compute_time_domain_metrics(sensor_a)
    sensor_b_stats = compute_time_domain_metrics(sensor_b)

    # FFT/PSD must use original windowed signals (before resampling/alignment).
    start_utc = _to_utc(cfg["window"]["start_utc"])
    end_utc = start_utc + timedelta(seconds=int(cfg["window"]["duration_seconds"]))
    pipeline_cfg = root_cfg.get("pipeline", {})
    sa_cfg = cfg["sensor_a"]
    sb_cfg = cfg["sensor_b"]
    sa_file = project_root / sa_cfg.get("file", pipeline_cfg.get("sensor_a", {}).get("processed_file", ""))
    sb_file = project_root / sb_cfg.get("file", pipeline_cfg.get("sensor_b", {}).get("processed_file", ""))

    raw_a = _load_window_raw(
        file_path=sa_file,
        time_col=sa_cfg["time_column"],
        value_col=sa_cfg["value_column"],
        start_utc=start_utc,
        end_utc=end_utc,
    )
    raw_b = _load_window_raw(
        file_path=sb_file,
        time_col=sb_cfg["time_column"],
        value_col=sb_cfg["value_column"],
        start_utc=start_utc,
        end_utc=end_utc,
    )
    if raw_a.empty or raw_b.empty:
        raise RuntimeError("No raw windowed data for FFT/PSD.")

    a_t = (raw_a[sa_cfg["time_column"]] - start_utc).dt.total_seconds().to_numpy()
    b_t = (raw_b[sb_cfg["time_column"]] - start_utc).dt.total_seconds().to_numpy()
    a_raw_g = _to_g(raw_a[sa_cfg["value_column"]].to_numpy(dtype=float), sa_cfg["unit"])
    b_raw_g = _to_g(raw_b[sb_cfg["value_column"]].to_numpy(dtype=float), sb_cfg["unit"])
    fs_a_raw = _estimate_fs(a_t)
    fs_b_raw = _estimate_fs(b_t)
    if fs_a_raw <= 0 or fs_b_raw <= 0:
        raise RuntimeError("Unable to estimate raw sampling frequency for FFT/PSD.")

    freq_a, mag_a = compute_fft(a_raw_g, fs_a_raw)
    freq_b, mag_b = compute_fft(b_raw_g, fs_b_raw)
    sensor_a_freq = compute_frequency_metrics(freq_a, mag_a)
    sensor_b_freq = compute_frequency_metrics(freq_b, mag_b)

    n_fft_a = min(4096, max(256, len(a_raw_g) // 4))
    n_fft_b = min(4096, max(256, len(b_raw_g) // 4))
    psd_f_a, psd_a = compute_psd(a_raw_g, fs_a_raw, n_fft=n_fft_a, window="hann")
    psd_f_b, psd_b = compute_psd(b_raw_g, fs_b_raw, n_fft=n_fft_b, window="hann")

    from src.analysis.correlation import compute_correlation
    from src.analysis.comparison import compute_error_metrics

    correlation = compute_correlation(sensor_a, sensor_b)
    error_metrics = compute_error_metrics(sensor_a, sensor_b)
    bland = bland_altman_analysis(sensor_a, sensor_b)

    results = {
        "sensor_a_stats": sensor_a_stats,
        "sensor_b_stats": sensor_b_stats,
        "correlation": correlation,
        "error_metrics": error_metrics,
        "sensor_a_freq": sensor_a_freq,
        "sensor_b_freq": sensor_b_freq,
    }

    full_cfg = cfg.get("full_report", {})
    report_md = project_root / full_cfg.get("report_md", "results/reports/full_report.md")
    metrics_csv = project_root / full_cfg.get(
        "metrics_csv", "results/tables/full_report_metrics.csv"
    )
    figures_dir = project_root / full_cfg.get("figures_dir", "results/figures/full_report")
    figures_dir.mkdir(parents=True, exist_ok=True)
    display_cfg = full_cfg.get("display", {})
    max_freq_hz = float(display_cfg.get("max_frequency_hz", fs / 2))
    max_freq_hz = max(0.1, min(max_freq_hz, fs / 2))
    fft_display_cfg = display_cfg.get("fft", {})
    fft_auto_yscale = bool(fft_display_cfg.get("auto_yscale", True))
    fft_y_percentile = float(fft_display_cfg.get("y_percentile", 99.5))
    fft_exclude_dc = bool(fft_display_cfg.get("exclude_dc", True))
    top_n_peaks = int(fft_display_cfg.get("top_n_peaks", 5))

    fig_time = figures_dir / "time_series.png"
    fig_fft = figures_dir / "fft.png"
    fig_psd = figures_dir / "psd.png"
    fig_scatter = figures_dir / "scatter.png"
    fig_ba = figures_dir / "bland_altman.png"

    plot_time_series(
        t,
        sensor_a,
        sensor_b,
        labels=(f"Sensor A ({sa_cfg['value_column']})", f"Sensor B ({sb_cfg['value_column']})"),
        title="Time Series Comparison",
        ylabel="Acceleration (g)",
        save_path=str(fig_time),
    )
    fft_ylim = None
    if fft_auto_yscale:
        mask_a = freq_a <= max_freq_hz
        mask_b = freq_b <= max_freq_hz
        if fft_exclude_dc:
            mask_a &= freq_a > 0
            mask_b &= freq_b > 0
        y_vals = np.concatenate([mag_a[mask_a], mag_b[mask_b]])
        if y_vals.size > 0:
            y_top = np.percentile(y_vals, fft_y_percentile)
            y_top = max(y_top * 1.2, 1e-6)
            fft_ylim = (0, y_top)

    # Peak detection in the first max_freq_hz band.
    mask_a_50 = (freq_a > 0) & (freq_a <= max_freq_hz)
    mask_b_50 = (freq_b > 0) & (freq_b <= max_freq_hz)
    fa = freq_a[mask_a_50]
    ma = mag_a[mask_a_50]
    fb = freq_b[mask_b_50]
    mb = mag_b[mask_b_50]

    def _top_peaks(freq: np.ndarray, mag: np.ndarray, top_n: int) -> pd.DataFrame:
        if len(freq) < 3:
            return pd.DataFrame(columns=["frequency_hz", "magnitude"])
        from scipy import signal

        h = float(np.mean(mag) + np.std(mag))
        peaks, props = signal.find_peaks(mag, height=h)
        if len(peaks) == 0:
            # fallback: select strongest bins directly
            idx = np.argsort(mag)[-top_n:][::-1]
            return pd.DataFrame(
                {"frequency_hz": freq[idx], "magnitude": mag[idx]}
            ).sort_values("magnitude", ascending=False, ignore_index=True)
        out = pd.DataFrame(
            {
                "frequency_hz": freq[peaks],
                "magnitude": props["peak_heights"],
            }
        ).sort_values("magnitude", ascending=False, ignore_index=True)
        return out.head(top_n)

    peaks_a = _top_peaks(fa, ma, top_n_peaks)
    peaks_b = _top_peaks(fb, mb, top_n_peaks)
    peaks_a["sensor"] = "sensor_a"
    peaks_b["sensor"] = "sensor_b"
    peaks_df = pd.concat([peaks_a, peaks_b], ignore_index=True)
    peaks_csv = project_root / full_cfg.get(
        "peaks_csv", "results/tables/comparison_pair_fft_peaks_0_50hz.csv"
    )
    peaks_csv.parent.mkdir(parents=True, exist_ok=True)
    peaks_df = peaks_df[["sensor", "frequency_hz", "magnitude"]]
    peaks_df.to_csv(peaks_csv, index=False)

    plot_fft(
        freq_a,
        mag_a,
        freq_b=freq_b,
        mag_b=mag_b,
        labels=("Sensor A", "Sensor B"),
        title="FFT Comparison",
        xlim=(0, max_freq_hz),
        ylim=fft_ylim,
        save_path=str(fig_fft),
    )
    plot_psd(
        psd_f_a,
        psd_a,
        freq_b=psd_f_b,
        psd_b=psd_b,
        labels=("Sensor A", "Sensor B"),
        title="PSD Comparison",
        xlim=(0, max_freq_hz),
        save_path=str(fig_psd),
    )
    plot_comparison(
        sensor_a,
        sensor_b,
        labels=("Sensor A (g)", "Sensor B (g)"),
        title="Scatter Comparison",
        save_path=str(fig_scatter),
    )
    plot_bland_altman(
        bland["mean_values"],
        bland["differences"],
        bland["mean_difference"],
        bland["upper_loa"],
        bland["lower_loa"],
        title="Bland-Altman Plot",
        save_path=str(fig_ba),
    )

    # Save tabular metrics
    export_metrics_to_csv(results, str(metrics_csv))

    # Save 3-panel time series figure with UTC axis
    fig_3panel = figures_dir / "time_series_3panel.png"
    _plot_3panel_utc(
        raw_a=raw_a,
        raw_b=raw_b,
        time_col_a=sa_cfg["time_column"],
        time_col_b=sb_cfg["time_column"],
        val_col_a=sa_cfg["value_column"],
        val_col_b=sb_cfg["value_column"],
        start_utc=start_utc,
        duration_s=int(cfg["window"]["duration_seconds"]),
        save_path=str(fig_3panel),
    )

    # Save markdown report
    report_path = generate_report(
        comparison_results=results,
        output_path=str(report_md),
        title=f"Full Comparison Report: Sensor A {sa_cfg['value_column']} vs Sensor B {sb_cfg['value_column']}",
        figures_dir=figures_dir,
        report_md=report_md,
    )

    # Save compact summary CSV
    summary = pd.DataFrame(
        [
            {
                "window_start_utc": pair_result["window_start_utc"],
                "window_end_utc": pair_result["window_end_utc"],
                "n_samples": pair_result["metrics"]["n_samples"],
                "fs_target_hz": pair_result["metrics"]["fs_target_hz"],
                "lag_seconds": pair_result["metrics"]["lag_seconds"],
                "pearson_r": pair_result["metrics"]["pearson_r"],
                "rmse": pair_result["metrics"]["rmse"],
                "mae": pair_result["metrics"]["mae"],
            }
        ]
    )
    summary_path = metrics_csv.with_name(metrics_csv.stem + "_summary.csv")
    summary.to_csv(summary_path, index=False)

    return {
        "report_md": report_path,
        "metrics_csv": str(metrics_csv),
        "peaks_csv": str(peaks_csv),
        "summary_csv": str(summary_path),
        "figures_dir": str(figures_dir),
        "aligned_csv": pair_result["aligned_path"],
    }
