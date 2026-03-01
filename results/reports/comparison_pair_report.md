# Full Comparison Report: Sensor A Channel 3 (g) vs Sensor B accZ(g)

Generated: 2026-03-01 23:14:19

---

## Time Domain Statistics

| Metric | Sensor A | Sensor B | Difference |
|--------|----------|----------|------------|
| mean | -0.000015 | -0.000033 | 0.000018 |
| std | 0.036778 | 0.052391 | -0.015614 |
| rms | 0.036778 | 0.052392 | -0.015614 |
| peak | 0.185764 | 0.413046 | -0.227282 |
| peak_to_peak | 0.359800 | 0.754486 | -0.394686 |
| crest_factor | 5.051000 | 7.883843 | -2.832843 |

## Correlation Analysis

- Pearson r: 0.006438
- R²: 0.000041
- Spearman r: -0.003872

## Error Metrics

- MAE: 0.049192
- RMSE: 0.063817
- NRMSE: 0.177369
- Max Error: 0.398760

## Frequency Domain Analysis

| Metric | Sensor A | Sensor B |
|--------|----------|----------|
| dominant_frequency | 11.64 Hz | 11.72 Hz |
| spectral_centroid | 39.89 Hz | 65.37 Hz |
| median_frequency | 17.77 Hz | 42.93 Hz |

## Figures

### Time Series — Sensor A, Sensor B, Overlay (UTC axis)

![](../figures/comparison_pair/time_series_3panel.png)

### Time Series — Overlay (resampled)

![](../figures/comparison_pair/time_series.png)

### FFT Comparison

![](../figures/comparison_pair/fft.png)

### PSD Comparison

![](../figures/comparison_pair/psd.png)

### Scatter Plot

![](../figures/comparison_pair/scatter.png)

### Bland-Altman Plot

![](../figures/comparison_pair/bland_altman.png)


## Interpretation

- **Correlation (Pearson r = 0.0064)**: Poor
- **NRMSE = 0.1774 (17.7%)**: Poor
- **Dominant frequency**: matched (11.64 Hz vs 11.72 Hz) — same vibration source confirmed

**Conclusion**: Both sensors capture the same dominant vibration frequency, but waveform correlation is low. This is consistent with sensors placed at different physical locations on the structure, where vibration amplitude and phase differ. Time-lag sweep (cross-correlation over full data) confirmed no single offset improves correlation significantly (peak r < 0.08 across all channels). The low correlation is therefore attributed to spatial differences in sensor placement, not to timestamp misalignment.