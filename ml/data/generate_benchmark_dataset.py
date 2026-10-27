"""
AI-NIDS: Benchmark Dataset Generator
Generates a statistically realistic, CIC-IDS2017 compatible network-flow dataset.
Simulates normal benign traffic and multiple cyberattack categories with authentic
packet-level and flow-level statistical signatures.
"""

import os
import numpy as np
import pandas as pd

def generate_network_dataset(num_samples: int = 15000, seed: int = 42, output_path: str = None) -> pd.DataFrame:
    """
    Generate synthetic yet statistically grounded network flows compatible with CIC-IDS2017 schema.
    Includes normal traffic and cyberattacks:
      - BENIGN (Normal Web, HTTPS, SSH, DNS)
      - DoS-Hulk (High volume HTTP flood, short IAT, high packet rate)
      - DDoS (Volumetric distributed flood, high SYN, tiny packet size)
      - PortScan (Probing many ports, 1-2 packets/flow, zero payload, high SYN/RST)
      - BruteForce (Repeated auth attempts, medium packets, elevated RST)
      - Botnet (Periodic beaconing, very low IAT variance, specific payload size)
      - Infiltration (Low-and-slow probing, unusual flag combinations)
    """
    np.random.seed(seed)

    # Class distributions (~55% BENIGN, ~45% Attacks across categories)
    classes = [
        ("BENIGN", int(num_samples * 0.52)),
        ("DoS-Hulk", int(num_samples * 0.14)),
        ("DDoS", int(num_samples * 0.12)),
        ("PortScan", int(num_samples * 0.10)),
        ("BruteForce", int(num_samples * 0.05)),
        ("Botnet", int(num_samples * 0.04)),
        ("Infiltration", int(num_samples * 0.03)),
    ]

    records = []

    for label, count in classes:
        for _ in range(count):
            if label == "BENIGN":
                # Standard web, API, DNS, and file transfer traffic
                duration = np.random.exponential(scale=350000) + 1000  # microseconds
                total_fwd_pkts = max(1, int(np.random.negative_binomial(5, 0.3)))
                total_bwd_pkts = max(1, int(np.random.negative_binomial(6, 0.25)))
                tot_len_fwd = total_fwd_pkts * np.random.normal(540, 150)
                tot_len_bwd = total_bwd_pkts * np.random.normal(920, 250)
                flow_iat_mean = duration / max(1, (total_fwd_pkts + total_bwd_pkts - 1))
                flow_iat_std = flow_iat_mean * np.random.uniform(0.4, 1.2)
                flow_iat_max = flow_iat_mean * np.random.uniform(1.5, 3.5)
                flow_iat_min = np.random.uniform(10, 500)
                syn_flag = 1 if np.random.rand() < 0.2 else 0
                fin_flag = 1 if np.random.rand() < 0.15 else 0
                rst_flag = 0 if np.random.rand() < 0.95 else 1
                psh_flag = 1 if np.random.rand() < 0.45 else 0
                ack_flag = 1
                fwd_header_len = total_fwd_pkts * 20
                bwd_header_len = total_bwd_pkts * 20
                init_win_fwd = int(np.random.choice([8192, 29200, 65535]))
                init_win_bwd = int(np.random.choice([8192, 29200, 65535]))

            elif label == "DoS-Hulk":
                # Massive volume HTTP flood, short duration, high forward packet count
                duration = np.random.exponential(scale=180000) + 500
                total_fwd_pkts = int(np.random.uniform(30, 250))
                total_bwd_pkts = int(np.random.uniform(0, 10))  # Server overwhelmed, low responses
                tot_len_fwd = total_fwd_pkts * np.random.normal(320, 40)
                tot_len_bwd = total_bwd_pkts * np.random.normal(120, 30)
                flow_iat_mean = max(5, duration / max(1, (total_fwd_pkts + total_bwd_pkts)))
                flow_iat_std = flow_iat_mean * np.random.uniform(0.1, 0.4)  # High regularity
                flow_iat_max = flow_iat_mean * 2.0
                flow_iat_min = np.random.uniform(1, 20)
                syn_flag = 1 if np.random.rand() < 0.6 else 0
                fin_flag = 0
                rst_flag = 1 if np.random.rand() < 0.3 else 0
                psh_flag = 1 if np.random.rand() < 0.75 else 0
                ack_flag = 1
                fwd_header_len = total_fwd_pkts * 20
                bwd_header_len = total_bwd_pkts * 20
                init_win_fwd = 8192
                init_win_bwd = 0 if total_bwd_pkts == 0 else 8192

            elif label == "DDoS":
                # Distributed volumetric packet surge, very high packet rates, short bursts
                duration = np.random.exponential(scale=60000) + 100
                total_fwd_pkts = int(np.random.uniform(50, 400))
                total_bwd_pkts = int(np.random.uniform(0, 5))
                tot_len_fwd = total_fwd_pkts * np.random.normal(140, 25)
                tot_len_bwd = total_bwd_pkts * 64
                flow_iat_mean = max(1, duration / max(1, (total_fwd_pkts + total_bwd_pkts)))
                flow_iat_std = flow_iat_mean * 0.2
                flow_iat_max = flow_iat_mean * 1.5
                flow_iat_min = 1.0
                syn_flag = 1 if np.random.rand() < 0.85 else 0
                fin_flag = 0
                rst_flag = 0
                psh_flag = 0 if np.random.rand() < 0.8 else 1
                ack_flag = 1 if np.random.rand() < 0.5 else 0
                fwd_header_len = total_fwd_pkts * 20
                bwd_header_len = total_bwd_pkts * 20
                init_win_fwd = 1024
                init_win_bwd = 0

            elif label == "PortScan":
                # Rapid probing across IP/ports: 1-2 packets per flow, minimal or zero payload
                duration = np.random.uniform(50, 5000)
                total_fwd_pkts = int(np.random.choice([1, 2, 3], p=[0.7, 0.2, 0.1]))
                total_bwd_pkts = int(np.random.choice([0, 1], p=[0.8, 0.2]))
                tot_len_fwd = total_fwd_pkts * int(np.random.choice([0, 40, 60]))
                tot_len_bwd = total_bwd_pkts * int(np.random.choice([0, 40]))
                flow_iat_mean = duration / max(1, total_fwd_pkts)
                flow_iat_std = 0.0
                flow_iat_max = duration
                flow_iat_min = duration
                syn_flag = 1  # Classic SYN scan
                fin_flag = 1 if np.random.rand() < 0.1 else 0  # FIN scan variant
                rst_flag = 1 if total_bwd_pkts > 0 else 0     # Target port closed
                psh_flag = 0
                ack_flag = 0 if np.random.rand() < 0.7 else 1
                fwd_header_len = total_fwd_pkts * 20
                bwd_header_len = total_bwd_pkts * 20
                init_win_fwd = 1024
                init_win_bwd = 0

            elif label == "BruteForce":
                # SSH/FTP repetitive auth attempts: frequent RSTs, medium packet count, specific payload sizes
                duration = np.random.exponential(scale=450000) + 10000
                total_fwd_pkts = int(np.random.uniform(15, 60))
                total_bwd_pkts = int(np.random.uniform(12, 50))
                tot_len_fwd = total_fwd_pkts * np.random.normal(210, 30)
                tot_len_bwd = total_bwd_pkts * np.random.normal(180, 25)
                flow_iat_mean = duration / max(1, (total_fwd_pkts + total_bwd_pkts))
                flow_iat_std = flow_iat_mean * 0.5
                flow_iat_max = flow_iat_mean * 2.2
                flow_iat_min = np.random.uniform(50, 300)
                syn_flag = 1 if np.random.rand() < 0.3 else 0
                fin_flag = 1 if np.random.rand() < 0.4 else 0
                rst_flag = 1 if np.random.rand() < 0.65 else 0  # High RST from failed auth
                psh_flag = 1 if np.random.rand() < 0.7 else 0
                ack_flag = 1
                fwd_header_len = total_fwd_pkts * 20
                bwd_header_len = total_bwd_pkts * 20
                init_win_fwd = 29200
                init_win_bwd = 29200

            elif label == "Botnet":
                # C2 Beaconing: strict periodic intervals (very low IAT std), small fixed command exchanges
                duration = np.random.uniform(500000, 1200000)
                total_fwd_pkts = int(np.random.uniform(8, 25))
                total_bwd_pkts = int(np.random.uniform(6, 20))
                tot_len_fwd = total_fwd_pkts * np.random.normal(160, 15)
                tot_len_bwd = total_bwd_pkts * np.random.normal(240, 20)
                flow_iat_mean = duration / max(1, (total_fwd_pkts + total_bwd_pkts))
                flow_iat_std = flow_iat_mean * 0.05  # Highly deterministic beaconing
                flow_iat_max = flow_iat_mean * 1.15
                flow_iat_min = flow_iat_mean * 0.85
                syn_flag = 0
                fin_flag = 0
                rst_flag = 0
                psh_flag = 1 if np.random.rand() < 0.6 else 0
                ack_flag = 1
                fwd_header_len = total_fwd_pkts * 20
                bwd_header_len = total_bwd_pkts * 20
                init_win_fwd = 65535
                init_win_bwd = 65535

            elif label == "Infiltration":
                # Stealthy data exfiltration / reconnaissance: slow, asymmetric payload ratio
                duration = np.random.uniform(800000, 2500000)
                total_fwd_pkts = int(np.random.uniform(20, 80))
                total_bwd_pkts = int(np.random.uniform(5, 15))
                tot_len_fwd = total_fwd_pkts * np.random.normal(780, 180)  # Heavy upload
                tot_len_bwd = total_bwd_pkts * np.random.normal(90, 20)
                flow_iat_mean = duration / max(1, (total_fwd_pkts + total_bwd_pkts))
                flow_iat_std = flow_iat_mean * 0.9
                flow_iat_max = flow_iat_mean * 4.0
                flow_iat_min = 100.0
                syn_flag = 1 if np.random.rand() < 0.2 else 0
                fin_flag = 1 if np.random.rand() < 0.3 else 0
                rst_flag = 0
                psh_flag = 1 if np.random.rand() < 0.8 else 0
                ack_flag = 1
                fwd_header_len = total_fwd_pkts * 20
                bwd_header_len = total_bwd_pkts * 20
                init_win_fwd = 14600
                init_win_bwd = 14600

            # Derived rate calculations
            duration_sec = max(duration / 1e6, 0.000001)
            flow_bytes_s = (tot_len_fwd + tot_len_bwd) / duration_sec
            flow_pkts_s = (total_fwd_pkts + total_bwd_pkts) / duration_sec
            fwd_pkts_s = total_fwd_pkts / duration_sec
            bwd_pkts_s = total_bwd_pkts / duration_sec

            tot_pkts = total_fwd_pkts + total_bwd_pkts
            avg_pkt_size = (tot_len_fwd + tot_len_bwd) / max(1, tot_pkts)
            pkt_len_mean = avg_pkt_size
            pkt_len_min = 0 if label == "PortScan" else max(0, int(avg_pkt_size * 0.2))
            pkt_len_max = max(pkt_len_min + 1, int(avg_pkt_size * 2.1))
            pkt_len_std = (pkt_len_max - pkt_len_min) / 3.5

            record = {
                "Flow Duration": max(1.0, float(round(duration, 2))),
                "Total Fwd Packets": int(total_fwd_pkts),
                "Total Backward Packets": int(total_bwd_pkts),
                "Total Length of Fwd Packets": float(round(tot_len_fwd, 2)),
                "Total Length of Bwd Packets": float(round(tot_len_bwd, 2)),
                "Flow Bytes/s": float(round(flow_bytes_s, 2)),
                "Flow Packets/s": float(round(flow_pkts_s, 2)),
                "Flow IAT Mean": float(round(flow_iat_mean, 2)),
                "Flow IAT Std": float(round(flow_iat_std, 2)),
                "Flow IAT Max": float(round(flow_iat_max, 2)),
                "Flow IAT Min": float(round(flow_iat_min, 2)),
                "Fwd IAT Total": float(round(duration * 0.9, 2)),
                "Bwd IAT Total": float(round(duration * (0.8 if total_bwd_pkts > 0 else 0.0), 2)),
                "Fwd Header Length": int(fwd_header_len),
                "Bwd Header Length": int(bwd_header_len),
                "Fwd Packets/s": float(round(fwd_pkts_s, 2)),
                "Bwd Packets/s": float(round(bwd_pkts_s, 2)),
                "Min Packet Length": float(round(pkt_len_min, 2)),
                "Max Packet Length": float(round(pkt_len_max, 2)),
                "Packet Length Mean": float(round(pkt_len_mean, 2)),
                "Packet Length Std": float(round(pkt_len_std, 2)),
                "FIN Flag Count": int(fin_flag),
                "SYN Flag Count": int(syn_flag),
                "RST Flag Count": int(rst_flag),
                "PSH Flag Count": int(psh_flag),
                "ACK Flag Count": int(ack_flag),
                "URG Flag Count": 0,
                "Average Packet Size": float(round(avg_pkt_size, 2)),
                "Subflow Fwd Packets": int(total_fwd_pkts),
                "Subflow Fwd Bytes": float(round(tot_len_fwd, 2)),
                "Init_Win_bytes_forward": int(init_win_fwd),
                "Init_Win_bytes_backward": int(init_win_bwd),
                "Label": label,
            }
            records.append(record)

    df = pd.DataFrame(records)

    # Introduce realistic edge-case testing: rare missing and infinite values
    # To test robust preprocessing handling without breaking statistical integrity
    inject_indices = np.random.choice(df.index, size=int(num_samples * 0.005), replace=False)
    for idx in inject_indices[: len(inject_indices) // 2]:
        df.loc[idx, "Flow Bytes/s"] = np.nan
    for idx in inject_indices[len(inject_indices) // 2 :]:
        df.loc[idx, "Flow Packets/s"] = np.inf

    # Shuffle records
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"[+] Dataset successfully generated at: {output_path}")
        print(f"[+] Total samples: {len(df)}")
        print("[+] Class distribution:")
        print(df["Label"].value_counts())

    return df

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_csv = os.path.join(current_dir, "sample_network_flows.csv")
    generate_network_dataset(num_samples=16000, output_path=target_csv)
