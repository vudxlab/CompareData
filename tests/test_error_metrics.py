"""
Unit tests for error metrics and Bland-Altman analysis.
"""

import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.comparison import (
    compute_error_metrics,
    bland_altman_analysis,
    compute_bootstrap_ci,
)


class TestComputeErrorMetrics:
    def test_identical_signals_zero_error(self):
        """Two identical signals should give RMSE = 0, MAE = 0."""
        sig = np.sin(2 * np.pi * 5 * np.arange(0, 1, 1 / 1000))
        result = compute_error_metrics(sig, sig)
        assert result["rmse"] == pytest.approx(0.0, abs=1e-15)
        assert result["mae"] == pytest.approx(0.0, abs=1e-15)
        assert result["max_error"] == pytest.approx(0.0, abs=1e-15)

    def test_known_error(self):
        """A constant offset should give known MAE and RMSE."""
        a = np.zeros(1000)
        b = np.ones(1000) * 0.5
        result = compute_error_metrics(a, b)
        assert result["mae"] == pytest.approx(0.5, abs=1e-10)
        assert result["rmse"] == pytest.approx(0.5, abs=1e-10)
        assert result["max_error"] == pytest.approx(0.5, abs=1e-10)


class TestBlandAltman:
    def test_ddof_1_used(self):
        """Bland-Altman std should use ddof=1 (sample std)."""
        rng = np.random.default_rng(42)
        a = rng.standard_normal(100)
        b = a + rng.standard_normal(100) * 0.1
        result = bland_altman_analysis(a, b)
        differences = a - b
        expected_std = np.std(differences, ddof=1)
        assert result["std_difference"] == pytest.approx(expected_std, rel=1e-10)

    def test_normality_test_present(self):
        """Bland-Altman should include normality test results."""
        rng = np.random.default_rng(42)
        a = rng.standard_normal(500)
        b = a + rng.standard_normal(500) * 0.1
        result = bland_altman_analysis(a, b)
        assert "normality_test" in result
        assert "statistic" in result["normality_test"]
        assert "p_value" in result["normality_test"]
        assert "is_normal" in result["normality_test"]

    def test_identical_signals(self):
        """Identical signals: mean_diff = 0, std_diff = 0."""
        sig = np.ones(100) * 3.0
        result = bland_altman_analysis(sig, sig)
        assert result["mean_difference"] == pytest.approx(0.0, abs=1e-15)
        assert result["std_difference"] == pytest.approx(0.0, abs=1e-15)


class TestBootstrapCI:
    def test_identical_signals_tight_ci(self):
        """Identical signals: Pearson r CI should be tight around 1.0."""
        sig = np.sin(2 * np.pi * 5 * np.arange(0, 1, 1 / 1000))
        result = compute_bootstrap_ci(sig, sig, n_bootstrap=200)
        r_lo, r_hi = result["pearson_r_ci"]
        assert r_lo > 0.999, f"Lower CI for identical signals should be > 0.999, got {r_lo}"
        assert r_hi <= 1.0 + 1e-10

    def test_ci_contains_point_estimate(self):
        """The CI should bracket the point estimate."""
        rng = np.random.default_rng(42)
        a = rng.standard_normal(500)
        b = a + rng.standard_normal(500) * 0.5
        result = compute_bootstrap_ci(a, b, n_bootstrap=500)
        from scipy.stats import pearsonr
        r_point, _ = pearsonr(a, b)
        r_lo, r_hi = result["pearson_r_ci"]
        assert r_lo <= r_point <= r_hi, (
            f"CI [{r_lo:.4f}, {r_hi:.4f}] should contain point estimate {r_point:.4f}"
        )

    def test_returns_all_keys(self):
        """Bootstrap should return CIs for pearson_r, rmse, mae."""
        a = np.ones(100)
        b = np.ones(100)
        result = compute_bootstrap_ci(a, b, n_bootstrap=50)
        assert "pearson_r_ci" in result
        assert "rmse_ci" in result
        assert "mae_ci" in result
        assert len(result["pearson_r_ci"]) == 2
        assert len(result["rmse_ci"]) == 2
        assert len(result["mae_ci"]) == 2
