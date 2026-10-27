# AI-NIDS: Project Viva & Technical Interview Preparation Guide

This document prepares candidates for final-year B.Tech / M.Tech project defense and cybersecurity technical interviews.

---

### Q1: What is the difference between a Signature-based NIDS and an AI-based NIDS?
**Answer:**
- **Signature-based NIDS** (e.g., traditional Snort, Suricata rules) relies on pre-compiled strings, packet hex patterns, and known vulnerability signatures. While fast and low on false positives for known attacks, it fails completely against zero-day exploits, encrypted payloads, and polymorphic attack mutations.
- **AI-based NIDS** models the statistical and behavioral characteristics of network flows (such as packet rate, inter-arrival time distributions, and flag ratios). It can detect novel attack variants, zero-day anomalies, and volumetric anomalies even without payload inspection or plaintext access.

---

### Q2: Why can't raw network packets (PCAP frames) be directly passed into a tabular Machine Learning model?
**Answer:**
Raw packets arrive as discrete, variable-length binary arrays (Ethernet frames, IP headers, TCP/UDP headers, and application payload bytes). Tabular Machine Learning algorithms (Random Forest, Gradient Boosting, SVM) require fixed-dimension, numerical feature vectors.
Furthermore, single isolated packets usually lack malicious context. An individual TCP SYN packet is completely normal; only when aggregated across a sliding 5-tuple time window to observe hundreds of unanswered SYNs in milliseconds does it become an identifiable SYN Flood or Port Scan. Therefore, raw packets must pass through a **Flow Feature Extractor** (like CICFlowMeter or Zeek) to calculate statistical aggregations.

---

### Q3: What is a 5-Tuple in network traffic analysis?
**Answer:**
A 5-tuple uniquely identifies a bidirectional network conversation:
1. **Source IP Address**
2. **Destination IP Address**
3. **Source Port**
4. **Destination Port**
5. **Transport Layer Protocol** (e.g., TCP, UDP, ICMP)

---

### Q4: What is Data Leakage in Machine Learning, and how does your project prevent it?
**Answer:**
Data leakage occurs when information outside the training dataset is inadvertently used to train the model, leading to overly optimistic evaluation metrics that fail in production. In AI-NIDS, data leakage is prevented by:
1. **Dropping non-informative metadata**: Removing Flow ID, Source IP, Destination IP, and Timestamps. If IPs are left in, the model simply memorizes that `192.168.1.105` was an attacker during training rather than learning the statistical characteristics of the attack.
2. **Strict Train/Test Split Ordering**: Splitting data into train/test sets *before* calculating imputation medians or fitting feature scalers (`StandardScaler`). Imputer and scaler parameters are learned strictly from the training set and applied to the test set.

---

### Q5: Why is Accuracy an insufficient metric for evaluating an Intrusion Detection System?
**Answer:**
Network traffic suffers from severe **Class Imbalance**. In a typical enterprise network, over 99% of flows are legitimate (`BENIGN`), while attacks may comprise less than 1%. A naive model that classifies 100% of flows as `BENIGN` would achieve 99% accuracy while missing every single intrusion.
Therefore, an IDS must be evaluated on:
- **Precision**: What fraction of flagged alerts were actual attacks?
- **Recall (Sensitivity)**: What fraction of actual attacks were successfully caught?
- **F1-Score (Macro & Weighted)**: Harmonic mean balancing precision and recall.
- **False Positive Rate (FPR)** on benign traffic: Measures alert fatigue risk in a SOC.

---

### Q6: Explain the trade-off between False Positives and False Negatives in a Security Operations Center (SOC).
**Answer:**
- **False Positive (Type I Error)**: A benign user action (e.g., large file backup or rapid API polling) is classified as an attack. A high False Positive Rate results in **Alert Fatigue**, causing overworked SOC analysts to ignore or disable alert feeds, allowing genuine breaches to slip through.
- **False Negative (Type II Error)**: A genuine cyberattack bypasses detection and establishes persistence inside the enterprise perimeter. In cybersecurity, False Negatives on critical vectors (such as DDoS, Ransomware, or Infiltration) carry catastrophic consequences.
- **Design Philosophy**: Our system optimizes for balanced F1-Macro and high recall on malicious categories while calibrating feature thresholds to keep Benign FPR as low as possible.

---

### Q7: Why did you choose Random Forest as your primary supervised model?
**Answer:**
1. **Non-linear decision boundaries**: Network attacks exhibit non-linear boundary thresholds (e.g., short duration combined with high SYN count).
2. **Resilience to multicollinearity**: Decision tree ensembles handle correlated network features naturally without requiring PCA.
3. **High inference throughput**: Fast prediction speed compared to deep neural networks, making it ideal for high-packet-rate network interfaces.
4. **Intrinsic Feature Importance (MDI)**: Generates Mean Decrease in Impurity scores, enabling native Explainable AI (XAI).

---

### Q8: What role does Isolation Forest play alongside Random Forest?
**Answer:**
Random Forest is a **supervised** model that excels at classifying known attack classes present in its training dataset. However, if a threat actor devises a completely novel attack vector, supervised models might misclassify it as benign.
**Isolation Forest** is an **unsupervised anomaly detection algorithm**. Trained exclusively on benign baseline traffic, it recursively isolates data points. Anomalous flows require fewer partitions to isolate than normal points. When Random Forest classifies a flow as BENIGN but Isolation Forest flags it as an outlier, AI-NIDS generates a **Zero-Day Anomaly Warning**.

---

### Q9: What features in CIC-IDS2017 are most discriminative for detecting Port Scans?
**Answer:**
1. `Total Fwd Packets`: Very low (1 to 3 packets).
2. `Total Length of Fwd Packets`: Zero or minimal payload bytes (typically 40-60 bytes).
3. `SYN Flag Count`: High (initiates handshake without completing payload transfer).
4. `RST Flag Count`: Elevated (returned by closed ports on target subnet).
5. `Flow Duration`: Extremely short (microseconds).

---

### Q10: How do you identify a Botnet Command and Control (C2) channel?
**Answer:**
Botnets maintain persistent communication with external C2 servers via periodic **beaconing**. In flow analysis, this appears as:
- Abnormally low variance in `Flow IAT Std` (Inter-Arrival Time Standard Deviation), representing strict heartbeat periodicity.
- Predictable, small `Average Packet Size` corresponding to command poll messages.
- Medium to long `Flow Duration` with low overall packet counts.

---

### Q11: How does your system provide Explainable AI (XAI)?
**Answer:**
Deep neural networks and complex ensembles often act as "black boxes." In a SOC environment, an analyst cannot take remedial action (e.g., blocking an IP or isolating a server) without understanding *why* a flow was flagged.
AI-NIDS implements:
1. **Global XAI**: Tree-based feature importance ranking the top discriminating network features across the dataset.
2. **Local Alert XAI**: For every triggered alert, the system compares the flow's parameters against benign empirical baselines, highlighting the top contributing factors (e.g., "SYN flag count 85% above normal baseline", "Flow packets/s matches volumetric flooding pattern").

---

### Q12: How is the database designed to prevent performance bottlenecks?
**Answer:**
1. Indexed columns on `timestamp`, `attack_type`, `severity`, and `status` to enable sub-millisecond pagination and filtering across thousands of records.
2. Structured separation between operational alerts (`alerts` table) and high-level batch execution metrics (`detection_history` table).
3. JSON column typing for optional raw feature inspection without bloating relational query performance.

---

### Q13: Why did you use FastAPI over traditional Flask or Django?
**Answer:**
1. **Asynchronous Throughput**: Built on Starlette and ASGI with native `async/await` support, allowing high-concurrency ingestion of streaming network flows.
2. **Automated Schema Validation**: Built-in Pydantic integration ensures all incoming network flow telemetry adheres to expected data types and bounds before touching the ML model.
3. **Interactive Documentation**: Auto-generates OpenAPI (Swagger) and ReDoc specifications at `/docs`.

---

### Q14: What ethical and legal constraints apply to Network Intrusion Detection?
**Answer:**
- Packet inspection must only occur on networks where explicit written authorization has been granted by network owners.
- Systems should avoid retaining unencrypted application-layer payloads containing personal identifiable information (PII) or credentials.
- AI-NIDS adheres to defensive operations: monitoring and alerting without unauthorized intrusive scanning, payload decryption, or offensive pivoting.
