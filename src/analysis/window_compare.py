"""
Config-driven single-channel comparison in a time window.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd

from src.analysis.comparison import compute_error_metrics
from src.analysis.correlation import compute_correlation
from src.utils.config import get_project_root, load_config


@dataclass
class SeriesSpec:
    file: Path
    time_column: str
    value_column: str
    unit: str


def _to_utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _load_window(
    spec: SeriesSpec,
    start_utc: datetime,
    end_utc: datetime,
    chunksize: int = 200000,
) -> pd.DataFrame:
    cols = [spec.time_column, spec.value_column]
    parts = []
    for chunk in pd.read_csv(spec.file, usecols=cols, chunksize=chunksize):
        raw_t = chunk[spec.time_column]
        # Robust parse:
        # - numeric column -> Unix seconds
        # - string column -> mixed datetime format
        if pd.api.types.is_numeric_dtype(raw_t):
            t = pd.to_datetime(raw_t, unit="s", utc=True, errors="coerce")
        else:
            t = pd.to_datetime(raw_t, utc=True, errors="coerce", format="mixed")
        m = (t >= start_utc) & (t < end_utc)
        if m.any():
            out = chunk.loc[m].copy()
            out[spec.time_column] = t.loc[m]
            parts.append(out)
    if not parts:
        return pd.DataFrame(columns=cols)
    return pd.concat(parts, ignore_index=True)


def _to_g(values: np.ndarray, unit: str) -> np.ndarray:
    if unit.lower() in {"g", "g-force"}:
        return values
    if unit.lower() in {"m/s^2", "m/s2"}:
        return values / 9.80665
    raise ValueError(f"Unsupported unit: {unit}")


def _estimate_fs(t: np.ndarray) -> float:
    dt = np.diff(t)
    dt = dt[dt > 0]
    if len(dt) == 0:
        return 0.0
    return float(1.0 / np.mean(dt))


def _resample_linear(t: np.ndarray, x: np.ndarray, fs: float) -> Tuple[np.ndarray, np.ndarray]:
    t0, t1 = float(t[0]), float(t[-1])
    n = int(np.floor((t1 - t0) * fs)) + 1
    t_new = t0 + np.arange(n) / fs
    x_new = np.interp(t_new, t, x)
    return t_new, x_new


def _align_xcorr(ref: np.ndarray, test: np.ndarray, fs: float, max_lag_s: float) -> Tuple[np.ndarray, np.ndarray, float]:
    max_lag = int(max_lag_s * fs)
    corr = np.correlate(ref - ref.mean(), test - test.mean(), mode="full")
    lags = np.arange(-len(test) + 1, len(ref))
    valid = np.abs(lags) <= max_lag
    lag = int(lags[valid][np.argmax(corr[valid])])

    if lag > 0:
        ref_a = ref[lag:]
        test_a = test[: len(ref_a)]
    elif lag < 0:
        test_a = test[-lag:]
        ref_a = ref[: len(test_a)]
    else:
        ref_a, test_a = ref, test

    n = min(len(ref_a), len(test_a))
    return ref_a[:n], test_a[:n], lag / fs


def compare_single_pair_from_config(config_path: str = "configs/project.yaml") -> Dict[str, object]:
    """
    Compare one configured channel pair in a configured UTC window.
    """
    project_root = get_project_root()
    root_cfg = load_config(config_path)
    if "comparison" in root_cfg:
        cfg = root_cfg.get("comparison", {})
    else:
        pipeline_cfg = root_cfg.get("pipeline", {})
        cfg = dict(pipeline_cfg.get("comparison", {}))
        sensor_a_cfg = dict(cfg.get("sensor_a", {}))
        sensor_b_cfg = dict(cfg.get("sensor_b", {}))
        if "file" not in sensor_a_cfg:
            sensor_a_cfg["file"] = pipeline_cfg.get("sensor_a", {}).get("processed_file")
        if "file" not in sensor_b_cfg:
            sensor_b_cfg["file"] = pipeline_cfg.get("sensor_b", {}).get("processed_file")
        cfg["sensor_a"] = sensor_a_cfg
        cfg["sensor_b"] = sensor_b_cfg

    start_utc = _to_utc(cfg["window"]["start_utc"])
    end_utc = start_utc + timedelta(seconds=int(cfg["window"]["duration_seconds"]))

    sa = cfg["sensor_a"]
    sb = cfg["sensor_b"]
    spec_a = SeriesSpec(
        file=project_root / sa["file"],
        time_column=sa["time_column"],
        value_column=sa["value_column"],
        unit=sa["unit"],
    )
    spec_b = SeriesSpec(
        file=project_root / sb["file"],
        time_column=sb["time_column"],
        value_column=sb["value_column"],
        unit=sb["unit"],
    )

    df_a = _load_window(spec_a, start_utc, end_utc)
    df_b = _load_window(spec_b, start_utc, end_utc)
    if df_a.empty or df_b.empty:
        raise RuntimeError("No data found in configured window for one of the sensors.")

    a_t = (df_a[spec_a.time_column] - start_utc).dt.total_seconds().to_numpy()
    b_t = (df_b[spec_b.time_column] - start_utc).dt.total_seconds().to_numpy()
    a_v = _to_g(df_a[spec_a.value_column].to_numpy(dtype=float), spec_a.unit)
    b_v = _to_g(df_b[spec_b.value_column].to_numpy(dtype=float), spec_b.unit)

    fs_a = _estimate_fs(a_t)
    fs_b = _estimate_fs(b_t)
    resampling_cfg = cfg.get("resampling", {})
    resampling_enabled = bool(resampling_cfg.get("enabled", True))

    if resampling_enabled:
        cfg_target_fs = float(resampling_cfg.get("target_fs_hz", 0.0))
        fs_target = cfg_target_fs if cfg_target_fs > 0 else min(fs_a, fs_b)
        if fs_target <= 0:
            raise RuntimeError("Unable to estimate sampling frequency.")

        ta, xa = _resample_linear(a_t, a_v, fs_target)
        tb, xb = _resample_linear(b_t, b_v, fs_target)
        t0 = max(ta[0], tb[0])
        t1 = min(ta[-1], tb[-1])
        tc = np.arange(t0, t1, 1.0 / fs_target)
        xa = np.interp(tc, ta, xa)
        xb = np.interp(tc, tb, xb)
    else:
        # No resampling mode: only safe when sampling rates are effectively identical.
        if fs_a <= 0 or fs_b <= 0:
            raise RuntimeError("Unable to estimate sampling frequency in no-resample mode.")
        rel_diff = abs(fs_a - fs_b) / max(fs_a, fs_b)
        if rel_diff > 0.01:
            raise RuntimeError(
                f"no-resample mode requires similar sampling rates, got fs_a={fs_a:.3f} Hz, fs_b={fs_b:.3f} Hz. "
                "Enable resampling or pre-align sampling rates first."
            )

        fs_target = min(fs_a, fs_b)
        n = min(len(a_v), len(b_v))
        xa = a_v[:n]
        xb = b_v[:n]

    lag_s = 0.0
    if cfg.get("alignment", {}).get("enabled", True):
        max_lag_s = float(cfg.get("alignment", {}).get("max_lag_seconds", 2.0))
        xa, xb, lag_s = _align_xcorr(xa, xb, fs_target, max_lag_s=max_lag_s)

    corr = compute_correlation(xa, xb)
    err = compute_error_metrics(xa, xb)
    metrics = {
        "sensor_a_column": spec_a.value_column,
        "sensor_b_column": spec_b.value_column,
        "n_samples": len(xa),
        "fs_target_hz": fs_target,
        "lag_seconds": lag_s,
        "pearson_r": corr["pearson_r"],
        "r_squared": corr["r_squared"],
        "mae": err["mae"],
        "rmse": err["rmse"],
        "nrmse": err["nrmse"],
    }

    out_cfg = cfg.get("output", {})
    metrics_path = project_root / out_cfg.get("metrics_csv", "results/tables/comparison_pair_metrics.csv")
    aligned_path = project_root / out_cfg.get("aligned_csv", "results/tables/comparison_pair_aligned.csv")
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    aligned_path.parent.mkdir(parents=True, exist_ok=True)

    pd.DataFrame([metrics]).to_csv(metrics_path, index=False)
    pd.DataFrame(
        {
            "time_s": np.arange(len(xa)) / fs_target,
            "sensor_a_g": xa,
            "sensor_b_g": xb,
            "error_g": xb - xa,
        }
    ).to_csv(aligned_path, index=False)

    return {
        "window_start_utc": start_utc.isoformat(),
        "window_end_utc": end_utc.isoformat(),
        "metrics_path": str(metrics_path),
        "aligned_path": str(aligned_path),
        "metrics": metrics,
    }
