# RazorGuard AI Architecture

```text
                         +--------------------+
                         | Payment Transaction|
                         +---------+----------+
                                   |
                                   v
                         +--------------------+
                         | Feature Validation |
                         | & Transformation   |
                         +---------+----------+
                                   |
                                   v
                         +--------------------+
                         | Random Forest Risk |
                         |      Model         |
                         +---------+----------+
                                   |
                                   v
                         +--------------------+
                         | Risk Probability   |
                         | + Risk Tier        |
                         +---------+----------+
                                   |
                         +---------+---------+
                         |                   |
                       LOW/MED              HIGH
                         |                   |
                         v                   v
                  Allow/Monitor       AI Investigation
                                             |
                                   +---------+---------+
                                   | Evidence extraction|
                                   | + explanation      |
                                   +---------+---------+
                                             |
                                             v
                                   Bounded recommendation
                                             |
                                             v
                                      Human approval
                                             |
                                             v
                                        Audit log
```

## Safety boundary

The system is designed for defensive risk detection only. It does not automate fraud, evasion, account takeover, payment abuse, or other offensive behavior.

## Evaluation boundary

The test set is held out before final evaluation. Metrics reported by `src/train.py` are calculated on that held-out set.
