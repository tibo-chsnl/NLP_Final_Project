# NLP Final Project: Automated Question Answering System

Ce dépôt contient le projet de fin d'études réalisé dans le cadre du cours de Master 2 (M2) intitulé "Natural Language Processing". L'objectif est de développer un système de Question Answering (QA) en domaine fermé capable de répondre intelligemment à des questions posées par des humains sur un texte donné.

## 📋 Description du Projet

Le système est conçu pour traiter des questions de type "factoïdes" (ex: "Où se situe le musée du Louvre ?") à partir d'un paragraphe fourni en entrée. Le modèle doit extraire ou générer la réponse correcte en se basant uniquement sur le contexte fourni.

### Caractéristiques principales :

* 
**Type de QA** : Domaine fermé (Closed-Domain).


* 
**Modèle** : Réseau de neurones profonds (Deep Neural Network).


* 
**Input** : Un paragraphe (contexte) et une question associée.


* 
**Output** : Une réponse intelligible extraite du texte.



---

## 📊 Dataset

Nous utilisons le **Stanford Question Answering Dataset (SQuAD) 2.0**.

* 
**Structure** : Le dataset est composé de titres, de contextes (paragraphes), de questions et de réponses acceptées.


* 
**Format** : Les données sont fournies au format JSON.


* 
**Spécificité** : Chaque réponse possède un indicateur `answer_start` précisant sa position exacte dans le texte. Les questions sans solution (is_impossible == true) ont été écartées pour ce projet.



---

## 🛠️ Architecture et Méthodologie

Conformément aux exigences du projet, notre approche inclut :

1. 
**Prétraitement des données** : Nettoyage et préparation du texte pour l'entraînement.


2. 
**Modélisation** : Implémentation d'un modèle neuronal dont chaque couche et algorithme est documenté.


3. 
**Entraînement** : Utilisation de **Google Colab** pour la puissance de calcul GPU, avec des sauvegardes régulières sur Google Drive.


4. 
**Optimisation** : Suivi des performances et du réglage des hyperparamètres (potentiellement via Tensorboard).



---

## 🚀 Présentation et Démonstration

Le projet fait l'objet d'une présentation de 15 minutes incluant :

* La méthodologie et l'intuition derrière le modèle choisi.


* Une description complète des couches du réseau de neurones.


* Une comparaison des résultats obtenus par rapport à l'état de l'art.


* Une **démonstration en direct** via un notebook pré-chargé.



---

## 👥 Équipe

Projet réalisé par une équipe de 3 étudiants : **Alon DEBASC**, **Axel STOLTZ** et **Thibault CHESNEL** sous la direction de l'instructeur **Khodor Hammoud**.