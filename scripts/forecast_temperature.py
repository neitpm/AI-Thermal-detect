#!/usr/bin/env python3
"""
Multi-Target Thermal Temperature Forecasting Inference Script
Loads multi-target autoregressive Linear Regression estimators (serving)
or MTKAN architecture (experimental).
"""

import os
import sys
import json
import argparse
import joblib
import numpy as np

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def run_forecast_linear_regression(model_dir):
    reg_path = os.path.join(model_dir, "linear_reg.pkl")
    scaler_x_path = os.path.join(model_dir, "scaler_X.pkl")
    scaler_y_path = os.path.join(model_dir, "scaler_y.pkl")
    cfg_path = os.path.join(model_dir, "config.json")

    print(f"Loading Linear Regression serving model from: {reg_path}")
    models = joblib.load(reg_path)
    scaler_x = joblib.load(scaler_x_path)
    scaler_y = joblib.load(scaler_y_path)
    
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    targets = cfg.get("targets", [])
    window_size = cfg.get("window_size", 5)
    horizon = cfg.get("horizon", 5)

    print(f"Config: {len(targets)} targets, window_size={window_size}, horizon={horizon} mins ahead.")
    
    # In production, each target model is an Autoregressive LinearRegression estimator
    # that accepts the 5 most recent lags of THAT target channel.
    predictions = {}
    print("\n--- 5-Minute Ahead Forecast Results ---")
    if isinstance(models, dict):
        for target_name, model in models.items():
            # Dummy 5 lag temperatures for this channel
            dummy_lags = np.random.uniform(32.0, 48.0, 5)
            pred = float(model.predict([dummy_lags])[0])
            predictions[target_name] = pred
            print(f"Target [{target_name}]: {pred:.2f} °C (input lags: {np.round(dummy_lags, 1)})")
    else:
        # Fallback if list
        for i, model in enumerate(models):
            dummy_lags = np.random.uniform(32.0, 48.0, 5)
            pred = float(model.predict([dummy_lags])[0])
            predictions[f"channel_{i}"] = pred
            print(f"Target [channel_{i}]: {pred:.2f} °C")

    return predictions

def run_forecast_mtkan(model_dir):
    keras_path = os.path.join(model_dir, "mtkan_model.keras")
    print(f"Checking experimental MTKAN model at: {keras_path}")
    if not os.path.exists(keras_path):
        print("MTKAN model file not found.")
        return None
    try:
        import tensorflow as tf
        print(f"TensorFlow {tf.__version__} detected. Attempting to load MTKAN...")
        model = tf.keras.models.load_model(keras_path, compile=False)
        model.summary()
        return model
    except Exception as e:
        print(f"MTKAN requires custom KAN / TKAN layers or compatible Keras runtime: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=str, default="timeseries_service/model", help="Path to forecasting models dir")
    parser.add_argument("--engine", type=str, default="linear", choices=["linear", "mtkan"], help="Model type to infer")
    args = parser.parse_args()

    if args.engine == "linear":
        run_forecast_linear_regression(args.dir)
    elif args.engine == "mtkan":
        run_forecast_mtkan(args.dir)
