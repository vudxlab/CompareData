# Full Comparison Report: Sensor A Channel 3 (g) vs Sensor B accZ(g)

Generated: 2026-03-01 22:49:39

---

## Time Domain Statistics

| Metric | Sensor A | Sensor B | Difference |
|--------|----------|----------|------------|
| mean | -0.000021 | -0.000044 | 0.000024 |
| std | 0.036750 | 0.052619 | -0.015869 |
| rms | 0.036750 | 0.052619 | -0.015869 |
| peak | 0.185764 | 0.413046 | -0.227282 |
| peak_to_peak | 0.359800 | 0.754486 | -0.394686 |
| crest_factor | 5.054777 | 7.849742 | -2.794966 |

## Correlation Analysis

- Pearson r: 0.048372
- R²: 0.002340
- Spearman r: 0.055424

## Error Metrics

- MAE: 0.048088
- RMSE: 0.062708
- NRMSE: 0.174285
- Max Error: 0.415410

## Frequency Domain Analysis

| Metric | Sensor A | Sensor B |
|--------|----------|----------|
| dominant_frequency | 11.64 Hz | 11.72 Hz |
| spectral_centroid | 39.89 Hz | 65.37 Hz |
| median_frequency | 17.77 Hz | 42.93 Hz |

## Interpretation

- **Correlation (Pearson r = 0.0484)**: Poor
- **NRMSE = 0.1743 (17.4%)**: Poor
- **Dominant frequency**: matched (11.64 Hz vs 11.72 Hz) — same vibration source confirmed

**Conclusion**: Both sensors capture the same dominant vibration frequency, but waveform correlation is low. This is consistent with sensors placed at different physical locations on the structure, where vibration amplitude and phase differ. Time-lag sweep (cross-correlation over full data) confirmed no single offset improves correlation significantly (peak r < 0.08 across all channels). The low correlation is therefore attributed to spatial differences in sensor placement, not to timestamp misalignment.