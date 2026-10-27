# AI-NIDS: Project Report Outline (B.Tech AI & Data Science)

Use this structured outline to author your final-year major project thesis or academic paper.

---

## Front Matter
1. Title Page (Project Title, Student Names, Roll Numbers, Guide Name, Department, College Seal)
2. Certificate of Originality
3. Declaration by Students
4. Acknowledgments
5. Abstract (250-300 words summarizing problem, methodology, results, and significance)
6. Table of Contents
7. List of Figures & List of Tables
8. Abbreviations (NIDS, HIDS, SOC, XAI, IAT, TCP, PCAP, FPR, ROC-AUC)

---

## Chapter 1: Introduction
- **1.1 Background and Motivation**: Growth of cloud computing, IoT expansion, and sophistication of cyberattacks (DDoS, Botnets, Advanced Persistent Threats).
- **1.2 Problem Statement**: Inadequacy of static signature rules against novel, polymorphic intrusions; high false-positive rates causing SOC analyst alert fatigue.
- **1.3 Objectives of the Project**:
  - Design a real-time flow-based detection pipeline.
  - Implement zero-leakage preprocessing for statistical flow features.
  - Benchmark multiple ML classifiers (Random Forest, Gradient Boosting, Logistic Regression, Isolation Forest).
  - Integrate Explainable AI (XAI) for transparent threat attribution.
  - Build a reactive SOC web dashboard with Mode A (CSV dataset analysis) and Mode B (live traffic monitoring/replay).
- **1.4 Scope and Limitations**: Flow-level statistical analysis vs encrypted payload inspection; scope of supported attack classes.
- **1.5 Report Organization**.

---

## Chapter 2: Literature Survey
- **2.1 Evolution of Intrusion Detection Systems**: Knowledge-based vs anomaly-based systems.
- **2.2 Review of Standard Intrusion Datasets**:
  - KDD Cup 99 & NSL-KDD (Historical limitations: outdated IP addresses, artificial synthetic traffic).
  - CIC-IDS2017 & CSE-CIC-IDS2018 (Authentic benign background traffic, modern diverse attack families).
  - UNSW-NB15 (Real network characteristics with low-footprint attack simulations).
- **2.3 Existing Machine Learning Approaches**: Review of SVM, Decision Trees, Naive Bayes, and Deep Neural Networks (CNN/LSTM) for NIDS.
- **2.4 Identified Research Gaps**: Black-box opacity in ML models, data leakage through identifier columns, neglecting benign false positive rate in SOC operations.

---

## Chapter 3: Proposed Methodology & System Architecture
- **3.1 System Architecture**: High-level block diagram and layered design (Ingestion, Preprocessing, ML/XAI, API, Frontend).
- **3.2 Modular Detection Pipeline**: Mode A (Batch CSV upload) vs Mode B (Live Ingestion / Replay).
- **3.3 Feature Extraction Mechanism**: From raw packet arrival to 5-tuple statistical aggregation.
- **3.4 Database Schema Design**: Entities for alerts, detection runs, and monitoring telemetry.

---

## Chapter 4: Data Preprocessing & Feature Engineering
- **4.1 Dataset Description**: CIC-IDS2017 schema, feature definitions, and class distributions.
- **4.2 Data Cleansing**: Duplicate detection, infinite value capping, and missing value median imputation.
- **4.3 Prevention of Data Leakage**: Strategic removal of non-informative identifiers (Source/Dest IPs, Port numbers, Flow IDs, Timestamps).
- **4.4 Feature Scaling & Normalization**: Application of `StandardScaler` fitted strictly on training partitions.
- **4.5 Label Encoding & Class Imbalance Analysis**: Mitigation through balanced ensemble class weighting.

---

## Chapter 5: Machine Learning Models & Algorithms
- **5.1 Supervised Classifiers**:
  - Random Forest Classifier (Bootstrap aggregation, Gini impurity, tree depth calibration).
  - Logistic Regression (Linear decision boundary baseline).
  - Gradient Boosting Classifier (Sequential error minimization).
- **5.2 Unsupervised Anomaly Detection**:
  - Isolation Forest (Path length partitioning for zero-day threat detection).
- **5.3 Explainable AI (XAI) Framework**: Global feature importance and local baseline divergence calculation.

---

## Chapter 6: Implementation & Dashboard Development
- **6.1 Backend API Development**: FastAPI routing, Pydantic request validation, CORS middleware, SQLAlchemy integration.
- **6.2 Frontend Architecture**: React.js, Vite build tooling, Tailwind CSS cybersecurity dark theme.
- **6.3 Key Dashboard Features**: Live KPI cards, 24-hour traffic volume timeline, attack distribution, paginated alert feed, forensic detail modal.

---

## Chapter 7: Results and Performance Evaluation
- **7.1 Evaluation Metrics**: Accuracy, Precision, Recall, F1-Score (Macro & Weighted), Confusion Matrix, Benign False Positive Rate (FPR).
- **7.2 Comparative Model Analysis**: Tabular and graphical comparison of Random Forest vs Gradient Boosting vs Logistic Regression.
- **7.3 Confusion Matrix Analysis**: Detailed true vs predicted classification analysis across all 7 traffic classes.
- **7.4 SOC Security Trade-Off Discussion**: Impact of False Positives on alert fatigue vs False Negatives on breach vulnerability.
- **7.5 XAI Findings**: Ranking the top 10 discriminative network features (Flow IAT Min, Initial Window Bytes, Packet Length Mean).

---

## Chapter 8: Conclusion & Future Enhancements
- **8.1 Summary of Contributions**.
- **8.2 Future Scope**:
  - Hardware acceleration with DPDK / eBPF for multi-gigabit line rates.
  - Automated threat mitigation via SDN / firewall rule injection.
  - Federated Learning for privacy-preserving cross-organizational NIDS.

---

## References (IEEE Format)
1. I. Sharafaldin, A. H. Lashkari, and A. A. Ghorbani, "Toward Generating a New Dataset for Intrusion Detection: Systematic Review and Objectivity Analysis," *IEEE EISIC*, 2018.
2. N. Moustafa and J. Slay, "UNSW-NB15: a comprehensive data set for network intrusion detection systems," *IEEE MilCIS*, 2015.
3. F. T. Liu, K. M. Ting, and Z.-H. Zhou, "Isolation Forest," *IEEE ICDM*, 2008.
4. L. Breiman, "Random Forests," *Machine Learning*, vol. 45, no. 1, pp. 5–32, 2001.
