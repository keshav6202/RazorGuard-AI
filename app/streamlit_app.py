import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import json
import pandas as pd
import streamlit as st

from src.risk_engine import RiskEngine
from src.investigator import investigate
from src.spike_detector import detect_fraud_spikes

st.set_page_config(page_title="RazorGuard AI", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.block-container {padding-top:1.4rem; padding-bottom:2rem;}
.hero {padding:1.35rem 1.5rem; border:1px solid rgba(140,150,170,.25); border-radius:20px; background:linear-gradient(135deg,#202532,#0f1117); margin-bottom:1rem;}
.hero h1 {margin:0;font-size:2.4rem;letter-spacing:-.5px;}
.hero p {margin:.35rem 0 0;color:#aab3c2;font-size:1rem;}
.pill {display:inline-block;padding:.25rem .65rem;border-radius:999px;font-size:.72rem;font-weight:800;letter-spacing:.5px;background:rgba(80,180,120,.14);}
.section {font-weight:750;font-size:1.05rem;margin-top:.4rem;}
.note {border:1px solid rgba(140,150,170,.2);border-radius:14px;padding:.85rem 1rem;background:rgba(255,255,255,.025);}
</style>
""", unsafe_allow_html=True)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "razorguard_transactions.csv"
METRICS = ROOT / "models" / "metrics.json"

try:
    engine = RiskEngine()
except Exception as exc:
    st.error("Risk model could not be loaded. Run `python src/train.py` first.")
    st.exception(exc)
    st.stop()

df = pd.read_csv(DATA) if DATA.exists() else pd.DataFrame()
metrics = json.loads(METRICS.read_text()) if METRICS.exists() else {}

st.markdown("""
<div class="hero">
  <span class="pill">DEFENSIVE FINTECH RISK INTELLIGENCE</span>
  <h1>🛡️ RazorGuard AI</h1>
  <p>Detect suspicious payment behavior → verify evidence → route elevated risk to controlled human review.</p>
</div>
""", unsafe_allow_html=True)

m1,m2,m3,m4 = st.columns(4)
m1.metric("Precision", f"{metrics.get('precision',0):.2%}")
m2.metric("Recall", f"{metrics.get('recall',0):.2%}")
m3.metric("F1 Score", f"{metrics.get('f1',0):.2%}")
m4.metric("ROC-AUC", f"{metrics.get('roc_auc',0):.2%}")
st.caption(
    f"Held-out prototype benchmark • "
    f"{metrics.get('test_rows', 0):,} synthetic test transactions • "
    f"Threshold selected on validation data • "
    f"Not production fraud performance"
)

tab1, tab2, tab3 = st.tabs(["🔎 Transaction Investigator", "📊 Risk Analytics", "🧠 Methodology"])

with tab1:
    st.markdown('<div class="section">Transaction investigation</div>', unsafe_allow_html=True)
    st.write("Use a preset for the demo or enter a transaction manually. The ML model estimates risk; a transparent behavioral guardrail adds explainable evidence.")

    with st.sidebar:
        st.header("Transaction")
        scenario = st.radio("Demo scenario", ["Normal", "Suspicious", "Boundary", "Custom"], index=1)
        presets = {
            "Normal": dict(amount=650.0, age=32, account_age=620, tx24=2, avg=700.0, failed=0, refunds=0, chargebacks=0, devices=0, ips=0, location=0, category="Grocery", hour=14, weekend=0),
            "Suspicious": dict(amount=18500.0, age=28, account_age=120, tx24=10, avg=750.0, failed=4, refunds=1, chargebacks=1, devices=2, ips=3, location=1, category="Electronics", hour=2, weekend=0),
            "Boundary": dict(amount=2200.0, age=35, account_age=400, tx24=4, avg=900.0, failed=1, refunds=0, chargebacks=0, devices=1, ips=1, location=0, category="Fashion", hour=19, weekend=0),
            "Custom": dict(amount=4500.0, age=28, account_age=120, tx24=8, avg=750.0, failed=3, refunds=1, chargebacks=0, devices=2, ips=3, location=0, category="Electronics", hour=2, weekend=0),
        }
        p = presets[scenario]
        amount = st.number_input("Amount (₹)", min_value=20.0, value=float(p["amount"]), step=100.0)
        age = st.number_input("Customer age", 18, 100, int(p["age"]))
        account_age = st.number_input("Account age (days)", 1, 5000, int(p["account_age"]))
        tx24 = st.number_input("Transactions in 24h", 1, 100, int(p["tx24"]))
        avg = st.number_input("Average transaction (₹)", 20.0, 100000.0, float(p["avg"]), step=50.0)
        failed = st.number_input("Failed transactions in 24h", 0, 100, int(p["failed"]))
        refunds = st.number_input("Refunds in 30d", 0, 50, int(p["refunds"]))
        chargebacks = st.number_input("Previous chargebacks", 0, 20, int(p["chargebacks"]))
        devices = st.number_input("Device changes in 7d", 0, 20, int(p["devices"]))
        ips = st.number_input("IP changes in 24h", 0, 50, int(p["ips"]))
        location = st.selectbox("Location changed?", [0,1], index=int(p["location"]))
        cats = ["Electronics","Fashion","Grocery","Travel","Food","Gaming","Services"]
        category = st.selectbox("Merchant category", cats, index=cats.index(p["category"]))
        hour = st.slider("Transaction hour", 0, 23, int(p["hour"]))
        weekend = st.selectbox("Weekend?", [0,1], index=int(p["weekend"]))

    tx = {
        "transaction_id":"LIVE-DEMO", "amount":amount, "customer_age":age,
        "account_age_days":account_age, "transactions_24h":tx24,
        "avg_transaction_amount":avg, "failed_transactions_24h":failed,
        "refund_count_30d":refunds, "chargeback_count":chargebacks,
        "device_changes_7d":devices, "ip_changes_24h":ips,
        "location_change":location, "account_velocity":min(tx24/10,1.0),
        "merchant_category":category, "hour":hour, "is_weekend":weekend,
    }

    if st.button("🔍 Investigate Transaction", type="primary", width="stretch"):
        result = engine.score(tx)
        inv = investigate(tx, result["risk_score"])
        st.session_state.last = {**result, **inv, "tx": tx}

    if "last" in st.session_state:
        r = st.session_state.last
        score = r["risk_score"]
        st.divider()
        a,b,c = st.columns(3)
        a.metric("Hybrid risk score", f"{score:.1%}")
        b.metric("Risk tier", r["risk_tier"])
        c.metric("Human review", "REQUIRED" if r["human_approval_required"] else "NOT REQUIRED")
        st.progress(min(score,1.0), text=f"Risk intensity: {score:.1%}")
        s1,s2 = st.columns(2)
        s1.metric("ML probability", f"{r.get('ml_probability',0):.1%}")
        s2.metric("Behavioral guardrail", f"{r.get('behavioral_risk',0):.1%}")
        if r["risk_tier"] == "HIGH": st.error("🔴 HIGH RISK — HOLD FOR HUMAN REVIEW")
        elif r["risk_tier"] == "MEDIUM": st.warning("🟠 MEDIUM RISK — STEP-UP REVIEW")
        else: st.success("🟢 LOW RISK — ALLOW WITH MONITORING")
        left,right = st.columns([1.25,1])
        with left:
            st.subheader("Why was it flagged?")
            for item in r["evidence"]: st.write("✓ " + item)
        with right:
            st.subheader("Recommended action")
            st.info(r["recommended_action"].replace("_"," "))
            st.markdown('<div class="note">Defense-only: elevated-risk recommendations require human review and do not execute irreversible financial actions.</div>', unsafe_allow_html=True)
        with st.expander("View audit record"):
            st.json({"timestamp":r["timestamp"],"risk_score":r["risk_score"],"ml_probability":r.get("ml_probability"),"behavioral_risk":r.get("behavioral_risk"),"evidence":r["evidence"],"recommended_action":r["recommended_action"],"human_approval_required":r["human_approval_required"],"defensive_only":r["defensive_only"]})
    else:
        st.info("Select **Suspicious** and click Investigate Transaction for the main demo.")

with tab2:
    st.subheader("Risk analytics")
    if df.empty:
        st.warning("Dataset not found.")
    else:
        x,y,z = st.columns(3)
        x.metric("Transactions", f"{len(df):,}")
        y.metric("Suspicious", f"{int(df.label.sum()):,}")
        z.metric("Suspicious rate", f"{df.label.mean():.2%}")
        spike = detect_fraud_spikes(df)
        st.markdown("### Suspicious-rate by transaction hour")
        st.bar_chart(spike.set_index("hour")["risk_rate"])
        st.markdown("### Highest-risk cohorts")
        show = spike.head(8).copy()
        show["risk_rate"] = show["risk_rate"].map(lambda v:f"{v:.2%}")
        show["risk_rate_lift"] = show["risk_rate_lift"].map(lambda v:f"{v:.1f}×")
        show["spike_flag"] = show["spike_flag"].map(lambda v:"🚨 YES" if v else "No")
        st.dataframe(show, hide_index=True, width="stretch")
        st.markdown("### Held-out evaluation")
        ev = pd.DataFrame({
            "Metric": ["Precision", "Recall", "F1", "ROC-AUC"],
            "Score": [
                metrics.get("precision", 0),
                metrics.get("recall", 0),
                metrics.get("f1", 0),
                metrics.get("roc_auc", 0)
            ]
        })
        ev["Score"] = ev["Score"].map(lambda v: f"{v:.2%}")
        st.dataframe(ev, hide_index=True, width="stretch")

        st.caption(
            f"False positives: {metrics.get('false_positive_count', '—')} • "
            f"False negatives: {metrics.get('false_negative_count', '—')} • "
            f"Estimated benchmark loss: ₹{metrics.get('estimated_test_loss', 0):,.0f}"
        )

        st.caption(
            f"Evaluation: {metrics.get('split', 'stratified train/validation/test split')} • "
            f"Threshold: {metrics.get('threshold', 0):.2f} • "
            f"{metrics.get('threshold_selection', 'validation-based threshold selection')}"
        )
        ev = pd.DataFrame({"Metric":["Precision","Recall","F1","ROC-AUC"],"Score":[metrics.get("precision",0),metrics.get("recall",0),metrics.get("f1",0),metrics.get("roc_auc",0)]})
        ev["Score"] = ev["Score"].map(lambda v:f"{v:.2%}")
        st.dataframe(ev, hide_index=True, width="stretch")
        st.caption(f"False positives: {metrics.get('false_positive_count', '—')} • "
                f"False negatives: {metrics.get('false_negative_count', '—')} • "
                f"Estimated benchmark loss: ₹{metrics.get('estimated_test_loss', 0):,.0f}"
)

        st.caption(f"Evaluation: {metrics.get('split', 'stratified train/validation/test split')} • "
                    f"Threshold: {metrics.get('threshold', 0):.2f} • "
                    f"{metrics.get('threshold_selection', 'validation-based threshold selection')}"
)

with tab3:
    st.subheader("System design")
    st.markdown("""
**Detection → Verification → Decision → Human Control**

1. **ML detector:** Random Forest learns nonlinear patterns from payment behavior.
2. **Behavioral guardrail:** transparent risk signals verify that multiple observable red flags are not ignored.
3. **Investigation layer:** converts signals into evidence a reviewer can understand.
4. **Bounded action:** LOW → monitoring, MEDIUM → step-up review, HIGH → human review.
5. **Auditability:** score, evidence and recommendation are preserved as a structured record.

### Why hybrid scoring?
The ML model is the primary learned signal. The transparent policy layer is a safety guardrail, not a claim of calibrated probability. In production, the hybrid score would be calibrated on a validation set and evaluated on privacy-safe historical outcomes.

### Data disclosure
The 20,000-row dataset is synthetic and reproducible. The benchmark must not be presented as real Razorpay fraud performance.
""")
    diagram = ROOT / "docs" / "architecture.png"
    if diagram.exists(): st.image(str(diagram), caption="RazorGuard AI architecture", width="stretch")

st.divider()
st.caption("RazorGuard AI • Defensive prototype • AI Risk Manager concept")
