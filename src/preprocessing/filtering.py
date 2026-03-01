"""
Signal filtering functions for accelerometer data
"""

import numpy as np
from scipy import signal
from typing import Union, Tuple


def lowpass_filter(
    data: np.ndarray,
    cutoff: float,
    fs: float,
    order: int = 4
) -> np.ndarray:
    """
    Apply Butterworth low-pass filter.
    
    Parameters
    ----------
    data : np.ndarray
        Input signal
    cutoff : float
        Cutoff frequency in Hz
    fs : float
        Sampling frequency in Hz
    order : int
        Filter order
    
    Returns
    -------
    np.ndarray
        Filtered signal
    """
    nyq = 0.5 * fs
    normalized_cutoff = cutoff / nyq
    
    if normalized_cutoff >= 1:
        return data
    
    b, a = signal.butter(order, normalized_cutoff, btype='low')
    filtered = signal.filtfilt(b, a, data)
    
    return filtered


def highpass_filter(
    data: np.ndarray,
    cutoff: float,
    fs: float,
    order: int = 4
) -> np.ndarray:
    """
    Apply Butterworth high-pass filter.
    
    Parameters
    ----------
    data : np.ndarray
        Input signal
    cutoff : float
        Cutoff frequency in Hz
    fs : float
        Sampling frequency in Hz
    order : int
        Filter order
    
    Returns
    -------
    np.ndarray
        Filtered signal
    """
    nyq = 0.5 * fs
    normalized_cutoff = cutoff / nyq
    
    if normalized_cutoff <= 0:
        return data
    
    b, a = signal.butter(order, normalized_cutoff, btype='high')
    filtered = signal.filtfilt(b, a, data)
    
    return filtered


def bandpass_filter(
    data: np.ndarray,
    lowcut: float,
    highcut: float,
    fs: float,
    order: int = 4
) -> np.ndarray:
    """
    Apply Butterworth band-pass filter.
    
    Parameters
    ----------
    data : np.ndarray
        Input signal
    lowcut : float
        Low cutoff frequency in Hz
    highcut : float
        High cutoff frequency in Hz
    fs : float
        Sampling frequency in Hz
    order : int
        Filter order
    
    Returns
    -------
    np.ndarray
        Filtered signal
    """
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    
    b, a = signal.butter(order, [low, high], btype='band')
    filtered = signal.filtfilt(b, a, data)
    
    return filtered


def moving_average(
    data: np.ndarray,
    window_size: int
) -> np.ndarray:
    """
    Apply moving average filter.
    
    Parameters
    ----------
    data : np.ndarray
        Input signal
    window_size : int
        Size of the moving window
    
    Returns
    -------
    np.ndarray
        Smoothed signal
    """
    kernel = np.ones(window_size) / window_size
    return np.convolve(data, kernel, mode='same')
