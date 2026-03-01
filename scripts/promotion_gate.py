import os
import sys

import mlflow

MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "")
MODEL_NAME = os.environ.get("MODEL_NAME", "qa-model")
F1_THRESHOLD = float(os.environ.get("F1_THRESHOLD", "0.5"))

if not MLFLOW_TRACKING_URI:
    print("MLFLOW_TRACKING_URI not set")
    sys.exit(1)

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
client = mlflow.tracking.MlflowClient()

versions = client.get_latest_versions(MODEL_NAME, stages=["Staging"])
if not versions:
    print(f"No model in Staging for '{MODEL_NAME}'")
    sys.exit(1)

model_version = versions[0]
run = client.get_run(model_version.run_id)
f1 = run.data.metrics.get("f1", 0.0)

print(f"Model: {MODEL_NAME} v{model_version.version}")
print(f"F1 Score: {f1}")
print(f"Threshold: {F1_THRESHOLD}")

if f1 < F1_THRESHOLD:
    print(f"BLOCKED: F1 {f1} is below threshold {F1_THRESHOLD}")
    sys.exit(1)

print("PASSED: promoting model to Production")
client.transition_model_version_stage(
    name=MODEL_NAME,
    version=model_version.version,
    stage="Production",
)
