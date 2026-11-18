# Primary results analysis

Generated from preserved exports with `python src/audit_results.py`. No database or retraining required.

| Model | Validation AUCPR | Test AUCPR | Paper S1 test | Descriptive delta | Outer-train minus test | Training (s) |
|---|---:|---:|---:|---:|---:|---:|
| LogisticRegression | 0.767759 | 0.796090 | 0.6971 | +0.098990 | 0.000222 | 1.695 |
| RandomForest | 0.721579 | 0.678773 | 0.5395 | +0.139273 | 0.135040 | 16.509 |
| MultilayerPerceptron | 0.771336 | 0.795566 | 0.6943 | +0.101266 | 0.009549 | 14.339 |

## Interpretation

- MLP has the highest mean validation AUCPR (0.771336).
- LR exceeds MLP on test by only 0.000524. One seed cannot establish meaningful superiority.
- RF has an outer-training-to-test gap of 0.135040; this is descriptive, not a causal diagnosis.
- Higher scores than the paper are not an improvement claim: report coverage, timestamps, settings and evaluation details differ.
- Scores are GDS AUCPR, not accuracy and not automatically scikit-learn average precision.
- Training durations are from the saved summaries, not independently verified by model catalogue metadata.
- No confidence interval or significance test is justified from these aggregate exports alone.

## Reference

Gulbay & Demirci (2024), APT-Scope, Table 6, Scenario 1. https://doi.org/10.1016/j.jestch.2024.101791
Paper reference values were transcribed from the supplied paper/audit. Scenario 2 is a different enriched experiment.
