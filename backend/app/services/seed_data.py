"""
AI-NIDS: Database Seeder
Seeds initial historical alerts and detection metrics for demonstrational analytics.
"""

from datetime import datetime, timedelta, timezone
import random
from backend.app.database.session import SessionLocal
from backend.app.models.entities import Alert, DetectionHistory
from backend.app.services.flow_extractor import FlowFeatureExtractor
from backend.app.services.ml_service import ml_service

def seed_initial_data_if_empty():
    db = SessionLocal()
    try:
        count = db.query(Alert).count()
        if count > 0:
            return  # Already populated

        print("[*] Seeding initial historical alerts for AI-NIDS dashboard...")
        attack_types = [
            ("DoS-Hulk", 14),
            ("DDoS", 18),
            ("PortScan", 22),
            ("BruteForce", 12),
            ("Botnet", 8),
            ("Infiltration", 6),
        ]

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        for attack_name, num_items in attack_types:
            for _ in range(num_items):
                flow_data = FlowFeatureExtractor.generate_simulated_flow(attack_type=attack_name)
                res = ml_service.predict_flow(flow_data["features"])
                offset_minutes = random.randint(5, 1440)  # past 24 hours
                created_time = now - timedelta(minutes=offset_minutes)

                alert = Alert(
                    timestamp=created_time,
                    flow_id=flow_data["flow_id"],
                    src_ip=flow_data["src_ip"],
                    dst_ip=flow_data["dst_ip"],
                    src_port=flow_data["src_port"],
                    dst_port=flow_data["dst_port"],
                    protocol=flow_data["protocol"],
                    attack_type=res["predicted_class"],
                    severity=res["severity"],
                    confidence=res["confidence"],
                    status=random.choice(["NEW", "NEW", "ACKNOWLEDGED", "RESOLVED"]),
                    is_anomaly=res.get("is_anomaly", False),
                    flow_features=flow_data["features"],
                    top_features=res.get("top_contributing_features", []),
                    security_insight=res.get("security_insight", "")
                )
                db.add(alert)

        # Seed detection history record
        hist = DetectionHistory(
            timestamp=now - timedelta(hours=2),
            filename="CIC-IDS2017_Friday_Batch01.csv",
            source="CSV_UPLOAD",
            total_flows=5420,
            normal_flows=4980,
            attack_flows=440,
            duration_seconds=3.2
        )
        db.add(hist)
        db.commit()
        print("[+] Seed data created successfully.")
    except Exception as e:
        print(f"[!] Warning seeding database: {e}")
        db.rollback()
    finally:
        db.close()
