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


def compute_freq_band_metrics(
    freq_a: np.ndarray,
    mag_a: np.ndarray,
    freq_b: np.ndarray,
    mag_b: np.ndarray,
    f_min: float = 0.0,
    f_max: float = 20.0,
) -> Dict[str, float]:
    """
    Compute comparison metrics between two spectra in a frequency band [f_min, f_max].

    Metrics (analogous to time domain):
    - mean_a / mean_b       : mean magnitude in band
    - std_a / std_b         : std of magnitude in band
    - rms_a / rms_b         : RMS magnitude in band
    - peak_a / peak_b       : peak magnitude in band
    - peak_freq_a / peak_freq_b : frequency of peak
    - mae                   : mean absolute error of magnitudes (interpolated to common grid)
    - rmse                  : root mean squared error
    - nrmse                 : RMSE / range(mag_a)
    - pearson_r             : Pearson correlation of magnitude spectra
    - spectral_energy_a / _b: total energy (sum of mag^2) in band
    - energy_ratio          : spectral_energy_a / spectral_energy_b
    """
    from scipy.interpolate import interp1d
    from scipy.stats import pearsonr

    mask_a = (freq_a >= f_min) & (freq_a <= f_max)
    mask_b = (freq_b >= f_min) & (freq_b <= f_max)
    fa, ma = freq_a[mask_a], mag_a[mask_a]
    fb, mb = freq_b[mask_b], mag_b[mask_b]

    metrics: Dict[str, float] = {}

    # Per-sensor stats
    for label, f, m in [("a", fa, ma), ("b", fb, mb)]:
        metrics[f"mean_{label}"] = float(np.mean(m))
        metrics[f"std_{label}"]  = float(np.std(m))
        metrics[f"rms_{label}"]  = float(np.sqrt(np.mean(m ** 2)))
        metrics[f"peak_{label}"] = float(np.max(m))
        metrics[f"peak_freq_{label}"] = float(f[np.argmax(m)]) if len(f) > 0 else 0.0
        metrics[f"spectral_energy_{label}"] = float(np.sum(m ** 2))

    metrics["energy_ratio"] = (
        metrics["spectral_energy_a"] / metrics["spectral_energy_b"]
        if metrics["spectral_energy_b"] > 0 else float("nan")
    )

    # Interpolate B onto A's frequency grid for comparison metrics
    if len(fa) > 1 and len(fb) > 1:
        f_common = fa
        mb_interp = interp1d(fb, mb, bounds_error=False, fill_value=0.0)(f_common)
        error = ma - mb_interp
        metrics["mae"]   = float(np.mean(np.abs(error)))
        metrics["rmse"]  = float(np.sqrt(np.mean(error ** 2)))
        rng = float(np.max(ma) - np.min(ma))
        metrics["nrmse"] = metrics["rmse"] / rng if rng > 0 else 0.0
        if np.std(ma) > 0 and np.std(mb_interp) > 0:
            metrics["pearson_r"] = float(pearsonr(ma, mb_interp)[0])
        else:
            metrics["pearson_r"] = 0.0
    else:
        metrics.update({"mae": float("nan"), "rmse": float("nan"),
                        "nrmse": float("nan"), "pearson_r": float("nan")})

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
