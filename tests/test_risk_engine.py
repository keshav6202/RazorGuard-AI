from src.risk_engine import RiskEngine

def test_risk_tiers():
    assert RiskEngine.risk_tier(.20) == "LOW"
    assert RiskEngine.risk_tier(.60) == "MEDIUM"
    assert RiskEngine.risk_tier(.90) == "HIGH"
