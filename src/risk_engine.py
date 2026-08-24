from pathlib import Path
import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "risk_model.joblib"

def add_features(df):
    df = df.copy()
    df["amount_ratio"] = df["amount"] / (df["avg_transaction_amount"] + 1e-6)
    df["log_amount_ratio"] = np.log1p(df["amount_ratio"])
    df["failure_rate"] = df["failed_transactions_24h"] / df["transactions_24h"].clip(lower=1)
    df["unusual_hour"] = ((df["hour"] <= 4) | (df["hour"] >= 23)).astype(int)
    df["new_account"] = (df["account_age_days"] < 30).astype(int)
    df["high_velocity"] = (df["transactions_24h"] >= 8).astype(int)
    return df

def behavioral_risk(tx):
    """Transparent safety-policy score based on observable risk signals."""
    amount_ratio = tx["amount"] / max(tx["avg_transaction_amount"], 1.0)
    amount_signal = min(max((amount_ratio - 1.0) / 9.0, 0.0), 1.0)
    failure_signal = min(tx["failed_transactions_24h"] / 5.0, 1.0)
    device_signal = min(tx["device_changes_7d"] / 3.0, 1.0)
    ip_signal = min(tx["ip_changes_24h"] / 4.0, 1.0)
    location_signal = float(tx["location_change"])
    chargeback_signal = min(tx["chargeback_count"] / 2.0, 1.0)
    late_signal = float(tx["hour"] <= 4 or tx["hour"] >= 23)
    velocity_signal = min(tx["transactions_24h"] / 12.0, 1.0)
    signals = [amount_signal, failure_signal, device_signal, ip_signal,
               location_signal, chargeback_signal, late_signal, velocity_signal]
    weights = [1.4, 1.4, 1.0, 1.0, 1.2, 1.3, .6, .8]
    return float(np.average(signals, weights=weights))

class RiskEngine:
    def __init__(self, model_path=MODEL_PATH):
        self.model = joblib.load(model_path)
        # The persisted classifier was trained with n_jobs=-1. In constrained
        # Windows environments, parallel prediction can fail while creating
        # worker resources, so serve interactive requests on one worker.
        if hasattr(self.model, "named_steps") and "model" in self.model.named_steps:
            self.model.named_steps["model"].n_jobs = 1

    @staticmethod
    def risk_tier(score):
        if score >= 0.70:
            return "HIGH"
        if score >= 0.45:
            return "MEDIUM"
        return "LOW"

    def score(self, transaction):
        tx_df = pd.DataFrame([transaction]).drop(columns=["transaction_id"], errors="ignore")
        features = add_features(tx_df)
        ml_score = float(self.model.predict_proba(features)[:, 1][0])
        policy_score = behavioral_risk(transaction)
        final_score = float(0.70 * ml_score + 0.30 * policy_score)
        return {
            "risk_score": final_score,
            "ml_probability": ml_score,
            "behavioral_risk": policy_score,
            "risk_tier": self.risk_tier(final_score),
        }
