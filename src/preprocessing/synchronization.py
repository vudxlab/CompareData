"""
Time synchronization functions for multi-sensor data
"""

import numpy as np
from scipy import signal
from typing import Tuple, Union


def find_time_offset(
    signal_a: np.ndarray,
    signal_b: np.ndarray,
    fs: float,
    max_lag: float = 1.0
) -> Tuple[float, float]:
    """
    Find time offset between two signals using cross-correlation.
    
    Parameters
    ----------
    signal_a : np.ndarray
        Reference signal
    signal_b : np.ndarray
        Signal to align
    fs : float
        Sampling frequency in Hz
    max_lag : float
        Maximum lag to search in seconds
    
    Returns
    -------
    tuple
        (offset_seconds, correlation_coefficient)
    """
    max_lag_samples = int(max_lag * fs)
    
    correlation = signal.correlate(signal_a, signal_b, mode='full')
    lags = signal.correlation_lags(len(signal_a), len(signal_b), mode='full')
    
    valid_idx = np.abs(lags) <= max_lag_samples
    correlation = correlation[valid_idx]
    lags = lags[valid_idx]
    
    best_idx = np.argmax(np.abs(correlation))
    best_lag = lags[best_idx]
    best_corr = correlation[best_idx] / (np.std(signal_a) * np.std(signal_b) * len(signal_a))
    
    offset_seconds = best_lag / fs
    
    return offset_seconds, best_corr


def synchronize_signals(
    signal_a: np.ndarray,
    signal_b: np.ndarray,
    offset_samples: int
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Synchronize two signals by applying offset.
    
    Parameters
    ----------
    signal_a : np.ndarray
        Reference signal
    signal_b : np.ndarray
        Signal to align
    offset_samples : int
        Offset in samples (positive = signal_b is delayed)
    
    Returns
    -------
    tuple
        (aligned_signal_a, aligned_signal_b)
    """
    if offset_samples > 0:
        signal_b_aligned = signal_b[offset_samples:]
        signal_a_aligned = signal_a[:len(signal_b_aligned)]
    elif offset_samples < 0:
        signal_a_aligned = signal_a[-offset_samples:]
        signal_b_aligned = signal_b[:len(signal_a_aligned)]
    else:
        signal_a_aligned = signal_a
        signal_b_aligned = signal_b
    
    min_len = min(len(signal_a_aligned), len(signal_b_aligned))
    
    return signal_a_aligned[:min_len], signal_b_aligned[:min_len]


def resample_to_common_rate(
    signal_a: np.ndarray,
    signal_b: np.ndarray,
    fs_a: float,
    fs_b: float,
    target_fs: float = None
) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    Resample signals to a common sampling rate.
    
    Parameters
    ----------
    signal_a : np.ndarray
        First signal
    signal_b : np.ndarray
        Second signal
    fs_a : float
        Sampling rate of signal_a
    fs_b : float
        Sampling rate of signal_b
    target_fs : float, optional
        Target sampling rate. If None, uses the higher rate.
    
    Returns
    -------
    tuple
        (resampled_a, resampled_b, target_fs)
    """
    if target_fs is None:
        target_fs = max(fs_a, fs_b)
    
    if fs_a != target_fs:
        num_samples = int(len(signal_a) * target_fs / fs_a)
        signal_a = signal.resample(signal_a, num_samples)
    
    if fs_b != target_fs:
        num_samples = int(len(signal_b) * target_fs / fs_b)
        signal_b = signal.resample(signal_b, num_samples)
    
    return signal_a, signal_b, target_fs
