import os
import sys

# Add the project root (one level up from this file) to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import random
import time

import mlflow

from src.tracking.mlflow_setup import init_tracking


def test_connection():
    print("🚀 Testing MLflow connection via Dagshub...")

    try:
        # Initialize tracking (will automatically use .env if parameters are omitted)
        init_tracking(experiment_name="test-experiment")
    except ValueError as e:
        print(f"❌ Error: {e}")
        return

    # Start a dummy run
    with mlflow.start_run(run_name="connection_test_run"):
        print("📝 Logging parameters...")
        mlflow.log_param("test_param", "hello_world")
        mlflow.log_param("epochs", 5)

        print("📈 Logging metrics...")
        for epoch in range(5):
            dummy_loss = 1.0 / (epoch + 1) + random.uniform(0, 0.1)
            mlflow.log_metric("loss", dummy_loss, step=epoch)
            time.sleep(0.5)  # Simulate some training time

        print("✅ Run completed successfully!")
        print("Check your Dagshub repository under the MLflow Experiments tab to see this run.")


if __name__ == "__main__":
    test_connection()
