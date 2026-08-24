# RazorGuard AI — Panel Questions

## 1. Why Random Forest?

It provides a strong tabular baseline, handles nonlinear feature interactions,
is robust for mixed financial-behavior features, and is easy to benchmark.
I would compare it with gradient boosting and calibrated alternatives before
production.

## 2. Why not optimize for accuracy?

Because the suspicious class is only about 5% in the synthetic benchmark.
A model that predicts everything as normal can achieve high accuracy while
missing the cases that matter. Precision and recall better describe the
risk-detection tradeoff.

## 3. What is data leakage?

Using information that would not be available when the prediction is made.
For example, using a post-investigation fraud-confirmation field would leak
the answer into the model.

## 4. Why held-out testing?

It estimates performance on unseen examples. Training performance alone can
hide overfitting.

## 5. Why is false-positive cost important?

A false positive can cause unnecessary customer friction or manual review.
The project therefore makes the cost assumption explicit rather than hiding
the tradeoff behind one accuracy number.

## 6. Why synthetic data?

It is safe and reproducible for a public prototype. It is not a substitute
for real-world validation. A production system would require privacy-safe
historical data, careful labeling, drift monitoring and calibration.

## 7. Is the system actually AI?

Yes. The core risk detector is a machine-learning model and the workflow
adds automated evidence generation and risk investigation. The design avoids
using an LLM where a measurable model is more appropriate.

## 8. Why not let the AI block payments automatically?

Financial actions need bounded authority. A high-risk prediction can be wrong.
The prototype therefore routes elevated risk to human review instead of
granting unrestricted autonomous financial control.

## 9. What happens when the model is wrong?

The audit trail preserves the score, evidence and recommendation. In a
production system, reviewer outcomes would become feedback for monitoring,
retraining and threshold calibration.

## 10. How would you improve the model?

Use a validation set for threshold tuning, compare gradient boosting,
calibrate probabilities, add temporal validation, monitor drift, test
segment-level performance, and validate against real historical outcomes.

## 11. How would you deploy it?

The project exposes a FastAPI endpoint and has a Streamlit demo. A production
deployment would place the API behind authentication, monitoring and rate
limits, with a versioned model registry and secure secrets management.

## 12. What is your strongest engineering decision?

Separating detection from action. The model estimates risk; the investigation
layer explains evidence; the policy layer bounds the action. That separation
makes the system easier to test, audit and replace.

## 13. What is the biggest weakness?

The benchmark data is synthetic. The reported metrics are useful for proving
the pipeline works, but they are not evidence of real-world fraud performance.
That limitation is explicitly disclosed.

## 14. Why this track?

It matches my background in Python, SQL, machine learning and risk analytics,
while forcing me to build a complete product rather than only a notebook.
