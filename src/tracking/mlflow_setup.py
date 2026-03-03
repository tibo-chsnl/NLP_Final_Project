import os

import dagshub
import mlflow
from dotenv import load_dotenv


def init_tracking(
    repo_owner: str = None, repo_name: str = None, experiment_name: str = "QA_Model_Training"
) -> None:
    """
    Initializes Dagshub and sets up MLflow tracking, prioritizing .env variables.
    Args:
        repo_owner: The owner of the Dagshub repository. Defaults to DAGSHUB_USER_NAME in .env.
        repo_name: The name of the Dagshub repository. Defaults to DAGSHUB_REPO_NAME in .env.
        experiment_name: The name of the MLflow experiment to log to.
    """
    # Load environment variables from .env file
    load_dotenv()

    _repo_owner = repo_owner or os.environ.get("DAGSHUB_USER_NAME")
    _repo_name = repo_name or os.environ.get("DAGSHUB_REPO_NAME")

    if not _repo_owner or not _repo_name:
        raise ValueError(
            "Missing Dagshub credentials. Please set DAGSHUB_USER_NAME and DAGSHUB_REPO_NAME "
            "in your .env file, or pass them directly to init_tracking()."
        )

    print(f"🔗 Connecting to Dagshub repository: {_repo_owner}/{_repo_name}")

    # Initialize Dagshub (this sets up the MLflow tracking URI automatically)
    dagshub.init(repo_name=_repo_name, repo_owner=_repo_owner, mlflow=True)

    # Set the MLflow experiment
    mlflow.set_experiment(experiment_name)
    print(f"🎯 MLflow Experiment set to: '{experiment_name}'")


if __name__ == "__main__":
    # Example usage / placeholder
    print("Please use this module by calling init_tracking() in your training scripts.")
