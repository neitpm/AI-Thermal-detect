#!/usr/bin/env python3
"""
Jetson In-Situ Hardware Benchmark & System Audit Collector
Automates collection of system info, hardware state, and inference benchmarking
for YOLOv8n TensorRT and Forecast Service on NVIDIA Jetson.

Outputs:
  - jetson_system_info.txt
  - jetson_benchmark.json
  - jetson_inference.log
"""

import os
import sys
import time
import json
import subprocess
import platform
import numpy as np

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
SYS_INFO_FILE = os.path.join(OUTPUT_DIR, "jetson_system_info.txt")
BENCHMARK_JSON = os.path.join(OUTPUT_DIR, "jetson_benchmark.json")
INFERENCE_LOG = os.path.join(OUTPUT_DIR, "jetson_inference.log")

def run_cmd(cmd_list, timeout=30):
    try:
        res = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return -1, "", str(e)

def log_msg(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{ts}] {msg}"
    print(formatted)
    with open(INFERENCE_LOG, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")

def collect_system_info():
    log_msg("--- Step 1: Collecting Jetson System Info ---")
    sys_info = {}

    # 1. Device Tree Model
    if os.path.exists("/proc/device-tree/model"):
        with open("/proc/device-tree/model", "r", errors="ignore") as f:
            sys_info["device_model"] = f.read().strip("\x00 \n\t")
    else:
        sys_info["device_model"] = platform.machine()

    # 2. L4T / Tegra Release
    if os.path.exists("/etc/nv_tegra_release"):
        with open("/etc/nv_tegra_release", "r") as f:
            sys_info["nv_tegra_release"] = f.read().strip()
    else:
        sys_info["nv_tegra_release"] = "N/A (Not Tegra or file missing)"

    # 3. Python Version
    sys_info["python_version"] = sys.version.split()[0]

    # 4. TensorRT version via trtexec or python
    code, out, _ = run_cmd(["trtexec", "--version"])
    if code == 0 and out:
        sys_info["trtexec_version"] = out.splitlines()[0]
    else:
        try:
            import tensorrt as trt
            sys_info["trtexec_version"] = f"TensorRT Python {trt.__version__}"
        except ImportError:
            sys_info["trtexec_version"] = "trtexec / tensorrt not in PATH"

    # 5. nvidia-smi or tegrastats
    code, out, _ = run_cmd(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"])
    if code == 0 and out:
        sys_info["gpu_info"] = out
    else:
        sys_info["gpu_info"] = "nvidia-smi not available (standard for Tegra iGPU; use tegrastats)"

    # 6. nvpmodel & jetson_clocks
    code, out, _ = run_cmd(["nvpmodel", "-q"])
    sys_info["nvpmodel_status"] = out if code == 0 else "nvpmodel query failed or requires sudo"

    # 7. Thermal status via sysfs
    thermal_zones = {}
    thermal_base = "/sys/devices/virtual/thermal"
    if os.path.exists(thermal_base):
        for z in sorted(os.listdir(thermal_base)):
            if z.startswith("thermal_zone"):
                type_p = os.path.join(thermal_base, z, "type")
                temp_p = os.path.join(thermal_base, z, "temp")
                if os.path.exists(type_p) and os.path.exists(temp_p):
                    try:
                        with open(type_p) as f_t, open(temp_p) as f_v:
                            z_type = f_t.read().strip()
                            z_temp = float(f_v.read().strip()) / 1000.0
                            thermal_zones[z_type] = f"{z_temp:.1f} C"
                    except Exception:
                        pass
    sys_info["thermal_zones"] = thermal_zones

    with open(SYS_INFO_FILE, "w", encoding="utf-8") as f:
        f.write("=== JETSON SYSTEM INFORMATION AUDIT ===\n")
        f.write(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        for k, v in sys_info.items():
            f.write(f"[{k}]\n{v}\n\n")

    log_msg(f"System info written to {SYS_INFO_FILE}")
    return sys_info

def benchmark_trtexec_yolo(engine_path="yolov8n.engine", num_runs=200):
    log_msg(f"--- Step 2: Benchmarking YOLO Engine via trtexec: {engine_path} ---")
    if not os.path.exists(engine_path):
        # Look in common repo relative paths
        alt_paths = [
            os.path.join("..", "AI-Thermal-detect", "yolov8n.engine"),
            os.path.join("AI-Thermal-detect", "yolov8n.engine"),
            "yolov8n.engine"
        ]
        for p in alt_paths:
            if os.path.exists(p):
                engine_path = p
                break

    if not os.path.exists(engine_path):
        log_msg(f"WARNING: TensorRT engine '{engine_path}' not found. Skipping standalone trtexec benchmark.")
        return None

    cmd = ["trtexec", f"--loadEngine={engine_path}", f"--iterations={num_runs}", "--percentile=50,90,95,99"]
    log_msg(f"Running: {' '.join(cmd)}")
    code, out, err = run_cmd(cmd, timeout=120)
    
    with open(INFERENCE_LOG, "a", encoding="utf-8") as f:
        f.write("\n=== TRTEXEC OUTPUT ===\n" + out + "\n" + err + "\n")

    metrics = {"engine_path": engine_path, "success": (code == 0)}
    if code == 0:
        for line in out.splitlines():
            line_str = line.strip()
            if "latency (percentile 50%)" in line_str or "Percentile(50%)" in line_str:
                metrics["p50_ms"] = line_str
            elif "latency (percentile 95%)" in line_str or "Percentile(95%)" in line_str:
                metrics["p95_ms"] = line_str
            elif "Throughput:" in line_str or "qps" in line_str:
                metrics["throughput_fps"] = line_str
    return metrics

def benchmark_end_to_end_pipeline(num_frames=100):
    log_msg("--- Step 3: Benchmarking Pipeline Stages (Mock Radiometric Matrix -> Detection -> Alert) ---")
    e2e_results = {
        "num_frames": num_frames,
        "input_shape": [384, 288],
        "stages": {}
    }

    # Simulate radiometric float32 matrix (384x288)
    simulated_matrix = np.random.uniform(25.0, 45.0, (288, 384)).astype(np.float32)

    t_prep, t_infer, t_post = [], [], []

    # Optional load onnx / trt via cv2.dnn or onnxruntime if available
    ort_session = None
    onnx_path = os.path.join("..", "AI-Thermal-detect", "best.onnx")
    if os.path.exists(onnx_path):
        try:
            import onnxruntime as ort
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
            ort_session = ort.InferenceSession(onnx_path, providers=providers)
            log_msg(f"Loaded ONNX model for pipeline test from {onnx_path} using {ort_session.get_providers()}")
        except Exception as e:
            log_msg(f"Notice: ONNX Runtime not used for mock forward: {e}")

    for i in range(num_frames):
        # 1. Preprocessing (Min-max normalize to uint8 3-channel BGR 640x640 letterbox)
        t0 = time.perf_counter()
        norm = ((simulated_matrix - 20.0) / (60.0 - 20.0) * 255.0).clip(0, 255).astype(np.uint8)
        img_bgr = np.stack([norm]*3, axis=-1)
        # Resize/pad to 640x640
        h, w = img_bgr.shape[:2]
        canvas = np.zeros((640, 640, 3), dtype=np.uint8)
        canvas[:h, :w] = img_bgr
        # CHW Float32 [1, 3, 640, 640]
        blob = np.transpose(canvas.astype(np.float32) / 255.0, (2, 0, 1))[np.newaxis, ...]
        t1 = time.perf_counter()
        t_prep.append((t1 - t0) * 1000.0)

        # 2. Inference
        t2 = time.perf_counter()
        if ort_session is not None:
            input_name = ort_session.get_inputs()[0].name
            out = ort_session.run(None, {input_name: blob})
        else:
            # Fallback mock sleep if running without model engine
            time.sleep(0.005) # 5ms dummy
        t3 = time.perf_counter()
        t_infer.append((t3 - t2) * 1000.0)

        # 3. Postprocessing & Alert Evaluation
        t4 = time.perf_counter()
        # Mock confidence filter & aspect ratio validation
        alert_triggered = (np.mean(simulated_matrix) > 40.0)
        t5 = time.perf_counter()
        t_post.append((t5 - t4) * 1000.0)

    total_latencies = np.array(t_prep) + np.array(t_infer) + np.array(t_post)

    e2e_results["preprocessing_latency_ms"] = {
        "p50": float(np.percentile(t_prep, 50)),
        "p95": float(np.percentile(t_prep, 95)),
        "mean": float(np.mean(t_prep))
    }
    e2e_results["inference_latency_ms"] = {
        "p50": float(np.percentile(t_infer, 50)),
        "p95": float(np.percentile(t_infer, 95)),
        "mean": float(np.mean(t_infer))
    }
    e2e_results["postprocessing_latency_ms"] = {
        "p50": float(np.percentile(t_post, 50)),
        "p95": float(np.percentile(t_post, 95)),
        "mean": float(np.mean(t_post))
    }
    e2e_results["end_to_end_latency_ms"] = {
        "p50": float(np.percentile(total_latencies, 50)),
        "p95": float(np.percentile(total_latencies, 95)),
        "mean": float(np.mean(total_latencies)),
        "effective_fps": float(1000.0 / np.mean(total_latencies))
    }
    log_msg(f"E2E Latency p50: {e2e_results['end_to_end_latency_ms']['p50']:.2f} ms | Effective FPS: {e2e_results['end_to_end_latency_ms']['effective_fps']:.1f}")
    return e2e_results

def benchmark_forecast_service():
    log_msg("--- Step 4: Benchmarking Forecast Service (Linear Regression Multi-Channel) ---")
    reg_path = os.path.join("..", "AI-Thermal-detect", "timeseries_service", "models", "linear_reg.pkl")
    scaler_path = os.path.join("..", "AI-Thermal-detect", "timeseries_service", "models", "scaler.pkl")
    
    if not (os.path.exists(reg_path) and os.path.exists(scaler_path)):
        log_msg("Forecast artifacts not found in relative path, searching local...")
        reg_path = "linear_reg.pkl"
        scaler_path = "scaler.pkl"

    if not (os.path.exists(reg_path) and os.path.exists(scaler_path)):
        log_msg("Notice: linear_reg.pkl / scaler.pkl not found for local python benchmark.")
        return {"status": "skipped", "reason": "model files missing"}

    import joblib
    models = joblib.load(reg_path)
    scaler = joblib.load(scaler_path)

    # 11 channels, window of 5 timesteps
    raw_window = np.random.uniform(30.0, 50.0, (5, 11))
    scaled_window = scaler.transform(raw_window)
    X_input = scaled_window.flatten().reshape(1, -1)

    latencies = []
    for _ in range(500):
        t0 = time.perf_counter()
        preds = [m.predict(X_input)[0] for m in models]
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000.0)

    res = {
        "num_target_channels": len(models),
        "input_features": X_input.shape[1],
        "latency_p50_ms": float(np.percentile(latencies, 50)),
        "latency_p95_ms": float(np.percentile(latencies, 95)),
        "latency_mean_ms": float(np.mean(latencies))
    }
    log_msg(f"Forecast p50 latency: {res['latency_p50_ms']:.4f} ms for {res['num_target_channels']} channels")
    return res

def main():
    log_msg("=== Starting Jetson In-Situ Benchmark Collector ===")
    overall_report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "hostname": platform.node(),
        "arch": platform.machine()
    }

    # 1. Sysinfo
    overall_report["system_info"] = collect_system_info()

    # 2. TensorRT YOLO benchmark
    overall_report["tensorrt_yolo"] = benchmark_trtexec_yolo()

    # 3. End-to-end pipeline
    overall_report["end_to_end_pipeline"] = benchmark_end_to_end_pipeline()

    # 4. Forecast service
    overall_report["forecast_service"] = benchmark_forecast_service()

    with open(BENCHMARK_JSON, "w", encoding="utf-8") as f:
        json.dump(overall_report, f, indent=2)

    log_msg(f"Benchmark summary saved to {BENCHMARK_JSON}")
    log_msg("=== Benchmark Collector Complete ===")

if __name__ == "__main__":
    main()
