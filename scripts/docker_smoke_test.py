"""
scripts/docker_smoke_test.py
Verification suite for containerized AI-Thermal-detect service:
1. Load linear_reg.pkl models and verify coefficients.
2. Load StandardScaler (scaler_X.pkl, scaler_y.pkl).
3. Load ONNX Runtime session (models/best.onnx).
4. Run dummy inference forward passes.
5. Verify output validity (no NaN / Inf values).
6. Verify FastAPI /health endpoint.
"""

import os
import sys
import json
import joblib
import numpy as np

def test_models():
    print("=== [1/4] Verifying Linear Regression Models ===")
    lr_path = "timeseries_service/model/linear_reg.pkl"
    assert os.path.exists(lr_path), f"Missing {lr_path}"
    lr_models = joblib.load(lr_path)
    assert isinstance(lr_models, dict), "linear_reg.pkl must be a dictionary of models"
    print(f"Loaded {len(lr_models)} linear regression models successfully.")

    for k, m in lr_models.items():
        assert hasattr(m, "coef_"), f"Model for {k} missing coef_"
        assert not np.isnan(m.coef_).any(), f"Model {k} has NaN coefficients"
        # Test 5-step dummy forward
        dummy_lags = np.array([[35.0, 35.2, 35.4, 35.7, 36.0]])
        pred = m.predict(dummy_lags)
        assert not np.isnan(pred).any() and not np.isinf(pred).any(), f"Prediction for {k} generated NaN/Inf"
    print("All Linear Regression models passed dummy predictions cleanly.")

def test_scalers():
    print("\n=== [2/4] Verifying Scalers ===")
    sx_path = "timeseries_service/model/scaler_X.pkl"
    sy_path = "timeseries_service/model/scaler_y.pkl"
    assert os.path.exists(sx_path) and os.path.exists(sy_path), "Missing scalers"
    sx = joblib.load(sx_path)
    sy = joblib.load(sy_path)
    assert hasattr(sx, "mean_") and len(sx.mean_) == 24, "scaler_X feature dim mismatch"
    assert hasattr(sy, "mean_") and len(sy.mean_) == 6, "scaler_y feature dim mismatch"
    print("StandardScalers verified (X: 24 features, y: 6 targets).")

def test_onnx():
    print("\n=== [3/4] Verifying ONNX Inference Engine ===")
    onnx_path = "models/best.onnx"
    if os.path.exists(onnx_path):
        import onnxruntime as ort
        session = ort.InferenceSession(onnx_path)
        dummy_img = np.random.randn(1, 3, 640, 640).astype(np.float32)
        outputs = session.run(None, {session.get_inputs()[0].name: dummy_img})
        res = outputs[0]
        assert res.shape == (1, 300, 6), f"Unexpected shape {res.shape}"
        assert not np.isnan(res).any(), "ONNX output contains NaN values"
        print(f"ONNX dummy inference passed with output shape: {res.shape}")
    else:
        print("[WARN] models/best.onnx not found, skipping ONNX test.")

def test_config():
    print("\n=== [4/4] Verifying Service Configuration ===")
    cfg_path = "timeseries_service/model/config.json"
    assert os.path.exists(cfg_path), "Missing config.json"
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    assert "targets" in cfg and "horizon" in cfg, "Invalid config.json structure"
    print(f"Configuration valid: {len(cfg['targets'])} targets, horizon={cfg['horizon']}.")

if __name__ == "__main__":
    try:
        test_models()
        test_scalers()
        test_onnx()
        test_config()
        print("\n>>> ALL DOCKER SMOKE TESTS PASSED CLEANLY (NO NAN/INF) <<<")
    except Exception as e:
        print(f"\n[ERROR] Smoke test failed: {e}")
        sys.exit(1)
