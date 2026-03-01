"""
Unit tests for filtering functions.
Uses synthetic signals with known properties.
"""

import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.preprocessing.filtering import lowpass_filter, highpass_filter


def _make_sine(freq_hz: float, fs: float, duration: float = 1.0) -> np.ndarray:
    t = np.arange(0, duration, 1 / fs)
    return np.sin(2 * np.pi * freq_hz * t)


class TestLowpassFilter:
    def test_passes_low_frequency(self):
        """A 10 Hz sine through a 50 Hz lowpass should be preserved."""
        fs = 1000.0
        sig = _make_sine(10.0, fs, duration=1.0)
        filtered = lowpass_filter(sig, cutoff=50.0, fs=fs, order=4)
        # Amplitude should remain close to 1.0 (ignoring edge effects)
        mid = filtered[len(filtered) // 4 : 3 * len(filtered) // 4]
        assert np.max(np.abs(mid)) > 0.9, "10 Hz signal should pass through 50 Hz lowpass"

    def test_attenuates_high_frequency(self):
        """A 100 Hz sine through a 50 Hz lowpass should be heavily attenuated."""
        fs = 1000.0
        sig = _make_sine(100.0, fs, duration=1.0)
        filtered = lowpass_filter(sig, cutoff=50.0, fs=fs, order=4)
        mid = filtered[len(filtered) // 4 : 3 * len(filtered) // 4]
        assert np.max(np.abs(mid)) < 0.1, "100 Hz signal should be attenuated by 50 Hz lowpass"

    def test_cutoff_above_nyquist_returns_original(self):
        """If cutoff >= Nyquist, data should be returned unchanged."""
        fs = 1000.0
        sig = _make_sine(10.0, fs)
        result = lowpass_filter(sig, cutoff=600.0, fs=fs, order=4)
        np.testing.assert_array_equal(result, sig)


class TestHighpassFilter:
    def test_passes_high_frequency(self):
        """A 100 Hz sine through a 50 Hz highpass should be preserved."""
        fs = 1000.0
        sig = _make_sine(100.0, fs, duration=1.0)
        filtered = highpass_filter(sig, cutoff=50.0, fs=fs, order=4)
        mid = filtered[len(filtered) // 4 : 3 * len(filtered) // 4]
        assert np.max(np.abs(mid)) > 0.9, "100 Hz signal should pass through 50 Hz highpass"

    def test_attenuates_low_frequency(self):
        """A 1 Hz sine through a 10 Hz highpass should be heavily attenuated."""
        fs = 1000.0
        sig = _make_sine(1.0, fs, duration=2.0)
        filtered = highpass_filter(sig, cutoff=10.0, fs=fs, order=4)
        mid = filtered[len(filtered) // 4 : 3 * len(filtered) // 4]
        assert np.max(np.abs(mid)) < 0.1, "1 Hz signal should be attenuated by 10 Hz highpass"
