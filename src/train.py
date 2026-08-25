import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
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

    df["amount_ratio"] = (
        df["amount"] / (df["avg_transaction_amount"] + 1e-6)
    )

    df["log_amount_ratio"] = np.log1p(df["amount_ratio"])

    df["failure_rate"] = (
        df["failed_transactions_24h"]
        / df["transactions_24h"].clip(lower=1)
    )

    df["unusual_hour"] = (
        (df["hour"] <= 4) | (df["hour"] >= 23)
    ).astype(int)

    df["new_account"] = (
        df["account_age_days"] < 30
    ).astype(int)

    df["high_velocity"] = (
        df["transactions_24h"] >= 8
    ).astype(int)

    return df


def choose_threshold(y_validation, validation_proba):
    """
    Choose the operating threshold using validation data only.
    The test set remains untouched during threshold selection.
    """

    best_threshold = 0.50
    best_f1 = -1.0
    best_recall = -1.0

    for threshold in np.linspace(0.05, 0.95, 181):

        pred = (
            validation_proba >= threshold
        ).astype(int)

        f1 = f1_score(
            y_validation,
            pred,
            zero_division=0,
        )

        recall = recall_score(
            y_validation,
            pred,
            zero_division=0,
        )

        if (
            f1 > best_f1
            or (
                np.isclose(f1, best_f1)
                and recall > best_recall
            )
        ):
            best_f1 = float(f1)
            best_recall = float(recall)
            best_threshold = float(threshold)

    return best_threshold


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

df = add_features(
    pd.read_csv(DATA)
)

y = df.pop("label")

X = df.drop(
    columns=["transaction_id"]
)


# ---------------------------------------------------------
# Preprocessing
# ---------------------------------------------------------

categorical = [
    "merchant_category"
]

numeric = [
    c for c in X.columns
    if c not in categorical
]

preprocess = ColumnTransformer(
    [
        (
            "num",
            "passthrough",
            numeric,
        ),
        (
            "cat",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical,
        ),
    ]
)


# ---------------------------------------------------------
# Random Forest
# ---------------------------------------------------------

model = RandomForestClassifier(
    n_estimators=450,
    max_depth=16,
    min_samples_leaf=2,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1,
)


pipe = Pipeline(
    [
        (
            "preprocess",
            preprocess,
        ),
        (
            "model",
            model,
        ),
    ]
)


# ---------------------------------------------------------
# 60 / 20 / 20 split
#
# 60% = training
# 20% = validation
# 20% = final untouched test
# ---------------------------------------------------------

X_train_val, X_test, y_train_val, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    stratify=y,
    random_state=42,
)


X_train, X_validation, y_train, y_validation = train_test_split(
    X_train_val,
    y_train_val,
    test_size=0.25,
    stratify=y_train_val,
    random_state=42,
)


print("\nDataset split:")
print(f"Training rows:   {len(X_train)}")
print(f"Validation rows: {len(X_validation)}")
print(f"Test rows:       {len(X_test)}")


# ---------------------------------------------------------
# Train ONLY on training data
# ---------------------------------------------------------

print("\nTraining Random Forest...")

pipe.fit(
    X_train,
    y_train,
)


# ---------------------------------------------------------
# Select threshold ONLY on validation data
# ---------------------------------------------------------

print("\nSelecting threshold using validation data...")

validation_proba = pipe.predict_proba(
    X_validation
)[:, 1]

threshold = choose_threshold(
    y_validation,
    validation_proba,
)

print(
    f"Selected validation threshold: "
    f"{threshold:.3f}"
)


# ---------------------------------------------------------
# FINAL TEST
#
# Test set has not been used for:
# - training
# - threshold selection
# ---------------------------------------------------------

print("\nEvaluating on untouched test set...")

test_proba = pipe.predict_proba(
    X_test
)[:, 1]

pred = (
    test_proba >= threshold
).astype(int)


# ---------------------------------------------------------
# Confusion matrix counts
# ---------------------------------------------------------

fp = int(
    (
        (pred == 1)
        & (y_test == 0)
    ).sum()
)

fn = int(
    (
        (pred == 0)
        & (y_test == 1)
    ).sum()
)


# ---------------------------------------------------------
# Metrics
# ---------------------------------------------------------

metrics = {

    "train_rows": int(
        len(X_train)
    ),

    "validation_rows": int(
        len(X_validation)
    ),

    "test_rows": int(
        len(X_test)
    ),

    "split":
        "60/20/20 stratified "
        "train/validation/test",

    "threshold":
        float(threshold),

    "threshold_selection":
        "maximum validation F1; "
        "recall used as tie-breaker",

    "precision":
        float(
            precision_score(
                y_test,
                pred,
                zero_division=0,
            )
        ),

    "recall":
        float(
            recall_score(
                y_test,
                pred,
                zero_division=0,
            )
        ),

    "f1":
        float(
            f1_score(
                y_test,
                pred,
                zero_division=0,
            )
        ),

    "roc_auc":
        float(
            roc_auc_score(
                y_test,
                test_proba,
            )
        ),

    "confusion_matrix":
        confusion_matrix(
            y_test,
            pred,
        ).tolist(),

    "false_positive_count":
        fp,

    "false_negative_count":
        fn,

    "false_positive_cost_per_case":
        150.0,

    "false_negative_cost_per_case":
        1000.0,
}


metrics["estimated_test_loss"] = (
    fp
    * metrics["false_positive_cost_per_case"]
    +
    fn
    * metrics["false_negative_cost_per_case"]
)


# ---------------------------------------------------------
# Save model and metrics
# ---------------------------------------------------------

joblib.dump(
    pipe,
    MODEL_DIR / "risk_model.joblib"
)

(
    MODEL_DIR / "metrics.json"
).write_text(
    json.dumps(
        metrics,
        indent=2,
    )
)


# ---------------------------------------------------------
# Display final results
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("FINAL HELD-OUT TEST RESULTS")
print("=" * 60)

print(
    json.dumps(
        metrics,
        indent=2,
    )
)

print(
    "\nClassification report:\n"
)

print(
    classification_report(
        y_test,
        pred,
        zero_division=0,
    )
)