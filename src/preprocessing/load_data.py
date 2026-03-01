"""
Load and preprocess raw data for Sensor_A (Setup5) and Sensor_B (ADXL355).
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from .cleaning import remove_offset
from .filtering import highpass_filter, lowpass_filter
from .time_conversion import add_relative_time_column, add_utc_column, get_time_info


def load_adxl355(file_path: str | Path) -> pd.DataFrame:
    """
    Load raw ADXL355 CSV file.
    """
    file_path = Path(file_path)
    return pd.read_csv(file_path)


def preprocess_adxl355(
    input_file: str | Path,
    output_file: str | Path | None = None,
    apply_filter: bool = True,
    remove_dc_offset: bool = True,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Preprocess ADXL355 data.
    """
    input_file = Path(input_file)
    df = load_adxl355(input_file).copy()

    if verbose:
        print("[adxl355] input:", input_file)

    df = add_utc_column(df, timestamp_col="timestamp", utc_col="datetime_utc")
    df = add_relative_time_column(df, timestamp_col="timestamp", relative_col="time_s")
    info = get_time_info(df, timestamp_col="timestamp")
    fs = info["sampling_rate_hz"]

    acc_cols = ["accX(g)", "accY(g)", "accZ(g)"]
    if remove_dc_offset:
        for col in acc_cols:
            df[col] = remove_offset(df[col].to_numpy(dtype=float), method="mean")

    if apply_filter:
        for col in acc_cols:
            filtered = highpass_filter(df[col].to_numpy(dtype=float), cutoff=0.5, fs=fs, order=2)
            filtered = lowpass_filter(filtered, cutoff=500, fs=fs, order=4)
            df[f"{col}_filtered"] = filtered

    df["acc_magnitude"] = np.sqrt(df["accX(g)"] ** 2 + df["accY(g)"] ** 2 + df["accZ(g)"] ** 2)

    cols = ["timestamp", "datetime_utc", "time_s", "accX(g)", "accY(g)", "accZ(g)", "acc_magnitude"]
    if apply_filter:
        cols += [f"{c}_filtered" for c in acc_cols]
    out_df = df[cols]

    if output_file is not None:
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(output_file, index=False)
        if verbose:
            print("[adxl355] saved:", output_file)

    return out_df


def load_setup5_with_metadata(file_path: str | Path) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Load Setup5 CSV with metadata lines that start with '#'.

    The function preserves original column names such as:
    - Time (s)
    - Channel 1 (...)
    - Channel 6 (...)
    """
    file_path = Path(file_path)
    metadata: Dict[str, str] = {}
    lines = file_path.read_text(encoding="latin1").splitlines()

    for line in lines:
        if not line.startswith("#"):
            break
        content = line[1:].strip()
        if ":" in content:
            key, value = content.split(":", 1)
            metadata[key.strip()] = value.strip().rstrip(",").strip()

    # Setup5 format: 5 metadata lines then header line
    df = pd.read_csv(file_path, skiprows=5, encoding="latin1")
    # Normalize accidental trailing spaces in exported headers.
    df.columns = [str(c).strip() for c in df.columns]
    return df, metadata


def detect_setup5_channel_columns(columns: List[str]) -> List[str]:
    """
    Detect and sort Setup5 channel columns by channel index.
    """
    pattern = re.compile(r"^Channel\s+(\d+)(?:\s+\(|$)")
    pairs = []
    for col in columns:
        match = pattern.match(col)
        if match:
            pairs.append((int(match.group(1)), col))
    pairs.sort(key=lambda x: x[0])
    return [col for _, col in pairs]


def preprocess_setup5_keep_channels(
    input_file: str | Path,
    output_file: str | Path | None = None,
    apply_filter: bool = True,
    remove_dc: bool = True,
    convert_to_g: bool = True,
    timezone_offset_hours: int = 0,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Preprocess Setup5 data and keep original Channel names.

    Added columns:
    - timestamp_unix
    - datetime_utc
    - time_s
    - <Channel n (...)>_filtered (if apply_filter=True)

    Notes:
    - Supports two timestamp formats:
        * Old format: "Time (s)" — relative seconds from a start time in metadata.
        * New format: "Time (UTC epoch s)" — Unix epoch seconds, possibly in local timezone.
    - timezone_offset_hours: hours to add to epoch to correct to UTC (e.g. 7 for UTC+7).
    - If convert_to_g=True, channel values are converted from m/s^2 to g
      and column units are renamed to "(g)" while keeping "Channel n" naming.
    """
    input_file = Path(input_file)
    df, metadata = load_setup5_with_metadata(input_file)

    channel_cols = detect_setup5_channel_columns(list(df.columns))
    if not channel_cols:
        raise ValueError("No channel columns detected in Setup5 file.")

    df = df.copy()
    if "Time (UTC epoch s)" in df.columns:
        tz_offset_s = timezone_offset_hours * 3600
        df["timestamp_unix"] = df["Time (UTC epoch s)"].astype(float) + tz_offset_s
        df["datetime_utc"] = pd.to_datetime(df["timestamp_unix"], unit="s", utc=True)
        df["time_s"] = df["timestamp_unix"] - df["timestamp_unix"].iloc[0]
        time_col_name = "Time (UTC epoch s)"
    elif "Time (s)" in df.columns:
        start_time_str = metadata.get("Start Time") or metadata.get("Start Time (UTC)")
        if not start_time_str:
            raise ValueError("Missing 'Start Time' in Setup5 metadata.")
        start_utc = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        df["time_s"] = df["Time (s)"].astype(float)
        df["datetime_utc"] = start_utc + pd.to_timedelta(df["time_s"], unit="s")
        df["timestamp_unix"] = df["datetime_utc"].astype("int64") / 1e9
        time_col_name = "Time (s)"
    else:
        raise ValueError("Missing required time column ('Time (s)' or 'Time (UTC epoch s)') in Setup5 file.")

    fs = 1.0 / np.mean(np.diff(df["time_s"].to_numpy()))

    if remove_dc:
        for col in channel_cols:
            df[col] = remove_offset(df[col].to_numpy(dtype=float), method="mean")

    if apply_filter:
        for col in channel_cols:
            filtered = highpass_filter(df[col].to_numpy(dtype=float), cutoff=0.5, fs=fs, order=2)
            filtered = lowpass_filter(filtered, cutoff=500, fs=fs, order=4)
            df[f"{col}_filtered"] = filtered

    ordered_cols = ["timestamp_unix", "datetime_utc", "time_s", time_col_name] + channel_cols
    filtered_cols: List[str] = []
    if apply_filter:
        filtered_cols = [f"{col}_filtered" for col in channel_cols]
        ordered_cols += filtered_cols

    if convert_to_g:
        g0 = 9.80665
        rename_map: Dict[str, str] = {}

        for col in channel_cols:
            match = re.match(r"^Channel\s+(\d+)", col)
            if match:
                new_col = f"Channel {match.group(1)} (g)"
            else:
                new_col = col.replace("(m/s²)", "(g)").replace("(m/s^2)", "(g)")
                if new_col == col:
                    new_col = f"{col} (g)"
            df[new_col] = df[col].to_numpy(dtype=float) / g0
            rename_map[col] = new_col

        for col in filtered_cols:
            match = re.match(r"^Channel\s+(\d+)", col)
            if match:
                new_col = f"Channel {match.group(1)}_filtered (g)"
            else:
                new_col = col.replace("(m/s²)", "(g)").replace("(m/s^2)", "(g)")
                if new_col == col:
                    new_col = f"{col} (g)"
            df[new_col] = df[col].to_numpy(dtype=float) / g0
            rename_map[col] = new_col

        ordered_cols = [rename_map.get(c, c) for c in ordered_cols]

    out_df = df[ordered_cols]

    if output_file is not None:
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(output_file, index=False)
        if verbose:
            print("[setup5] saved:", output_file)

    return out_df
