# Work Division: NLP & MLOps Final Project (QA System Web App)

## 👥 Team Roles Overview

To successfully deliver a production-grade machine learning system that satisfies the requirements for both the NLP and MLOps projects, the responsibilities have been cross-functionally divided. Each member contributes to both the core Machine Learning modeling (NLP) and the Engineering/Deployment lifecycle (MLOps).

| Role | Focus Area | Primary Responsibilities |
| :--- | :--- | :--- |
| **Thibault CHESNEL** | **Data Engineering & CI/CD** | Dataset Loading/Preprocessing (NLP), Data Versioning/DVC, GitHub Actions (CI/CD Pipelines), Unit Tests. |
| **Axel STOLTZ** | **Model Architect & Backend API** | Neural Network Design (NLP), Python Backend (FastAPI/Flask API), MLflow Tracking, Integration Tests. |
| **Alon DEBASC** | **Training, Frontend & Deployment** | Model Training & Tuning (NLP), Staging/Prod Deployment, Model Promotion Gates, React/Next.js UI, E2E Tests. |

---

## 🛠️ Detailed Responsibilities

### 🧑‍💻 Thibault CHESNEL: Data Engineering & CI/CD (The Pipeline)
**Goal:** Ensure the model is fed clean, versioned data and that all code/models are automatically tested and built safely.

*   **NLP Focus (Data Engine):**
    *   Load and parse **SQuAD 2.0** JSON data. Add cleaning and tokenization.
    *   Separate Data into Train, Validation, and Test sets.
    *   Implement **Exact Match (EM)** and **F1 Score** evaluation metrics.
*   **MLOps Focus (Data & Operations):**
    *   Setup and manage **DVC** (Data Version Control) to track raw training data remotely.
    *   Manage data augmentation (incorporating new SQuAD-format data collected from the Web UI).
    *   Create **GitHub Actions** CI/CD pipelines (PR verification, Unit tests).
    *   Write the required **Unit Tests** for the data processing functions.

### 🧑‍💻 Axel STOLTZ: Model Architect & Backend API (The Brain & API)
**Goal:** Build the Deep Neural Network that processes the inputs, and wrap it in a robust versioned backend for inference.

*   **NLP Focus (Core Architecture):**
    *   Define the PyTorch/TensorFlow Module structure (Encoding, Attention mechanisms).
    *   Design the Output Layer to predict `Start Index` and `End Index` logits.
    *   Document layer implementations and algorithms.
*   **MLOps Focus (Tracking & Serving):**
    *   Build the **Python Backend** (using FastAPI or Flask) to serve the model as an API endpoint to the frontend.
    *   Integrate **MLflow** experiments and Model Registry (logging metrics, parameters, and model weights).
    *   Write the required **Integration Tests** uniting the model within the backend service.

### 🧑‍💻 Alon DEBASC: Training, Frontend & Deployment (The Engine & Face)
**Goal:** Train and hyper-tune the NLP model, present it through a user-friendly frontend, and securely deploy the full system.

*   **NLP Focus (Training Loop):**
    *   Implement the main optimization loop (Forward -> Loss -> Backward -> Step).
    *   Tune Hyperparameters and maintain Google Colab training efficiency.
*   **MLOps Focus (Promotion & Web App):**
    *   Build the **Node.js Frontend** (React/Next.js) for the interactive QA Assistant Web UI (including the user feedback loop for data augmentation).
    *   Manage **Cloud Deployment** (e.g., Render, Railway) ensuring isolated `dev`, `staging`, and `main` environments via 12-Factor App methodology.
    *   Implement **Model Promotion Quality Gates** (e.g., stopping deployment if the candidate model fails the F1 Score threshold).
    *   Write **End-to-End (E2E) Tests** for the full application stack.

---

## 🔄 Collaboration Points & Workflows

*   **Git Branching Model**: All work is strictly done on `feature/*` branches, merged into `dev` after passing PR gates, then promoted to `staging` and finally `main`.
*   **Model Lifecycle**: 
    1. Training uses DVC-tracked data and logs metrics to MLflow.
    2. Candidate models are pushed to the Model Registry.
    3. Pipeline automatically deploys the staging app with the candidate model.
    4. Only upon passing quality gates does the model reach `main` (Production).
