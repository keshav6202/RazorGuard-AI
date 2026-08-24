# 🛡️ RazorGuard AI

**Defensive payment-risk intelligence for the Razorpay AI Buildathon — AI Risk Manager track.**

RazorGuard AI is a working prototype that combines a tabular ML model with a transparent behavioral guardrail to detect suspicious payment behavior, explain the evidence, identify risk spikes, and route elevated-risk cases to human review.

> **Important:** the included 20,000-row dataset is synthetic. Reported metrics are prototype benchmark results and are **not** claims of production Razorpay fraud performance.

## Why this is different

RazorGuard is not just a fraud classifier. It separates:

1. **Detection** — Random Forest estimates learned risk.
2. **Verification** — a transparent behavioral policy checks directly observable risk signals.
3. **Investigation** — evidence is generated for a reviewer.
4. **Decision** — LOW / MEDIUM / HIGH tiers map to bounded defensive actions.
5. **Governance** — elevated-risk actions require human review and produce an audit record.
6. **Batch intelligence** — hourly risk-rate spikes help identify emerging patterns.

### Hybrid risk score

For the prototype demo, the final risk score is:

`0.70 × ML probability + 0.30 × behavioral risk`

This is **not presented as a calibrated production probability**. Production work would calibrate the score on a validation set and test it against privacy-safe historical outcomes.

## Architecture

```text
Payment Event
     │
     ▼
Feature Engineering ───────────────┐
     │                             │
     ▼                             ▼
Random Forest ML            Behavioral Guardrail
     │                             │
     └──────────────┬──────────────┘
                    ▼
             Hybrid Risk Score
                    │
                    ▼
          LOW / MEDIUM / HIGH
                    │
                    ▼
          Evidence Investigation
                    │
                    ▼
          Bounded Recommendation
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
     Monitoring          Human Review
          │                   │
          └─────────┬─────────┘
                    ▼
                Audit Log

Batch layer: transaction cohorts → risk-rate → spike detection
```

## Current benchmark

| Metric | Held-out result |
|---|---:|
| Precision | **80.28%** |
| Recall | **87.50%** |
| F1 | **83.73%** |
| ROC-AUC | **99.45%** |
| Test rows | **4,000** |
| False positives | **43** |
| False negatives | **25** |

These results come from the synthetic benchmark and must be described that way in any pitch or submission.

## Demo

The Streamlit dashboard includes:

- Transaction investigator
- One-click suspicious scenario
- Hybrid risk score decomposition
- Evidence explanation
- Human-review decision
- Audit record
- Risk analytics
- Fraud-spike analysis
- Held-out evaluation metrics
- Methodology and production roadmap

For the strongest demo, use the **Suspicious** scenario and show:

`input → ML probability → behavioral verification → evidence → HIGH risk → human review → audit record`

## Project structure

```text
RazorGuard-AI/
├── app/
│   └── streamlit_app.py
├── data/
│   └── razorguard_transactions.csv
├── docs/
│   ├── architecture.md
│   ├── architecture.png
│   ├── 5_minute_pitch.md
│   ├── panel_qa.md
│   ├── demo_scenarios.md
│   ├── risk_scoring.md
│   ├── submission_checklist.md
│   └── github_release_checklist.md
├── models/
│   ├── risk_model.joblib
│   └── metrics.json
├── src/
│   ├── generate_data.py
│   ├── train.py
│   ├── risk_engine.py
│   ├── investigator.py
│   ├── spike_detector.py
│   └── api.py
├── tests/
│   ├── test_risk_engine.py
│   └── smoke_demo.py
├── Dockerfile
├── requirements.txt
├── LICENSE
└── README.md
```

## Run locally

Use Python 3.11–3.13 for the most predictable local demo environment.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src\train.py
python -m streamlit run app\streamlit_app.py
```

Open `http://localhost:8501`.

### API

```bash
uvicorn src.api:app --reload
```

Health check:

`GET /health`

Investigation endpoint:

`POST /v1/investigate`

A sample payload is in `docs/api_example.json`.

## Testing

```bash
python -m pytest -q
```

The clean package currently passes the included risk-engine test suite.

## Safety and limitations

This project is strictly defensive. It does not provide instructions for fraud, payment bypasses, credential theft, or attacks on payment systems. The prototype does not execute irreversible financial actions.

The biggest limitation is the synthetic benchmark. Before production use, the system would need privacy-safe historical data, temporal validation, probability calibration, drift monitoring, segment-level evaluation, model versioning, secure authentication/secrets, and a human-review feedback loop.

## Submission materials

See:

- `docs/5_minute_pitch.md` — demo script
- `docs/panel_qa.md` — likely evaluator questions
- `docs/submission_checklist.md` — submission checklist
- `docs/github_release_checklist.md` — public-repository checks

Before submission, verify the current official Razorpay challenge page, deadline, eligibility and form requirements.
