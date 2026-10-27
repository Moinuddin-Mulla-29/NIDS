"""
AI-NIDS: Deep Evaluation and Security Trade-Off Analysis
Provides:
- Comprehensive model comparison tables
- Security trade-off breakdown (False Positives vs False Negatives in SOC operations)
- Confusion Matrix inspection
- Per-class precision, recall, and F1-score analysis
"""

import os
import sys
import json
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def display_evaluation_report(metrics_path: str = None) -> None:
    metrics_path = metrics_path or os.path.join(CURRENT_DIR, "saved_models", "metrics.json")
    if not os.path.exists(metrics_path):
        print(f"[!] No metrics found at {metrics_path}. Run 'python ml/train.py' first.")
        return

    with open(metrics_path, "r") as f:
        data = json.load(f)

    print("=" * 82)
    print("                     AI-NIDS MODEL EVALUATION REPORT                      ")
    print("=" * 82)
    print(f"Selected Primary Model: {data.get('best_model')}")
    print(f"Total Features Utilized: {data.get('num_features')}")
    print(f"Detected Attack Classes: {', '.join(data.get('classes', []))}")
    print("-" * 82)

    # 1. Comparative Model Summary Table
    print(f"{'Model':<22} | {'Accuracy':<10} | {'F1-Macro':<10} | {'Recall':<10} | {'Benign FPR':<10}")
    print("-" * 82)
    for model_name, m in data.get("metrics", {}).items():
        if "accuracy" in m:
            print(
                f"{model_name:<22} | "
                f"{m['accuracy']*100:>8.2f}% | "
                f"{m['f1_macro']:>10.4f} | "
                f"{m['recall_macro']:>10.4f} | "
                f"{m['benign_fpr']*100:>8.2f}%"
            )
        else:
            print(f"{model_name:<22} | [Unsupervised Anomaly Detector - Contamination: {m.get('contamination', 0.05)}]")
    print("-" * 82)

    # 2. Per-Class Performance of Best Model
    best_name = data.get("best_model", "RandomForest")
    best_metrics = data.get("metrics", {}).get(best_name, {})
    per_class = best_metrics.get("per_class", {})

    print(f"\n[*] PER-CLASS DETAILED BREAKDOWN ({best_name}):")
    print(f"{'Attack Category':<18} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10} | {'Support':<8}")
    print("-" * 68)
    for cat, stats in per_class.items():
        print(
            f"{cat:<18} | "
            f"{stats['precision']:>10.4f} | "
            f"{stats['recall']:>10.4f} | "
            f"{stats['f1_score']:>10.4f} | "
            f"{stats['support']:>8}"
        )
    print("-" * 68)

    # 3. Top Discriminating Network Features
    feat_imps = data.get("feature_importances", {})
    if feat_imps:
        print("\n[*] TOP 10 DISCRIMINATING NETWORK FLOW FEATURES (XAI):")
        for i, (k, v) in enumerate(list(feat_imps.items())[:10], 1):
            bar = "#" * int(v * 40)
            print(f" {i:2d}. {k:<30} | {v*100:>5.2f}% {bar}")

    # 4. Cybersecurity Trade-Off Analysis
    print("\n" + "=" * 82)
    print("                    SECURITY TRADE-OFF ANALYSIS (SOC CONTEXT)                    ")
    print("=" * 82)
    print("1. False Positives (FP) Trade-off:")
    print("   - High Benign FPR leads directly to 'Alert Fatigue' among SOC analysts.")
    print("   - When thousands of legitimate web or file transfers trigger alerts, critical intrusions get ignored.")
    print(f"   - Current AI-NIDS Benign FPR is calibrated to: {best_metrics.get('benign_fpr', 0.0)*100:.2f}%.")
    print("\n2. False Negatives (FN) Trade-off:")
    print("   - A False Negative occurs when an attack bypasses detection and enters the internal network.")
    print("   - In cybersecurity, FN on DoS, DDoS, and Infiltration has disastrous consequences.")
    print("   - We prioritized F1-Macro and high recall on malicious categories rather than raw overall accuracy.")
    print("=" * 82)

if __name__ == "__main__":
    display_evaluation_report()
