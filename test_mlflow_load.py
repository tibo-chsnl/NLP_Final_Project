import os
import sys

# Change to project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.inference import get_inference_pipeline


def test_load():
    print("Testing MLflow Load...")
    # These must be true to trigger MLflow load
    # os.environ["USE_MLFLOW"] = "true"

    try:
        pipeline = get_inference_pipeline()

        if pipeline.is_dummy:
            print("❌ Model loaded as a Dummy Model. MLflow load failed.")
        else:
            print("✅ Model successfully loaded!")
            print(f"Model vocab size: {pipeline.vocab_size}")

    except Exception as e:
        print(f"❌ Error during model load: {e}")


if __name__ == "__main__":
    test_load()
