"""
Time conversion utilities for sensor data
"""

import numpy as np
import pandas as pd
from datetime import datetime, timezone
from typing import Union, Optional


def unix_to_utc(
    timestamp: Union[float, np.ndarray, pd.Series],
    output_format: str = 'datetime'
) -> Union[datetime, pd.Series, np.ndarray]:
    """
    Convert Unix timestamp to UTC datetime.
    
    Parameters
    ----------
    timestamp : float, array-like, or pd.Series
        Unix timestamp(s) in seconds
    output_format : str
        Output format: 'datetime', 'string', 'iso'
    
    Returns
    -------
    datetime, pd.Series, or np.ndarray
        Converted datetime(s)
    """
    if isinstance(timestamp, (int, float)):
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        if output_format == 'string':
            return dt.strftime('%Y-%m-%d %H:%M:%S.%f')
        elif output_format == 'iso':
            return dt.isoformat()
        return dt
    
    if isinstance(timestamp, pd.Series):
        dt_series = pd.to_datetime(timestamp, unit='s', utc=True)
        if output_format == 'string':
            return dt_series.dt.strftime('%Y-%m-%d %H:%M:%S.%f')
        elif output_format == 'iso':
            return dt_series.dt.isoformat()
        return dt_series
    
    timestamps = np.asarray(timestamp)
    dt_array = pd.to_datetime(timestamps, unit='s', utc=True)
    return dt_array


def unix_to_relative_time(
    timestamp: Union[np.ndarray, pd.Series],
    reference: str = 'first'
) -> Union[np.ndarray, pd.Series]:
    """
    Convert Unix timestamp to relative time (seconds from start).
    
    Parameters
    ----------
    timestamp : array-like or pd.Series
        Unix timestamps
    reference : str
        Reference point: 'first' (first sample) or 'zero' (Unix epoch)
    
    Returns
    -------
    array-like or pd.Series
        Relative time in seconds
    """
    if reference == 'first':
        return timestamp - timestamp.iloc[0] if isinstance(timestamp, pd.Series) else timestamp - timestamp[0]
    return timestamp


def add_utc_column(
    df: pd.DataFrame,
    timestamp_col: str = 'timestamp',
    utc_col: str = 'datetime_utc'
) -> pd.DataFrame:
    """
    Add UTC datetime column to DataFrame.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with Unix timestamp
    timestamp_col : str
        Name of timestamp column
    utc_col : str
        Name for new UTC datetime column
    
    Returns
    -------
    pd.DataFrame
        DataFrame with added UTC column
    """
    df = df.copy()
    df[utc_col] = pd.to_datetime(df[timestamp_col], unit='s', utc=True)
    return df


def add_relative_time_column(
    df: pd.DataFrame,
    timestamp_col: str = 'timestamp',
    relative_col: str = 'time_s'
) -> pd.DataFrame:
    """
    Add relative time column (seconds from start) to DataFrame.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with Unix timestamp
    timestamp_col : str
        Name of timestamp column
    relative_col : str
        Name for new relative time column
    
    Returns
    -------
    pd.DataFrame
        DataFrame with added relative time column
    """
    df = df.copy()
    df[relative_col] = df[timestamp_col] - df[timestamp_col].iloc[0]
    return df


def get_time_info(df: pd.DataFrame, timestamp_col: str = 'timestamp') -> dict:
    """
    Get time information from DataFrame.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with Unix timestamp
    timestamp_col : str
        Name of timestamp column
    
    Returns
    -------
    dict
        Dictionary with time information
    """
    timestamps = df[timestamp_col]
    
    start_unix = timestamps.iloc[0]
    end_unix = timestamps.iloc[-1]
    
    start_utc = datetime.fromtimestamp(start_unix, tz=timezone.utc)
    end_utc = datetime.fromtimestamp(end_unix, tz=timezone.utc)
    
    duration = end_unix - start_unix
    n_samples = len(timestamps)
    
    dt = np.diff(timestamps)
    sampling_rate = 1.0 / np.mean(dt) if len(dt) > 0 else 0
    
    return {
        'start_unix': start_unix,
        'end_unix': end_unix,
        'start_utc': start_utc,
        'end_utc': end_utc,
        'duration_s': duration,
        'n_samples': n_samples,
        'sampling_rate_hz': sampling_rate,
        'dt_mean_ms': np.mean(dt) * 1000 if len(dt) > 0 else 0,
        'dt_std_ms': np.std(dt) * 1000 if len(dt) > 0 else 0
    }
