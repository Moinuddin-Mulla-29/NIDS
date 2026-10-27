"""
AI-NIDS: Model Metrics & Explainability Endpoints
Exposes comparative model benchmarks, confusion matrices, and feature importances.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.entities import Alert
from backend.app.services.ml_service import ml_service
from backend.app.schemas.metrics import ModelMetricsResponse

router = APIRouter(prefix="/model", tags=["Model"])

@router.get("/metrics", response_model=ModelMetricsResponse)
def get_model_metrics():
    """Retrieve full comparative model evaluation benchmarks and confusion matrices."""
    metrics = ml_service.get_metrics()
    if not metrics:
        raise HTTPException(status_code=503, detail="Model metrics have not been computed yet.")

    return ModelMetricsResponse(
        best_model=metrics.get("best_model", "RandomForest"),
        models_evaluated=metrics.get("models_evaluated", []),
        metrics=metrics.get("metrics", {}),
        feature_importances=metrics.get("feature_importances", {}),
        classes=metrics.get("classes", []),
        num_features=metrics.get("num_features", 32),
        training_metadata=metrics.get("training_metadata", {})
    )

@router.get("/features")
def get_model_features():
    """List 32 flow features with global importance weights."""
    return {
        "features": ml_service.get_features(),
        "importances": ml_service.get_feature_importances()
    }

@router.get("/explain/{alert_id}")
def explain_alert(alert_id: int, db: Session = Depends(get_db)):
    """Retrieve XAI attribution for a specific alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert #{alert_id} not found.")

    return {
        "alert_id": alert.id,
        "attack_type": alert.attack_type,
        "confidence": alert.confidence,
        "severity": alert.severity,
        "top_features": alert.top_features or [],
        "security_insight": alert.security_insight or "",
        "disclaimer": "Notice: Model confidence denotes statistical pattern similarity, not an irrefutable proof of attack."
    }
