"""
scripts/visualize_architecture.py
Generates 6 publication-quality, 300 DPI architecture and workflow figures:
1. docs/figures/1_end_to_end_pipeline.png
2. docs/figures/2_thermal_detection_pipeline.png
3. docs/figures/3_timeseries_forecasting_pipeline.png
4. docs/figures/4_mtkan_architecture.png
5. docs/figures/5_edge_to_station_architecture.png
6. docs/figures/6_model_comparison.png

Rules:
- High contrast, elegant color scheme.
- No overlapping text.
- Verified components strictly aligned with code and checkpoints.
"""

import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Common styling helpers
FONT_FAMILY = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["axes.edgecolor"] = "#CBD5E1"
plt.rcParams["axes.linewidth"] = 0.8

def draw_rounded_box(ax, x, y, w, h, title, subtitle="", color="#FFFFFF", border="#334155", title_color="#0F172A", sub_color="#475569", title_size=10, sub_size=8, pad=0.08):
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad={pad},rounding_size=0.12",
        facecolor=color, edgecolor=border, linewidth=1.4, zorder=2
    )
    ax.add_patch(rect)
    if subtitle:
        ax.text(x + w / 2, y + h * 0.68, title, fontsize=title_size, fontweight="bold", ha="center", va="center", color=title_color, family=FONT_FAMILY, zorder=3)
        ax.text(x + w / 2, y + h * 0.32, subtitle, fontsize=sub_size, ha="center", va="center", color=sub_color, multialignment="center", family=FONT_FAMILY, zorder=3)
    else:
        ax.text(x + w / 2, y + h * 0.5, title, fontsize=title_size, fontweight="bold", ha="center", va="center", color=title_color, family=FONT_FAMILY, zorder=3)

def draw_arrow(ax, x1, y1, x2, y2, label="", color="#475569", lw=1.5, label_pos=0.5, label_offset=0.22):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(facecolor=color, edgecolor=color, width=lw, headwidth=6, headlength=7, shrink=0.05),
        zorder=4
    )
    if label:
        lx = x1 + (x2 - x1) * label_pos
        ly = y1 + (y2 - y1) * label_pos + label_offset
        ax.text(lx, ly, label, fontsize=7.5, fontweight="bold", ha="center", va="center", color="#1E293B",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="#FFFFFF", edgecolor="#CBD5E1", alpha=0.95), zorder=5)


# ==============================================================================
# Figure 1: End-to-End Pipeline
# ==============================================================================
def generate_fig1():
    fig, ax = plt.subplots(figsize=(13, 8), dpi=300)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8)
    ax.axis("off")

    ax.text(6.5, 7.6, "1. END-TO-END THERMAL & VISUAL MONITORING PIPELINE", fontsize=14, fontweight="bold", ha="center", color="#0F172A")
    ax.text(6.5, 7.25, "Hikvision Bi-Spectrum Sensor -> NVIDIA Jetson Edge Node -> Master Station Central Backend", fontsize=8.5, ha="center", color="#64748B")

    # Sensor
    draw_rounded_box(ax, 0.6, 5.0, 3.2, 1.6, "Hikvision Bi-Spectrum Camera", "IP: 192.168.10.152\nOptical RTSP: CH 102 (H.264)\nThermal ISAPI: CH 2 (P2P Multipart)", color="#E0F2FE", border="#0284C7")

    # Edge Node Container
    edge_bg = patches.FancyBboxPatch((4.3, 0.8), 4.8, 6.0, boxstyle="round,pad=0.15,rounding_size=0.15", facecolor="#F8FAFC", edgecolor="#94A3B8", linewidth=1.5, linestyle="--")
    ax.add_patch(edge_bg)
    ax.text(6.7, 6.5, "NVIDIA Jetson Edge Node (AI-Thermal-detect)", fontsize=10.5, fontweight="bold", ha="center", color="#0369A1")

    # Inside Edge Node
    draw_rounded_box(ax, 4.6, 4.9, 4.2, 1.2, "Headless Daemon Orchestrator", "main_all.py | Signal handling\nProcess supervisor & subprocess pipe relay", color="#FFFFFF", border="#64748B")
    draw_rounded_box(ax, 4.6, 3.2, 4.2, 1.3, "Thermal PPE/Uniform Detection", "yolo_detect.py | TensorRT FP16\nInput: [1, 3, 640, 640] -> Output: [1, 300, 6]\nThreshold: 0.55 | 60s Alert Cooldown", color="#FEF3C7", border="#D97706")
    draw_rounded_box(ax, 4.6, 1.2, 4.2, 1.6, "Thermal Time-Series Service", "FastAPI :8080 | ISAPI Matrix Extract\nServing Model: Autoregressive Linear Regression (Lags=5)\nExperimental Model: MTKAN + STL (Keras 3)\nHorizon: 5 min ahead", color="#DCFCE7", border="#16A34A")

    # Station Node
    draw_rounded_box(ax, 9.6, 3.2, 2.8, 2.5, "Master Station (StationOS)", "C# ASP.NET Core .NET 8 Backend\nSignalR Realtime WebSockets\nReact 18 + Electron Dashboard\nSnap7 PLC S7 Ingestion", color="#EDE9FE", border="#7C3AED")

    # Arrows
    draw_arrow(ax, 3.8, 6.0, 4.6, 5.5, label="Dual Streams")
    draw_arrow(ax, 6.7, 4.9, 6.7, 4.5)
    draw_arrow(ax, 6.7, 3.2, 6.7, 2.8)
    draw_arrow(ax, 8.8, 3.85, 9.6, 4.2, label="POST /api/person-detection")
    draw_arrow(ax, 8.8, 2.0, 9.6, 3.6, label="POST /api/prediction")

    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "1_end_to_end_pipeline.png", dpi=300)
    plt.close(fig)
    print("Generated 1_end_to_end_pipeline.png")


# ==============================================================================
# Figure 2: Thermal Detection Pipeline
# ==============================================================================
def generate_fig2():
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.5)
    ax.axis("off")

    ax.text(6.0, 7.1, "2. EDGE PPE / UNIFORM DETECTION PIPELINE (YOLOv8n TENSORRT)", fontsize=13, fontweight="bold", ha="center", color="#0F172A")
    ax.text(6.0, 6.75, "RTSP Ingestion -> Bilinear Resize -> TensorRT FP16 Engine -> Geometric Filter & Cooldown -> REST Alert", fontsize=8.5, ha="center", color="#64748B")

    draw_rounded_box(ax, 0.5, 4.8, 2.4, 1.4, "RTSP Video Stream", "IP: 192.168.10.152\nSub-stream: 640x360 H.264\nTransport: TCP / No-buffer", color="#E0F2FE", border="#0284C7")
    draw_rounded_box(ax, 3.4, 4.8, 2.5, 1.4, "Preprocessing", "cv2.resize((640, 640))\nBGR to RGB | Transpose (3, H, W)\nNormalize float32 / 255.0", color="#F1F5F9", border="#64748B")
    draw_rounded_box(ax, 6.4, 4.8, 2.7, 1.4, "TensorRT FP16 Engine", "yolov8n.engine / best.onnx\nInput: [1, 3, 640, 640]\nOutput: [1, 300, 6] End2End NMS\n(x1, y1, x2, y2, score, class 0)", color="#FEF3C7", border="#D97706")
    draw_rounded_box(ax, 9.6, 4.8, 2.0, 1.4, "Detection Parsing", "Score >= 0.55\nTarget Class: uniform (0)\nScale back to (w0, h0)", color="#F1F5F9", border="#64748B")

    draw_rounded_box(ax, 4.0, 1.5, 3.8, 2.0, "Heuristic Geometric Validator", "Filter False Positives:\n• Area >= 800 px (or 4000 in api_send)\n• Width >= 20 px, Height >= 40 px\n• Aspect Ratio: 0.20 <= W/H <= 1.20", color="#FEE2E2", border="#EF4444")
    draw_rounded_box(ax, 8.5, 1.5, 3.0, 2.0, "Alert Dispatcher & Cooldown", "Cooldown Window: 60s\nPayload: JSON metadata + Boxes\nTarget: StationOS API\nPOST /api/person-detection", color="#EDE9FE", border="#7C3AED")

    draw_arrow(ax, 2.9, 5.5, 3.4, 5.5)
    draw_arrow(ax, 5.9, 5.5, 6.4, 5.5)
    draw_arrow(ax, 9.1, 5.5, 9.6, 5.5)
    draw_arrow(ax, 10.6, 4.8, 6.0, 3.5, label="Candidate Boxes")
    draw_arrow(ax, 7.8, 2.5, 8.5, 2.5, label="Valid Detection")

    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "2_thermal_detection_pipeline.png", dpi=300)
    plt.close(fig)
    print("Generated 2_thermal_detection_pipeline.png")


# ==============================================================================
# Figure 3: Timeseries Forecasting Pipeline
# ==============================================================================
def generate_fig3():
    fig, ax = plt.subplots(figsize=(13, 8), dpi=300)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8)
    ax.axis("off")

    ax.text(6.5, 7.6, "3. MULTI-TARGET TEMPERATURE FORECASTING PIPELINE", fontsize=14, fontweight="bold", ha="center", color="#0F172A")
    ax.text(6.5, 7.25, "Radiometric P2P Extraction -> Dynamic Buffer -> Multi-Target Regression & MTKAN Evaluation", fontsize=8.5, ha="center", color="#64748B")

    draw_rounded_box(ax, 0.5, 4.8, 2.6, 1.8, "Hikvision ISAPI P2P", "HTTP Digest GET\n/ISAPI/Thermal/.../jpegPic\nWithAppendData\nMultipart boundary split", color="#E0F2FE", border="#0284C7")
    draw_rounded_box(ax, 3.6, 4.8, 2.7, 1.8, "Radiometric Extraction", "raw_data byte stream\nnp.frombuffer(p2pData, float32)\nReshape: (288, 384) matrix\nTrue Celsius reading", color="#F1F5F9", border="#64748B")
    draw_rounded_box(ax, 6.8, 4.8, 2.7, 1.8, "Target Sampling", "thermal_points.json\nMap Points P1-P9 & Zones V1-V2\nNormalized coords (x, y) -> (mx, my)\n5-minute cycle polling", color="#FEF3C7", border="#D97706")
    draw_rounded_box(ax, 10.0, 4.8, 2.5, 1.8, "Buffer & Storage", "live_thermal_history.csv\nSchema self-rotation\nDynamic target expansion\nMissing data interpolation", color="#F1F5F9", border="#64748B")

    # Serving Model Box
    draw_rounded_box(ax, 1.5, 1.0, 4.6, 2.6, "Production Serving: Autoregressive Linear Regression", "Artifact: linear_reg.pkl\nAlgorithm: Multi-target Ordinary Least Squares\nInput: 5 consecutive lag values (window_size=5)\nOutput: Future temperature (horizon = 5 min ahead)\nRetraining: Background thread every 2 days if data >= min_len", color="#DCFCE7", border="#16A34A")

    # Experimental Model Box
    draw_rounded_box(ax, 7.0, 1.0, 4.8, 2.6, "Experimental Benchmark: MTKAN + STL Decomposition", "Artifact: mtkan_model.keras | Framework: Keras 3\nSTL Feature Engine: 24 features (Trend, Seasonal, Resid)\nInput Shape: [None, 5, 24] -> Output Shape: [None, 6]\nReported Test Performance (6 targets):\nMAE: 0.38 - 0.56 C | R2: 0.920 - 0.979", color="#F3E8FF", border="#9333EA")

    draw_arrow(ax, 3.1, 5.7, 3.6, 5.7)
    draw_arrow(ax, 6.3, 5.7, 6.8, 5.7)
    draw_arrow(ax, 9.5, 5.7, 10.0, 5.7)
    draw_arrow(ax, 11.2, 4.8, 3.8, 3.6, label="Serving Lags")
    draw_arrow(ax, 11.2, 4.8, 9.4, 3.6, label="Benchmark Data")

    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "3_timeseries_forecasting_pipeline.png", dpi=300)
    plt.close(fig)
    print("Generated 3_timeseries_forecasting_pipeline.png")


# ==============================================================================
# Figure 4: MTKAN Architecture
# ==============================================================================
def generate_fig4():
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.5)
    ax.axis("off")

    ax.text(6.0, 7.1, "4. MULTIVARIATE TEMPORAL KOLMOGOROV-ARNOLD NETWORK (MTKAN)", fontsize=13, fontweight="bold", ha="center", color="#0F172A")
    ax.text(6.0, 6.75, "Detailed Architectural Graph of Experimental mtkan_model.keras (Keras 3.14)", fontsize=8.5, ha="center", color="#64748B")

    layers = [
        ("InputLayer", "Shape: [None, 5, 24]\n5 time-steps x 24 STL features", "#F1F5F9", "#64748B"),
        ("TKAN Layer 1", "Units: 64 | return_sequences=True\nactivation='tanh' | recurrent='sigmoid'\nKAN Sub-network Spline Activations", "#EDE9FE", "#7C3AED"),
        ("Dropout Layer", "Rate: 0.10 | Regularization", "#F1F5F9", "#94A3B8"),
        ("TKAN Layer 2", "Units: 32 | return_sequences=False\nTemporal Summarization Feature Vector", "#EDE9FE", "#7C3AED"),
        ("Dense Hidden", "Units: 32 | activation='relu'\nFully Connected Representation", "#FEF3C7", "#D97706"),
        ("Dropout Layer", "Rate: 0.10 | Regularization", "#F1F5F9", "#94A3B8"),
        ("Dense Output", "Units: 6 | activation='linear'\n[ID_1_t5, ID_2_t5, ..., ID_6_t5]", "#DCFCE7", "#16A34A")
    ]

    x_start = 0.6
    w_box = 1.3
    gap = 0.35

    for i, (l_name, l_desc, bg_col, bdr_col) in enumerate(layers):
        cx = x_start + i * (w_box + gap)
        draw_rounded_box(ax, cx, 2.2, w_box, 3.2, l_name, l_desc, color=bg_col, border=bdr_col, title_size=9, sub_size=7.5)
        if i < len(layers) - 1:
            draw_arrow(ax, cx + w_box, 3.8, cx + w_box + gap, 3.8)

    # Annotation box
    draw_rounded_box(ax, 2.0, 0.5, 8.0, 1.2, "Mathematical Foundation: Kolmogorov-Arnold Representation Theorem", "Replaces fixed linear matrix weights with learnable 1D B-spline activation functions on edges.\nDesigned for non-linear, multi-scale industrial temperature trend capture with robust resistance to gradient collapse.", color="#FFFFFF", border="#CBD5E1", title_size=8.5, sub_size=7.5)

    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "4_mtkan_architecture.png", dpi=300)
    plt.close(fig)
    print("Generated 4_mtkan_architecture.png")


# ==============================================================================
# Figure 5: Edge to Station Architecture
# ==============================================================================
def generate_fig5():
    fig, ax = plt.subplots(figsize=(13, 8), dpi=300)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8)
    ax.axis("off")

    ax.text(6.5, 7.6, "5. EDGE-TO-STATION HARDWARE & COMMUNICATION TOPOLOGY", fontsize=14, fontweight="bold", ha="center", color="#0F172A")
    ax.text(6.5, 7.25, "Physical Deployment, Network Boundary, and REST / SignalR Protocol Contracts", fontsize=8.5, ha="center", color="#64748B")

    # Edge Container
    rect_edge = patches.FancyBboxPatch((0.6, 0.8), 5.4, 6.0, boxstyle="round,pad=0.15,rounding_size=0.15", facecolor="#F8FAFC", edgecolor="#0284C7", linewidth=1.5)
    ax.add_patch(rect_edge)
    ax.text(3.3, 6.5, "EDGE COMPUTING NODE (NVIDIA Jetson)", fontsize=11, fontweight="bold", ha="center", color="#0369A1")

    draw_rounded_box(ax, 1.0, 4.6, 4.6, 1.5, "Camera Acquisition & ISAPI Client", "Get-Thermal-Jetson-nano & thermal_sender.py\nHTTP Digest Auth | Multipart P2P Binary Stream\n384x288 Radiometric Matrix Parsing", color="#E0F2FE", border="#0284C7")
    draw_rounded_box(ax, 1.0, 2.8, 4.6, 1.5, "YOLOv8n TensorRT Detector", "yolo_detect.py | Headless Daemon\nRTSP H.264 Ingestion | TensorRT FP16 Inference\nEvent-triggered MP4 recording & Alert dispatch", color="#FEF3C7", border="#D97706")
    draw_rounded_box(ax, 1.0, 1.0, 4.6, 1.5, "FastAPI Thermal Forecasting Service", "timeseries_service/thermal_receiver.py :8080\nLive CSV History Ingestion | 5-min Horizon Prediction\nAutonomous Background Model Retraining", color="#DCFCE7", border="#16A34A")

    # Station Container
    rect_station = patches.FancyBboxPatch((7.0, 0.8), 5.4, 6.0, boxstyle="round,pad=0.15,rounding_size=0.15", facecolor="#F8FAFC", edgecolor="#7C3AED", linewidth=1.5)
    ax.add_patch(rect_station)
    ax.text(9.7, 6.5, "CENTRAL ORCHESTRATION (Master-Station)", fontsize=11, fontweight="bold", ha="center", color="#5B21B6")

    draw_rounded_box(ax, 7.4, 4.6, 4.6, 1.5, "Backend Core (StationOS.Api)", "C# ASP.NET Core .NET 8 | Port: 5000\nEntity Framework Core (SQLite / PostgreSQL)\nSnap7 PLC Siemens S7 Ingestion Worker\nRule Evaluation Worker (Threshold alerts)", color="#EDE9FE", border="#7C3AED")
    draw_rounded_box(ax, 7.4, 2.8, 4.6, 1.5, "AI Engine Service (ai_engine)", "Python FastAPI | Port: 8000 | go2rtc RTSP Relay\nLine Crossing Detection (YOLOv8n Object Tracking)\nPartial Discharge Acoustic Analyzer (HSV Hotspot)", color="#EDE9FE", border="#7C3AED")
    draw_rounded_box(ax, 7.4, 1.0, 4.6, 1.5, "Monitoring Desktop Frontend", "React 18 + Vite + TailwindCSS + Electron Client\nDynamic SVG Single Line Diagram (SLD)\nSub-second WebRTC Camera View & Alert History", color="#FCE7F3", border="#DB2777")

    # Communication Arrows
    draw_arrow(ax, 5.6, 3.55, 7.4, 5.35, label="POST /api/person-detection")
    draw_arrow(ax, 5.6, 1.75, 7.4, 4.85, label="POST /api/prediction")
    draw_arrow(ax, 7.4, 4.4, 5.6, 1.3, label="POST /config/thermal (Sync)")

    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "5_edge_to_station_architecture.png", dpi=300)
    plt.close(fig)
    print("Generated 5_edge_to_station_architecture.png")


# ==============================================================================
# Figure 6: Model Comparison
# ==============================================================================
def generate_fig6():
    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    ax.axis("off")

    ax.text(0.5, 0.95, "6. SYSTEM MODEL AUDIT & SPECIFICATION COMPARISON", fontsize=13, fontweight="bold", ha="left", color="#0F172A", transform=ax.transAxes)
    ax.text(0.5, 0.91, "Direct Artifact Verification Matrix: Vision, Regression, and Neural Network Modules", fontsize=8.5, ha="left", color="#64748B", transform=ax.transAxes)

    table_data = [
        ["Model Property", "Uniform/PPE Detector", "Live Thermal Forecaster", "Experimental MTKAN", "Line Crossing Detector"],
        ["Artifact File", "models/best.onnx\nmodels/yolov8n.engine", "timeseries_service/model/\nlinear_reg.pkl", "timeseries_service/model/\nmtkan_model.keras", "Master-Station/ai_engine/\nyolov8n.pt"],
        ["Framework", "TensorRT / PyTorch (Ultralytics)", "Scikit-Learn LinearRegression", "TensorFlow / Keras 3.14 (TKAN)", "Ultralytics PyTorch"],
        ["Runtime Status", "Production Serving", "Production Serving", "Experimental / Benchmark", "Production Serving"],
        ["Input Tensor / Dtype", "[1, 3, 640, 640] float32 RGB", "[5] float32 (Lags t-4 to t)", "[None, 5, 24] float32 (STL)", "[1, 3, H, W] BGR (RTSP)"],
        ["Output Dimension", "[1, 300, 6] (End2End NMS)", "1 float scalar per target", "[None, 6] (6 target predictions)", "Bounding Boxes + Track IDs"],
        ["Target Semantics", "uniform (Class ID: 0)", "Celsius (+5 min forecast)", "Celsius (+5 min, 6 points)", "person (0), car (2)"],
        ["Reported Metrics", "Not committed in repo", "Extrapolation baseline", "MAE: 0.38-0.56 C | R2: 0.92-0.98", "Pretrained COCO Weights"],
        ["Hardware Role", "Jetson Orin Nano TensorRT", "Jetson Orin Nano CPU/RAM", "Jetson / Server Fallback", "Station Server CPU / CUDA"]
    ]

    col_widths = [0.22, 0.20, 0.20, 0.20, 0.18]
    table = ax.table(cellText=table_data, colWidths=col_widths, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(7.8)
    table.scale(1.0, 2.2)

    # Style table headers and cells
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#CBD5E1")
        if row == 0:
            cell.set_facecolor("#1E293B")
            cell.get_text().set_color("#FFFFFF")
            cell.get_text().set_weight("bold")
        elif col == 0:
            cell.set_facecolor("#F8FAFC")
            cell.get_text().set_weight("bold")
            cell.get_text().set_color("#0F172A")
        elif row % 2 == 1:
            cell.set_facecolor("#FFFFFF")
        else:
            cell.set_facecolor("#F1F5F9")

    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "6_model_comparison.png", dpi=300)
    plt.close(fig)
    print("Generated 6_model_comparison.png")

if __name__ == "__main__":
    generate_fig1()
    generate_fig2()
    generate_fig3()
    generate_fig4()
    generate_fig5()
    generate_fig6()
    print("All 6 architecture diagrams generated successfully at 300 DPI.")
