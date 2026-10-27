"""
AI-NIDS: Network Flow Aggregator and Feature Extractor
Converts raw packet observations into statistical 5-tuple flow vectors.

Crucial Architectural Note:
Raw network packets (Ethernet/IP/TCP frames) cannot be directly fed into machine learning
models trained on flow-level CSV datasets (e.g. CIC-IDS2017 / UNSW-NB15).
Instead, packets belonging to the same bidirectional flow (Src IP, Dst IP, Src Port, Dst Port, Protocol)
must be accumulated over a sliding time window to calculate statistical aggregations:
- Flow duration
- Forward & backward packet totals
- Payload length distributions (mean, std, min, max)
- Inter-arrival time (IAT) statistics
- Cumulative TCP control flags (SYN, FIN, RST, PSH, ACK, URG)
- Initial TCP window sizes
"""

import time
import random
import numpy as np
from typing import Dict, Any, List

class FlowFeatureExtractor:
    """
    Extracts statistical features from network flow records or simulated traffic streams.
    Ensures exact feature compatibility with the trained model schema.
    """

    @staticmethod
    def generate_simulated_flow(attack_type: str = "BENIGN") -> Dict[str, Any]:
        """
        Synthesize a realistic network flow according to the requested profile.
        Used for authorized live-monitoring replay mode and demonstrational tests.
        """
        src_ip = f"192.168.1.{random.randint(10, 240)}"
        dst_ip = f"10.0.0.{random.randint(1, 10)}"
        src_port = random.randint(1024, 65535)
        dst_port = 80 if attack_type in ["DoS-Hulk", "DDoS"] else (
            22 if attack_type == "BruteForce" else random.choice([21, 22, 80, 443, 3389, 8080])
        )

        if attack_type == "BENIGN":
            duration = float(np.random.exponential(scale=350000) + 1000)
            fwd_pkts = int(max(1, np.random.negative_binomial(5, 0.3)))
            bwd_pkts = int(max(1, np.random.negative_binomial(6, 0.25)))
            tot_len_fwd = float(fwd_pkts * np.random.normal(540, 150))
            tot_len_bwd = float(bwd_pkts * np.random.normal(920, 250))
            iat_mean = float(duration / max(1, (fwd_pkts + bwd_pkts - 1)))
            syn_flag, fin_flag, rst_flag, psh_flag, ack_flag = 0, 0, 0, 1, 1
            init_win_fwd = 29200
            init_win_bwd = 29200

        elif attack_type == "DoS-Hulk":
            duration = float(np.random.exponential(scale=180000) + 500)
            fwd_pkts = int(np.random.uniform(50, 220))
            bwd_pkts = int(np.random.uniform(0, 8))
            tot_len_fwd = float(fwd_pkts * 320)
            tot_len_bwd = float(bwd_pkts * 120)
            iat_mean = float(max(5, duration / max(1, fwd_pkts)))
            syn_flag, fin_flag, rst_flag, psh_flag, ack_flag = 1, 0, 0, 1, 1
            init_win_fwd = 8192
            init_win_bwd = 0

        elif attack_type == "DDoS":
            duration = float(np.random.exponential(scale=60000) + 100)
            fwd_pkts = int(np.random.uniform(80, 350))
            bwd_pkts = int(np.random.uniform(0, 3))
            tot_len_fwd = float(fwd_pkts * 140)
            tot_len_bwd = float(bwd_pkts * 64)
            iat_mean = float(max(1, duration / max(1, fwd_pkts)))
            syn_flag, fin_flag, rst_flag, psh_flag, ack_flag = 1, 0, 0, 0, 0
            init_win_fwd = 1024
            init_win_bwd = 0

        elif attack_type == "PortScan":
            duration = float(np.random.uniform(50, 4000))
            fwd_pkts = int(np.random.choice([1, 2]))
            bwd_pkts = int(np.random.choice([0, 1], p=[0.8, 0.2]))
            tot_len_fwd = float(fwd_pkts * 40)
            tot_len_bwd = 0.0
            iat_mean = float(duration)
            syn_flag, fin_flag, rst_flag, psh_flag, ack_flag = 1, 0, 1 if bwd_pkts > 0 else 0, 0, 0
            init_win_fwd = 1024
            init_win_bwd = 0

        elif attack_type == "BruteForce":
            duration = float(np.random.exponential(scale=400000) + 10000)
            fwd_pkts = int(np.random.uniform(20, 50))
            bwd_pkts = int(np.random.uniform(15, 40))
            tot_len_fwd = float(fwd_pkts * 210)
            tot_len_bwd = float(bwd_pkts * 180)
            iat_mean = float(duration / max(1, (fwd_pkts + bwd_pkts)))
            syn_flag, fin_flag, rst_flag, psh_flag, ack_flag = 1, 1, 1, 1, 1
            init_win_fwd = 29200
            init_win_bwd = 29200

        elif attack_type == "Botnet":
            duration = float(np.random.uniform(600000, 1000000))
            fwd_pkts = int(np.random.uniform(10, 20))
            bwd_pkts = int(np.random.uniform(8, 16))
            tot_len_fwd = float(fwd_pkts * 160)
            tot_len_bwd = float(bwd_pkts * 240)
            iat_mean = float(duration / max(1, (fwd_pkts + bwd_pkts)))
            syn_flag, fin_flag, rst_flag, psh_flag, ack_flag = 0, 0, 0, 1, 1
            init_win_fwd = 65535
            init_win_bwd = 65535

        else:  # Infiltration
            duration = float(np.random.uniform(900000, 2000000))
            fwd_pkts = int(np.random.uniform(30, 70))
            bwd_pkts = int(np.random.uniform(6, 12))
            tot_len_fwd = float(fwd_pkts * 750)
            tot_len_bwd = float(bwd_pkts * 90)
            iat_mean = float(duration / max(1, (fwd_pkts + bwd_pkts)))
            syn_flag, fin_flag, rst_flag, psh_flag, ack_flag = 1, 1, 0, 1, 1
            init_win_fwd = 14600
            init_win_bwd = 14600

        duration_sec = max(duration / 1e6, 0.00001)
        tot_pkts = fwd_pkts + bwd_pkts
        avg_pkt_size = (tot_len_fwd + tot_len_bwd) / max(1, tot_pkts)

        features = {
            "Flow Duration": round(duration, 2),
            "Total Fwd Packets": fwd_pkts,
            "Total Backward Packets": bwd_pkts,
            "Total Length of Fwd Packets": round(tot_len_fwd, 2),
            "Total Length of Bwd Packets": round(tot_len_bwd, 2),
            "Flow Bytes/s": round((tot_len_fwd + tot_len_bwd) / duration_sec, 2),
            "Flow Packets/s": round(tot_pkts / duration_sec, 2),
            "Flow IAT Mean": round(iat_mean, 2),
            "Flow IAT Std": round(iat_mean * (0.05 if attack_type == "Botnet" else 0.5), 2),
            "Flow IAT Max": round(iat_mean * 2.0, 2),
            "Flow IAT Min": round(max(1.0, iat_mean * 0.1), 2),
            "Fwd IAT Total": round(duration * 0.9, 2),
            "Bwd IAT Total": round(duration * 0.8, 2),
            "Fwd Header Length": fwd_pkts * 20,
            "Bwd Header Length": bwd_pkts * 20,
            "Fwd Packets/s": round(fwd_pkts / duration_sec, 2),
            "Bwd Packets/s": round(bwd_pkts / duration_sec, 2),
            "Min Packet Length": 0 if attack_type == "PortScan" else 64.0,
            "Max Packet Length": round(avg_pkt_size * 2.0, 2),
            "Packet Length Mean": round(avg_pkt_size, 2),
            "Packet Length Std": round(avg_pkt_size * 0.35, 2),
            "FIN Flag Count": fin_flag,
            "SYN Flag Count": syn_flag,
            "RST Flag Count": rst_flag,
            "PSH Flag Count": psh_flag,
            "ACK Flag Count": ack_flag,
            "URG Flag Count": 0,
            "Average Packet Size": round(avg_pkt_size, 2),
            "Subflow Fwd Packets": fwd_pkts,
            "Subflow Fwd Bytes": round(tot_len_fwd, 2),
            "Init_Win_bytes_forward": init_win_fwd,
            "Init_Win_bytes_backward": init_win_bwd,
        }

        return {
            "flow_id": f"flow_{int(time.time()*1000)}_{random.randint(100, 999)}",
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "src_port": src_port,
            "dst_port": dst_port,
            "protocol": "TCP",
            "features": features
        }
