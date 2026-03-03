"""Model Promotion Quality Gate.

Checks the latest model version in the MLflow Model Registry against
an F1 threshold. If it passes, promotes it to Production.

Supports two lookup strategies:
  1. Staging-based: checks models explicitly set to the "Staging" stage.
  2. Latest-version fallback: if no Staging model exists, checks the most
     recently registered version (used by the automated fine-tuning pipeline).

Environment variables:
    MLFLOW_TRACKING_URI   — MLflow tracking server URL (required)
    MODEL_NAME            — registered model name (default: QA_Model)
    F1_THRESHOLD          — minimum F1 to pass (default: 0.5)
"""

import os
import sys

import mlflow

MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "")
MODEL_NAME = os.environ.get("MODEL_NAME", "QA_Model")
F1_THRESHOLD = float(os.environ.get("F1_THRESHOLD", "0.5"))

if not MLFLOW_TRACKING_URI:
    print("MLFLOW_TRACKING_URI not set")
    sys.exit(1)

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
client = mlflow.tracking.MlflowClient()

# Strategy 1: look for models explicitly in "Staging"
model_version = None
try:
    versions = client.get_latest_versions(MODEL_NAME, stages=["Staging"])
    if versions:
        model_version = versions[0]
        print(f"Found model in Staging: v{model_version.version}")
except Exception:
    pass

# Strategy 2: fallback to the latest registered version (any stage)
if model_version is None:
    try:
        all_versions = client.search_model_versions(f"name='{MODEL_NAME}'")
        if all_versions:
            model_version = max(all_versions, key=lambda v: int(v.version))
            print(f"No Staging model — using latest version: v{model_version.version}")
    except Exception as e:
        print(f"Failed to search model versions: {e}")

if model_version is None:
    print(f"No model versions found for '{MODEL_NAME}'")
    sys.exit(1)

run = client.get_run(model_version.run_id)
# Check both 'best_val_f1' (from trainer) and 'f1' as fallback
f1 = (
    run.data.metrics.get("best_val_f1")
    or run.data.metrics.get("val_f1")
    or run.data.metrics.get("f1", 0.0)
)

print(f"Model: {MODEL_NAME} v{model_version.version}")
print(f"F1 Score: {f1}")
print(f"Threshold: {F1_THRESHOLD}")

if f1 < F1_THRESHOLD:
    print(f"BLOCKED: F1 {f1} is below threshold {F1_THRESHOLD}")
    sys.exit(1)

print("PASSED: promoting model to Production")
try:
    client.transition_model_version_stage(
        name=MODEL_NAME,
        version=model_version.version,
        stage="Production",
    )
    print(f"✅ Model v{model_version.version} promoted to Production")
except Exception as e:
    # MLflow v2+ may use aliases instead of stages
    print(f"⚠️  Stage transition failed ({e}), attempting alias-based promotion...")
    try:
        client.set_registered_model_alias(MODEL_NAME, "production", model_version.version)
        print(f"✅ Model v{model_version.version} aliased as 'production'")
    except Exception as e2:
        print(f"❌ Alias promotion also failed: {e2}")
        sys.exit(1)
