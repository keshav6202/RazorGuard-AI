from datetime import datetime, timezone

def investigate(transaction: dict, risk_score: float) -> dict:
    evidence = []
    amount = float(transaction["amount"])
    avg = max(float(transaction["avg_transaction_amount"]), 1.0)
    ratio = amount / avg
    if ratio >= 5:
        evidence.append(f"Amount is {ratio:.1f}× the customer's recent average.")
    elif ratio >= 2:
        evidence.append(f"Amount is elevated at {ratio:.1f}× the customer's recent average.")
    if int(transaction["failed_transactions_24h"]) >= 3:
        evidence.append("Multiple failed transactions occurred in the last 24 hours.")
    if int(transaction["device_changes_7d"]) >= 2:
        evidence.append("Multiple device changes were observed recently.")
    if int(transaction["ip_changes_24h"]) >= 3:
        evidence.append("Multiple IP changes were observed recently.")
    if int(transaction["location_change"]) == 1:
        evidence.append("The transaction location differs from the recent pattern.")
    if int(transaction["chargeback_count"]) > 0:
        evidence.append("The account has previous chargeback history.")
    if int(transaction["hour"]) <= 4 or int(transaction["hour"]) >= 23:
        evidence.append("The transaction occurred in an unusual late-night window.")
    if int(transaction["account_age_days"]) < 30:
        evidence.append("The account is relatively new.")
    if risk_score >= 0.70:
        action = "HOLD_FOR_HUMAN_REVIEW"
    elif risk_score >= 0.45:
        action = "STEP_UP_REVIEW"
    else:
        action = "ALLOW_WITH_MONITORING"
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "risk_score": round(risk_score, 4),
        "evidence": evidence or ["No strong risk signal detected."],
        "recommended_action": action,
        "human_approval_required": risk_score >= 0.45,
        "defensive_only": True,
    }
