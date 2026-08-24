# RazorGuard Hybrid Risk Scoring

RazorGuard separates two signals:

1. **ML probability** — learned from the training data using a class-weighted Random Forest.
2. **Behavioral policy score** — transparent aggregation of directly observable high-risk behaviors.

The demo score is:

`0.70 × ML probability + 0.30 × behavioral policy score`

This is a prototype risk score, **not a calibrated production probability**. The policy layer is a safety guardrail so several strong observable signals cannot be hidden by a single model probability.

Production work would calibrate this hybrid score on a validation set and evaluate it against real, privacy-safe historical outcomes.
