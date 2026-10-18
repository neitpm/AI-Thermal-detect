---
license: mit
tags:
- edge-ai
- thermal-imaging
- yolo
- yolov8
- tensorrt
- time-series
- forecasting
- ppe-detection
pipeline_tag: object-detection
---

# Thermal AI Models: Detection & Temperature Forecasting

This repository hosts official production checkpoints and research models for the **AI-Thermal-detect** edge monitoring system.

## Repository Contents

```text
models/
  yolo_uniform.onnx              # Ultralytics YOLOv8n exported to ONNX FP32 [1, 5, 8400]
  yolo_uniform.pt                # PyTorch checkpoint (names: {0: 'uniform'})
  yolov8n.engine                 # TensorRT FP16 compiled engine
forecasting/
  linear_reg.pkl                 # Multi-target Autoregressive Linear Regression (11 estimators, serving)
  scaler_X.pkl                   # Feature MinMaxScaler (55 inputs)
  scaler_y.pkl                   # Target MinMaxScaler (11 outputs)
  mtkan_model.keras              # Experimental Temporal KAN model (Keras 3)
  mtkan_weights.weights.h5       # MTKAN model weights
  config.json                    # Channel definitions, window size (5), horizon (5)
  metrics_test.csv               # Empirical test split metrics for forecasting
scripts/
  infer_yolo.py                  # ONNX & PyTorch YOLO inference script
  forecast_temperature.py        # Linear Regression & MTKAN inference script
metadata/
  model_manifest.json            # Exact input/output contracts, shapes, byte sizes
  checksums.sha256               # Cryptographic SHA-256 digests
```

---

## 1. Object Detection: Thermal Uniform / PPE Monitoring

* **Architecture**: Ultralytics YOLOv8n
* **Class Names**: `{0: "uniform"}` (Extracted directly from checkpoint metadata)
* **Input Tensor**: `images` shape `[1, 3, 640, 640]`, dtype `float32`, normalized to range `[0.0, 1.0]`
* **Output Tensor**: `output0` shape `[1, 5, 8400]`, where each candidate contains `[cx, cy, w, h, uniform_conf]`
* **Hardware Target**: 
  * CPU/Server: `yolo_uniform.onnx` via ONNX Runtime
  * NVIDIA Jetson Edge: `yolov8n.engine` compiled via TensorRT FP16

> **Validation Note**: No external mAP claim is asserted beyond the explicit checkpoint metadata and verifiable tensor contracts.

---

## 2. Multi-Target Temperature Forecasting

### Production Serving Model: Autoregressive Linear Regression
* **File**: `forecasting/linear_reg.pkl`
* **Type**: 11 independent linear regression estimators trained on autoregressive historical features.
* **Input Window**: 5 minutes historical window across 11 measurement points ($5 \times 11 = 55$ features), scaled via `scaler_X.pkl`.
* **Forecast Horizon**: 5 minutes ahead for all 11 monitored targets, inverse-scaled via `scaler_y.pkl`.
* **Execution Latency**: sub-millisecond CPU forward pass ($< 0.2\text{ ms}$).

### Experimental Research Model: MTKAN (Temporal Kolmogorov-Arnold Network)
* **File**: `forecasting/mtkan_model.keras`
* **Architecture**: 2x TKAN recurrent layers + Dense layers (implemented in Keras 3.14).
* **Role**: Research benchmark exploring non-linear spline activation forecasting on STL-decomposed thermal series.

### Empirical Test Set Metrics (from `metrics_test.csv`)
Evaluation metrics across 6 designated test channels:

| Target ID | MAE (°C) | RMSE (°C) | R² Score |
| :--- | :---: | :---: | :---: |
| **ID_1** | 0.478 | 0.588 | 0.969 |
| **ID_2** | 0.400 | 0.502 | 0.979 |
| **ID_3** | 0.508 | 0.649 | 0.955 |
| **ID_4** | 0.560 | 0.668 | 0.920 |
| **ID_5** | 0.435 | 0.554 | 0.970 |
| **ID_6** | 0.377 | 0.471 | 0.962 |

---

## 3. How to Download and Verify

```python
from huggingface_hub import snapshot_download

# Download all verified artifacts into a local directory
local_dir = snapshot_download(
    repo_id="neitpm/ai-thermal-detect-models",
    local_dir="models_from_hub",
    repo_type="model"
)
```

Run inference with the included scripts:

```bash
# YOLO Detection via ONNX Runtime
python scripts/infer_yolo.py --model models/yolo_uniform.onnx

# 5-Minute Ahead Temperature Forecasting
python scripts/forecast_temperature.py --dir forecasting/ --engine linear
```
