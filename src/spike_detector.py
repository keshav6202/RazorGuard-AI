import pandas as pd
import numpy as np

def detect_fraud_spikes(df, time_col="hour"):
    d = df.copy()

    # Synthetic dataset has hour-of-day, so we use hourly cohorts.
    hourly = (
        d.groupby(time_col)
        .agg(
            transactions=("transaction_id", "count"),
            suspicious=("label", "sum"),
            total_amount=("amount", "sum"),
        )
        .reset_index()
    )

    hourly["risk_rate"] = hourly["suspicious"] / hourly["transactions"].clip(lower=1)
    baseline = hourly["risk_rate"].median()
    hourly["risk_rate_lift"] = hourly["risk_rate"] / max(baseline, 1e-9)
    hourly["spike_flag"] = hourly["risk_rate_lift"] >= 2.0

    return hourly.sort_values("risk_rate", ascending=False).reset_index(drop=True)
