"""
AI-NIDS: Machine Learning Unit Tests
Verifies preprocessing pipeline, model inference, and XAI attribution.
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.preprocessing import PreprocessingPipeline, FEATURE_COLUMNS
from ml.predict import NIDSPredictor

def test_preprocessing_inf_and_nan_handling():
    """Ensure preprocessor safely sanitizes infinite and missing values without data leakage."""
    pipeline = PreprocessingPipeline()
    sample_df = pd.DataFrame({
        col: [100.0, 200.0, np.nan, np.inf] for col in FEATURE_COLUMNS
    })
    sample_df["Label"] = ["BENIGN", "BENIGN", "DDoS", "DDoS"]

    X_train, X_test, y_train, y_test, meta = pipeline.fit_transform(sample_df, test_size=0.5, random_state=42)

    assert not np.isnan(X_train).any()
    assert not np.isinf(X_train).any()
    assert not np.isnan(X_test).any()
    assert not np.isinf(X_test).any()
    assert pipeline.is_fitted is True

def test_inference_engine_prediction():
    """Ensure trained model predictor produces expected structure and confidence score."""
    predictor = NIDSPredictor()
    assert predictor.is_loaded is True

    test_flow = {
        "Flow Duration": 50000.0,
        "Total Fwd Packets": 150,
        "Total Backward Packets": 2,
        "Total Length of Fwd Packets": 48000.0,
        "Total Length of Bwd Packets": 128.0,
        "Flow Bytes/s": 962560.0,
        "Flow Packets/s": 3040.0,
        "Flow IAT Mean": 330.0,
        "SYN Flag Count": 1,
        "RST Flag Count": 0,
        "Average Packet Size": 316.0
    }

    res = predictor.predict_single(test_flow)
    assert "predicted_class" in res
    assert "confidence" in res
    assert 0.0 <= res["confidence"] <= 1.0
    assert "severity" in res
    assert "top_contributing_features" in res
    assert "security_insight" in res

def test_batch_df_prediction():
    """Test batch prediction handles multiple rows gracefully."""
    predictor = NIDSPredictor()
    sample_df = pd.DataFrame([
        {"Flow Duration": 120000.0, "Total Fwd Packets": 5, "SYN Flag Count": 0},
        {"Flow Duration": 200.0, "Total Fwd Packets": 1, "SYN Flag Count": 1}
    ])
    results = predictor.predict_batch_df(sample_df)
    assert len(results) == 2
    assert "predicted_class" in results[0]
