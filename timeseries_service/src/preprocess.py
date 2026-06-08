import json
import joblib
import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL

import os

# Default values
config = {}
FEATURE_COLS = []
WINDOW_SIZE = 5
TARGETS = []
SEASONAL_PERIOD = 60
scaler_X = None

def load_config(camera_id: str = "192_168_10_152"):
    global config, FEATURE_COLS, WINDOW_SIZE, TARGETS, SEASONAL_PERIOD, scaler_X
    config_path = f"model/{camera_id}_config.json"
    if not os.path.exists(config_path):
        config_path = "model/config.json"
    
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            FEATURE_COLS = config.get("feature_cols", [])
            WINDOW_SIZE = config.get("window_size", 5)
            TARGETS = config.get("targets", [])
            SEASONAL_PERIOD = config.get("seasonal_period", 60)
        except Exception as e:
            print(f"[PREPROCESS-ERROR] Lỗi load config: {e}")
            
    scaler_path = f"model/{camera_id}_scaler_X.pkl"
    if not os.path.exists(scaler_path):
        scaler_path = "model/scaler_X.pkl"
    if os.path.exists(scaler_path):
        try:
            scaler_X = joblib.load(scaler_path)
        except Exception:
            pass

# Khởi tạo mặc định
load_config()


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    rename_map = {}
    for c in df.columns:
        if c.startswith("ID:"):
            rename_map[c] = c.replace(":", "_")
    return df.rename(columns=rename_map)


def preprocess_raw_input(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)

    required = ["Timestamp"] + TARGETS
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Thiếu cột raw input: {missing}")

    df = df.copy()
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    df = df.dropna(subset=["Timestamp"]).copy()
    df = df.sort_values("Timestamp").reset_index(drop=True)
    df = df.drop_duplicates(subset=["Timestamp"], keep="last").reset_index(drop=True)

    for col in TARGETS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df.loc[(df[col] < 0) | (df[col] > 100), col] = np.nan

    df = df.set_index("Timestamp")
    df[TARGETS] = df[TARGETS].interpolate(method="time", limit_direction="both")
    df = df.resample("1min").mean().interpolate(method="time", limit_direction="both").reset_index()

    return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for col in TARGETS:
        stl = STL(df[col], period=SEASONAL_PERIOD, robust=True)
        res = stl.fit()
        df[f"{col}_trend"] = res.trend
        df[f"{col}_seasonal"] = res.seasonal
        df[f"{col}_residual"] = res.resid

    return df


def prepare_feature_df(data_df: pd.DataFrame) -> pd.DataFrame:
    # nếu đã đủ feature thì dùng luôn
    if all(col in data_df.columns for col in FEATURE_COLS):
        return data_df.copy()

    # nếu là raw CSV thì tự build feature
    df = preprocess_raw_input(data_df)
    df = build_features(df)
    return df


def create_input_last_window(data_df: pd.DataFrame):
    df = prepare_feature_df(data_df)

    missing_cols = [col for col in FEATURE_COLS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Thiếu các cột đầu vào sau feature engineering: {missing_cols}")

    if len(df) < WINDOW_SIZE:
        raise ValueError(
            f"Cần ít nhất {WINDOW_SIZE} dòng dữ liệu, hiện tại chỉ có {len(df)} dòng."
        )

    X_raw = df[FEATURE_COLS].values
    X_scaled = scaler_X.transform(X_raw)

    X_window = X_scaled[-WINDOW_SIZE:]
    X_window = X_window.reshape(1, WINDOW_SIZE, -1)

    return X_window, df


def create_input_all_windows(data_df: pd.DataFrame):
    df = prepare_feature_df(data_df)

    missing_cols = [col for col in FEATURE_COLS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Thiếu các cột đầu vào sau feature engineering: {missing_cols}")

    if len(df) < WINDOW_SIZE:
        raise ValueError(
            f"Cần ít nhất {WINDOW_SIZE} dòng dữ liệu, hiện tại chỉ có {len(df)} dòng."
        )

    X_raw = df[FEATURE_COLS].values
    X_scaled = scaler_X.transform(X_raw)

    windows = []
    end_indices = []

    for end_idx in range(WINDOW_SIZE, len(X_scaled) + 1):
        start_idx = end_idx - WINDOW_SIZE
        X_window = X_scaled[start_idx:end_idx]
        windows.append(X_window)
        end_indices.append(end_idx - 1)

    X_all = np.array(windows)
    return X_all, end_indices, df
