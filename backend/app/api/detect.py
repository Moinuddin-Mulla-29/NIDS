"""
AI-NIDS: Detection & Inspection Endpoints
Handles real-time single-flow classification, CSV file uploads, and CSV alert reports.
"""

import io
import time
import pandas as pd
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.entities import Alert, DetectionHistory
from backend.app.services.ml_service import ml_service
from backend.app.schemas.traffic import SingleFlowRequest, SingleDetectionResponse, BatchDetectionResponse

router = APIRouter(prefix="", tags=["Detection"])

@router.post("/detect", response_model=SingleDetectionResponse)
def detect_single_flow(payload: SingleFlowRequest, db: Session = Depends(get_db)):
    """Classify an individual 5-tuple network flow with XAI feature attribution."""
    if not ml_service.is_ready():
        raise HTTPException(status_code=503, detail="Machine learning model is not initialized.")

    result = ml_service.predict_flow(payload.features)
    flow_id = f"flow_{int(time.time()*1000)}"

    # If classified as malicious, persist alert
    if result["is_malicious"] or result.get("is_anomaly", False):
        alert = Alert(
            flow_id=flow_id,
            src_ip=payload.src_ip or "192.168.1.100",
            dst_ip=payload.dst_ip or "10.0.0.1",
            src_port=payload.src_port or 54321,
            dst_port=payload.dst_port or 80,
            protocol=payload.protocol or "TCP",
            attack_type=result["predicted_class"],
            severity=result["severity"],
            confidence=result["confidence"],
            status="NEW",
            is_anomaly=result.get("is_anomaly", False),
            flow_features=payload.features,
            top_features=result.get("top_contributing_features", []),
            security_insight=result.get("security_insight", "")
        )
        db.add(alert)
        db.commit()

    return SingleDetectionResponse(
        flow_id=flow_id,
        src_ip=payload.src_ip or "192.168.1.100",
        dst_ip=payload.dst_ip or "10.0.0.1",
        src_port=payload.src_port or 54321,
        dst_port=payload.dst_port or 80,
        protocol=payload.protocol or "TCP",
        predicted_class=result["predicted_class"],
        is_malicious=result["is_malicious"],
        is_anomaly=result.get("is_anomaly", False),
        confidence=result["confidence"],
        severity=result["severity"],
        top_contributing_features=result.get("top_contributing_features", []),
        security_insight=result.get("security_insight", ""),
        disclaimer=result.get("disclaimer", "")
    )

@router.post("/detect/csv", response_model=BatchDetectionResponse)
async def detect_csv_file(
    file: UploadFile = File(...),
    max_rows: int = Query(5000, description="Maximum flow rows to analyze in one request"),
    db: Session = Depends(get_db)
):
    """
    Safely process and classify network flows from an uploaded CSV file.
    Validates file extension, bounds file size, and applies batch inference.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV formatted network capture.")

    start_time = time.time()
    try:
        content = await file.read()
        # Enforce 25MB max size limit
        if len(content) > 25 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File size exceeds the 25MB safety limit.")

        df = pd.read_csv(io.BytesIO(content), nrows=max_rows, low_memory=False)
        df.columns = df.columns.str.strip()

        # Execute batch inference
        results = ml_service.predict_dataframe(df)

        normal_count = sum(1 for r in results if not r["is_malicious"])
        malicious_count = sum(1 for r in results if r["is_malicious"])
        critical_count = sum(1 for r in results if r["severity"] == "Critical")

        # Persist a batch of malicious flow alerts into the database (up to 50 alerts per upload)
        new_alerts = 0
        for r in results:
            if r["is_malicious"] and new_alerts < 50:
                row_idx = r["index"]
                row_features = df.iloc[row_idx].to_dict()
                alert = Alert(
                    flow_id=f"csv_flow_{int(time.time())}_{row_idx}",
                    src_ip=str(row_features.get("Source IP", f"10.10.1.{100 + row_idx % 100}")),
                    dst_ip=str(row_features.get("Destination IP", "192.168.1.1")),
                    src_port=int(row_features.get("Source Port", 40000 + row_idx % 20000)),
                    dst_port=int(row_features.get("Destination Port", 80)),
                    protocol=str(row_features.get("Protocol", "TCP")),
                    attack_type=r["predicted_class"],
                    severity=r["severity"],
                    confidence=r["confidence"],
                    status="NEW",
                    is_anomaly=False,
                    flow_features=row_features,
                    top_features=[],
                    security_insight=f"Detected {r['predicted_class']} pattern during CSV batch analysis."
                )
                db.add(alert)
                new_alerts += 1

        # Record history
        elapsed = round(time.time() - start_time, 2)
        history = DetectionHistory(
            filename=file.filename,
            source="CSV_UPLOAD",
            total_flows=len(results),
            normal_flows=normal_count,
            attack_flows=malicious_count,
            duration_seconds=elapsed
        )
        db.add(history)
        db.commit()

        return BatchDetectionResponse(
            total_analyzed=len(results),
            normal_count=normal_count,
            malicious_count=malicious_count,
            critical_alerts=critical_count,
            records=results[:100]  # Return preview of first 100 records
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error evaluating CSV file: {str(e)}")

@router.get("/export/alerts")
def export_alerts_csv(db: Session = Depends(get_db)):
    """Export all stored alerts as an audit-ready CSV report."""
    alerts = db.query(Alert).order_by(Alert.timestamp.desc()).all()

    output = io.StringIO()
    output.write("ID,Timestamp,Flow_ID,Source_IP,Dest_IP,Source_Port,Dest_Port,Protocol,Attack_Type,Severity,Confidence,Status,Is_Anomaly\n")
    for a in alerts:
        output.write(
            f'"{a.id}","{a.timestamp}","{a.flow_id}","{a.src_ip}","{a.dst_ip}",'
            f'"{a.src_port}","{a.dst_port}","{a.protocol}","{a.attack_type}",'
            f'"{a.severity}","{a.confidence}","{a.status}","{a.is_anomaly}"\n'
        )

    output.seek(0)
    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=nids_alerts_report.csv"
    return response
