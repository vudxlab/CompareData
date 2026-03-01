"""
Shared helper functions used by window_compare and full_plan_compare.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd


def to_utc(value: str) -> datetime:
    """Parse an ISO 8601 string to a timezone-aware UTC datetime."""
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def to_g(values: np.ndarray, unit: str) -> np.ndarray:
    """Convert acceleration values to g-force units."""
    u = unit.lower()
    if u in {"g", "g-force"}:
        return values
    if u in {"m/s^2", "m/s2"}:
        return values / 9.80665
    raise ValueError(f"Unsupported unit: {unit}")


def estimate_fs(t: np.ndarray) -> float:
    """Estimate sampling frequency from a time array."""
    dt = np.diff(t)
    dt = dt[dt > 0]
    if len(dt) == 0:
        return 0.0
    return float(1.0 / np.mean(dt))


def load_window_raw(
    file_path: Path,
    time_col: str,
    value_col: str,
    start_utc: datetime,
    end_utc: datetime,
    chunksize: int = 200000,
) -> pd.DataFrame:
    """Load a time window from a CSV file, parsing timestamps robustly."""
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
