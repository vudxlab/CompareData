"""
Statistical analysis functions for accelerometer data
"""

import numpy as np
from scipy import stats
from typing import Dict, Union


def compute_time_domain_metrics(data: np.ndarray) -> Dict[str, float]:
    """
    Compute time-domain statistical metrics.
    
    Parameters
    ----------
    data : np.ndarray
        Input signal
    
    Returns
    -------
    dict
        Dictionary of computed metrics
    """
    metrics = {}
    
    metrics['mean'] = np.mean(data)
    metrics['std'] = np.std(data)
    metrics['variance'] = np.var(data)
    metrics['rms'] = np.sqrt(np.mean(data**2))
    metrics['peak'] = np.max(np.abs(data))
    metrics['peak_to_peak'] = np.max(data) - np.min(data)
    metrics['crest_factor'] = metrics['peak'] / metrics['rms'] if metrics['rms'] > 0 else 0
    metrics['kurtosis'] = stats.kurtosis(data)
    metrics['skewness'] = stats.skew(data)
    metrics['min'] = np.min(data)
    metrics['max'] = np.max(data)
    
    percentiles = [5, 25, 50, 75, 95]
    for p in percentiles:
        metrics[f'percentile_{p}'] = np.percentile(data, p)
    
    return metrics


def compute_rms_over_windows(
    data: np.ndarray,
    window_size: int,
    overlap: float = 0.5
) -> np.ndarray:
    """
    Compute RMS values over sliding windows.
    
    Parameters
    ----------
    data : np.ndarray
        Input signal
    window_size : int
        Window size in samples
    overlap : float
        Overlap ratio (0 to 1)
    
    Returns
    -------
    np.ndarray
        Array of RMS values
    """
    step = int(window_size * (1 - overlap))
    n_windows = (len(data) - window_size) // step + 1
    
    rms_values = np.zeros(n_windows)
    for i in range(n_windows):
        start = i * step
        end = start + window_size
        rms_values[i] = np.sqrt(np.mean(data[start:end]**2))
    
    return rms_values


def compute_vector_magnitude(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray
) -> np.ndarray:
    """
    Compute vector magnitude from 3-axis accelerometer data.
    
    Parameters
    ----------
    x, y, z : np.ndarray
        Acceleration components
    
    Returns
    -------
    np.ndarray
        Vector magnitude
    """
    return np.sqrt(x**2 + y**2 + z**2)
