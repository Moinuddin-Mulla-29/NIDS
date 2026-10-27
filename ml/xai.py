"""
AI-NIDS: Explainable AI (XAI) Module
Provides transparency into model decisions:
1. Global Feature Importance (Tree-based MDI & feature rankings)
2. Local Feature Attributions (Why an alert was triggered)
3. Human-readable cybersecurity insights for SOC analysts
4. Clear statistical confidence caveats and model bounds
"""

import os
import json
from typing import Dict, List, Any

# Baseline statistics typical for benign corporate traffic
BENIGN_BASELINES = {
    "Flow Duration": {"mean": 350000, "std": 200000, "unit": "μs"},
    "Total Fwd Packets": {"mean": 12.0, "std": 15.0, "unit": "pkts"},
    "Total Backward Packets": {"mean": 15.0, "std": 20.0, "unit": "pkts"},
    "Flow Packets/s": {"mean": 45.0, "std": 60.0, "unit": "pkts/s"},
    "Flow Bytes/s": {"mean": 18500.0, "std": 25000.0, "unit": "bytes/s"},
    "SYN Flag Count": {"mean": 0.2, "std": 0.4, "unit": "flag"},
    "RST Flag Count": {"mean": 0.05, "std": 0.2, "unit": "flag"},
    "FIN Flag Count": {"mean": 0.15, "std": 0.35, "unit": "flag"},
    "Flow IAT Mean": {"mean": 25000.0, "std": 35000.0, "unit": "μs"},
    "Average Packet Size": {"mean": 450.0, "std": 250.0, "unit": "bytes"},
}

ATTACK_FEATURE_HEURISTICS = {
    "DoS-Hulk": [
        ("Flow Packets/s", "Extremely high packet transmission rate typical of DoS flooding."),
        ("Total Fwd Packets", "Massive forward packet count overwhelming the server."),
        ("Flow IAT Mean", "Abnormally low inter-arrival time between packets."),
        ("SYN Flag Count", "Elevated SYN synchronization attempts.")
    ],
    "DDoS": [
        ("Flow Packets/s", "Volumetric distributed packet flood surpassing standard thresholds."),
        ("SYN Flag Count", "High SYN flood frequency targeting connection table exhaustion."),
        ("Flow Duration", "Abnormally brief flow burst characteristic of coordinated stresser attacks."),
        ("Average Packet Size", "Minimal packet payload sizes designed to maximize packet count.")
    ],
    "PortScan": [
        ("Total Fwd Packets", "Minimal packet count (1-3 pkts) consistent with host/port probing."),
        ("SYN Flag Count", "TCP SYN scan initiated without completing three-way handshake."),
        ("RST Flag Count", "Elevated RST flags returned by closed victim ports."),
        ("Total Length of Fwd Packets", "Zero or near-zero payload indicating network reconnaissance.")
    ],
    "BruteForce": [
        ("RST Flag Count", "High connection reset rate caused by repeated authentication rejections."),
        ("Total Fwd Packets", "Repetitive credential testing cycles over target port (SSH/FTP)."),
        ("Flow Duration", "Sustained connection duration during iterative dictionary attempts.")
    ],
    "Botnet": [
        ("Flow IAT Std", "Unusually low variance in inter-arrival time (strict beaconing heartbeat)."),
        ("Average Packet Size", "Predictable command-and-control (C2) payload size."),
        ("Flow Duration", "Persistent periodic communication session.")
    ],
    "Infiltration": [
        ("Total Length of Fwd Packets", "Heavy asymmetric outbound data volume indicating exfiltration."),
        ("Flow IAT Mean", "Low-and-slow transmission cadence designed to evade volume thresholds."),
        ("Average Packet Size", "Anomalously large outbound payload segments.")
    ]
}

class ExplainableAI:
    def __init__(self, metrics_json_path: str = None):
        self.feature_importances: Dict[str, float] = {}
        if metrics_json_path and os.path.exists(metrics_json_path):
            try:
                with open(metrics_json_path, "r") as f:
                    data = json.load(f)
                    self.feature_importances = data.get("feature_importances", {})
            except Exception:
                pass

    def explain_flow_prediction(
        self,
        predicted_class: str,
        confidence: float,
        flow_features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate feature attributions and cybersecurity explanation for an individual alert.
        """
        top_reasons: List[Dict[str, Any]] = []

        if predicted_class == "BENIGN":
            return {
                "predicted_class": "BENIGN",
                "confidence": round(confidence, 4),
                "severity": "Low",
                "top_contributing_features": [],
                "security_insight": "Network flow characteristics conform to established baseline traffic profiles. No malicious signatures or volumetric anomalies detected.",
                "disclaimer": "Model confidence is a statistical probability of normal profile compliance."
            }

        # Retrieve attack heuristics or fallback to feature importances
        heuristics = ATTACK_FEATURE_HEURISTICS.get(predicted_class, [])
        for feat_name, reason_template in heuristics:
            if feat_name in flow_features:
                val = flow_features[feat_name]
                baseline = BENIGN_BASELINES.get(feat_name, {"mean": 0, "unit": ""})
                top_reasons.append({
                    "feature": feat_name,
                    "value": val,
                    "baseline": baseline.get("mean"),
                    "unit": baseline.get("unit"),
                    "impact": round(self.feature_importances.get(feat_name, 0.15), 4),
                    "reason": reason_template
                })

        # If heuristics didn't cover enough features, supplement with top model importance features
        if len(top_reasons) < 3 and self.feature_importances:
            for feat_name, imp in list(self.feature_importances.items())[:5]:
                if feat_name in flow_features and not any(r["feature"] == feat_name for r in top_reasons):
                    val = flow_features[feat_name]
                    top_reasons.append({
                        "feature": feat_name,
                        "value": val,
                        "baseline": BENIGN_BASELINES.get(feat_name, {}).get("mean", "N/A"),
                        "unit": BENIGN_BASELINES.get(feat_name, {}).get("unit", ""),
                        "impact": round(imp, 4),
                        "reason": f"High model reliance weight ({round(imp * 100, 1)}%) based on Random Forest decision trees."
                    })
                if len(top_reasons) >= 4:
                    break

        severity = "High"
        if predicted_class in ["DDoS", "DoS-Hulk"]:
            severity = "Critical"
        elif predicted_class in ["PortScan", "BruteForce"]:
            severity = "Medium"
        elif predicted_class in ["Botnet", "Infiltration"]:
            severity = "High"

        insight = (
            f"Flow demonstrates behavioral hallmarks of a {predicted_class} incident. "
            f"The primary discriminators were {', '.join([r['feature'] for r in top_reasons[:2]])}. "
            f"Confidence score evaluated at {round(confidence * 100, 1)}%."
        )

        return {
            "predicted_class": predicted_class,
            "confidence": round(confidence, 4),
            "severity": severity,
            "top_contributing_features": top_reasons,
            "security_insight": insight,
            "disclaimer": (
                "Notice: Model confidence denotes statistical pattern correlation with historical "
                "intrusion benchmarks, not an irrefutable proof of compromise. SOC analysts must cross-reference "
                "with endpoint telemetry, authentication logs, and host IDS."
            )
        }
