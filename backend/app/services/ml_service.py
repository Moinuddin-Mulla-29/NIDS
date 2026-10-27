"""
AI-NIDS: Machine Learning Service
Thread-safe singleton service providing ML inference, feature validation, and XAI.
"""

import os
import json
import threading
from typing import Dict, Any, List, Optional
import pandas as pd

from backend.app.config import settings
from ml.predict import NIDSPredictor

class MLService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MLService, cls).__new__(cls)
                cls._instance.predictor = NIDSPredictor(model_dir=settings.SAVED_MODELS_DIR)
                cls._instance.metrics = cls._instance._load_metrics()
        return cls._instance

    def _load_metrics(self) -> Dict[str, Any]:
        if os.path.exists(settings.METRICS_PATH):
            try:
                with open(settings.METRICS_PATH, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[!] Warning reading metrics: {e}")
        return {}

    def is_ready(self) -> bool:
        return self.predictor.is_loaded

    def predict_flow(self, flow_dict: Dict[str, Any]) -> Dict[str, Any]:
        return self.predictor.predict_single(flow_dict)

    def predict_dataframe(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        return self.predictor.predict_batch_df(df)

    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics

    def get_features(self) -> List[str]:
        if self.predictor.pipeline:
            return self.predictor.pipeline.feature_columns
        return []

    def get_feature_importances(self) -> Dict[str, float]:
        return self.metrics.get("feature_importances", {})

# Global singleton accessor
ml_service = MLService()
