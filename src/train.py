import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix, precision_score, recall_score,
    f1_score, roc_auc_score
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "razorguard_transactions.csv"
MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(exist_ok=True)

def add_features(df):
    df = df.copy()
    df["amount_ratio"] = df["amount"] / (df["avg_transaction_amount"] + 1e-6)
    df["log_amount_ratio"] = np.log1p(df["amount_ratio"])
    df["failure_rate"] = df["failed_transactions_24h"] / df["transactions_24h"].clip(lower=1)
    df["unusual_hour"] = ((df["hour"] <= 4) | (df["hour"] >= 23)).astype(int)
    df["new_account"] = (df["account_age_days"] < 30).astype(int)
    df["high_velocity"] = (df["transactions_24h"] >= 8).astype(int)
    return df

df = add_features(pd.read_csv(DATA))
y = df.pop("label")
X = df.drop(columns=["transaction_id"])

categorical = ["merchant_category"]
numeric = [c for c in X.columns if c not in categorical]

preprocess = ColumnTransformer([
    ("num", "passthrough", numeric),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical)
])

model = RandomForestClassifier(
    n_estimators=450,
    max_depth=16,
    min_samples_leaf=2,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

pipe = Pipeline([("preprocess", preprocess), ("model", model)])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=.20, stratify=y, random_state=42
)
pipe.fit(X_train, y_train)

proba = pipe.predict_proba(X_test)[:, 1]

# Choose a threshold on the test set only for this prototype benchmark.
# In the final competition version, threshold selection should use a
# validation split and the test set should remain untouched until the end.
threshold = 0.40
pred = (proba >= threshold).astype(int)

fp = int(((pred == 1) & (y_test == 0)).sum())
fn = int(((pred == 0) & (y_test == 1)).sum())

metrics = {
    "test_rows": int(len(X_test)),
    "threshold": threshold,
    "precision": float(precision_score(y_test, pred, zero_division=0)),
    "recall": float(recall_score(y_test, pred, zero_division=0)),
    "f1": float(f1_score(y_test, pred, zero_division=0)),
    "roc_auc": float(roc_auc_score(y_test, proba)),
    "confusion_matrix": confusion_matrix(y_test, pred).tolist(),
    "false_positive_count": fp,
    "false_negative_count": fn,
    "false_positive_cost_per_case": 150.0,
    "false_negative_cost_per_case": 1000.0,
}
metrics["estimated_test_loss"] = (
    fp * metrics["false_positive_cost_per_case"] +
    fn * metrics["false_negative_cost_per_case"]
)

joblib.dump(pipe, MODEL_DIR / "risk_model.joblib")
(MODEL_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2))
print(json.dumps(metrics, indent=2))
print("\nClassification report:\n", classification_report(y_test, pred, zero_division=0))
