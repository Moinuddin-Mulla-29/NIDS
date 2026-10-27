"""
AI-NIDS: Machine Learning Training Pipeline
Trains, evaluates, and persists multiple ML models for intrusion detection:
1. Random Forest (Ensemble tree classifier with balanced class weighting)
2. Logistic Regression (Baseline linear model)
3. Gradient Boosting Classifier (Sequential boosting)
4. Isolation Forest (Unsupervised novelty & anomaly detection on benign baseline)

Calculates security-oriented evaluation metrics (F1-score, Recall, FPR, Confusion Matrix).
Selects and persists the best model for real-time inference.
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)

# Add parent directory to path so relative imports work seamlessly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.preprocessing import PreprocessingPipeline
from ml.data.generate_benchmark_dataset import generate_network_dataset

def compute_security_metrics(y_true: np.ndarray, y_pred: np.ndarray, classes: list) -> Dict[str, Any]:
    """
    Calculate comprehensive evaluation metrics with cybersecurity context:
    - Accuracy, Macro/Weighted Precision, Recall, F1
    - Confusion Matrix
    - False Positive Rate (FPR) on BENIGN traffic (vital for SOC alert fatigue)
    - Per-class breakdown
    """
    acc = float(accuracy_score(y_true, y_pred))
    p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)
    p_weighted, r_weighted, f1_weighted, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted", zero_division=0)
    cm = confusion_matrix(y_true, y_pred).tolist()

    # Per-class metrics
    p_per, r_per, f1_per, sup_per = precision_recall_fscore_support(y_true, y_pred, average=None, zero_division=0)
    per_class = {}
    for idx, class_name in enumerate(classes):
        per_class[class_name] = {
            "precision": round(float(p_per[idx]), 4),
            "recall": round(float(r_per[idx]), 4),
            "f1_score": round(float(f1_per[idx]), 4),
            "support": int(sup_per[idx])
        }

    # Calculate False Positive Rate specifically for BENIGN class (Class 0 usually or label 'BENIGN')
    # Benign False Positive = True Benign classified as any Attack
    fpr_benign = 0.0
    if "BENIGN" in classes:
        benign_idx = classes.index("BENIGN")
        cm_np = np.array(cm)
        # Row benign_idx is true benign: cm_np[benign_idx, :]
        true_benign_total = np.sum(cm_np[benign_idx, :])
        false_positives = true_benign_total - cm_np[benign_idx, benign_idx]
        if true_benign_total > 0:
            fpr_benign = round(float(false_positives / true_benign_total), 4)

    return {
        "accuracy": round(acc, 4),
        "precision_macro": round(float(p_macro), 4),
        "recall_macro": round(float(r_macro), 4),
        "f1_macro": round(float(f1_macro), 4),
        "precision_weighted": round(float(p_weighted), 4),
        "recall_weighted": round(float(r_weighted), 4),
        "f1_weighted": round(float(f1_weighted), 4),
        "benign_fpr": fpr_benign,
        "confusion_matrix": cm,
        "per_class": per_class
    }

def train_and_evaluate(dataset_csv_path: str = None, save_dir: str = None) -> Dict[str, Any]:
    save_dir = save_dir or os.path.join(CURRENT_DIR, "saved_models")
    os.makedirs(save_dir, exist_ok=True)

    # 1. Load or Generate Dataset
    if dataset_csv_path is None or not os.path.exists(dataset_csv_path):
        benchmark_csv = os.path.join(CURRENT_DIR, "data", "sample_network_flows.csv")
        if not os.path.exists(benchmark_csv):
            print("[*] Generating benchmark network flow dataset...")
            generate_network_dataset(num_samples=16000, output_path=benchmark_csv)
        dataset_csv_path = benchmark_csv

    print(f"[*] Loading training dataset from {dataset_csv_path}...")
    df = pd.read_csv(dataset_csv_path, low_memory=False)

    # 2. Preprocessing & Leakage-Free Splitting
    print("[*] Initializing Preprocessing Pipeline (zero data leakage)...")
    pipeline = PreprocessingPipeline()
    X_train, X_test, y_train, y_test, metadata = pipeline.fit_transform(df, target_col="Label", test_size=0.25)
    classes = metadata["classes"]
    print(f"[+] Cleaned dataset: {len(X_train)} train samples, {len(X_test)} test samples across {len(classes)} classes.")

    models = {}
    eval_results = {}

    # 3. Train Model 1: Random Forest
    print("\n--- [1/4] Training Random Forest Classifier ---")
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=16,
        min_samples_split=4,
        class_weight="balanced",
        n_jobs=-1,
        random_state=42
    )
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    metrics_rf = compute_security_metrics(y_test, y_pred_rf, classes)
    models["RandomForest"] = rf
    eval_results["RandomForest"] = metrics_rf
    print(f"[+] Random Forest -> Accuracy: {metrics_rf['accuracy']*100:.2f}%, F1-Macro: {metrics_rf['f1_macro']:.4f}, Benign FPR: {metrics_rf['benign_fpr']*100:.2f}%")

    # 4. Train Model 2: Logistic Regression (Baseline)
    print("\n--- [2/4] Training Logistic Regression Classifier (Baseline) ---")
    lr = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
    lr.fit(X_train, y_train)
    y_pred_lr = lr.predict(X_test)
    metrics_lr = compute_security_metrics(y_test, y_pred_lr, classes)
    models["LogisticRegression"] = lr
    eval_results["LogisticRegression"] = metrics_lr
    print(f"[+] Logistic Regression -> Accuracy: {metrics_lr['accuracy']*100:.2f}%, F1-Macro: {metrics_lr['f1_macro']:.4f}, Benign FPR: {metrics_lr['benign_fpr']*100:.2f}%")

    # 5. Train Model 3: Gradient Boosting
    print("\n--- [3/4] Training Gradient Boosting Classifier ---")
    gb = GradientBoostingClassifier(n_estimators=60, learning_rate=0.1, max_depth=6, random_state=42)
    gb.fit(X_train, y_train)
    y_pred_gb = gb.predict(X_test)
    metrics_gb = compute_security_metrics(y_test, y_pred_gb, classes)
    models["GradientBoosting"] = gb
    eval_results["GradientBoosting"] = metrics_gb
    print(f"[+] Gradient Boosting -> Accuracy: {metrics_gb['accuracy']*100:.2f}%, F1-Macro: {metrics_gb['f1_macro']:.4f}, Benign FPR: {metrics_gb['benign_fpr']*100:.2f}%")

    # 6. Train Model 4: Isolation Forest (Unsupervised Anomaly Detection)
    print("\n--- [4/4] Training Isolation Forest for Zero-Day Anomaly Detection ---")
    # Train on BENIGN samples only to learn normal network baseline
    if "BENIGN" in classes:
        benign_idx = classes.index("BENIGN")
        X_train_benign = X_train[y_train == benign_idx]
    else:
        X_train_benign = X_train

    iso_forest = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    iso_forest.fit(X_train_benign)
    # Isolation forest predicts 1 for inlier (normal), -1 for outlier (anomaly)
    iso_preds_test = iso_forest.predict(X_test)
    # Mark inliers as BENIGN, outliers as Anomaly
    eval_results["IsolationForest"] = {
        "description": "Unsupervised anomaly detector trained exclusively on benign traffic baselines.",
        "contamination": 0.05,
        "test_detected_anomalies": int(np.sum(iso_preds_test == -1)),
        "test_total": len(iso_preds_test)
    }
    models["IsolationForest"] = iso_forest
    print(f"[+] Isolation Forest trained on {len(X_train_benign)} benign flows.")

    # 7. Model Selection based on Security Criteria
    # Security Rule: Pick the model with highest F1-Macro and lowest Benign FPR (least alert fatigue for SOC analysts)
    best_model_name = "RandomForest"
    best_f1 = -1.0
    for name in ["RandomForest", "GradientBoosting", "LogisticRegression"]:
        score = eval_results[name]["f1_macro"] - (eval_results[name]["benign_fpr"] * 0.5)
        if score > best_f1:
            best_f1 = score
            best_model_name = name

    print(f"\n[+] Best Selected Model: {best_model_name} (Highest balanced security metric)")

    # 8. Feature Importance for Explainable AI (XAI)
    feature_importances = {}
    if hasattr(models[best_model_name], "feature_importances_"):
        raw_importances = models[best_model_name].feature_importances_
        sorted_indices = np.argsort(raw_importances)[::-1]
        for idx in sorted_indices:
            feat_name = pipeline.feature_columns[idx]
            feature_importances[feat_name] = round(float(raw_importances[idx]), 4)

    # 9. Save Artifacts
    print(f"[*] Persisting models and preprocessing pipeline to {save_dir}...")
    pipeline.save(os.path.join(save_dir, "preprocessor.joblib"))
    joblib.dump(models["RandomForest"], os.path.join(save_dir, "rf_model.joblib"))
    joblib.dump(models["LogisticRegression"], os.path.join(save_dir, "lr_model.joblib"))
    joblib.dump(models["GradientBoosting"], os.path.join(save_dir, "gb_model.joblib"))
    joblib.dump(models["IsolationForest"], os.path.join(save_dir, "iforest_model.joblib"))
    # Save the selected primary production model alias
    joblib.dump(models[best_model_name], os.path.join(save_dir, "best_model.joblib"))

    summary_manifest = {
        "best_model": best_model_name,
        "models_evaluated": list(eval_results.keys()),
        "metrics": eval_results,
        "feature_importances": feature_importances,
        "classes": classes,
        "label_mapping": metadata["label_mapping"],
        "num_features": len(pipeline.feature_columns),
        "features": pipeline.feature_columns,
        "training_metadata": {
            "train_samples": metadata["train_samples"],
            "test_samples": metadata["test_samples"],
            "class_imbalance": metadata["class_imbalance"]
        }
    }

    metrics_path = os.path.join(save_dir, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(summary_manifest, f, indent=2)
    print(f"[+] Evaluation metrics & manifest saved to: {metrics_path}")

    return summary_manifest

if __name__ == "__main__":
    train_and_evaluate()
