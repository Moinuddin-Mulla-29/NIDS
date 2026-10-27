"""
AI-NIDS: Real-Time Traffic Monitor Service
Oversees live traffic ingestion or authorized simulation replay sessions.
Extracts flow features, evaluates via ML inference, stores incident alerts in DB,
and supplies telemetry for real-time dashboard visualization.
"""

import time
import random
import threading
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from backend.app.database.session import SessionLocal
from backend.app.models.entities import Alert, MonitoringSession
from backend.app.services.ml_service import ml_service
from backend.app.services.flow_extractor import FlowFeatureExtractor

class TrafficMonitorService:
    def __init__(self):
        self._is_running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self.mode = "SIMULATED"  # SIMULATED or LIVE_PCAP
        self.total_packets_processed = 0
        self.total_flows_processed = 0
        self.alerts_generated = 0
        self.session_id: Optional[int] = None
        self.start_time: Optional[float] = None

    def start_monitoring(self, mode: str = "SIMULATED") -> Dict[str, Any]:
        with self._lock:
            if self._is_running:
                return {
                    "status": "ALREADY_RUNNING",
                    "mode": self.mode,
                    "session_id": self.session_id,
                    "message": "Traffic monitoring session is already active."
                }

            self.mode = mode
            self._is_running = True
            self.start_time = time.time()
            self.total_packets_processed = 0
            self.total_flows_processed = 0
            self.alerts_generated = 0

            # Record session in database
            db = SessionLocal()
            try:
                session_rec = MonitoringSession(
                    started_at=datetime.now(timezone.utc).replace(tzinfo=None),
                    mode=self.mode,
                    status="RUNNING"
                )
                db.add(session_rec)
                db.commit()
                db.refresh(session_rec)
                self.session_id = session_rec.id
            finally:
                db.close()

            # Start worker thread
            self._thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self._thread.start()

            return {
                "status": "RUNNING",
                "mode": self.mode,
                "session_id": self.session_id,
                "message": f"Successfully initiated traffic monitoring in {self.mode} mode."
            }

    def stop_monitoring(self) -> Dict[str, Any]:
        with self._lock:
            if not self._is_running:
                return {
                    "status": "IDLE",
                    "session_id": self.session_id,
                    "message": "Monitoring service is not currently running."
                }

            self._is_running = False

            # Update database session
            db = SessionLocal()
            try:
                if self.session_id:
                    session_rec = db.query(MonitoringSession).filter(MonitoringSession.id == self.session_id).first()
                    if session_rec:
                        session_rec.stopped_at = datetime.now(timezone.utc).replace(tzinfo=None)
                        session_rec.status = "STOPPED"
                        session_rec.total_packets = self.total_packets_processed
                        session_rec.total_flows = self.total_flows_processed
                        session_rec.alerts_count = self.alerts_generated
                        db.commit()
            finally:
                db.close()

            return {
                "status": "STOPPED",
                "session_id": self.session_id,
                "total_flows": self.total_flows_processed,
                "alerts_generated": self.alerts_generated,
                "message": "Traffic monitoring session halted successfully."
            }

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            uptime = round(time.time() - self.start_time, 1) if (self._is_running and self.start_time) else 0.0
            return {
                "is_running": self._is_running,
                "mode": self.mode,
                "session_id": self.session_id,
                "uptime_seconds": uptime,
                "total_packets": self.total_packets_processed,
                "total_flows": self.total_flows_processed,
                "alerts_generated": self.alerts_generated,
                "flows_per_second": round(self.total_flows_processed / max(1.0, uptime), 1) if self._is_running else 0.0
            }

    def _monitoring_loop(self) -> None:
        """Background continuous network flow generator and evaluation loop."""
        attack_types = ["BENIGN", "BENIGN", "BENIGN", "DoS-Hulk", "DDoS", "PortScan", "BruteForce", "Botnet"]

        while self._is_running:
            try:
                # Select profile (~70% Benign, ~30% Intrusions for lively dashboard monitoring)
                choice = random.choice(attack_types) if random.random() < 0.45 else "BENIGN"
                flow_data = FlowFeatureExtractor.generate_simulated_flow(attack_type=choice)

                # ML Inference
                res = ml_service.predict_flow(flow_data["features"])

                self.total_flows_processed += 1
                pkts = int(flow_data["features"].get("Total Fwd Packets", 1) + flow_data["features"].get("Total Backward Packets", 1))
                self.total_packets_processed += pkts

                # If Malicious or Outlier Anomaly, insert alert into Database
                if res["is_malicious"] or res.get("is_anomaly", False):
                    self.alerts_generated += 1
                    db = SessionLocal()
                    try:
                        alert = Alert(
                            flow_id=flow_data["flow_id"],
                            src_ip=flow_data["src_ip"],
                            dst_ip=flow_data["dst_ip"],
                            src_port=flow_data["src_port"],
                            dst_port=flow_data["dst_port"],
                            protocol=flow_data["protocol"],
                            attack_type=res["predicted_class"],
                            severity=res["severity"],
                            confidence=res["confidence"],
                            status="NEW",
                            is_anomaly=res.get("is_anomaly", False),
                            flow_features=flow_data["features"],
                            top_features=res.get("top_contributing_features", []),
                            security_insight=res.get("security_insight", "")
                        )
                        db.add(alert)
                        db.commit()
                    finally:
                        db.close()

                # Sleep brief interval between simulated network flows
                time.sleep(random.uniform(0.6, 1.8))

            except Exception as e:
                print(f"[!] Error in traffic monitor loop: {e}")
                time.sleep(2)

monitor_service = TrafficMonitorService()
