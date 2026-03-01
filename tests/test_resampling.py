"""
Unit tests for resampling with anti-aliasing.
"""

import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.window_compare import _resample_linear
from src.analysis.frequency import compute_fft


def _make_sine(freq_hz: float, fs: float, duration: float = 1.0):
    t = np.arange(0, duration, 1 / fs)
    x = np.sin(2 * np.pi * freq_hz * t)
    return t, x


class TestResampleLinear:
    def test_preserves_frequency_when_downsampling(self):
        """A 10 Hz sine resampled from 1000 to 500 Hz should still peak at 10 Hz."""
        t, x = _make_sine(10.0, fs=1000.0, duration=1.0)
        t_new, x_new = _resample_linear(t, x, fs=500.0, fs_source=1000.0)
        freqs, mag = compute_fft(x_new, fs=500.0, window=None)
        peak_freq = freqs[np.argmax(mag)]
        assert abs(peak_freq - 10.0) < 2.0, f"Peak should be near 10 Hz, got {peak_freq}"

    def test_anti_aliasing_prevents_alias(self):
        """A 400 Hz sine resampled to 500 Hz should be attenuated (near Nyquist)."""
        t, x = _make_sine(400.0, fs=1000.0, duration=1.0)
        # Without anti-aliasing
        t_no_aa, x_no_aa = _resample_linear(t, x, fs=500.0, fs_source=0.0)
        # With anti-aliasing
        t_aa, x_aa = _resample_linear(t, x, fs=500.0, fs_source=1000.0)
        # The anti-aliased version should have lower amplitude
        rms_no_aa = np.sqrt(np.mean(x_no_aa**2))
        rms_aa = np.sqrt(np.mean(x_aa**2))
        assert rms_aa < rms_no_aa, (
            f"Anti-aliased RMS ({rms_aa:.4f}) should be less than non-AA ({rms_no_aa:.4f})"
        )

    def test_upsample_no_filter(self):
        """Upsampling should not apply anti-aliasing filter."""
        t, x = _make_sine(10.0, fs=500.0, duration=1.0)
        t_new, x_new = _resample_linear(t, x, fs=1000.0, fs_source=500.0)
        # Signal should be preserved
        mid = x_new[len(x_new) // 4 : 3 * len(x_new) // 4]
        assert np.max(np.abs(mid)) > 0.9, "Upsampled signal should preserve amplitude"

    def test_output_length(self):
        """Output length should match expected sample count."""
        fs_source = 1000.0
        fs_target = 500.0
        duration = 1.0
        t, x = _make_sine(10.0, fs_source, duration)
        t_new, x_new = _resample_linear(t, x, fs=fs_target, fs_source=fs_source)
        expected_n = int(np.floor(duration * fs_target)) + 1
        assert abs(len(x_new) - expected_n) <= 1, (
            f"Expected ~{expected_n} samples, got {len(x_new)}"
        )
