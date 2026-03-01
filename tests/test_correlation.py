"""
Unit tests for correlation and coherence functions.
"""

import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.correlation import compute_correlation, coherence


class TestComputeCorrelation:
    def test_identical_signals_perfect_correlation(self):
        """Two identical signals should have Pearson r ~= 1.0."""
        sig = np.sin(2 * np.pi * 5 * np.arange(0, 1, 1 / 1000))
        result = compute_correlation(sig, sig)
        assert abs(result["pearson_r"] - 1.0) < 1e-10
        assert abs(result["r_squared"] - 1.0) < 1e-10

    def test_anticorrelated_signals(self):
        """Signal and its negation should have Pearson r ~= -1.0."""
        sig = np.sin(2 * np.pi * 5 * np.arange(0, 1, 1 / 1000))
        result = compute_correlation(sig, -sig)
        assert abs(result["pearson_r"] + 1.0) < 1e-10

    def test_uncorrelated_signals(self):
        """Two independent random signals should have low correlation."""
        rng = np.random.default_rng(42)
        a = rng.standard_normal(10000)
        b = rng.standard_normal(10000)
        result = compute_correlation(a, b)
        assert abs(result["pearson_r"]) < 0.05, (
            f"Random signals should have near-zero correlation, got {result['pearson_r']}"
        )


class TestCoherence:
    def test_identical_signals_high_coherence(self):
        """Two identical signals should have coherence ~= 1.0 at all frequencies."""
        fs = 1000.0
        t = np.arange(0, 1, 1 / fs)
        sig = np.sin(2 * np.pi * 10 * t) + 0.5 * np.sin(2 * np.pi * 30 * t)
        freqs, coh = coherence(sig, sig, fs=fs, n_fft=256)
        assert np.mean(coh) > 0.99, (
            f"Identical signals should have mean coherence > 0.99, got {np.mean(coh):.4f}"
        )

    def test_independent_signals_low_coherence(self):
        """Two independent noise signals should have low coherence."""
        fs = 1000.0
        rng = np.random.default_rng(42)
        a = rng.standard_normal(10000)
        b = rng.standard_normal(10000)
        freqs, coh = coherence(a, b, fs=fs, n_fft=256)
        assert np.mean(coh) < 0.2, (
            f"Independent signals should have low coherence, got {np.mean(coh):.4f}"
        )
