"""
scripts/visualize_architecture.py
Generates high-resolution 3D volumetric tensor block diagrams for AI-Thermal-detect:
1. docs/figures/1_end_to_end_thermal_pipeline.png
2. docs/figures/2_yolov8n_tensor_rt.png
3. docs/figures/3_thermal_matrix_pipeline.png
4. docs/figures/4_linear_regression_forecaster.png
5. docs/figures/5_mtkan_architecture.png
6. docs/figures/6_model_comparison.png

Canvas: 16x10 inches, 300 DPI.
Isometric 3D volumetric tensor blocks with distinct front, top, and right facets.
"""

from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
import numpy as np

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Color themes: [Front, Top, Right]
THEMES = {
    "camera": ["#0284C7", "#38BDF8", "#0369A1"],      # Cyan / Sky
    "preprocess": ["#475569", "#94A3B8", "#334155"],  # Slate Gray
    "backbone": ["#D97706", "#FBBF24", "#B45309"],    # Amber / Orange
    "fusion": ["#7C3AED", "#A78BFA", "#6D28D9"],      # Purple
    "detector": ["#DC2626", "#F87171", "#B91C1C"],    # Crimson Red
    "forecast": ["#059669", "#34D399", "#047857"],    # Emerald Green
    "backend": ["#4F46E5", "#818CF8", "#3730A3"],     # Indigo
    "ui": ["#DB2777", "#F472B6", "#9D174D"],          # Rose / Pink
    "dark_bg": "#0B1120",
    "card_bg": "#1E293B",
    "card_border": "#334155",
    "text_white": "#F8FAFC",
    "text_muted": "#94A3B8",
    "text_yellow": "#FEF08A"
}

def draw_3d_block(ax, x, y, w, h, depth=0.35, theme="camera", label="", sublabel="", tensor_shape="", desc="", desc_pos="bottom"):
    """
    Draw a volumetric 3D isometric block with distinct front, top, and right facets.
    x, y: bottom-left coordinates of front face
    w, h: width and height of front face
    depth: isometric projection offset
    """
    front_c, top_c, side_c = THEMES[theme]
    dx = depth * 0.7
    dy = depth * 0.7

    # 1. Right Side facet
    side_pts = [
        [x + w, y],
        [x + w + dx, y + dy],
        [x + w + dx, y + h + dy],
        [x + w, y + h]
    ]
    ax.add_patch(Polygon(side_pts, closed=True, facecolor=side_c, edgecolor="#0F172A", lw=1.2, zorder=2))

    # 2. Top facet
    top_pts = [
        [x, y + h],
        [x + dx, y + h + dy],
        [x + w + dx, y + h + dy],
        [x + w, y + h]
    ]
    ax.add_patch(Polygon(top_pts, closed=True, facecolor=top_c, edgecolor="#0F172A", lw=1.2, zorder=2))

    # 3. Front facet
    front_pts = [
        [x, y],
        [x + w, y],
        [x + w, y + h],
        [x, y + h]
    ]
    ax.add_patch(Polygon(front_pts, closed=True, facecolor=front_c, edgecolor="#0F172A", lw=1.2, zorder=3))

    # Typography inside front face
    cx = x + w / 2.0
    cy = y + h / 2.0

    if label:
        ax.text(cx, cy + h * 0.22, label, ha="center", va="center", color=THEMES["text_white"],
                fontsize=9.5, fontweight="bold", zorder=4)
    if sublabel:
        ax.text(cx, cy + h * 0.02, sublabel, ha="center", va="center", color="#F1F5F9",
                fontsize=8.0, zorder=4)
    if tensor_shape:
        ax.text(cx, cy - h * 0.22, tensor_shape, ha="center", va="center", color=THEMES["text_yellow"],
                fontsize=8.0, fontweight="bold", family="monospace", zorder=4)

    if desc:
        if desc_pos == "bottom":
            ax.text(cx + dx/2, y - 0.35, desc, ha="center", va="top", color=THEMES["text_muted"],
                    fontsize=7.8, zorder=4)
        else:
            ax.text(cx + dx/2, y + h + dy + 0.35, desc, ha="center", va="bottom", color=THEMES["text_muted"],
                    fontsize=7.8, zorder=4)

def draw_3d_arrow(ax, x1, y1, x2, y2, color="#38BDF8", text="", text_offset_y=0.25):
    """Draw a clean directional connection arrow with optional text badge."""
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(facecolor=color, edgecolor=color, width=1.8, headwidth=6, headlength=7, shrink=0.06),
        zorder=5
    )
    if text:
        mid_x = (x1 + x2) / 2.0
        mid_y = (y1 + y2) / 2.0 + text_offset_y
        ax.text(mid_x, mid_y, text, ha="center", va="center", color="#FFFFFF",
                fontsize=7.5, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.2", facecolor=THEMES["card_bg"], edgecolor=THEMES["card_border"], alpha=0.95),
                zorder=6)


# ==============================================================================
# Figure 1: 3D End-to-End Thermal Pipeline
# ==============================================================================
def generate_fig1():
    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
    fig.patch.set_facecolor(THEMES["dark_bg"])
    ax.set_facecolor(THEMES["dark_bg"])
    ax.set_xlim(-0.5, 16.5)
    ax.set_ylim(-0.5, 9.5)
    ax.axis("off")

    ax.text(8.0, 8.8, "End-to-End Edge AI Thermal Monitoring Pipeline", ha="center", va="center",
            color=THEMES["text_white"], fontsize=18, fontweight="bold")
    ax.text(8.0, 8.35, "Hikvision Bi-Spectrum Sensor -> Jetson Edge Node (YOLOv8n TRT + Forecasting) -> Master Station SCADA",
            ha="center", va="center", color=THEMES["text_muted"], fontsize=10.5)

    # 1. Camera Node
    draw_3d_block(ax, 0.4, 4.2, 2.2, 2.6, depth=0.4, theme="camera",
                  label="Bi-Spectrum Cam", sublabel="Hikvision 152", tensor_shape="Dual Sensor",
                  desc="Optical CH102 (H.264)\nThermal CH2 (P2P)")

    # 2. Jetson Ingestion
    draw_3d_block(ax, 3.5, 4.2, 2.3, 2.6, depth=0.4, theme="preprocess",
                  label="Jetson Daemon", sublabel="main_all.py", tensor_shape="Supervisor",
                  desc="Threaded frame queue\nSubprocess pipe relay")

    # 3. Vision Detection Branch (Top)
    draw_3d_block(ax, 6.8, 5.6, 2.5, 2.4, depth=0.4, theme="detector",
                  label="YOLOv8n TRT", sublabel="FP16 Engine", tensor_shape="[1, 300, 6]",
                  desc="640x640 Bilinear RGB\nClass 0: uniform / PPE")

    # 4. Thermal Forecasting Branch (Bottom)
    draw_3d_block(ax, 6.8, 1.8, 2.5, 2.4, depth=0.4, theme="forecast",
                  label="Timeseries Svc", sublabel="FastAPI :8080", tensor_shape="(288, 384) f32",
                  desc="P2P Radiometric Extract\nHistory CSV Buffering")

    # 5. Model Serving Box
    draw_3d_block(ax, 10.3, 1.8, 2.6, 2.4, depth=0.4, theme="forecast",
                  label="Linear Regressor", sublabel="linear_reg.pkl", tensor_shape="Lags=5 -> t+5m",
                  desc="Autoregressive Serving\nMTKAN (Keras 3 Fallback)")

    # 6. Master Station Platform
    draw_3d_block(ax, 13.7, 3.6, 2.4, 2.8, depth=0.4, theme="backend",
                  label="Master Station", sublabel="StationOS .NET 8", tensor_shape="C# API :5000",
                  desc="SignalR Realtime Hub\nSnap7 S7 PLC | React UI")

    # Arrows
    draw_3d_arrow(ax, 2.9, 5.5, 3.5, 5.5, text="RTSP + ISAPI")
    draw_3d_arrow(ax, 6.1, 6.0, 6.8, 6.8, text="Video Frames")
    draw_3d_arrow(ax, 6.1, 5.0, 6.8, 3.0, text="ISAPI P2P")
    draw_3d_arrow(ax, 9.6, 3.0, 10.3, 3.0, text="Lag Window")
    draw_3d_arrow(ax, 9.6, 6.8, 13.7, 5.6, text="POST /api/person-detection")
    draw_3d_arrow(ax, 13.2, 3.0, 13.7, 4.4, text="POST /api/prediction")

    fig.savefig(OUTPUT_DIR / "1_end_to_end_thermal_pipeline.png", dpi=300)
    plt.close(fig)
    print("Generated 1_end_to_end_thermal_pipeline.png")


# ==============================================================================
# Figure 2: YOLOv8n TensorRT FP16 Architecture
# ==============================================================================
def generate_fig2():
    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
    fig.patch.set_facecolor(THEMES["dark_bg"])
    ax.set_facecolor(THEMES["dark_bg"])
    ax.set_xlim(-0.5, 16.5)
    ax.set_ylim(-0.5, 9.5)
    ax.axis("off")

    ax.text(8.0, 8.8, "YOLOv8n TensorRT FP16 Detection Architecture", ha="center", va="center",
            color=THEMES["text_white"], fontsize=18, fontweight="bold")
    ax.text(8.0, 8.35, "RTSP H.264 Ingestion -> Bilinear RGB Normalization -> TensorRT FP16 -> End-to-End NMS -> Cooldown Dispatcher",
            ha="center", va="center", color=THEMES["text_muted"], fontsize=10.5)

    stages = [
        {"x": 0.4, "w": 2.1, "h": 2.8, "theme": "camera", "label": "RTSP Input", "sub": "OpenCV Capture", "shape": "(3, H, W)", "desc": "IP: 192.168.10.152\nSub-stream 102"},
        {"x": 3.1, "w": 2.1, "h": 2.8, "theme": "preprocess", "label": "Bilinear Prep", "sub": "Resize & Norm", "shape": "[1, 3, 640, 640]", "desc": "BGR to RGB / 255.0\nNCHW float32"},
        {"x": 5.8, "w": 2.3, "h": 2.8, "theme": "backbone", "label": "YOLOv8n Core", "sub": "Backbone + PAN", "shape": "CSPDarknet+C2f", "desc": "Multiscale Feature\nPyramid (P3, P4, P5)"},
        {"x": 8.7, "w": 2.2, "h": 2.8, "theme": "detector", "label": "TensorRT FP16", "sub": "Engine Runtime", "shape": "yolov8n.engine", "desc": "CUDA Deserialized\nKernel Optimizations"},
        {"x": 11.5, "w": 2.1, "h": 2.8, "theme": "detector", "label": "End2End NMS", "sub": "Hardware Output", "shape": "[1, 300, 6]", "desc": "x1, y1, x2, y2, score\nClass 0: uniform"},
        {"x": 14.1, "w": 2.1, "h": 2.8, "theme": "backend", "label": "Heuristic Filter", "sub": "Alert Cooldown", "shape": "REST Dispatch", "desc": "Area>=800px, 0.2<=AR<=1.2\n60s Anti-Spam Timer"}
    ]

    for s in stages:
        draw_3d_block(ax, s["x"], 3.2, s["w"], s["h"], depth=0.35, theme=s["theme"],
                      label=s["label"], sublabel=s["sub"], tensor_shape=s["shape"], desc=s["desc"])

    draw_3d_arrow(ax, 2.8, 4.6, 3.1, 4.6)
    draw_3d_arrow(ax, 5.4, 4.6, 5.8, 4.6)
    draw_3d_arrow(ax, 8.3, 4.6, 8.7, 4.6)
    draw_3d_arrow(ax, 11.1, 4.6, 11.5, 4.6)
    draw_3d_arrow(ax, 13.8, 4.6, 14.1, 4.6)

    fig.savefig(OUTPUT_DIR / "2_yolov8n_tensor_rt.png", dpi=300)
    plt.close(fig)
    print("Generated 2_yolov8n_tensor_rt.png")


# ==============================================================================
# Figure 3: Thermal Matrix Pipeline
# ==============================================================================
def generate_fig3():
    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
    fig.patch.set_facecolor(THEMES["dark_bg"])
    ax.set_facecolor(THEMES["dark_bg"])
    ax.set_xlim(-0.5, 16.5)
    ax.set_ylim(-0.5, 9.5)
    ax.axis("off")

    ax.text(8.0, 8.8, "ISAPI P2P Radiometric Temperature Matrix Extraction", ha="center", va="center",
            color=THEMES["text_white"], fontsize=18, fontweight="bold")
    ax.text(8.0, 8.35, "HTTP Digest Protocol -> Multipart Split -> Little-Endian Binary Float32 Decode -> Coordinate Sampling -> History CSV",
            ha="center", va="center", color=THEMES["text_muted"], fontsize=10.5)

    stages = [
        {"x": 0.4, "w": 2.2, "h": 2.8, "theme": "camera", "label": "ISAPI HTTP GET", "sub": "Digest Auth", "shape": "Channel 2", "desc": "jpegPicWithAppendData\nBoundary: --boundary"},
        {"x": 3.2, "w": 2.2, "h": 2.8, "theme": "preprocess", "label": "Multipart Split", "sub": "parse_multipart", "shape": "Header + P2P", "desc": "Extracts JSON meta &\nraw byte chunk"},
        {"x": 6.0, "w": 2.4, "h": 2.8, "theme": "forecast", "label": "Matrix Decode", "sub": "np.frombuffer", "shape": "(288, 384) f32", "desc": "IEEE-754 32-bit float\nCalibrated Celsius"},
        {"x": 9.0, "w": 2.3, "h": 2.8, "theme": "forecast", "label": "Zone Sampler", "sub": "thermal_points", "shape": "Points P1-P9", "desc": "Norm coords (x,y) -> (mx,my)\nROI Area Max/Mean"},
        {"x": 12.0, "w": 2.3, "h": 2.8, "theme": "forecast", "label": "History Logger", "sub": "Self-Rotating CSV", "shape": "live_history", "desc": "Dynamic header sync\n5-minute aggregation"},
        {"x": 14.8, "w": 1.4, "h": 2.8, "theme": "backend", "label": "REST Push", "sub": "FastAPI", "shape": ":8080", "desc": "To Forecaster"}
    ]

    for s in stages:
        draw_3d_block(ax, s["x"], 3.2, s["w"], s["h"], depth=0.35, theme=s["theme"],
                      label=s["label"], sublabel=s["sub"], tensor_shape=s["shape"], desc=s["desc"])

    draw_3d_arrow(ax, 2.9, 4.6, 3.2, 4.6)
    draw_3d_arrow(ax, 5.6, 4.6, 6.0, 4.6)
    draw_3d_arrow(ax, 8.6, 4.6, 9.0, 4.6)
    draw_3d_arrow(ax, 11.5, 4.6, 12.0, 4.6)
    draw_3d_arrow(ax, 14.5, 4.6, 14.8, 4.6)

    fig.savefig(OUTPUT_DIR / "3_thermal_matrix_pipeline.png", dpi=300)
    plt.close(fig)
    print("Generated 3_thermal_matrix_pipeline.png")


# ==============================================================================
# Figure 4: Linear Regression Forecaster
# ==============================================================================
def generate_fig4():
    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
    fig.patch.set_facecolor(THEMES["dark_bg"])
    ax.set_facecolor(THEMES["dark_bg"])
    ax.set_xlim(-0.5, 16.5)
    ax.set_ylim(-0.5, 9.5)
    ax.axis("off")

    ax.text(8.0, 8.8, "Autoregressive Multi-Target Linear Regression Forecaster", ha="center", va="center",
            color=THEMES["text_white"], fontsize=18, fontweight="bold")
    ax.text(8.0, 8.35, "Live Production Serving Model: 5-Lag Sliding Window -> Multi-Target OLS -> 5-Minute Ahead Horizon Prediction",
            ha="center", va="center", color=THEMES["text_muted"], fontsize=10.5)

    stages = [
        {"x": 0.5, "w": 2.4, "h": 2.8, "theme": "preprocess", "label": "Sliding Window", "sub": "History CSV", "shape": "window_size=5", "desc": "Lags: [t-4, t-3, t-2, t-1, t]\nPer target point"},
        {"x": 3.6, "w": 2.4, "h": 2.8, "theme": "preprocess", "label": "Lag Tensor", "sub": "Vectorization", "shape": "[1, 5] float32", "desc": "Clean NaN -> 30.0C default\nTemporal ordering"},
        {"x": 6.8, "w": 2.8, "h": 2.8, "theme": "forecast", "label": "Linear Model", "sub": "linear_reg.pkl", "shape": "11 Multi-Models", "desc": "y_pred = w * X + b\nPoints 1-9, Zones 1-2"},
        {"x": 10.3, "w": 2.5, "h": 2.8, "theme": "forecast", "label": "Prediction Vector", "sub": "Target Horizon", "shape": "11 Scalar Temps", "desc": "Forecast at t+5 minutes\nCapped: [0C, 500C]"},
        {"x": 13.5, "w": 2.4, "h": 2.8, "theme": "backend", "label": "Callback Relay", "sub": "HTTP POST", "shape": ":8100/api/pred", "desc": "StationOS Ingestion\nAlarm Threshold Check"}
    ]

    for s in stages:
        draw_3d_block(ax, s["x"], 3.2, s["w"], s["h"], depth=0.35, theme=s["theme"],
                      label=s["label"], sublabel=s["sub"], tensor_shape=s["shape"], desc=s["desc"])

    draw_3d_arrow(ax, 3.1, 4.6, 3.6, 4.6)
    draw_3d_arrow(ax, 6.2, 4.6, 6.8, 4.6)
    draw_3d_arrow(ax, 9.8, 4.6, 10.3, 4.6)
    draw_3d_arrow(ax, 13.0, 4.6, 13.5, 4.6)

    fig.savefig(OUTPUT_DIR / "4_linear_regression_forecaster.png", dpi=300)
    plt.close(fig)
    print("Generated 4_linear_regression_forecaster.png")


# ==============================================================================
# Figure 5: MTKAN Neural Architecture
# ==============================================================================
def generate_fig5():
    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
    fig.patch.set_facecolor(THEMES["dark_bg"])
    ax.set_facecolor(THEMES["dark_bg"])
    ax.set_xlim(-0.5, 16.5)
    ax.set_ylim(-0.5, 9.5)
    ax.axis("off")

    ax.text(8.0, 8.8, "Experimental MTKAN Temporal Architecture (Keras 3.14)", ha="center", va="center",
            color=THEMES["text_white"], fontsize=18, fontweight="bold")
    ax.text(8.0, 8.35, "Input [batch, 5, 24] -> STL Decomposition -> TKAN(64) -> Dropout -> TKAN(32) -> Dense(32) -> Dense(6)",
            ha="center", va="center", color=THEMES["text_muted"], fontsize=10.5)

    layers = [
        {"x": 0.4, "w": 1.8, "h": 2.8, "theme": "preprocess", "label": "STL Features", "sub": "statsmodels STL", "shape": "[None, 5, 24]", "desc": "Trend, Seasonal, Resid\n6 targets x 4 = 24 dims"},
        {"x": 2.7, "w": 2.0, "h": 2.8, "theme": "fusion", "label": "TKAN Layer 1", "sub": "units=64", "shape": "[None, 5, 64]", "desc": "return_sequences=True\nactivation='tanh'"},
        {"x": 5.2, "w": 1.6, "h": 2.8, "theme": "preprocess", "label": "Dropout 1", "sub": "rate=0.10", "shape": "[None, 5, 64]", "desc": "Regularization"},
        {"x": 7.3, "w": 2.0, "h": 2.8, "theme": "fusion", "label": "TKAN Layer 2", "sub": "units=32", "shape": "[None, 32]", "desc": "return_sequences=False\nSpline weight functions"},
        {"x": 9.8, "w": 1.9, "h": 2.8, "theme": "backbone", "label": "Dense Layer", "sub": "units=32", "shape": "[None, 32]", "desc": "activation='relu'\nRepresentation map"},
        {"x": 12.2, "w": 1.6, "h": 2.8, "theme": "preprocess", "label": "Dropout 2", "sub": "rate=0.10", "shape": "[None, 32]", "desc": "Regularization"},
        {"x": 14.3, "w": 1.8, "h": 2.8, "theme": "detector", "label": "Output Head", "sub": "units=6", "shape": "[None, 6]", "desc": "[ID_1_t5 ... ID_6_t5]\nReported MAE: 0.38-0.56"}
    ]

    for l in layers:
        draw_3d_block(ax, l["x"], 3.2, l["w"], l["h"], depth=0.35, theme=l["theme"],
                      label=l["label"], sublabel=l["sub"], tensor_shape=l["shape"], desc=l["desc"])

    draw_3d_arrow(ax, 2.4, 4.6, 2.7, 4.6)
    draw_3d_arrow(ax, 4.9, 4.6, 5.2, 4.6)
    draw_3d_arrow(ax, 7.0, 4.6, 7.3, 4.6)
    draw_3d_arrow(ax, 9.5, 4.6, 9.8, 4.6)
    draw_3d_arrow(ax, 11.9, 4.6, 12.2, 4.6)
    draw_3d_arrow(ax, 14.0, 4.6, 14.3, 4.6)

    fig.savefig(OUTPUT_DIR / "5_mtkan_architecture.png", dpi=300)
    plt.close(fig)
    print("Generated 5_mtkan_architecture.png")


# ==============================================================================
# Figure 6: Model Comparison 3D Matrix
# ==============================================================================
def generate_fig6():
    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
    fig.patch.set_facecolor(THEMES["dark_bg"])
    ax.set_facecolor(THEMES["dark_bg"])
    ax.set_xlim(-0.5, 16.5)
    ax.set_ylim(-0.5, 9.5)
    ax.axis("off")

    ax.text(8.0, 8.8, "System Model Role & Technical Specification Comparison", ha="center", va="center",
            color=THEMES["text_white"], fontsize=18, fontweight="bold")
    ax.text(8.0, 8.35, "Direct Artifact Verification: Vision Detector, Serving Forecaster, and Research Deep Learning Model",
            ha="center", va="center", color=THEMES["text_muted"], fontsize=10.5)

    # 3 Big volumetric comparative cards
    draw_3d_block(ax, 0.6, 2.2, 4.6, 4.8, depth=0.45, theme="detector",
                  label="YOLOv8n TensorRT", sublabel="models/best.onnx\nmodels/yolov8n.engine", tensor_shape="[1, 3, 640, 640] -> [1, 300, 6]",
                  desc="Role: Production PPE Detection\nTarget: class 0 (uniform)\nThreshold: 0.55 | Cooldown: 60s\nRuntime: TensorRT FP16 Engine")

    draw_3d_block(ax, 5.8, 2.2, 4.6, 4.8, depth=0.45, theme="forecast",
                  label="Linear Regression", sublabel="timeseries_service/model/\nlinear_reg.pkl", tensor_shape="[5 Lags] -> [1 Future Scalar]",
                  desc="Role: Production Serving Forecaster\nAlgorithm: Multi-target OLS\nHorizon: 5 min ahead (11 targets)\nTraining: Background auto-retrain")

    draw_3d_block(ax, 11.0, 2.2, 4.6, 4.8, depth=0.45, theme="fusion",
                  label="MTKAN (Temporal KAN)", sublabel="timeseries_service/model/\nmtkan_model.keras", tensor_shape="[None, 5, 24] -> [None, 6]",
                  desc="Role: Experimental Benchmark\nArchitecture: 2x TKAN + 2x Dense\nReported Test MAE: 0.38 - 0.56 C\nReported Test R2: 0.920 - 0.979")

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
    print("AI-Thermal-detect: All 6 3D volumetric tensor block figures generated successfully at 300 DPI.")
