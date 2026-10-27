"""
AI-NIDS: Database Entities
SQLAlchemy models for intrusion alerts, detection history, and monitoring sessions.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from backend.app.database.session import Base

def utc_now():
    """Return naive UTC datetime without Python 3.12+ deprecation warnings."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utc_now, index=True)
    flow_id = Column(String(64), index=True)
    src_ip = Column(String(45), default="192.168.1.105")
    dst_ip = Column(String(45), default="10.0.0.1")
    src_port = Column(Integer, default=44321)
    dst_port = Column(Integer, default=80)
    protocol = Column(String(10), default="TCP")
    attack_type = Column(String(50), index=True)
    severity = Column(String(20), index=True)  # Low, Medium, High, Critical
    confidence = Column(Float)
    status = Column(String(20), default="NEW", index=True)  # NEW, ACKNOWLEDGED, RESOLVED, FALSE_POSITIVE
    is_anomaly = Column(Boolean, default=False)
    flow_features = Column(JSON, nullable=True)
    top_features = Column(JSON, nullable=True)  # XAI attributions
    security_insight = Column(Text, nullable=True)

class DetectionHistory(Base):
    __tablename__ = "detection_history"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utc_now, index=True)
    filename = Column(String(255), nullable=True)
    source = Column(String(50), default="CSV_UPLOAD")  # CSV_UPLOAD, LIVE_CAPTURE, SIMULATION
    total_flows = Column(Integer, default=0)
    normal_flows = Column(Integer, default=0)
    attack_flows = Column(Integer, default=0)
    duration_seconds = Column(Float, default=0.0)

class MonitoringSession(Base):
    __tablename__ = "monitoring_sessions"

    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime, default=utc_now)
    stopped_at = Column(DateTime, nullable=True)
    mode = Column(String(50), default="SIMULATED")  # SIMULATED, LIVE_PCAP
    status = Column(String(20), default="IDLE")    # IDLE, RUNNING, STOPPED
    total_packets = Column(Integer, default=0)
    total_flows = Column(Integer, default=0)
    alerts_count = Column(Integer, default=0)
