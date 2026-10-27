"""
AI-NIDS: Real-Time Monitor Endpoints
Controls live network traffic monitoring and simulated replay streaming.
"""

from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.entities import Alert
from backend.app.services.traffic_monitor import monitor_service
from backend.app.services.flow_extractor import FlowFeatureExtractor
from backend.app.services.ml_service import ml_service

router = APIRouter(prefix="/monitor", tags=["Traffic Monitoring"])

@router.get("/status")
def get_monitor_status():
    """Retrieve operational telemetry and health of the traffic monitoring engine."""
    return monitor_service.get_status()

@router.post("/start")
def start_traffic_monitor(mode: str = Query("SIMULATED", description="Monitoring mode: SIMULATED or LIVE_PCAP")):
    """
    Initiate traffic monitoring.
    Note: Real packet capture requires explicit local interface authorization and root privileges.
    SIMULATED mode replays realistic CIC-IDS2017 compliant network flows safely.
    """
    return monitor_service.start_monitoring(mode=mode)

@router.post("/stop")
def stop_traffic_monitor():
    """Terminate active traffic monitoring session."""
    return monitor_service.stop_monitoring()

@router.post("/simulate")
def trigger_simulated_burst(
    attack_type: str = Query("DDoS", description="Attack type to simulate: DDoS, DoS-Hulk, PortScan, BruteForce, Botnet, Infiltration, BENIGN"),
    count: int = Query(5, ge=1, le=50, description="Number of flow samples to inject"),
    db: Session = Depends(get_db)
):
    """
    Inject an authorized burst of test flows into the system for live demonstration.
    Immediately updates dashboard feeds and evaluates through the ML model.
    """
    results = []
    for _ in range(count):
        flow_data = FlowFeatureExtractor.generate_simulated_flow(attack_type=attack_type)
        pred = ml_service.predict_flow(flow_data["features"])

        if pred["is_malicious"] or pred.get("is_anomaly", False):
            alert = Alert(
                flow_id=flow_data["flow_id"],
                src_ip=flow_data["src_ip"],
                dst_ip=flow_data["dst_ip"],
                src_port=flow_data["src_port"],
                dst_port=flow_data["dst_port"],
                protocol=flow_data["protocol"],
                attack_type=pred["predicted_class"],
                severity=pred["severity"],
                confidence=pred["confidence"],
                status="NEW",
                is_anomaly=pred.get("is_anomaly", False),
                flow_features=flow_data["features"],
                top_features=pred.get("top_contributing_features", []),
                security_insight=pred.get("security_insight", "")
            )
            db.add(alert)

        results.append({
            "flow_id": flow_data["flow_id"],
            "simulated_type": attack_type,
            "predicted_class": pred["predicted_class"],
            "confidence": pred["confidence"],
            "severity": pred["severity"],
            "is_malicious": pred["is_malicious"]
        })

    db.commit()
    return {
        "message": f"Successfully injected {count} simulated {attack_type} flows.",
        "flows": results
    }
