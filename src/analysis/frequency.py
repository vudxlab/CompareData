"""
Frequency domain analysis functions
"""

import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq
from typing import Dict, Tuple


def compute_fft(
    data: np.ndarray,
    fs: float,
    n_fft: int = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute FFT of signal.
    
    Parameters
    ----------
    data : np.ndarray
        Input signal
    fs : float
        Sampling frequency in Hz
    n_fft : int, optional
        FFT size. If None, uses signal length.
    
    Returns
    -------
    tuple
        (frequencies, magnitude)
    """
    if n_fft is None:
        n_fft = len(data)
    
    fft_result = fft(data, n_fft)
    frequencies = fftfreq(n_fft, 1/fs)
    
    positive_freq_idx = frequencies >= 0
    frequencies = frequencies[positive_freq_idx]
    magnitude = np.abs(fft_result[positive_freq_idx]) * 2 / n_fft
    
    return frequencies, magnitude


def compute_psd(
    data: np.ndarray,
    fs: float,
    n_fft: int = 4096,
    window: str = 'hanning',
    overlap: float = 0.5
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute Power Spectral Density using Welch's method.
    
    Parameters
    ----------
    data : np.ndarray
        Input signal
    fs : float
        Sampling frequency in Hz
    n_fft : int
        FFT size
    window : str
        Window function
    overlap : float
        Overlap ratio
    
    Returns
    -------
    tuple
        (frequencies, psd)
    """
    noverlap = int(n_fft * overlap)
    frequencies, psd = signal.welch(
        data,
        fs=fs,
        window=window,
        nperseg=n_fft,
        noverlap=noverlap
    )
    
    return frequencies, psd


def compute_frequency_metrics(
    frequencies: np.ndarray,
    magnitude: np.ndarray
) -> Dict[str, float]:
    """
    Compute frequency-domain metrics.
    
    Parameters
    ----------
    frequencies : np.ndarray
        Frequency array
    magnitude : np.ndarray
        Magnitude array
    
    Returns
    -------
    dict
        Dictionary of frequency metrics
    """
    metrics = {}
    
    dominant_idx = np.argmax(magnitude)
    metrics['dominant_frequency'] = frequencies[dominant_idx]
    metrics['dominant_amplitude'] = magnitude[dominant_idx]
    
    total_power = np.sum(magnitude**2)
    if total_power > 0:
        metrics['spectral_centroid'] = np.sum(frequencies * magnitude**2) / total_power
    else:
        metrics['spectral_centroid'] = 0
    
    normalized_psd = magnitude**2 / total_power if total_power > 0 else magnitude**2
    normalized_psd = normalized_psd[normalized_psd > 0]
    metrics['spectral_entropy'] = -np.sum(normalized_psd * np.log2(normalized_psd))
    
    cumsum = np.cumsum(magnitude**2)
    if total_power > 0:
        half_power_idx = np.searchsorted(cumsum, total_power / 2)
        metrics['median_frequency'] = frequencies[min(half_power_idx, len(frequencies)-1)]
    else:
        metrics['median_frequency'] = 0
    
    return metrics


def find_peaks_in_spectrum(
    frequencies: np.ndarray,
    magnitude: np.ndarray,
    height_threshold: float = None,
    distance: int = 10
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Find peaks in frequency spectrum.
    
    Parameters
    ----------
    frequencies : np.ndarray
        Frequency array
    magnitude : np.ndarray
        Magnitude array
    height_threshold : float, optional
        Minimum peak height
    distance : int
        Minimum distance between peaks
    
    Returns
    -------
    tuple
        (peak_frequencies, peak_magnitudes)
    """
    if height_threshold is None:
        height_threshold = np.mean(magnitude) + np.std(magnitude)
    
    peaks, properties = signal.find_peaks(
        magnitude,
        height=height_threshold,
        distance=distance
    )
    
    return frequencies[peaks], magnitude[peaks]
