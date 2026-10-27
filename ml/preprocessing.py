"""
AI-NIDS: Data Preprocessing Pipeline
Handles:
- Missing value imputation
- Infinite value replacement (capping / median substitution)
- Duplicate record removal
- Feature selection & non-informative identifier removal
- Feature scaling (RobustScaler or StandardScaler)
- Label encoding with human-readable class mappings
- Zero data leakage (fit exclusively on train split)
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Any, Optional
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer

# Features expected in the CIC-IDS2017 compliant schema
FEATURE_COLUMNS = [
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Total Length of Fwd Packets",
    "Total Length of Bwd Packets",
    "Flow Bytes/s",
    "Flow Packets/s",
    "Flow IAT Mean",
    "Flow IAT Std",
    "Flow IAT Max",
    "Flow IAT Min",
    "Fwd IAT Total",
    "Bwd IAT Total",
    "Fwd Header Length",
    "Bwd Header Length",
    "Fwd Packets/s",
    "Bwd Packets/s",
    "Min Packet Length",
    "Max Packet Length",
    "Packet Length Mean",
    "Packet Length Std",
    "FIN Flag Count",
    "SYN Flag Count",
    "RST Flag Count",
    "PSH Flag Count",
    "ACK Flag Count",
    "URG Flag Count",
    "Average Packet Size",
    "Subflow Fwd Packets",
    "Subflow Fwd Bytes",
    "Init_Win_bytes_forward",
    "Init_Win_bytes_backward",
]

# Non-informative metadata columns that cause data leakage if used for training
COLUMNS_TO_DROP = [
    "Flow ID", "Source IP", "Src IP", "Source Port",
    "Destination IP", "Dst IP", "Destination Port", "Dst Port",
    "Timestamp", "Date", "Unnamed: 0"
]

class PreprocessingPipeline:
    def __init__(self, feature_columns: Optional[List[str]] = None):
        self.feature_columns = feature_columns or FEATURE_COLUMNS
        self.scaler = StandardScaler()
        self.imputer = SimpleImputer(strategy="median")
        self.label_encoder = LabelEncoder()
        self.feature_medians: Dict[str, float] = {}
        self.label_mapping: Dict[int, str] = {}
        self.is_fitted: bool = False

    def clean_raw_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean raw DataFrame:
        - Strip whitespace from column names
        - Drop non-informative / leakage columns
        - Handle infinite numbers by replacing with NaN
        - Drop duplicates
        """
        df_clean = df.copy()
        # Clean column names
        df_clean.columns = df_clean.columns.str.strip()

        # Drop identifiers that cause data leakage
        drop_cols = [c for c in COLUMNS_TO_DROP if c in df_clean.columns]
        if drop_cols:
            df_clean = df_clean.drop(columns=drop_cols)

        # Drop exact duplicate rows
        initial_count = len(df_clean)
        df_clean = df_clean.drop_duplicates()
        dropped_dupes = initial_count - len(df_clean)
        if dropped_dupes > 0:
            print(f"[*] Removed {dropped_dupes} duplicate flow records.")

        # Replace infinite values with NaN for proper imputation
        for col in df_clean.select_dtypes(include=[np.number]).columns:
            df_clean[col] = df_clean[col].replace([np.inf, -np.inf], np.nan)

        return df_clean

    def fit_transform(
        self,
        df: pd.DataFrame,
        target_col: str = "Label",
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Fit preprocessing pipeline ONLY on the training split to guarantee zero data leakage.
        Returns:
            X_train_scaled, X_test_scaled, y_train, y_test, metadata
        """
        df_clean = self.clean_raw_dataframe(df)

        if target_col not in df_clean.columns:
            raise ValueError(f"Target column '{target_col}' not found in dataframe.")

        # Ensure all required feature columns exist
        available_features = [col for col in self.feature_columns if col in df_clean.columns]
        if len(available_features) < len(self.feature_columns):
            missing = set(self.feature_columns) - set(available_features)
            print(f"[!] Warning: Missing {len(missing)} expected features. Using {len(available_features)} available features.")
        self.feature_columns = available_features

        X = df_clean[self.feature_columns].copy()
        y = df_clean[target_col].astype(str).str.strip()

        # Perform train/test split BEFORE any imputation or scaling to prevent leakage
        X_train_raw, X_test_raw, y_train_raw, y_test_raw = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        # Impute missing values using train medians
        X_train_imputed = self.imputer.fit_transform(X_train_raw)
        X_test_imputed = self.imputer.transform(X_test_raw)

        # Store medians for single-record inference fallback
        for idx, col in enumerate(self.feature_columns):
            self.feature_medians[col] = float(self.imputer.statistics_[idx])

        # Scale features using train distribution parameters
        X_train_scaled = self.scaler.fit_transform(X_train_imputed)
        X_test_scaled = self.scaler.transform(X_test_imputed)

        # Encode labels
        y_train = self.label_encoder.fit_transform(y_train_raw)
        y_test = self.label_encoder.transform(y_test_raw)

        # Map integer encoded labels back to original attack string names
        self.label_mapping = {int(idx): str(label) for idx, label in enumerate(self.label_encoder.classes_)}
        self.is_fitted = True

        # Class imbalance analysis
        class_counts = pd.Series(y_train_raw).value_counts().to_dict()
        total_samples = len(y_train_raw)
        imbalance_summary = {
            label: {
                "count": count,
                "percentage": round((count / total_samples) * 100, 2)
            }
            for label, count in class_counts.items()
        }

        metadata = {
            "num_features": len(self.feature_columns),
            "features": self.feature_columns,
            "classes": self.label_encoder.classes_.tolist(),
            "label_mapping": self.label_mapping,
            "train_samples": len(X_train_scaled),
            "test_samples": len(X_test_scaled),
            "class_imbalance": imbalance_summary,
            "feature_medians": self.feature_medians,
        }

        return X_train_scaled, X_test_scaled, y_train, y_test, metadata

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """
        Transform new unseen flow data using the fitted pipeline.
        Handles missing columns by filling with learned medians.
        """
        if not self.is_fitted:
            raise RuntimeError("Pipeline must be fitted before calling transform.")

        df_input = df.copy()
        df_input.columns = df_input.columns.str.strip()

        # Fill any missing columns with training medians
        for col in self.feature_columns:
            if col not in df_input.columns:
                df_input[col] = self.feature_medians.get(col, 0.0)

        # Clean numericals
        for col in self.feature_columns:
            df_input[col] = pd.to_numeric(df_input[col], errors="coerce")
            df_input[col] = df_input[col].replace([np.inf, -np.inf], np.nan)

        X = df_input[self.feature_columns]
        X_imputed = self.imputer.transform(X)
        X_scaled = self.scaler.transform(X_imputed)
        return X_scaled

    def transform_single_dict(self, record: Dict[str, Any]) -> np.ndarray:
        """Transform a single dictionary of flow features for real-time inference."""
        df = pd.DataFrame([record])
        return self.transform(df)

    def save(self, filepath: str) -> None:
        """Persist fitted pipeline artifacts to disk."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        state = {
            "feature_columns": self.feature_columns,
            "scaler": self.scaler,
            "imputer": self.imputer,
            "label_encoder": self.label_encoder,
            "feature_medians": self.feature_medians,
            "label_mapping": self.label_mapping,
            "is_fitted": self.is_fitted,
        }
        joblib.dump(state, filepath)
        print(f"[+] Pipeline successfully saved to: {filepath}")

    @classmethod
    def load(cls, filepath: str) -> "PreprocessingPipeline":
        """Load fitted pipeline artifacts from disk."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Pipeline file not found: {filepath}")
        state = joblib.load(filepath)
        instance = cls(feature_columns=state["feature_columns"])
        instance.scaler = state["scaler"]
        instance.imputer = state["imputer"]
        instance.label_encoder = state["label_encoder"]
        instance.feature_medians = state["feature_medians"]
        instance.label_mapping = state["label_mapping"]
        instance.is_fitted = state["is_fitted"]
        return instance
