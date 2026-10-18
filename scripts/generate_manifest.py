#!/usr/bin/env python3
"""
Model Manifest Generator for AI-Thermal-detect
Generates metadata/model_manifest.json and metadata/checksums.sha256
with full contracts, shapes, byte sizes, and SHA-256 hashes.
"""

import os
import json
import hashlib

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def generate_manifest():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    metadata_dir = os.path.join(base_dir, "metadata")
    os.makedirs(metadata_dir, exist_ok=True)

    artifacts = [
        {
            "artifact": "models/yolo_uniform.onnx",
            "local_path": "models/best.onnx",
            "type": "detection",
            "architecture": "Ultralytics YOLOv8n (FP32 ONNX export)",
            "input_contract": "images: [1, 3, 640, 640] float32, normalized to [0, 1]",
            "output_contract": "output0: [1, 5, 8400] float32 (cx, cy, w, h, uniform_conf)",
            "classes": {"0": "uniform"}
        },
        {
            "artifact": "models/yolo_uniform.pt",
            "local_path": "models/best.pt",
            "type": "detection",
            "architecture": "Ultralytics YOLOv8n (PyTorch Checkpoint)",
            "input_contract": "images: [1, 3, 640, 640] float32",
            "output_contract": "Ultralytics Results objects / tensor [1, 5, 8400]",
            "classes": {"0": "uniform"}
        },
        {
            "artifact": "models/yolov8n.engine",
            "local_path": "models/yolov8n.engine",
            "type": "detection",
            "architecture": "TensorRT FP16 Engine compiled from best.onnx",
            "input_contract": "images: [1, 3, 640, 640] float32/fp16",
            "output_contract": "output0: [1, 5, 8400] fp16",
            "classes": {"0": "uniform"}
        },
        {
            "artifact": "forecasting/linear_reg.pkl",
            "local_path": "timeseries_service/model/linear_reg.pkl",
            "type": "forecasting_serving",
            "architecture": "Multi-target Autoregressive Linear Regression (11 independent estimators)",
            "input_contract": "Per-target autoregressive lag vector: [1, 5] (5 most recent historical temperatures per channel)",
            "output_contract": "Predicted temperature 5 minutes ahead: float (evaluated across 11 targets in parallel)",
            "horizon_minutes": 5,
            "window_size": 5
        },
        {
            "artifact": "forecasting/scaler_X.pkl",
            "local_path": "timeseries_service/model/scaler_X.pkl",
            "type": "preprocessor",
            "architecture": "StandardScaler for 24 multi-channel time-series features"
        },
        {
            "artifact": "forecasting/scaler_y.pkl",
            "local_path": "timeseries_service/model/scaler_y.pkl",
            "type": "preprocessor",
            "architecture": "StandardScaler for 6 target temperature points"
        },
        {
            "artifact": "forecasting/mtkan_model.keras",
            "local_path": "timeseries_service/model/mtkan_model.keras",
            "type": "forecasting_experimental",
            "architecture": "Temporal Kolmogorov-Arnold Network (Keras 3.14: 2x TKAN + Dense)",
            "input_contract": "Time-series sequence [batch, window_size, 44] (including STL trend/seasonal/resid)",
            "output_contract": "Predicted temperatures [batch, 11]"
        },
        {
            "artifact": "forecasting/mtkan_weights.weights.h5",
            "local_path": "timeseries_service/model/mtkan_weights.weights.h5",
            "type": "forecasting_experimental_weights",
            "architecture": "H5 weights for mtkan_model.keras"
        },
        {
            "artifact": "forecasting/config.json",
            "local_path": "timeseries_service/model/config.json",
            "type": "configuration",
            "architecture": "Channel targets definition, window size (5), horizon (5), STL feature mapping"
        },
        {
            "artifact": "forecasting/metrics_test.csv",
            "local_path": "timeseries_service/model/metrics_test.csv",
            "type": "benchmark_metrics",
            "architecture": "Test set evaluation results (MAE 0.38-0.56 C, R2 >= 0.92 across 6 test targets)"
        }
    ]

    manifest = []
    checksum_lines = []

    for item in artifacts:
        full_p = os.path.join(base_dir, item["local_path"])
        if os.path.exists(full_p):
            size_bytes = os.path.getsize(full_p)
            digest = sha256_file(full_p)
            entry = dict(item)
            entry["size_bytes"] = size_bytes
            entry["sha256"] = digest
            manifest.append(entry)
            checksum_lines.append(f"{digest}  {item['artifact']}")
            print(f"Verified: {item['artifact']} ({size_bytes:,} bytes) - SHA256: {digest[:12]}...")
        else:
            print(f"Skipped missing: {item['local_path']}")

    manifest_path = os.path.join(metadata_dir, "model_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    checksums_path = os.path.join(metadata_dir, "checksums.sha256")
    with open(checksums_path, "w", encoding="utf-8") as f:
        f.write("\n".join(checksum_lines) + "\n")

    print(f"\nSaved manifest to {manifest_path}")
    print(f"Saved checksums to {checksums_path}")

if __name__ == "__main__":
    generate_manifest()
