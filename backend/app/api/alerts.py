"""
AI-NIDS: Alert Management Endpoints
Provides search, filtering, pagination, and status triaging for security incidents.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.entities import Alert
from backend.app.schemas.alert import AlertResponse, AlertStatusUpdate, AlertPaginationResponse

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("", response_model=AlertPaginationResponse)
def get_alerts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(15, ge=1, le=100, description="Items per page"),
    severity: Optional[str] = Query(None, description="Filter by severity: Low, Medium, High, Critical"),
    attack_type: Optional[str] = Query(None, description="Filter by attack type"),
    status: Optional[str] = Query(None, description="Filter by status: NEW, ACKNOWLEDGED, RESOLVED, FALSE_POSITIVE"),
    search: Optional[str] = Query(None, description="Search by IP, port, attack type, or flow ID"),
    db: Session = Depends(get_db)
):
    """Retrieve filtered, paginated alert feed."""
    query = db.query(Alert)

    if severity:
        query = query.filter(Alert.severity == severity)
    if attack_type:
        query = query.filter(Alert.attack_type == attack_type)
    if status:
        query = query.filter(Alert.status == status)
    if search:
        search_filter = (
            Alert.src_ip.ilike(f"%{search}%") |
            Alert.dst_ip.ilike(f"%{search}%") |
            Alert.attack_type.ilike(f"%{search}%") |
            Alert.flow_id.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)

    total = query.count()
    total_pages = max(1, (total + page_size - 1) // page_size)
    items = query.order_by(Alert.timestamp.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return AlertPaginationResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=items
    )

@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert_by_id(alert_id: int, db: Session = Depends(get_db)):
    """Fetch complete forensic details and XAI feature breakdown for a single alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert #{alert_id} not found.")
    return alert

@router.patch("/{alert_id}/status", response_model=AlertResponse)
def update_alert_status(alert_id: int, payload: AlertStatusUpdate, db: Session = Depends(get_db)):
    """Update SOC triage status (e.g., ACKNOWLEDGED, RESOLVED, FALSE_POSITIVE)."""
    valid_statuses = {"NEW", "ACKNOWLEDGED", "RESOLVED", "FALSE_POSITIVE"}
    if payload.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert #{alert_id} not found.")

    alert.status = payload.status
    db.commit()
    db.refresh(alert)
    return alert

@router.delete("/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """Delete an individual alert from incident records."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert #{alert_id} not found.")

    db.delete(alert)
    db.commit()
    return {"message": f"Alert #{alert_id} deleted successfully."}
