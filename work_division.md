# Work Division: NLP Final Project (Question Answering System)

Based on the project requirements outlined in the README and the team size of 3 developers, here is a proposed division of work to ensure efficient parallel development and clear ownership.

## 👥 Team Roles Overview

| Role | Focus Area | Primary Responsibilities |
| :--- | :--- | :--- |
| **Developer 1** | **Data & Evaluation** | Dataset loading, Preprocessing, Tokenization, Evaluation Metrics. |
| **Developer 2** | **Model Architecture** | Neural Network Design, Layer Implementation, Forward Pass Logic. |
| **Developer 3** | **Training & Ops** | Training Loop, Optimization, Checkpointing, Colab/GPU Setup, Experiments. |

---

## 🛠️ Detailed Responsibilities

### 🧑‍💻 Developer 1: Data Engineer (The Foundation)
**Goal:** Ensure the model is fed clean, correctly shaped data and can be evaluated accurately.

*   **Dataset Handling**:
    *   Load and parse **SQuAD 2.0** JSON data.
    *   Separate Data into Train, Validation, and Test sets.
    *   Handle `is_impossible` questions (filter them out as per requirements).
*   **Preprocessing & Tokenization**:
    *   Implement text cleaning (lowercasing, punctuation removal).
    *   Build Vocabulary and Word Embeddings (Glossary/Index mapping).
    *   Convert Contexts and Questions into numerical indices/tensors.
    *   **Crucial**: Map `answer_start` character indices to token indices.
*   **Evaluation Metrics**:
    *   Implement **Exact Match (EM)** score.
    *   Implement **F1 Score**.
    *   Create a robust validation function to compare specific predictions vs. ground truth.

### 🧑‍💻 Developer 2: Model Architect (The Brain)
**Goal:** Build the Deep Neural Network that processes the inputs and predicts the answer span.

*   **Model Design**:
    *   Define the PyTorch/TensorFlow Module structure.
    *   **Embedding Layer**: Implement word embeddings (Glove, Word2Vec, or Iearned).
*   **Core Architecture**:
    *   Implement Encoding Layers (RNNs, LSTMs, GRUs, or Transformers/Attention mechanisms).
    *   Implement Context-Question Interaction layers (Attention mechanisms, etc.).
*   **Output Layer**:
    *   Design the output head to predict `Start Index` and `End Index` logits.
    *   Ensure model handles variable-length sequences (Padding/Masking logic).
*   **Documentation**:
    *   Document every layer and algorithm choice as required by the project description.

### 🧑‍💻 Developer 3: MLOps & Training Engineer (The Engine)
**Goal:** Create the environment where the model learns, optimizes, and improves.

*   **Training Loop**:
    *   Implement the main optimization loop (Forward pass -> Loss Calculation -> Backward pass -> Optimizer Step).
    *   Define the Loss Function (e.g., CrossEntropyLoss for Start and End pointers).
*   **Optimization**:
    *   Tune Hyperparameters (Learning Rate, Batch Size, Dropout, Hidden Dims).
    *   Setup Optimizers (Adam, SGD, etc.).
*   **Infrastructure & Monitoring**:
    *   **Google Colab Setup**: Ensure GPU acceleration is correctly utilized.
    *   **Checkpointing**: Implement logic to save and load model state (`model.pt`) to/from Google Drive to prevent data loss.
    *   **Visualization**: Integrate **TensorBoard** to track Loss and Accuracy curves over epochs.
    *   Create the "Live Demo" notebook logic.

---

## 🔄 Collaboration Points (Integration)

*   **Dev 1 & Dev 2**: Agree on **Input Shapes** (Batch Size, Seq Length) and **Embedding Dimensions**.
*   **Dev 2 & Dev 3**: Agree on the model's `forward()` output format (Logits? Softmax?) to ensure the Loss Function is applied correctly.
*   **All**: Weekly sync to merge code and ensure the Data Generator feeds the Model correctly for the Training Loop.
