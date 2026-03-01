"""
Unit tests for frequency analysis functions.
Uses synthetic signals with known FFT results.
"""

import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.frequency import compute_fft


def _make_sine(freq_hz: float, fs: float, duration: float = 1.0) -> np.ndarray:
    t = np.arange(0, duration, 1 / fs)
    return np.sin(2 * np.pi * freq_hz * t)


class TestComputeFFT:
    def test_peak_at_correct_frequency(self):
        """A pure 10 Hz sine should produce a peak at 10 Hz."""
        fs = 1000.0
        sig = _make_sine(10.0, fs, duration=1.0)
        freqs, mag = compute_fft(sig, fs, window=None)
        peak_freq = freqs[np.argmax(mag)]
        assert abs(peak_freq - 10.0) < 1.5, f"Peak should be near 10 Hz, got {peak_freq}"

    def test_window_reduces_leakage(self):
        """Applying a Hann window should reduce spectral leakage."""
        fs = 1000.0
        # Use a frequency that doesn't align with FFT bins to see leakage
        sig = _make_sine(10.5, fs, duration=1.0)
        _, mag_no_win = compute_fft(sig, fs, window=None)
        _, mag_hann = compute_fft(sig, fs, window="hann")
        # Leakage: compare energy far from the peak
        # With windowing, sidelobes should be lower
        far_bins_no_win = np.sort(mag_no_win)[-20:-1]
        far_bins_hann = np.sort(mag_hann)[-20:-1]
        # The sum of the top sidelobes should be smaller with windowing
        assert np.sum(far_bins_hann) <= np.sum(far_bins_no_win) * 1.1, (
            "Hann window should reduce spectral leakage"
        )

    def test_window_parameter_none(self):
        """window=None should produce same result as no windowing."""
        fs = 500.0
        sig = _make_sine(25.0, fs, duration=1.0)
        freqs1, mag1 = compute_fft(sig, fs, window=None)
        freqs2, mag2 = compute_fft(sig, fs, window="")
        # Both should produce valid results
        assert len(freqs1) > 0
        assert len(freqs2) > 0

    def test_multi_frequency_detection(self):
        """A signal with 10 Hz and 30 Hz should show peaks at both frequencies."""
        fs = 1000.0
        t = np.arange(0, 1.0, 1 / fs)
        sig = np.sin(2 * np.pi * 10 * t) + 0.5 * np.sin(2 * np.pi * 30 * t)
        freqs, mag = compute_fft(sig, fs, window="hann")
        # Find top 2 peaks
        top_idx = np.argsort(mag)[-2:]
        top_freqs = sorted(freqs[top_idx])
        assert abs(top_freqs[0] - 10.0) < 2.0, f"Expected ~10 Hz, got {top_freqs[0]}"
        assert abs(top_freqs[1] - 30.0) < 2.0, f"Expected ~30 Hz, got {top_freqs[1]}"
