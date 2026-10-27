"""
AI-NIDS: Unified Inference Engine
Provides single-flow and batch-flow classification with:
- Model confidence scores
- Anomaly detection checks (Isolation Forest)
- Integrated Explainable AI (XAI) feature attributions
- Fallback handling for missing features
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Union, Optional

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.preprocessing import PreprocessingPipeline
from ml.xai import ExplainableAI

class NIDSPredictor:
    def __init__(self, model_dir: Optional[str] = None):
        self.model_dir = model_dir or os.path.join(CURRENT_DIR, "saved_models")
        self.preprocessor_path = os.path.join(self.model_dir, "preprocessor.joblib")
        self.best_model_path = os.path.join(self.model_dir, "best_model.joblib")
        self.iforest_path = os.path.join(self.model_dir, "iforest_model.joblib")
        self.metrics_path = os.path.join(self.model_dir, "metrics.json")

        self.pipeline: Optional[PreprocessingPipeline] = None
        self.classifier = None
        self.anomaly_detector = None
        self.xai = ExplainableAI(self.metrics_path)
        self.is_loaded = False
        self._load_models()

    def _load_models(self) -> None:
        if not os.path.exists(self.preprocessor_path) or not os.path.exists(self.best_model_path):
            print(f"[!] Warning: Model files not found in {self.model_dir}. Please run 'python ml/train.py' first.")
            return

        try:
            self.pipeline = PreprocessingPipeline.load(self.preprocessor_path)
            self.classifier = joblib.load(self.best_model_path)
            if os.path.exists(self.iforest_path):
                self.anomaly_detector = joblib.load(self.iforest_path)
            self.is_loaded = True
            print(f"[+] Successfully loaded AI-NIDS models from {self.model_dir}")
        except Exception as e:
            print(f"[!] Error loading models: {e}")

    def predict_single(self, flow_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Classify an individual network flow with explainability and anomaly scoring."""
        if not self.is_loaded:
            raise RuntimeError("NIDS models are not loaded. Train models before running inference.")

        # Transform features
        X_scaled = self.pipeline.transform_single_dict(flow_dict)

        # Predict class & confidence
        if hasattr(self.classifier, "predict_proba"):
            probs = self.classifier.predict_proba(X_scaled)[0]
            pred_idx = int(np.argmax(probs))
            confidence = float(probs[pred_idx])
        else:
            pred_idx = int(self.classifier.predict(X_scaled)[0])
            confidence = 1.0

        class_name = self.pipeline.label_mapping.get(pred_idx, str(pred_idx))

        # Check unsupervised anomaly detector
        is_novelty_anomaly = False
        if self.anomaly_detector is not None:
            iso_res = self.anomaly_detector.predict(X_scaled)[0]
            if iso_res == -1 and class_name == "BENIGN":
                is_novelty_anomaly = True

        # Generate XAI attributions
        explanation = self.xai.explain_flow_prediction(
            predicted_class=class_name,
            confidence=confidence,
            flow_features=flow_dict
        )

        # Determine severity level
        severity = explanation["severity"]
        if is_novelty_anomaly:
            severity = "Medium"
            explanation["security_insight"] += " [Notice: Classified as Benign by signature, but flagged as Outlier Anomaly by Isolation Forest - potential zero-day variant]."

        return {
            "predicted_class": class_name,
            "is_malicious": class_name != "BENIGN",
            "is_anomaly": is_novelty_anomaly,
            "confidence": round(confidence, 4),
            "severity": severity,
            "top_contributing_features": explanation["top_contributing_features"],
            "security_insight": explanation["security_insight"],
            "disclaimer": explanation["disclaimer"]
        }

    def predict_batch_df(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Batch predict on a DataFrame of network flows."""
        if not self.is_loaded:
            raise RuntimeError("NIDS models are not loaded.")

        X_scaled = self.pipeline.transform(df)

        if hasattr(self.classifier, "predict_proba"):
            probs_matrix = self.classifier.predict_proba(X_scaled)
            pred_indices = np.argmax(probs_matrix, axis=1)
            confidences = np.max(probs_matrix, axis=1)
        else:
            pred_indices = self.classifier.predict(X_scaled)
            confidences = np.ones(len(df))

        results = []
        for i in range(len(df)):
            idx = int(pred_indices[i])
            conf = float(confidences[i])
            class_name = self.pipeline.label_mapping.get(idx, str(idx))
            row_dict = df.iloc[i].to_dict()

            severity = "Low"
            if class_name in ["DDoS", "DoS-Hulk"]:
                severity = "Critical"
            elif class_name in ["PortScan", "BruteForce"]:
                severity = "Medium"
            elif class_name in ["Botnet", "Infiltration"]:
                severity = "High"

            results.append({
                "index": i,
                "predicted_class": class_name,
                "is_malicious": class_name != "BENIGN",
                "confidence": round(conf, 4),
                "severity": severity,
                "flow_duration": float(row_dict.get("Flow Duration", 0.0)),
                "total_fwd_packets": int(row_dict.get("Total Fwd Packets", 0)),
                "flow_packets_s": float(row_dict.get("Flow Packets/s", 0.0)),
            })

        return results

if __name__ == "__main__":
    predictor = NIDSPredictor()
    if predictor.is_loaded:
        sample_benign = {
            "Flow Duration": 250000.0,
            "Total Fwd Packets": 8,
            "Total Backward Packets": 10,
            "Total Length of Fwd Packets": 1200.0,
            "Total Length of Bwd Packets": 4500.0,
            "Flow Bytes/s": 22800.0,
            "Flow Packets/s": 72.0,
            "Flow IAT Mean": 18000.0,
            "SYN Flag Count": 0,
            "RST Flag Count": 0,
            "Average Packet Size": 316.0
        }
        res = predictor.predict_single(sample_benign)
        print("\n--- Sample Prediction Result ---")
        print(f"Class: {res['predicted_class']} | Confidence: {res['confidence']*100:.1f}% | Severity: {res['severity']}")
        print(f"Insight: {res['security_insight']}")
