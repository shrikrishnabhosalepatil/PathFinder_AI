"""
Machine Learning Training Pipeline for PathFinder AI.
Generates synthetic placement dataset (if not existing), cleans and trains a
Random Forest Classifier, computes actual test evaluation metrics, and serializes
the model and metadata for production inference.
"""

import os
import json
from datetime import datetime
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import config

def generate_synthetic_dataset(num_samples: int = 1500, random_seed: int = 42) -> pd.DataFrame:
    """
    Generates a realistic campus placement dataset modeled after typical
    engineering college recruitment drives.

    Features:
    - CGPA: 5.0 to 9.8 (Beta/Normal distribution)
    - Aptitude Score: 30 to 98 (out of 100)
    - Technical Score: 1 to 10
    - Communication Score: 1 to 10
    - Internships: 0 to 4
    - Projects: 0 to 6
    - Active Backlogs: 0 to 5
    """
    np.random.seed(random_seed)

    # 1. CGPA: Realistic bell curve centered around 7.2
    cgpa = np.random.normal(loc=7.2, scale=1.1, size=num_samples)
    cgpa = np.clip(np.round(cgpa, 2), 4.5, 9.9)

    # 2. Aptitude Score: Correlated with CGPA to reflect problem-solving ability
    aptitude_base = 35 + (cgpa / 10.0) * 45
    aptitude_noise = np.random.normal(loc=0, scale=8.0, size=num_samples)
    aptitude_score = np.clip(np.round(aptitude_base + aptitude_noise, 1), 25.0, 99.0)

    # 3. Technical Score (1 to 10)
    tech_base = (cgpa / 10.0) * 6 + np.random.uniform(0.5, 3.5, size=num_samples)
    technical_score = np.clip(np.round(tech_base, 1), 1.0, 10.0)

    # 4. Communication Score (1 to 10)
    comm_base = np.random.normal(loc=6.5, scale=1.6, size=num_samples)
    communication_score = np.clip(np.round(comm_base, 1), 1.0, 10.0)

    # 5. Internships: Poisson distribution (most have 0-1, few have 2-3)
    internships = np.random.poisson(lam=0.9, size=num_samples)
    internships = np.clip(internships, 0, 4)

    # 6. Projects: 1 to 5 projects
    projects = np.random.poisson(lam=2.4, size=num_samples)
    projects = np.clip(projects, 0, 6)

    # 7. Active Backlogs: most students have 0, some 1, few 2+
    backlog_probs = [0.72, 0.16, 0.07, 0.03, 0.015, 0.005]
    backlogs = np.random.choice([0, 1, 2, 3, 4, 5], size=num_samples, p=backlog_probs)

    # Placement Decision Logic (Ground Truth modeling):
    # - Companies have strict criteria: backlogs >= 1 severely penalize.
    # - CGPA >= 7.0, Tech >= 6.0, Aptitude >= 60 are strong positive drivers.
    latent_score = (
        1.55 * (cgpa - 6.5) +
        0.05 * (aptitude_score - 55.0) +
        0.52 * (technical_score - 5.0) +
        0.38 * (communication_score - 5.0) +
        0.65 * internships +
        0.30 * projects -
        2.20 * backlogs
    )

    # Sigmoid function to derive probabilities
    prob_placed = 1.0 / (1.0 + np.exp(-latent_score))

    # Add small stochastic real-world noise (e.g. interview day luck, niche hiring)
    prob_with_noise = np.clip(prob_placed + np.random.normal(0, 0.06, num_samples), 0.01, 0.99)
    placement_status = (prob_with_noise >= 0.50).astype(int)

    # Hard campus placement rule: > 2 active backlogs almost always halts placement drives
    placement_status[backlogs >= 3] = 0

    df = pd.DataFrame({
        "cgpa": cgpa,
        "aptitude_score": aptitude_score,
        "technical_score": technical_score,
        "communication_score": communication_score,
        "internships": internships,
        "projects": projects,
        "backlogs": backlogs,
        "placement_status": placement_status
    })

    return df

def train_and_evaluate_model():
    """
    Trains the Random Forest model and saves artifacts.
    """
    print("=" * 60)
    print("PathFinder AI — Machine Learning Pipeline Training")
    print("=" * 60)

    # Step 1: Ensure dataset exists or generate synthetic
    if not config.DATASET_PATH.exists():
        print(f"[*] Generating synthetic placement dataset (1,500 students) at {config.DATASET_PATH}...")
        df = generate_synthetic_dataset(num_samples=1500)
        df.to_csv(config.DATASET_PATH, index=False)
        print("  -> Dataset generated successfully.")
    else:
        print(f"[*] Loading existing dataset from {config.DATASET_PATH}...")
        df = pd.read_csv(config.DATASET_PATH)

    print(f"[*] Dataset summary: {len(df)} records, {len(df.columns)} columns.")
    placed_count = int(df["placement_status"].sum())
    unplaced_count = len(df) - placed_count
    print(f"  -> Placed: {placed_count} ({placed_count/len(df)*100:.1f}%), Unplaced: {unplaced_count} ({unplaced_count/len(df)*100:.1f}%)")

    # Step 2: Feature Matrix and Target Vector
    X = df[config.FEATURE_COLUMNS]
    y = df["placement_status"]

    # Step 3: Train-Test Split (80% train, 20% test, stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"[*] Split data: {len(X_train)} training samples, {len(X_test)} testing samples.")

    # Step 4: Machine Learning Pipeline
    # Standard Scaler ensures normalized distance, Random Forest performs ensemble learning
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestClassifier(
            n_estimators=120,
            max_depth=8,
            min_samples_split=4,
            min_samples_leaf=2,
            random_state=42,
            class_weight="balanced"
        ))
    ])

    print("[*] Training Random Forest Classifier...")
    pipeline.fit(X_train, y_train)

    # Step 5: Evaluation on Held-Out Test Set
    y_pred = pipeline.predict(X_test)
    y_pred_proba = pipeline.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred))
    rec = float(recall_score(y_test, y_pred))
    f1 = float(f1_score(y_test, y_pred))
    roc_auc = float(roc_auc_score(y_test, y_pred_proba))
    cm = confusion_matrix(y_test, y_pred).tolist()

    # Extract Feature Importances from Random Forest estimator
    rf_model = pipeline.named_steps["rf"]
    feature_importances = {
        col: round(float(imp) * 100, 2)
        for col, imp in zip(config.FEATURE_COLUMNS, rf_model.feature_importances_)
    }
    # Sort descending
    sorted_features = dict(sorted(feature_importances.items(), key=lambda item: item[1], reverse=True))

    print("\n" + "-" * 40)
    print("MODEL EVALUATION METRICS (Test Set):")
    print("-" * 40)
    print(f"  * Accuracy:  {acc * 100:.2f}%")
    print(f"  * Precision: {prec * 100:.2f}%")
    print(f"  * Recall:    {rec * 100:.2f}%")
    print(f"  * F1-Score:  {f1 * 100:.2f}%")
    print(f"  * ROC-AUC:   {roc_auc * 100:.2f}%")
    print(f"  * Confusion Matrix (TN, FP / FN, TP):\n    {cm}")
    print("\nFeature Importances (%):")
    for feat, imp in sorted_features.items():
        print(f"  - {feat:20s}: {imp:5.2f}%")
    print("-" * 40)

    # Step 6: Serialize Model and Evaluation Metrics
    metadata = {
        "model_type": "Random Forest Classifier (Ensemble)",
        "features": config.FEATURE_COLUMNS,
        "metrics": {
            "accuracy": round(acc * 100, 2),
            "precision": round(prec * 100, 2),
            "recall": round(rec * 100, 2),
            "f1_score": round(f1 * 100, 2),
            "roc_auc": round(roc_auc * 100, 2)
        },
        "confusion_matrix": cm,
        "feature_importances": sorted_features,
        "dataset_info": {
            "total_records": len(df),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "placed_ratio": round(placed_count / len(df) * 100, 1)
        },
        "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "disclaimer": "Metrics calculated on synthetic demonstration dataset. Real-world placement outcomes depend on market conditions, company cutoffs, and soft-skill interviews."
    }

    # Save Pipeline
    joblib.dump(pipeline, config.MODEL_PATH)
    print(f"\n[+] Trained pipeline model saved to: {config.MODEL_PATH}")

    # Save Metrics JSON
    with open(config.METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
    print(f"[+] Model evaluation metrics saved to: {config.METRICS_PATH}")

    return pipeline, metadata

if __name__ == "__main__":
    train_and_evaluate_model()
