import numpy as np
import pandas as pd
from pathlib import Path

SEED = 42
N = 20000
rng = np.random.default_rng(SEED)

def make_dataset(n=N):
    amount = np.clip(rng.lognormal(7.0, 1.0, n), 20, 100000).round(2)
    avg_amount = np.clip(rng.lognormal(6.7, 0.75, n), 20, 50000).round(2)
    customer_age = rng.integers(18, 65, n)
    account_age_days = rng.integers(7, 2000, n)
    transactions_24h = rng.poisson(3, n) + 1
    failed_transactions_24h = np.minimum(transactions_24h, rng.binomial(transactions_24h, 0.12))
    refund_count_30d = rng.poisson(0.35, n)
    chargeback_count = rng.binomial(2, 0.03, n)
    device_changes_7d = rng.poisson(0.25, n)
    ip_changes_24h = rng.poisson(0.4, n)
    location_change = rng.binomial(1, 0.08, n)
    hour = rng.integers(0, 24, n)
    is_weekend = rng.binomial(1, 2/7, n)
    merchant_category = rng.choice(
        ["Electronics", "Fashion", "Grocery", "Travel", "Food", "Gaming", "Services"],
        n, p=[.16,.16,.18,.10,.16,.08,.16]
    )

    amount_ratio = np.clip(amount / avg_amount, 0, 100)
    failure_rate = failed_transactions_24h / transactions_24h
    velocity_score = np.clip(transactions_24h / 10, 0, 1)

    latent_risk = (
        .85*np.log1p(amount_ratio) +
        1.15*failure_rate +
        .70*np.clip(device_changes_7d/3, 0, 1) +
        .65*np.clip(ip_changes_24h/4, 0, 1) +
        .85*location_change +
        .95*np.clip(chargeback_count, 0, 1) +
        .30*np.clip(refund_count_30d/3, 0, 1) +
        .55*velocity_score +
        .35*((hour <= 4) | (hour >= 23)).astype(int) +
        .25*(account_age_days < 30).astype(int)
    )

    probability = 1/(1+np.exp(-(latent_risk - 4.8)))
    label = rng.binomial(1, probability)

    # Keep the synthetic positive class near 5% for a realistic baseline.
    target = int(n * .05)
    if not .04*n <= label.sum() <= .06*n:
        label[:] = 0
        label[np.argsort(latent_risk)[-target:]] = 1

    df = pd.DataFrame({
        "transaction_id": [f"TX{100000+i}" for i in range(n)],
        "amount": amount,
        "customer_age": customer_age,
        "account_age_days": account_age_days,
        "transactions_24h": transactions_24h,
        "avg_transaction_amount": avg_amount,
        "failed_transactions_24h": failed_transactions_24h,
        "refund_count_30d": refund_count_30d,
        "chargeback_count": chargeback_count,
        "device_changes_7d": device_changes_7d,
        "ip_changes_24h": ip_changes_24h,
        "location_change": location_change,
        "account_velocity": velocity_score.round(4),
        "merchant_category": merchant_category,
        "hour": hour,
        "is_weekend": is_weekend,
        "label": label
    })
    return df.sample(frac=1, random_state=SEED).reset_index(drop=True)

if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "data" / "razorguard_transactions.csv"
    out.parent.mkdir(exist_ok=True)
    df = make_dataset()
    df.to_csv(out, index=False)
    print(f"Saved {len(df):,} rows to {out}")
    print(df["label"].value_counts(normalize=True).mul(100).round(2))
