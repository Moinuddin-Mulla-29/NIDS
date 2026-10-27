"""
AI-NIDS: Backend API Integration Tests
Tests endpoints using FastAPI TestClient.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_dashboard_summary_endpoint():
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_flows" in data
    assert "suspicious_flows" in data
    assert "critical_alerts" in data

def test_traffic_timeseries_endpoint():
    response = client.get("/api/dashboard/traffic-timeseries")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "normal_count" in data[0]

def test_attack_distribution_endpoint():
    response = client.get("/api/dashboard/attack-distribution")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "name" in data[0]
        assert "count" in data[0]

def test_single_flow_detection_endpoint():
    payload = {
        "src_ip": "192.168.1.105",
        "dst_ip": "10.0.0.1",
        "src_port": 50221,
        "dst_port": 80,
        "protocol": "TCP",
        "features": {
            "Flow Duration": 150000.0,
            "Total Fwd Packets": 10,
            "Total Backward Packets": 12,
            "Total Length of Fwd Packets": 2500.0,
            "Total Length of Bwd Packets": 8500.0,
            "Flow Bytes/s": 73333.3,
            "Flow Packets/s": 146.6,
            "Flow IAT Mean": 6800.0,
            "SYN Flag Count": 0,
            "RST Flag Count": 0,
            "Average Packet Size": 500.0
        }
    }
    response = client.post("/api/detect", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_class" in data
    assert "confidence" in data
    assert "severity" in data

def test_alerts_pagination_and_filter():
    response = client.get("/api/alerts?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)

def test_model_metrics_endpoint():
    response = client.get("/api/model/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "best_model" in data
    assert "metrics" in data
    assert "feature_importances" in data

def test_monitor_status_endpoint():
    response = client.get("/api/monitor/status")
    assert response.status_code == 200
    data = response.json()
    assert "is_running" in data
    assert "mode" in data
