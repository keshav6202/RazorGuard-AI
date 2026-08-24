from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.risk_engine import RiskEngine
from src.investigator import investigate

app = FastAPI(title="RazorGuard AI API", version="1.0.0")
engine = RiskEngine()

class Transaction(BaseModel):
    transaction_id: str = "API-DEMO"
    amount: float = Field(gt=0)
    customer_age: int = Field(ge=18, le=100)
    account_age_days: int = Field(ge=1)
    transactions_24h: int = Field(ge=1)
    avg_transaction_amount: float = Field(gt=0)
    failed_transactions_24h: int = Field(ge=0)
    refund_count_30d: int = Field(ge=0)
    chargeback_count: int = Field(ge=0)
    device_changes_7d: int = Field(ge=0)
    ip_changes_24h: int = Field(ge=0)
    location_change: int = Field(ge=0, le=1)
    account_velocity: float = Field(ge=0, le=1)
    merchant_category: str
    hour: int = Field(ge=0, le=23)
    is_weekend: int = Field(ge=0, le=1)

@app.get("/health")
def health():
    return {"status": "ok", "system": "RazorGuard AI", "defensive_only": True}

@app.post("/v1/investigate")
def investigate_transaction(tx: Transaction):
    payload = tx.model_dump()
    score = engine.score(payload)
    investigation = investigate(payload, score["risk_score"])
    return {**payload, **score, **investigation}
