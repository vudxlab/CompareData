"""
Correlation analysis functions
"""

import numpy as np
from scipy import stats, signal
from typing import Dict, Tuple


def compute_correlation(
    signal_a: np.ndarray,
    signal_b: np.ndarray
) -> Dict[str, float]:
    """
    Compute correlation metrics between two signals.
    
    Parameters
    ----------
    signal_a : np.ndarray
        First signal
    signal_b : np.ndarray
        Second signal
    
    Returns
    -------
    dict
        Dictionary of correlation metrics
    """
    min_len = min(len(signal_a), len(signal_b))
    signal_a = signal_a[:min_len]
    signal_b = signal_b[:min_len]
    
    metrics = {}
    
    pearson_r, pearson_p = stats.pearsonr(signal_a, signal_b)
    metrics['pearson_r'] = pearson_r
    metrics['pearson_p'] = pearson_p
    
    spearman_r, spearman_p = stats.spearmanr(signal_a, signal_b)
    metrics['spearman_r'] = spearman_r
    metrics['spearman_p'] = spearman_p
    
    metrics['r_squared'] = pearson_r ** 2
    
    return metrics


def cross_correlation(
    signal_a: np.ndarray,
    signal_b: np.ndarray,
    normalize: bool = True
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute cross-correlation between two signals.
    
    Parameters
    ----------
    signal_a : np.ndarray
        First signal
    signal_b : np.ndarray
        Second signal
    normalize : bool
        Whether to normalize the correlation
    
    Returns
    -------
    tuple
        (lags, correlation)
    """
    correlation = signal.correlate(signal_a, signal_b, mode='full')
    lags = signal.correlation_lags(len(signal_a), len(signal_b), mode='full')
    
    if normalize:
        correlation = correlation / (np.std(signal_a) * np.std(signal_b) * len(signal_a))
    
    return lags, correlation


def coherence(
    signal_a: np.ndarray,
    signal_b: np.ndarray,
    fs: float,
    n_fft: int = 4096
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute coherence between two signals.
    
    Parameters
    ----------
    signal_a : np.ndarray
        First signal
    signal_b : np.ndarray
        Second signal
    fs : float
        Sampling frequency
    n_fft : int
        FFT size
    
    Returns
    -------
    tuple
        (frequencies, coherence)
    """
    frequencies, coh = signal.coherence(
        signal_a, signal_b,
        fs=fs,
        nperseg=n_fft
    )
    
    return frequencies, coh
