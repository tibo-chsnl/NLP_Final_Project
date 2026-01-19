# NLP Final Project: Automated Question Answering System

This repository contains the final project realized within the framework of the Master 2 (M2) course titled "Natural Language Processing". The objective is to develop a Closed-Domain Question Answering (QA) system capable of intelligently answering questions asked by humans on a given text.

## 📋 Project Description

The system is designed to process "factoid" questions (e.g., "Where is the Louvre Museum located?") based on an input paragraph. The model must extract or generate the correct answer relying solely on the provided context.

### Main Characteristics:

* **QA Type**: Closed-Domain.


* **Model**: Deep Neural Network.


* **Input**: A paragraph (context) and an associated question.


* **Output**: An intelligible answer extracted from the text.



---

## 📊 Dataset

We use the **Stanford Question Answering Dataset (SQuAD) 2.0**.

* **Structure**: The dataset is composed of titles, contexts (paragraphs), questions, and accepted answers.


* **Format**: Data is provided in JSON format.


* **Specificity**: Each answer has an `answer_start` indicator specifying its exact position in the text. Questions without a solution (is_impossible == true) have been discarded for this project.



---

## 🛠️ Architecture and Methodology

In accordance with project requirements, our approach includes:

1. **Data Preprocessing**: Cleaning and preparation of text for training.


2. **Modeling**: Implementation of a neural model where each layer and algorithm is documented.


3. **Training**: Use of **Google Colab** for GPU computing power, with regular backups to Google Drive.


4. **Optimization**: Performance monitoring and hyperparameter tuning (potentially via TensorBoard).



---

## 🚀 Presentation and Demonstration

The project is the subject of a 15-minute presentation including:

* The methodology and intuition behind the chosen model.


* A complete description of the neural network layers.


* A comparison of results obtained versus the state of the art.


* A **live demonstration** via a pre-loaded notebook.



---

## 👥 Team

Project realized by a team of 3 students: **Alon DEBASC**, **Axel STOLTZ**, and **Thibault CHESNEL** under the supervision of instructor **Khodor Hammoud**.