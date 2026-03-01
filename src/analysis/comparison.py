"""
Sensor comparison analysis functions
"""

import numpy as np
from typing import Dict, Tuple
from scipy.stats import pearsonr
from .statistics import compute_time_domain_metrics
from .frequency import compute_fft, compute_frequency_metrics
from .correlation import compute_correlation


def compare_sensors(
    signal_a: np.ndarray,
    signal_b: np.ndarray,
    fs: float
) -> Dict[str, any]:
    """
    Comprehensive comparison between two sensor signals.
    
    Parameters
    ----------
    signal_a : np.ndarray
        Signal from sensor A
    signal_b : np.ndarray
        Signal from sensor B
    fs : float
        Sampling frequency
    
    Returns
    -------
    dict
        Comprehensive comparison results
    """
    min_len = min(len(signal_a), len(signal_b))
    signal_a = signal_a[:min_len]
    signal_b = signal_b[:min_len]
    
    results = {}
    
    results['sensor_a_stats'] = compute_time_domain_metrics(signal_a)
    results['sensor_b_stats'] = compute_time_domain_metrics(signal_b)
    
    results['correlation'] = compute_correlation(signal_a, signal_b)
    
    results['error_metrics'] = compute_error_metrics(signal_a, signal_b)
    
    freq_a, mag_a = compute_fft(signal_a, fs)
    freq_b, mag_b = compute_fft(signal_b, fs)
    results['sensor_a_freq'] = compute_frequency_metrics(freq_a, mag_a)
    results['sensor_b_freq'] = compute_frequency_metrics(freq_b, mag_b)
    
    return results


def compute_error_metrics(
    reference: np.ndarray,
    measured: np.ndarray
) -> Dict[str, float]:
    """
    Compute error metrics between reference and measured signals.
    
    Parameters
    ----------
    reference : np.ndarray
        Reference signal (ground truth)
    measured : np.ndarray
        Measured signal
    
    Returns
    -------
    dict
        Dictionary of error metrics
    """
    min_len = min(len(reference), len(measured))
    reference = reference[:min_len]
    measured = measured[:min_len]
    
    error = measured - reference
    
    metrics = {}
    
    metrics['mae'] = np.mean(np.abs(error))
    metrics['mse'] = np.mean(error**2)
    metrics['rmse'] = np.sqrt(metrics['mse'])
    metrics['max_error'] = np.max(np.abs(error))
    
    ref_range = np.max(reference) - np.min(reference)
    if ref_range > 0:
        metrics['nrmse'] = metrics['rmse'] / ref_range
    else:
        metrics['nrmse'] = 0
    
    nonzero_mask = reference != 0
    if np.any(nonzero_mask):
        metrics['mape'] = np.mean(np.abs(error[nonzero_mask] / reference[nonzero_mask])) * 100
    else:
        metrics['mape'] = np.nan
    
    return metrics


def compute_bootstrap_ci(signal_a, signal_b, n_bootstrap=1000, ci=0.95, seed=42):
    """Compute bootstrap confidence intervals for Pearson r, RMSE, and MAE."""
    rng = np.random.default_rng(seed)
    n = min(len(signal_a), len(signal_b))
    signal_a = signal_a[:n]
    signal_b = signal_b[:n]
    pearson_rs, rmses, maes = [], [], []
    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        a, b = signal_a[idx], signal_b[idx]
        r, _ = pearsonr(a, b)
        pearson_rs.append(r)
        rmses.append(np.sqrt(np.mean((a - b) ** 2)))
        maes.append(np.mean(np.abs(a - b)))
    alpha = (1 - ci) / 2
    return {
        "pearson_r_ci": (float(np.percentile(pearson_rs, alpha * 100)),
                         float(np.percentile(pearson_rs, (1 - alpha) * 100))),
        "rmse_ci": (float(np.percentile(rmses, alpha * 100)),
                    float(np.percentile(rmses, (1 - alpha) * 100))),
        "mae_ci": (float(np.percentile(maes, alpha * 100)),
                   float(np.percentile(maes, (1 - alpha) * 100))),
    }


def bland_altman_analysis(
    signal_a: np.ndarray,
    signal_b: np.ndarray,
    confidence: float = 0.95
) -> Dict[str, float]:
    """
    Perform Bland-Altman analysis for method comparison.

    Parameters
    ----------
    signal_a : np.ndarray
        Measurements from method A
    signal_b : np.ndarray
        Measurements from method B
    confidence : float
        Confidence level for limits of agreement

    Returns
    -------
    dict
        Bland-Altman analysis results
    """
    min_len = min(len(signal_a), len(signal_b))
    signal_a = signal_a[:min_len]
    signal_b = signal_b[:min_len]

    mean_values = (signal_a + signal_b) / 2
    differences = signal_a - signal_b

    results = {}

    results['mean_difference'] = np.mean(differences)
    results['std_difference'] = np.std(differences, ddof=1)

    from scipy import stats
    z = stats.norm.ppf((1 + confidence) / 2)

    results['upper_loa'] = results['mean_difference'] + z * results['std_difference']
    results['lower_loa'] = results['mean_difference'] - z * results['std_difference']

    results['mean_values'] = mean_values
    results['differences'] = differences

    # Proportional bias (linregress fails if all mean_values are identical)
    if np.ptp(mean_values) > 0:
        slope, intercept, r_value, p_value, std_err = stats.linregress(mean_values, differences)
        results['proportional_bias'] = {
            'slope': slope,
            'intercept': intercept,
            'r_value': r_value,
            'p_value': p_value
        }
    else:
        results['proportional_bias'] = {
            'slope': 0.0,
            'intercept': float(results['mean_difference']),
            'r_value': 0.0,
            'p_value': 1.0
        }

    # Normality test on differences (Shapiro-Wilk)
    from scipy.stats import shapiro
    test_data = differences if len(differences) <= 5000 else np.random.default_rng(42).choice(differences, 5000, replace=False)
    shapiro_stat, shapiro_p = shapiro(test_data)
    results['normality_test'] = {
        'statistic': float(shapiro_stat),
        'p_value': float(shapiro_p),
        'is_normal': bool(shapiro_p > 0.05),
    }

    return results
