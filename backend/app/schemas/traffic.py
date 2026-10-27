"""
AI-NIDS: Traffic & Detection Schemas
Pydantic models for incoming flow inspection requests.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class SingleFlowRequest(BaseModel):
    src_ip: Optional[str] = Field("192.168.1.50", description="Source IP Address")
    dst_ip: Optional[str] = Field("10.0.0.1", description="Destination IP Address")
    src_port: Optional[int] = Field(54321, description="Source Port")
    dst_port: Optional[int] = Field(80, description="Destination Port")
    protocol: Optional[str] = Field("TCP", description="Transport Protocol")
    features: Dict[str, float] = Field(
        ...,
        description="Dictionary of 32 CIC-IDS2017 compliant flow metrics (e.g. Flow Duration, Total Fwd Packets, etc.)"
    )

class SingleDetectionResponse(BaseModel):
    flow_id: str
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    predicted_class: str
    is_malicious: bool
    is_anomaly: bool
    confidence: float
    severity: str
    top_contributing_features: List[Dict[str, Any]]
    security_insight: str
    disclaimer: str

class BatchDetectionResponse(BaseModel):
    total_analyzed: int
    normal_count: int
    malicious_count: int
    critical_alerts: int
    records: List[Dict[str, Any]]
