"""
AI-NIDS: Alert Schemas
Pydantic schemas for security incident feeds, details, and SOC status updates.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    flow_id: Optional[str]
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    attack_type: str
    severity: str
    confidence: float
    status: str
    is_anomaly: bool
    top_features: Optional[List[Dict[str, Any]]] = None
    security_insight: Optional[str] = None

class AlertStatusUpdate(BaseModel):
    status: str  # NEW, ACKNOWLEDGED, RESOLVED, FALSE_POSITIVE

class AlertPaginationResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[AlertResponse]
