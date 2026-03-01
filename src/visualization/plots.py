"""
Visualization functions for accelerometer data
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Tuple, List
import os


def setup_plot_style():
    """Set up consistent plot style."""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams['figure.figsize'] = (12, 6)
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['legend.fontsize'] = 10


def plot_time_series(
    time: np.ndarray,
    signal_a: np.ndarray,
    signal_b: np.ndarray = None,
    labels: Tuple[str, str] = ('Sensor A', 'Sensor B'),
    title: str = 'Time Series Comparison',
    ylabel: str = 'Acceleration (g)',
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot time series data from one or two sensors.
    
    Parameters
    ----------
    time : np.ndarray
        Time array
    signal_a : np.ndarray
        First signal
    signal_b : np.ndarray, optional
        Second signal
    labels : tuple
        Labels for the signals
    title : str
        Plot title
    ylabel : str
        Y-axis label
    save_path : str, optional
        Path to save the figure
    
    Returns
    -------
    plt.Figure
        Matplotlib figure
    """
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.plot(time, signal_a, label=labels[0], color='#1f77b4', alpha=0.8, linewidth=0.8)
    
    if signal_b is not None:
        ax.plot(time, signal_b, label=labels[1], color='#ff7f0e', alpha=0.8, linewidth=0.8)
    
    ax.set_xlabel('Time (s)')
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_fft(
    freq_a: np.ndarray,
    mag_a: np.ndarray,
    freq_b: np.ndarray = None,
    mag_b: np.ndarray = None,
    labels: Tuple[str, str] = ('Sensor A', 'Sensor B'),
    title: str = 'Frequency Spectrum',
    xlim: Tuple[float, float] = None,
    ylim: Tuple[float, float] = None,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot FFT magnitude spectrum.
    """
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(freq_a, mag_a, label=labels[0], color='#1f77b4', alpha=0.8)
    
    if freq_b is not None and mag_b is not None:
        ax.plot(freq_b, mag_b, label=labels[1], color='#ff7f0e', alpha=0.8)
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Magnitude')
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    if xlim:
        ax.set_xlim(xlim)
    if ylim:
        ax.set_ylim(ylim)
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_psd(
    freq_a: np.ndarray,
    psd_a: np.ndarray,
    freq_b: np.ndarray = None,
    psd_b: np.ndarray = None,
    labels: Tuple[str, str] = ('Sensor A', 'Sensor B'),
    title: str = 'Power Spectral Density',
    log_scale: bool = True,
    xlim: Tuple[float, float] = None,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot Power Spectral Density.
    """
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.semilogy(freq_a, psd_a, label=labels[0], color='#1f77b4', alpha=0.8)
    
    if freq_b is not None and psd_b is not None:
        ax.semilogy(freq_b, psd_b, label=labels[1], color='#ff7f0e', alpha=0.8)
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('PSD (g²/Hz)')
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    if xlim:
        ax.set_xlim(xlim)
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_comparison(
    signal_a: np.ndarray,
    signal_b: np.ndarray,
    labels: Tuple[str, str] = ('Sensor A', 'Sensor B'),
    title: str = 'Sensor Comparison',
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot scatter comparison between two sensors.
    """
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(8, 8))
    
    ax.scatter(signal_a, signal_b, alpha=0.3, s=1)
    
    min_val = min(signal_a.min(), signal_b.min())
    max_val = max(signal_a.max(), signal_b.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', label='Identity line')
    
    ax.set_xlabel(labels[0])
    ax.set_ylabel(labels[1])
    ax.set_title(title)
    ax.legend()
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_bland_altman(
    mean_values: np.ndarray,
    differences: np.ndarray,
    mean_diff: float,
    upper_loa: float,
    lower_loa: float,
    title: str = 'Bland-Altman Plot',
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Create Bland-Altman plot for method comparison.
    """
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(10, 8))

    ax.scatter(mean_values, differences, alpha=0.3, s=1)

    ax.axhline(y=mean_diff, color='blue', linestyle='-', label=f'Mean: {mean_diff:.4f}')
    ax.axhline(y=upper_loa, color='red', linestyle='--', label=f'+1.96 SD: {upper_loa:.4f}')
    ax.axhline(y=lower_loa, color='red', linestyle='--', label=f'-1.96 SD: {lower_loa:.4f}')

    ax.set_xlabel('Mean of Two Measurements')
    ax.set_ylabel('Difference (A - B)')
    ax.set_title(title)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig


def plot_coherence(
    frequencies: np.ndarray,
    coherence_values: np.ndarray,
    max_freq_hz: float = 50.0,
    title: str = 'Coherence Analysis',
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot coherence vs frequency with threshold lines.
    """
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(12, 6))

    mask = frequencies <= max_freq_hz
    f_plot = frequencies[mask]
    c_plot = coherence_values[mask]

    ax.plot(f_plot, c_plot, color='#2ca02c', linewidth=1.0, label='Coherence')
    ax.axhline(y=0.95, color='red', linestyle='--', alpha=0.7, label='Excellent (0.95)')
    ax.axhline(y=0.80, color='orange', linestyle='--', alpha=0.7, label='Good (0.80)')

    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Coherence')
    ax.set_title(title)
    ax.set_ylim(0, 1.05)
    ax.set_xlim(0, max_freq_hz)
    ax.legend(loc='lower left')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig
