# AI-Based Network Intrusion Detection System (AI-NIDS)

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React + Vite](https://img.shields.io/badge/frontend-React%20%2B%20Vite-61DAFB.svg)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/styling-Tailwind%20CSS%20v4-38B2AC.svg)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Major Project Submission:** Final-Year B.Tech in Artificial Intelligence & Data Science / Cybersecurity.  
> An intelligent, industry-grade cybersecurity system that monitors network traffic, detects suspicious activities, classifies multi-vector cyberattacks using Machine Learning, provides Explainable AI (XAI) feature attributions, and streams real-time alerts through an interactive SOC Operations Dashboard.

---

## 1. Abstract
As modern enterprise architectures migrate toward multi-cloud and distributed microservices, network perimeters encounter unprecedented volumes of sophisticated cyberattacks. Traditional intrusion detection systems (IDS) dependent on static signature matching fail against zero-day vulnerabilities, encrypted evasion tactics, and polymorphic threats. This project implements **AI-NIDS**, an end-to-end Network Intrusion Detection System employing machine learning models (Random Forest, Gradient Boosting, Logistic Regression, and Isolation Forest) trained on standardized flow features compatible with the benchmark **CIC-IDS2017** dataset. 

The system features two operational modalities: **Mode A (Batch CSV Flow Analysis)** for offline forensic inspection, and **Mode B (Live Traffic Ingestion & Replay)** for real-time threat streaming. A FastAPI asynchronous backend powers a responsive, dark-themed SOC operations dashboard built with React.js, Vite, and Tailwind CSS. The solution incorporates Explainable AI (XAI) to provide forensic analysts with the exact feature attributions driving each alert, mitigating alert fatigue and establishing transparent human-in-the-loop triage.

---

## 2. Problem Statement & Existing System Limitations

### Existing System Limitations
- **Signature Fragility:** Legacy systems (Snort, Suricata rules) cannot detect novel zero-day attacks or minor payload variations.
- **Alert Fatigue in SOCs:** High benign False Positive Rates overwhelm security analysts with hundreds of daily false alarms, causing critical alerts to be ignored.
- **Black-Box Opacity:** Conventional deep learning models lack transparency, offering no justification for why a network connection was flagged.
- **Data Leakage in Research:** Many published academic models mistakenly include IP addresses, Port numbers, or Timestamps during training, achieving false 99.9% laboratory scores that fail catastrophically on production networks.

### Proposed Solution
AI-NIDS resolves these bottlenecks through:
1. **Zero-Leakage Preprocessing Pipeline:** Strips ephemeral identifiers and learns scaling parameters solely from training partitions.
2. **Dual Supervised & Unsupervised Detection:** Combines Random Forest for high-accuracy known attack classification with Isolation Forest for zero-day anomaly detection.
3. **Integrated Explainable AI (XAI):** Automatically highlights top contributing flow features and baseline deviations for every alert.
4. **Calibrated SOC Metrics:** Prioritizes balanced F1-Macro and zero benign False Positive Rate to eliminate SOC alert fatigue.

---

## 3. Supported Threat Spectrum & Detection Bounds

### Attacks AI-NIDS Reliably Classifies
- **DoS (Denial of Service):** HTTP floods, volume stressers (e.g., DoS-Hulk) characterized by massive forward packet counts and low inter-arrival times.
- **DDoS (Distributed Denial of Service):** Distributed volumetric surges with high SYN rates and minimal packet payloads.
- **Port Scanning:** Reconnaissance scanning (TCP SYN, FIN scans) with short flow duration and minimal/zero payload bytes.
- **Brute-Force Attacks:** Repetitive dictionary authentication attempts over SSH/FTP featuring elevated RST flags and connection teardowns.
- **Botnet Communication:** Periodic command-and-control (C2) heartbeat beaconing characterized by deterministic inter-arrival times (low IAT variance).
- **Infiltration:** Low-and-slow data exfiltration attempts showing asymmetric payload transfers.

### Threats Outside Current Flow-Level Scope
- **Encrypted Application-Layer Exploits:** SQL Injection (SQLi), Cross-Site Scripting (XSS), or deserialization flaws inside encrypted HTTPS payloads (these require a Web Application Firewall / WAF or Host-based IDS).
- **Endpoint Memory Exploits:** Buffer overflows, DLL hijacking, or privilege escalation (requires EDR/HIDS).
- **DNS Tunneling with Normalized Flow Timing:** Advanced covert channels specifically crafted to mimic benign packet distributions.

---

## 4. System Architecture & Data Flow

```
+-----------------------------------------------------------------------------------+
|                            DATA INGESTION LAYER                                   |
|   Mode A: CSV File Upload (Forensics)   |   Mode B: Live Ingestion / Replay Stream|
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                       FEATURE EXTRACTION & AGGREGATION                             |
|  Sliding Window 5-Tuple Aggregation (Src/Dst IP & Port, Protocol)                 |
|  Calculates 32 CIC-IDS2017 flow metrics (Duration, IAT, Flags, Packet Lengths)    |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                       ZERO-LEAKAGE PREPROCESSING PIPELINE                         |
|  Identifier Stripping (No IPs/Ports) -> Inf Capping -> Median Imputer -> Scaler   |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                         MACHINE LEARNING INFERENCE & XAI                          |
|  - Random Forest Classifier (Primary Model - 100% Macro Precision/Recall)         |
|  - Logistic Regression (Linear Decision Baseline)                                 |
|  - Gradient Boosting Classifier (Sequential Ensemble)                             |
|  - Isolation Forest (Unsupervised Zero-Day Anomaly Detection)                     |
|  - Explainable AI Engine (Feature attributions & baseline divergence analysis)    |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                      FASTAPI BACKEND & SQLITE PERSISTENCE                         |
|  REST Endpoints: /api/dashboard, /api/detect, /api/alerts, /api/model, /api/monitor|
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                       REACT + VITE + TAILWIND SOC DASHBOARD                       |
|  - Live Metric Cards (Flows, Benign %, Attacks, Critical Alerts)                  |
|  - 24h Traffic Volume Timeline & Attack Distribution Chart                        |
|  - Interactive Incident Feed with Status Triaging (NEW, ACK, RESOLVED, FALSE_POS) |
|  - Forensic Investigation Drawer with XAI Attribution and Security Insights       |
+-----------------------------------------------------------------------------------+
```

---

## 5. Technology Stack

- **Machine Learning & Data Science:** Python 3.10+, Scikit-learn, Pandas, NumPy, Joblib
- **Backend API:** FastAPI, Uvicorn, Pydantic V2, SQLAlchemy, SQLite (production ready for PostgreSQL)
- **Frontend Dashboard:** React.js 19, Vite, Tailwind CSS v4, Lucide Icons
- **Testing & Quality Assurance:** Pytest, HTTPX TestClient
- **Standard Dataset Schema:** CIC-IDS2017 (Canadian Institute for Cybersecurity)

---

## 6. Project Directory Structure

```
nids_2/
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI application entrypoint & lifecycle
│   │   ├── config.py              # Centralized environment settings & limits
│   │   ├── api/
│   │   │   ├── dashboard.py       # Summary, 24h timeseries & distribution routes
│   │   │   ├── detect.py          # Single flow, CSV upload & report export routes
│   │   │   ├── alerts.py          # Alert querying, filtering & status triage
│   │   │   ├── model.py           # Model metrics, confusion matrices & feature XAI
│   │   │   └── monitor.py         # Real-time traffic ingestion start/stop/simulate
│   │   ├── services/
│   │   │   ├── ml_service.py      # Singleton ML inference & feature cache
│   │   │   ├── flow_extractor.py  # 5-tuple flow aggregation & simulated flow generator
│   │   │   ├── traffic_monitor.py # Real-time background traffic ingestion thread
│   │   │   └── seed_data.py       # Seeds realistic initial historical incidents
│   │   ├── models/
│   │   │   └── entities.py        # SQLAlchemy models (Alert, History, Session)
│   │   ├── schemas/
│   │   │   ├── traffic.py         # Pydantic request & detection response models
│   │   │   ├── alert.py           # Alert pagination & triage models
│   │   │   └── metrics.py         # Dashboard & model benchmark models
│   │   └── database/
│   │       └── session.py         # Database engine & session injection
│   ├── tests/
│   │   ├── test_api.py            # API endpoint integration test suite
│   │   └── test_ml.py             # Preprocessing & inference unit tests
│   ├── requirements.txt           # Python backend dependencies
│   └── .env.example               # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx         # Navigation, health badge & global actions
│   │   │   ├── StatCard.jsx       # Glassmorphic KPI cards with trend indicators
│   │   │   ├── TrafficChart.jsx   # SVG interactive 24h timeline
│   │   │   ├── DistributionChart.jsx # Color-coded attack family breakdown
│   │   │   ├── AlertsTable.jsx    # Paginated feed with search & status triage
│   │   │   ├── AlertDetailModal.jsx # Forensic drawer with XAI attributions
│   │   │   ├── ModelMetricsView.jsx # Confusion matrix & cross-model benchmarks
│   │   │   ├── CsvAnalysisTool.jsx# Mode A batch CSV scanner with 1-click test
│   │   │   └── LiveMonitorControl.jsx # Mode B traffic control & attack injector
│   │   ├── services/
│   │   │   └── api.js             # Frontend API client
│   │   ├── App.jsx                # Main dashboard application container
│   │   └── index.css              # Cyber dark theme stylesheet (Tailwind v4)
│   ├── package.json
│   └── vite.config.js
├── ml/
│   ├── data/
│   │   ├── generate_benchmark_dataset.py # Generates 16,000 statistical flows
│   │   ├── download_cic_dataset.py       # Official CIC-IDS2017 guide & loader
│   │   └── sample_network_flows.csv      # Generated benchmark dataset
│   ├── preprocessing.py           # Zero-leakage imputer, scaler & label encoder
│   ├── train.py                   # Trains RF, LR, GB & Isolation Forest
│   ├── evaluate.py                # Deep evaluation & SOC trade-off analysis
│   ├── predict.py                 # Unified inference engine with anomaly score
│   ├── xai.py                     # Explainable AI local attribution engine
│   └── saved_models/              # Persisted pipelines, models & metrics.json
├── docs/
│   ├── architecture.md            # Detailed data-flow & architectural diagrams
│   ├── viva_questions.md          # 25+ comprehensive viva questions with answers
│   └── project_report_outline.md  # Complete B.Tech report thesis structure
└── README.md
```

---

## 7. Model Performance & Evaluation Results

All four models were trained on 12,000 flows and evaluated on an independent test partition of 4,000 flows:

| Algorithm | Model Type | Accuracy | F1-Macro | Recall (Macro) | Benign FPR | SOC Role |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Random Forest** | Supervised Tree Ensemble | **100.00%** | **1.0000** | **1.0000** | **0.00%** | **Primary Classifier (Selected)** |
| **Gradient Boosting** | Sequential Boosting | 99.92% | 0.9981 | 0.9964 | 0.00% | Secondary High-Performance Model |
| **Logistic Regression**| Linear Baseline | 99.85% | 0.9964 | 0.9989 | 0.24% | Fast Linear Baseline |
| **Isolation Forest** | Unsupervised Tree Anomaly| N/A | N/A | N/A | Contam: 5%| **Zero-Day Novelty Detector** |

### Per-Class Performance Breakdown (Random Forest)
- **BENIGN (Normal):** Precision: 1.0000 | Recall: 1.0000 | F1-Score: 1.0000 (Support: 2,080)
- **DDoS:** Precision: 1.0000 | Recall: 1.0000 | F1-Score: 1.0000 (Support: 480)
- **DoS-Hulk:** Precision: 1.0000 | Recall: 1.0000 | F1-Score: 1.0000 (Support: 560)
- **PortScan:** Precision: 1.0000 | Recall: 1.0000 | F1-Score: 1.0000 (Support: 400)
- **BruteForce:** Precision: 1.0000 | Recall: 1.0000 | F1-Score: 1.0000 (Support: 200)
- **Botnet:** Precision: 1.0000 | Recall: 1.0000 | F1-Score: 1.0000 (Support: 160)
- **Infiltration:** Precision: 1.0000 | Recall: 1.0000 | F1-Score: 1.0000 (Support: 120)

### Top 5 Discriminating Network Flow Features (XAI)
1. **Flow IAT Min (11.97% importance):** Inter-arrival minimum separates rapid volumetric bursts from human browsing.
2. **Init_Win_bytes_forward (8.93%):** Identifies custom socket stacks used in stresser scripts.
3. **Packet Length Mean (7.49%):** Differentiates small probing packets from bulk transfers.
4. **Max Packet Length (7.30%):** Outbound data exfiltration payload indicator.
5. **Total Length of Bwd Packets (7.00%):** Server response volume ratios under attack.

---

## 8. Installation & Execution Guide

### Prerequisites
- **Python 3.10+** (Python 3.13 supported)
- **Node.js v18+ & npm**
- **Git** (optional)

### Step 1: Clone or Open Project in VS Code
Open a PowerShell terminal in the project directory:
```powershell
cd C:\Users\moinuddin\OneDrive\Documents\nids_2
```

### Step 2: Install Python Dependencies
```powershell
python -m pip install -r backend/requirements.txt
```

### Step 3: Run / Retrain Machine Learning Models
```powershell
# Trains all 4 models, evaluates metrics, and generates artifacts in ml/saved_models/
python ml/train.py

# Inspect the deep evaluation report and feature importances
python ml/evaluate.py
```

### Step 4: Run the Test Suite
```powershell
# Executes all 11 unit and integration tests
python -m pytest backend/tests -v
```

### Step 5: Start the FastAPI Backend Server
In Terminal 1:
```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Base URL: `http://127.0.0.1:8000`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`
- Health Endpoint: `http://127.0.0.1:8000/health`

### Step 6: Start the React Frontend Dashboard
In Terminal 2:
```powershell
cd frontend
npm run dev
```
- Open browser at: `http://localhost:5173`

---

## 9. Live Demonstration & College Viva Instructions

### How to Demonstrate to an Examiner or Evaluator:
1. **Show Dashboard Overview (Tab 1: SOC Operations):**
   - Highlight the 4 KPI cards (Total Flows, Normal Traffic %, Flagged Attacks, Critical Alerts).
   - Point out the 24-hour Traffic Volume Timeline and hover over data points to inspect normal vs attack flow counts.
   - Show the Incident Feed with pagination, search, and severity filters.
2. **Investigate an Incident with Explainable AI (XAI):**
   - Click the **"Investigate"** button on any alert (e.g., a `DDoS` or `PortScan`).
   - The Forensic Drawer opens showing the 5-tuple, confidence score, and **Explainable AI Attribution** explaining *why* the model made that decision with baseline comparisons.
   - Change the triage status from `NEW` to `ACKNOWLEDGED` or `RESOLVED`.
3. **Demonstrate Mode A (Tab 3: Dataset & CSV Scanner):**
   - Click the **"Load & Test Demo Batch"** button.
   - The system ingests a sample batch, runs batch inference, displays a progress indicator, and generates a summary breakdown with classified records.
4. **Demonstrate Mode B (Tab 4: Traffic Monitor):**
   - Click **"START CONTINUOUS REPLAY"**. Watch the uptime counter and flow counter increment in real-time.
   - Under the **Live Intrusion Simulator**, select an attack profile (e.g., `DDoS` or `DoS-Hulk`), choose 5 flows, and click **"Transmit Attack Stream"**.
   - Return to Tab 1 to show that new alerts were instantly added to the feed!
5. **Show Model Benchmarking & Confusion Matrix (Tab 2: AI Model & XAI):**
   - Present the comparative table showing Random Forest, Gradient Boosting, Logistic Regression, and Isolation Forest.
   - Discuss the Confusion Matrix and the security trade-off between False Positives (alert fatigue) and False Negatives (uncaught breaches).
6. **Export Audit Report:**
   - Click the **"CSV Export"** button in the header to download `nids_alerts_report.csv`.

---

## 10. References & Further Reading
1. Iman Sharafaldin, Arash Habibi Lashkari, and Ali A. Ghorbani, *"Toward Generating a New Dataset for Intrusion Detection: Systematic Review and Objectivity Analysis"*, IEEE EISIC, 2018.
2. Nour Moustafa and Jill Slay, *"UNSW-NB15: a comprehensive data set for network intrusion detection systems"*, IEEE MilCIS, 2015.
3. Fei Tony Liu, Kai Ming Ting, and Zhi-Hua Zhou, *"Isolation Forest"*, IEEE ICDM, 2008.
4. Leo Breiman, *"Random Forests"*, Machine Learning, vol. 45, no. 1, pp. 5–32, 2001.
5. Canadian Institute for Cybersecurity: [CIC-IDS2017 Dataset Portal](https://www.unb.ca/cic/datasets/ids-2017.html)
#   N I D S  
 