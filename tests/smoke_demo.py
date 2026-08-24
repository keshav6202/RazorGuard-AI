import sys
sys.path.insert(0, ".")
from src.risk_engine import RiskEngine

tx = {"transaction_id":"DEMO","amount":18500,"customer_age":28,"account_age_days":120,"transactions_24h":10,"avg_transaction_amount":750,"failed_transactions_24h":4,"refund_count_30d":1,"chargeback_count":1,"device_changes_7d":2,"ip_changes_24h":3,"location_change":1,"account_velocity":1.0,"merchant_category":"Electronics","hour":2,"is_weekend":0}
r = RiskEngine().score(tx)
assert r["risk_tier"] == "HIGH", r
assert r["risk_score"] >= .70, r
print(r)
