"""
AI-NIDS: Dashboard Metrics & Model Performance Schemas
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel

class DashboardSummaryResponse(BaseModel):
    total_flows: int
    normal_flows: int
    suspicious_flows: int
    critical_alerts: int
    benign_percentage: float
    malicious_percentage: float
    active_monitoring_mode: str
    active_monitoring_status: str
    last_updated: str

class AttackDistributionItem(BaseModel):
    name: str
    count: int
    percentage: float
    severity: str

class TrafficTimeSeriesPoint(BaseModel):
    timestamp: str
    normal_count: int
    attack_count: int
    total: int

class ModelMetricsResponse(BaseModel):
    best_model: str
    models_evaluated: List[str]
    metrics: Dict[str, Any]
    feature_importances: Dict[str, float]
    classes: List[str]
    num_features: int
    training_metadata: Dict[str, Any]
