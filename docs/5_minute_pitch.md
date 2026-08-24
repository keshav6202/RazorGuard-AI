# RazorGuard AI — 5-Minute Pitch

## 0:00–0:30 — Problem

"Merchants don't lose money only when a single transaction is obviously fraudulent.
They lose money when suspicious behavior is buried inside legitimate payment traffic.

RazorGuard AI is a defensive risk intelligence system that detects suspicious
transactions, explains the evidence, detects risk spikes, and routes high-risk
cases to human review."

## 0:30–1:05 — Why this approach

"Instead of optimizing for accuracy alone, I designed the system around the
cost of mistakes.

A false positive can interrupt a genuine customer. A false negative can allow
a loss. Therefore I measure precision, recall, F1, ROC-AUC and explicit
false-positive/false-negative costs on a held-out test set."

## 1:05–1:45 — Architecture

Show `docs/architecture.png`.

Walk through:

1. Transaction input
2. Feature engineering
3. Random Forest risk model
4. Risk probability and tier
5. Evidence-based investigation
6. Bounded recommendation
7. Human approval
8. Audit log

"Nothing irreversible happens automatically. The system is defense-only."

## 1:45–3:00 — Live demo

### Demo 1: Normal transaction

Enter a mature account, normal amount, no unusual device/IP/location changes.

Show:
- LOW risk
- Allow with monitoring
- Evidence says no strong risk signal

### Demo 2: Suspicious transaction

Enter:
- amount far above average
- several failed transactions
- multiple device changes
- multiple IP changes
- location change
- late-night hour

Show:
- HIGH risk
- evidence list
- HOLD_FOR_HUMAN_REVIEW
- audit record

### Demo 3: Batch signal

Show the fraud-spike detector and explain that a merchant can inspect
risk-rate changes by cohort instead of investigating every transaction
individually.

## 3:00–3:50 — Results

"On the reproducible synthetic benchmark, the model achieved:

- Precision: 80.28%
- Recall: 87.50%
- F1: 83.73%
- ROC-AUC: 99.45%

on 4,000 held-out transactions.

There were 43 false positives and 25 false negatives under the documented
cost assumptions.

These are synthetic-data results, not production fraud claims."

## 3:50–4:30 — AI judgment and safety

"I intentionally did not use an LLM to make the core risk decision.
The risk decision is deterministic and measurable through the ML model.

The investigation layer converts model output into structured evidence and a
bounded recommendation. This keeps the financial decision auditable and avoids
giving an unconstrained model authority to execute financial actions."

## 4:30–5:00 — Production direction

"In production I would validate against real, privacy-safe historical data,
calibrate thresholds on a validation set, monitor drift, add model versioning,
and integrate approved workflows with payment and dispute systems.

The key design principle would remain the same: measurable risk detection,
explainable evidence, bounded actions, and human control."

End with:

"RazorGuard AI is not just a fraud classifier. It is a defensive risk
investigation workflow designed around the economics of payment risk."
