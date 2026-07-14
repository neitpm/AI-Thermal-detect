import os
import math
from PIL import Image, ImageDraw, ImageFont

DIAGRAMS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagrams")
os.makedirs(DIAGRAMS_DIR, exist_ok=True)

# Color Palette Config
BG_COLOR = "#FCFDFD"
BOX_BG = "#EEF4F8"
BOX_BORDER = "#2C5282"
TEXT_COLOR = "#2D3748"
HEADER_BG = "#D0E1FD"
ARROW_COLOR = "#3182CE"
WHITE = "#FFFFFF"
GRAY = "#718096"

class DiagramPainter:
    def __init__(self, width, height, title=""):
        self.width = width
        self.height = height
        self.image = Image.new("RGBA", (width, height), BG_COLOR)
        self.draw = ImageDraw.Draw(self.image)
        
        # Load fonts
        self.font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        self.font_bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if not os.path.exists(self.font_path):
            self.font_path = "DejaVuSans.ttf"  # Fallback to current dir if not in standard path
            self.font_bold_path = "DejaVuSans-Bold.ttf"

        if title:
            self.draw_text(width // 2, 25, title, font_type="bold", size=18, fill=BOX_BORDER, anchor="mm")

    def get_font(self, font_type="regular", size=12):
        path = self.font_bold_path if font_type == "bold" else self.font_path
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            return ImageFont.load_default()

    def draw_box(self, x1, y1, x2, y2, fill=BOX_BG, border=BOX_BORDER, border_width=2, rx=6):
        self.draw.rounded_rectangle([x1, y1, x2, y2], radius=rx, fill=fill, outline=border, width=border_width)

    def draw_header_box(self, x1, y1, x2, y2, header_h=30, fill=BOX_BG, header_fill=HEADER_BG, border=BOX_BORDER, border_width=2, rx=6):
        # Draw base box
        self.draw_box(x1, y1, x2, y2, fill=fill, border=border, border_width=border_width, rx=rx)
        # Draw header section
        self.draw.rounded_rectangle([x1, y1, x2, y1 + header_h], radius=rx, fill=header_fill, outline=border, width=border_width)
        # Overwrite lower border of header rounded corners with simple rect
        self.draw.rectangle([x1 + border_width, y1 + header_h - 5, x2 - border_width, y1 + header_h], fill=header_fill)
        self.draw.line([(x1, y1 + header_h), (x2, y1 + header_h)], fill=border, width=border_width)

    def draw_line(self, points, fill=BOX_BORDER, width=1):
        self.draw.line(points, fill=fill, width=width)

    def draw_text(self, x, y, text, font_type="regular", size=12, fill=TEXT_COLOR, anchor="mm"):
        font = self.get_font(font_type, size)
        self.draw.text((x, y), text, fill=fill, font=font, anchor=anchor)

    def draw_multiline_text(self, x, y, lines, font_type="regular", size=11, fill=TEXT_COLOR, spacing=15, anchor="lm"):
        font = self.get_font(font_type, size)
        for i, line in enumerate(lines):
            self.draw.text((x, y + i * spacing), line, fill=fill, font=font, anchor=anchor)

    def draw_arrow(self, x1, y1, x2, y2, fill=ARROW_COLOR, width=2, text=None, text_size=10, text_fill=TEXT_COLOR, is_dashed=False):
        # Draw the line
        if is_dashed:
            # Simple dashed line implementation
            dist = math.hypot(x2 - x1, y2 - y1)
            dash_len = 6
            gap_len = 4
            num_dashes = int(dist / (dash_len + gap_len))
            dx = (x2 - x1) / dist
            dy = (y2 - y1) / dist
            for i in range(num_dashes):
                sx = x1 + i * (dash_len + gap_len) * dx
                sy = y1 + i * (dash_len + gap_len) * dy
                ex = sx + dash_len * dx
                ey = sy + dash_len * dy
                self.draw.line([(sx, sy), (ex, ey)], fill=fill, width=width)
        else:
            self.draw.line([(x1, y1), (x2, y2)], fill=fill, width=width)
        
        # Calculate arrowhead
        angle = math.atan2(y2 - y1, x2 - x1)
        arrow_len = 9
        arrow_angle = math.pi / 6 # 30 deg
        
        ax1 = x2 - arrow_len * math.cos(angle - arrow_angle)
        ay1 = y2 - arrow_len * math.sin(angle - arrow_angle)
        ax2 = x2 - arrow_len * math.cos(angle + arrow_angle)
        ay2 = y2 - arrow_len * math.sin(angle + arrow_angle)
        
        self.draw.polygon([(x2, y2), (ax1, ay1), (ax2, ay2)], fill=fill)
        
        # Line Masking for Text
        if text:
            font = self.get_font("regular", text_size)
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2
            
            bbox = self.draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            
            # Mask behind text
            pad_w = 5
            pad_h = 3
            self.draw.rectangle([mx - tw/2 - pad_w, my - th/2 - pad_h, mx + tw/2 + pad_w, my + th/2 + pad_h], fill=BG_COLOR)
            self.draw.text((mx, my), text, fill=text_fill, font=font, anchor="mm")

    def save(self, filename):
        path = os.path.join(DIAGRAMS_DIR, filename)
        # Convert RGBA to RGB for saving if needed, but PNG supports RGBA
        self.image.save(path, "PNG")
        print(f"[SUCCESS] Đã lưu sơ đồ offline: {path}")

def generate_system_architecture():
    p = DiagramPainter(1200, 900, "SƠ ĐỒ KIẾN TRÚC HỆ THỐNG BIÊN (EDGE SYSTEM ARCHITECTURE)")
    
    # 1. External devices (Left)
    p.draw_box(40, 80, 1160, 860, fill="#FAFAFA", border=GRAY, border_width=1, rx=8)
    p.draw_text(600, 845, "Kiến Trúc Luồng Dữ Liệu Toàn Cục", font_type="bold", size=12, fill=GRAY)
    
    # External Area
    p.draw_box(60, 120, 280, 800, fill="#F7FAFC", border=BOX_BORDER, border_width=1)
    p.draw_text(170, 145, "THIẾT BỊ NGOẠI VI", font_type="bold", size=13, fill=BOX_BORDER)
    
    # Opt Camera
    p.draw_header_box(80, 220, 260, 360)
    p.draw_text(170, 235, "Camera IP Quang", font_type="bold", size=12)
    p.draw_multiline_text(90, 275, ["- RTSP Port 554", "- Luồng H.264/H.265", "- Chụp ảnh đột nhập"])
    
    # Thermal Camera
    p.draw_header_box(80, 520, 260, 660)
    p.draw_text(170, 535, "Camera Nhiệt Hikvision", font_type="bold", size=12)
    p.draw_multiline_text(90, 575, ["- API ISAPI HTTP", "- Multipart Temp Raw", "- Quét lưới điểm nhiệt"])

    # 2. Edge Node (Center)
    p.draw_box(340, 120, 860, 800, fill="#EDF2F7", border=BOX_BORDER, border_width=2)
    p.draw_text(600, 145, "THIẾT BỊ BIÊN (JETSON EDGE NODE)", font_type="bold", size=14, fill=BOX_BORDER)

    # YOLO Sub-process
    p.draw_box(360, 180, 590, 770, fill="#FFFFFF", border="#2B6CB0", border_width=1)
    p.draw_text(475, 205, "Module Phát hiện Xâm nhập", font_type="bold", size=12, fill="#2B6CB0")
    
    p.draw_header_box(380, 240, 570, 350)
    p.draw_text(475, 255, "FrameReader", font_type="bold", size=12)
    p.draw_multiline_text(390, 290, ["- Đọc luồng RTSP", "- Hàng đợi Non-blocking", "- Tránh tràn RAM"])
    
    p.draw_header_box(380, 420, 570, 530)
    p.draw_text(475, 435, "YoloDetector", font_type="bold", size=12)
    p.draw_multiline_text(390, 470, ["- TensorRT YOLOv8n", "- Lọc Aspect Ratio", "- High-FPS (~251 FPS)"])

    p.draw_header_box(380, 600, 570, 710)
    p.draw_text(475, 615, "EventRecorder", font_type="bold", size=12)
    p.draw_multiline_text(390, 650, ["- Trích xuất sự kiện", "- Ghi hình MP4 3s grace", "- Chống spam Cooldown"])

    p.draw_arrow(475, 350, 475, 420)
    p.draw_arrow(475, 530, 475, 600)

    # Thermal Sub-process
    p.draw_box(610, 180, 840, 770, fill="#FFFFFF", border="#2B6CB0", border_width=1)
    p.draw_text(725, 205, "Module Giám sát Nhiệt độ", font_type="bold", size=12, fill="#2B6CB0")

    p.draw_header_box(630, 230, 820, 320)
    p.draw_text(725, 245, "thermal_sender.py", font_type="bold", size=12)
    p.draw_multiline_text(640, 280, ["- Lấy ma trận nhiệt", "- HTTP POST JSON"])

    p.draw_header_box(630, 360, 820, 450)
    p.draw_text(725, 375, "thermal_receiver.py", font_type="bold", size=12)
    p.draw_multiline_text(640, 410, ["- FastAPI (Port 8080)", "- Ghi CSV lịch sử"])

    p.draw_header_box(630, 480, 820, 570)
    p.draw_text(725, 495, "preprocess.py", font_type="bold", size=12)
    p.draw_multiline_text(640, 530, ["- Phân rã STL", "- Nội suy dữ liệu khuyết"])

    p.draw_header_box(630, 600, 820, 690)
    p.draw_text(725, 615, "predict_all.py", font_type="bold", size=12)
    p.draw_multiline_text(640, 650, ["- Mô hình MTKAN", "- Dự báo nhiệt độ t+5"])

    p.draw_header_box(630, 710, 820, 760)
    p.draw_text(725, 725, "train.py (Auto-Retrain)", font_type="bold", size=10)

    p.draw_arrow(725, 320, 725, 360)
    p.draw_arrow(725, 450, 725, 480)
    p.draw_arrow(725, 570, 725, 600)
    p.draw_arrow(725, 410, 725, 710, is_dashed=True, text="Auto-train ngầm", text_size=8)

    # 3. Central Station (Right)
    p.draw_box(920, 120, 1140, 800, fill="#F7FAFC", border=BOX_BORDER, border_width=1)
    p.draw_text(1030, 145, "MÁY CHỦ TRUNG TÂM", font_type="bold", size=13, fill=BOX_BORDER)

    p.draw_header_box(940, 360, 1120, 470)
    p.draw_text(1030, 375, "central_station.py", font_type="bold", size=12)
    p.draw_multiline_text(950, 410, ["- Nhận cảnh báo YOLO", "- Nhận kết quả dự báo", "- API Endpoint"])

    p.draw_header_box(940, 560, 1120, 670)
    p.draw_text(1030, 575, "Web Dashboard", font_type="bold", size=12)
    p.draw_multiline_text(950, 610, ["- Đồ thị nhiệt độ", "- Danh sách đột nhập", "- Video clip phát lại"])

    p.draw_arrow(1030, 470, 1030, 560)

    # External to Edge connections
    p.draw_arrow(260, 290, 380, 290, text="RTSP Stream", text_size=9)
    p.draw_arrow(260, 590, 630, 275, text="API Poll & HTTP POST", text_size=9)

    # Edge to Central connections
    p.draw_arrow(570, 655, 940, 415, text="POST Alert & MP4", text_size=9)
    p.draw_arrow(820, 645, 940, 435, text="Callback Forecast", text_size=9)

    p.save("system_architecture.png")

def generate_database_erd():
    p = DiagramPainter(1000, 800, "SƠ ĐỒ CƠ SỞ DỮ LIỆU CHI TIẾT (DATABASE ERD)")
    
    # 6 Entities
    # 1. THERMAL_POINTS_JSON
    p.draw_header_box(50, 100, 320, 260)
    p.draw_text(185, 115, "THERMAL_POINTS_JSON", font_type="bold", size=11)
    p.draw_multiline_text(60, 145, [
        "PK  camera_ip        : string",
        "    points           : list<POINT>"
    ], font_type="regular", size=11, spacing=20)
    
    # 2. POINT_OBJECT
    p.draw_header_box(380, 100, 650, 260)
    p.draw_text(515, 115, "POINT_OBJECT (Mỗi điểm đo)", font_type="bold", size=11)
    p.draw_multiline_text(390, 145, [
        "PK  id               : string",
        "    label            : string (Tên điểm)",
        "    x                : float (Tỉ lệ X)",
        "    y                : float (Tỉ lệ Y)"
    ], font_type="regular", size=11, spacing=20)

    # 3. THERMAL_HISTORY_CSV
    p.draw_header_box(710, 100, 960, 300)
    p.draw_text(835, 115, "THERMAL_HISTORY_CSV", font_type="bold", size=11)
    p.draw_multiline_text(720, 145, [
        "PK  timestamp        : datetime",
        "    [target_1]       : float (Nhiệt độ)",
        "    [target_2]       : float",
        "    [target_N]       : float",
        "*(Các cột nhiệt độ thay đổi động)"
    ], font_type="regular", size=10, spacing=20)

    # 4. CONFIG_JSON
    p.draw_header_box(50, 450, 320, 680)
    p.draw_text(185, 465, "CONFIG_JSON (Cấu hình Model)", font_type="bold", size=11)
    p.draw_multiline_text(60, 495, [
        "PK  camera_ip        : string",
        "    window_size      : int (Mặc định: 12)",
        "    horizon          : int (Mặc định: 5)",
        "    seasonal_period  : int (Mặc định: 288)",
        "    targets          : list<string>",
        "    feature_cols     : list<string>",
        "    target_cols      : list<string>"
    ], font_type="regular", size=10, spacing=20)

    # 5. TRAINING_META_JSON
    p.draw_header_box(380, 450, 650, 650)
    p.draw_text(515, 465, "TRAINING_META_JSON", font_type="bold", size=11)
    p.draw_multiline_text(390, 495, [
        "PK  camera_ip        : string",
        "    last_trained     : datetime",
        "    train_loss       : float",
        "    val_loss         : float",
        "    training_columns : list<string>"
    ], font_type="regular", size=11, spacing=20)

    # 6. LIVE_PREDICTIONS_CSV
    p.draw_header_box(710, 450, 960, 630)
    p.draw_text(835, 465, "LIVE_PREDICTIONS_CSV", font_type="bold", size=11)
    p.draw_multiline_text(720, 495, [
        "PK  timestamp        : datetime",
        "    [target_1_pred]  : float (Nhiệt t+5)",
        "    [target_2_pred]  : float",
        "    [target_N_pred]  : float"
    ], font_type="regular", size=11, spacing=20)

    # Drawing ERD relationships
    # Relation 1: THERMAL_POINTS_JSON ||--o{ POINT_OBJECT
    p.draw_arrow(320, 180, 380, 180, text="1 : N (định nghĩa)", text_size=9)
    # Relation 2: POINT_OBJECT ||--o{ THERMAL_HISTORY_CSV
    p.draw_arrow(650, 180, 710, 180, text="khớp cột", text_size=9)
    # Relation 3: CONFIG_JSON ||--o{ THERMAL_HISTORY_CSV
    p.draw_arrow(185, 450, 750, 300, text="chọn mục tiêu", text_size=9)
    # Relation 4: CONFIG_JSON ||--|| TRAINING_META_JSON
    p.draw_arrow(320, 550, 380, 550, text="1 : 1 (theo dõi)", text_size=9)
    # Relation 5: THERMAL_HISTORY_CSV ||--|| LIVE_PREDICTIONS_CSV
    p.draw_arrow(835, 300, 835, 450, text="đầu vào dự báo", text_size=9)

    p.save("database_erd.png")

def generate_use_case_diagram():
    p = DiagramPainter(1000, 700, "SƠ ĐỒ USE CASE HỆ THỐNG")
    
    # Actors (Boxes on left/right for clarity)
    # Operator
    p.draw_header_box(40, 180, 240, 280, fill="#D0E1FD", header_fill=HEADER_BG)
    p.draw_text(140, 230, "Vận hành viên", font_type="bold", size=12)
    
    # Guard
    p.draw_header_box(40, 420, 240, 520, fill="#D0E1FD", header_fill=HEADER_BG)
    p.draw_text(140, 470, "Bảo vệ trạm", font_type="bold", size=12)

    # EdgeSys
    p.draw_header_box(760, 180, 960, 280, fill="#D0E1FD", header_fill=HEADER_BG)
    p.draw_text(860, 230, "Hệ thống Edge AI", font_type="bold", size=12)

    # CentralServer
    p.draw_header_box(760, 420, 960, 520, fill="#D0E1FD", header_fill=HEADER_BG)
    p.draw_text(860, 470, "Server Trung tâm", font_type="bold", size=12)

    # Use Case System Border
    p.draw_box(300, 80, 700, 650, fill="#FFFFFF", border=GRAY, border_width=1)
    p.draw_text(500, 100, "Hệ Thống Smart Camera Edge", font_type="bold", size=12, fill=GRAY)

    # Use Cases (drawn as rounded pill boxes representing ellipses)
    ucs = [
        ("UC1", "Cấu hình điểm đo nhiệt độ", 130),
        ("UC2", "Xem trực tiếp video & nhiệt độ", 210),
        ("UC3", "Nhận cảnh báo xâm nhập người", 290),
        ("UC4", "Truy xuất video sự kiện MP4", 370),
        ("UC5", "Dự báo cảnh báo sớm quá nhiệt", 450),
        ("UC6", "Tự động huấn luyện lại mô hình", 530),
        ("UC7", "Giám sát trạng thái thiết bị biên", 600)
    ]

    for uc_id, uc_name, y in ucs:
        p.draw_box(330, y, 670, y + 45, fill="#EEF4F8", border=BOX_BORDER, rx=20)
        p.draw_text(500, y + 22, f"{uc_id}: {uc_name}", font_type="bold", size=11)

    # Connections (Lines between Actors and Use Cases)
    # Operator
    p.draw_arrow(240, 230, 330, 152, fill=ARROW_COLOR, width=1)
    p.draw_arrow(240, 230, 330, 232, fill=ARROW_COLOR, width=1)
    
    # Guard
    p.draw_arrow(240, 470, 330, 312, fill=ARROW_COLOR, width=1)
    p.draw_arrow(240, 470, 330, 392, fill=ARROW_COLOR, width=1)

    # EdgeSys
    p.draw_arrow(760, 230, 670, 312, fill=ARROW_COLOR, width=1)
    p.draw_arrow(760, 230, 670, 472, fill=ARROW_COLOR, width=1)
    p.draw_arrow(760, 230, 670, 552, fill=ARROW_COLOR, width=1)

    # CentralServer
    p.draw_arrow(760, 470, 670, 152, fill=ARROW_COLOR, width=1)
    p.draw_arrow(760, 470, 670, 232, fill=ARROW_COLOR, width=1)
    p.draw_arrow(760, 470, 670, 312, fill=ARROW_COLOR, width=1)
    p.draw_arrow(760, 470, 670, 622, fill=ARROW_COLOR, width=1)

    p.save("use_case_diagram.png")

def generate_class_diagram():
    p = DiagramPainter(1100, 800, "SƠ ĐỒ LỚP CHI TIẾT (UML CLASS DIAGRAM)")
    
    # Row 1: YOLO Process
    # FrameReader
    p.draw_header_box(50, 80, 320, 280)
    p.draw_text(185, 95, "FrameReader", font_type="bold", size=12)
    p.draw_multiline_text(60, 125, [
        "+ rtsp_url  : string",
        "+ queue     : queue",
        "+ running   : bool",
        "+ thread    : thread"
    ], font_type="regular", size=10, spacing=18)
    p.draw_line([(50, 195), (320, 195)], fill=BOX_BORDER, width=1)
    p.draw_multiline_text(60, 210, [
        "+ start()   : void",
        "+ read()    : ndarray",
        "+ stop()    : void"
    ], font_type="regular", size=10, spacing=18)

    # YoloDetector
    p.draw_header_box(410, 80, 680, 280)
    p.draw_text(545, 95, "YoloDetector", font_type="bold", size=12)
    p.draw_multiline_text(420, 125, [
        "+ engine_path  : string",
        "+ conf_thresh  : float",
        "+ min_aspect   : float",
        "+ max_aspect   : float"
    ], font_type="regular", size=10, spacing=18)
    p.draw_line([(410, 195), (680, 195)], fill=BOX_BORDER, width=1)
    p.draw_multiline_text(420, 210, [
        "+ detect(frame) : list<Box>"
    ], font_type="regular", size=10, spacing=18)

    # EventRecorder
    p.draw_header_box(770, 80, 1040, 280)
    p.draw_text(905, 95, "EventRecorder", font_type="bold", size=12)
    p.draw_multiline_text(780, 125, [
        "+ output_dir   : string",
        "+ grace_sec    : int (3s)",
        "+ is_recording : bool",
        "+ cooldown_sec : int (5s)"
    ], font_type="regular", size=10, spacing=18)
    p.draw_line([(770, 195), (1040, 195)], fill=BOX_BORDER, width=1)
    p.draw_multiline_text(780, 210, [
        "+ write_frame(f): void",
        "+ start_rec()   : void",
        "+ stop_rec()    : void"
    ], font_type="regular", size=10, spacing=18)

    p.draw_arrow(320, 180, 410, 180, text="feeds frames", text_size=9)
    p.draw_arrow(680, 180, 770, 180, text="triggers event", text_size=9)

    # Row 2: Thermal Process
    # ThermalSender
    p.draw_header_box(50, 400, 320, 580)
    p.draw_text(185, 415, "ThermalSender", font_type="bold", size=12)
    p.draw_multiline_text(60, 445, [
        "+ camera_ip : string",
        "+ isapi_url : string"
    ], font_type="regular", size=10, spacing=18)
    p.draw_line([(50, 490), (320, 490)], fill=BOX_BORDER, width=1)
    p.draw_multiline_text(60, 505, [
        "+ poll_isapi()    : bytes",
        "+ parse_multi()   : float[][]",
        "+ send_payload()  : void"
    ], font_type="regular", size=10, spacing=18)

    # ThermalReceiver
    p.draw_header_box(410, 400, 680, 580)
    p.draw_text(545, 415, "ThermalReceiver (FastAPI)", font_type="bold", size=11)
    p.draw_multiline_text(420, 445, [
        "+ app             : FastAPI",
        "+ config_path     : string"
    ], font_type="regular", size=10, spacing=18)
    p.draw_line([(410, 490), (680, 490)], fill=BOX_BORDER, width=1)
    p.draw_multiline_text(420, 505, [
        "+ receive_data()  : JSON",
        "+ get_config()    : JSON",
        "+ update_config() : JSON"
    ], font_type="regular", size=10, spacing=18)

    # CSVDataManager
    p.draw_header_box(770, 400, 1040, 580)
    p.draw_text(905, 415, "CSVDataManager", font_type="bold", size=12)
    p.draw_multiline_text(780, 445, [
        "+ csv_path        : string"
    ], font_type="regular", size=10, spacing=18)
    p.draw_line([(770, 490), (1040, 490)], fill=BOX_BORDER, width=1)
    p.draw_multiline_text(780, 505, [
        "+ sync_headers()  : void",
        "+ append_row()    : void",
        "+ interpolate()   : DataFrame"
    ], font_type="regular", size=10, spacing=18)

    p.draw_arrow(320, 490, 410, 490, text="HTTP POST JSON", text_size=9)
    p.draw_arrow(680, 490, 770, 490, text="saves raw data", text_size=9)

    # STLPreprocessor
    p.draw_header_box(230, 620, 500, 770)
    p.draw_text(365, 635, "STLPreprocessor", font_type="bold", size=12)
    p.draw_multiline_text(240, 665, [
        "+ seasonal_period : int"
    ], font_type="regular", size=10, spacing=18)
    p.draw_line([(230, 690), (500, 690)], fill=BOX_BORDER, width=1)
    p.draw_multiline_text(240, 705, [
        "+ build_features() : DataFrame"
    ], font_type="regular", size=10, spacing=18)

    # MTKANForecastingModel
    p.draw_header_box(590, 620, 860, 770)
    p.draw_text(725, 635, "MTKANForecastingModel", font_type="bold", size=11)
    p.draw_multiline_text(600, 665, [
        "+ model_path : string",
        "+ window     : int (12)",
        "+ horizon    : int (5)"
    ], font_type="regular", size=10, spacing=18)
    p.draw_line([(590, 715), (860, 715)], fill=BOX_BORDER, width=1)
    p.draw_multiline_text(600, 725, [
        "+ predict(X) : float[]",
        "+ train(csv) : void"
    ], font_type="regular", size=10, spacing=18)

    p.draw_arrow(905, 580, 365, 620, text="prepares", text_size=9)
    p.draw_arrow(500, 695, 590, 695, text="feeds features", text_size=9)

    p.save("class_diagram.png")

def generate_activity_diagram():
    p = DiagramPainter(800, 1200, "SƠ ĐỒ HOẠT ĐỘNG DỊCH VỤ NHIỆT ĐỘ (ACTIVITY DIAGRAM)")
    
    # Start node (circle)
    p.draw.ellipse([385, 80, 415, 110], fill="#2C5282", outline=BOX_BORDER)
    p.draw_text(400, 65, "Bắt đầu chu kỳ", font_type="bold", size=11)
    
    # 1. Read ISAPI
    p.draw_box(280, 140, 520, 190)
    p.draw_text(400, 165, "Đọc luồng dữ liệu ISAPI", font_type="bold", size=11)
    p.draw_arrow(400, 110, 400, 140)

    # 2. Parse Multipart
    p.draw_box(280, 220, 520, 270)
    p.draw_text(400, 245, "Trích xuất ma trận nhiệt Float32", font_type="bold", size=11)
    p.draw_arrow(400, 190, 400, 220)

    # 3. HTTP POST to Receiver
    p.draw_box(280, 300, 520, 350)
    p.draw_text(400, 325, "Gửi HTTP POST lên Receiver API", font_type="bold", size=11)
    p.draw_arrow(400, 270, 400, 300)

    # Subgraph System Container (FastAPI Process)
    p.draw_box(100, 380, 700, 1000, fill="#FAFAFA", border=GRAY, border_width=1)
    p.draw_text(400, 395, "Xử lý nội bộ tại API Biên (FastAPI)", font_type="bold", size=12, fill=GRAY)

    # 4. Check Schema Decision Diamond (X = 400, Y = 450)
    p.draw.polygon([(400, 420), (500, 450), (400, 480), (300, 450)], fill=HEADER_BG, outline=BOX_BORDER, width=2)
    p.draw_text(400, 450, "Cấu hình targets đổi?", font_type="bold", size=10)
    p.draw_arrow(400, 350, 400, 420)

    # 5. SyncHeaders (On Left / Yes branch)
    p.draw_box(130, 425, 270, 475)
    p.draw_text(200, 450, "Cập nhật schema CSV", font_type="bold", size=11)
    p.draw_arrow(300, 450, 270, 450, text="Có", text_size=10)

    # 6. AppendCSV
    p.draw_box(280, 520, 520, 570)
    p.draw_text(400, 545, "Ghi dòng dữ liệu mới vào CSV", font_type="bold", size=11)
    p.draw_arrow(400, 480, 400, 520, text="Không", text_size=10)
    p.draw_arrow(200, 475, 200, 545, fill=ARROW_COLOR)
    p.draw_arrow(200, 545, 280, 545, fill=ARROW_COLOR)

    # 7. FillNaN
    p.draw_box(280, 600, 520, 650)
    p.draw_text(400, 625, "Nội suy dữ liệu khuyết (FillNaN)", font_type="bold", size=11)
    p.draw_arrow(400, 570, 400, 600)

    # 8. STL Decomposition
    p.draw_box(280, 680, 520, 730)
    p.draw_text(400, 705, "Phân rã STL (Trend, Seasonal)", font_type="bold", size=11)
    p.draw_arrow(400, 650, 400, 680)

    # 9. Predict MTKAN
    p.draw_box(280, 760, 520, 810)
    p.draw_text(400, 785, "Dự báo nhiệt độ qua MTKAN (t+5)", font_type="bold", size=11)
    p.draw_arrow(400, 730, 400, 760)

    # 10. Compare Decision Diamond (X = 400, Y = 870)
    p.draw.polygon([(400, 830), (520, 870), (400, 910), (280, 870)], fill=HEADER_BG, outline=BOX_BORDER, width=2)
    p.draw_text(400, 870, "Dự báo nhiệt > Ngưỡng?", font_type="bold", size=10)
    p.draw_arrow(400, 810, 400, 830)

    # 11. Trigger Alert (Yes branch)
    p.draw_box(130, 845, 260, 895)
    p.draw_text(195, 870, "Gửi Cảnh Báo Sớm", font_type="bold", size=11)
    p.draw_arrow(280, 870, 260, 870, text="Có", text_size=10)

    # End Node
    p.draw.ellipse([385, 1060, 415, 1090], fill=WHITE, outline=BOX_BORDER, width=4)
    p.draw.ellipse([391, 1066, 409, 1084], fill=BOX_BORDER)
    p.draw_text(400, 1105, "Kết thúc chu kỳ", font_type="bold", size=11)

    p.draw_arrow(400, 910, 400, 1060, text="Không", text_size=10)
    p.draw_arrow(195, 895, 195, 980, fill=ARROW_COLOR)
    p.draw_arrow(195, 980, 400, 980, fill=ARROW_COLOR)

    p.save("activity_diagram.png")

def generate_state_diagram():
    p = DiagramPainter(900, 800, "SƠ ĐỒ TRẠNG THÁI BỘ PHÁT HIỆN NGƯỜI (STATE DIAGRAM)")
    
    # Start Node
    p.draw.ellipse([85, 120, 105, 140], fill=BOX_BORDER)
    
    # State 1: Idle (Giám sát bình thường)
    p.draw_header_box(50, 200, 220, 280, rx=12)
    p.draw_text(135, 215, "Idle", font_type="bold", size=12)
    p.draw_text(135, 250, "Giám sát bình thường", size=10)
    p.draw_arrow(95, 140, 95, 200)

    # State 2: Intrusion_Detected (Lồng trạng thái lớn)
    p.draw_box(300, 100, 850, 520, fill="#FFFFFF", border=BOX_BORDER, border_width=2, rx=16)
    p.draw_text(575, 125, "TRẠNG THÁI: PHÁT HIỆN XÂM NHẬP (Intrusion_Detected)", font_type="bold", size=12, fill=BOX_BORDER)

    # Sub-states inside Intrusion_Detected
    # Start_Record
    p.draw_header_box(330, 180, 510, 250, rx=8)
    p.draw_text(420, 195, "Start_Record", font_type="bold", size=11)
    p.draw_text(420, 225, "Khởi tạo ghi file MP4", size=9)

    # Writing_Frames
    p.draw_header_box(330, 310, 510, 380, rx=8)
    p.draw_text(420, 325, "Writing_Frames", font_type="bold", size=11)
    p.draw_text(420, 355, "Ghi hình luồng video", size=9)
    p.draw_arrow(420, 250, 420, 310)

    # Check_Frame
    p.draw_header_box(330, 440, 510, 500, rx=8)
    p.draw_text(420, 455, "Check_Frame", font_type="bold", size=11)
    p.draw_text(420, 480, "Nhận diện frame mới", size=9)
    p.draw_arrow(420, 380, 420, 440)
    
    # Loop from Check_Frame to Writing_Frames
    p.draw.arc([280, 340, 330, 480], 90, 270, fill=ARROW_COLOR)
    p.draw_arrow(305, 340, 330, 340, fill=ARROW_COLOR, text="Thấy người", text_size=8)

    # Grace_Period
    p.draw_header_box(620, 310, 810, 430, rx=8)
    p.draw_text(715, 325, "Grace_Period (Đợi 3s)", font_type="bold", size=11)
    p.draw_text(715, 360, "- Đếm ngược 3 giây", size=9)
    p.draw_text(715, 380, "- Lọc mất dấu tạm thời", size=9)
    
    p.draw_arrow(510, 470, 715, 430, text="Không thấy người", text_size=8)
    p.draw_arrow(715, 310, 510, 330, text="Người xuất hiện lại", text_size=8)

    # Transition from Idle to Intrusion_Detected
    p.draw_arrow(220, 240, 300, 240, text="Phát hiện người", text_size=9)

    # Save_And_Alert
    p.draw_header_box(600, 600, 820, 680, rx=12)
    p.draw_text(710, 615, "Save_And_Alert", font_type="bold", size=12)
    p.draw_text(710, 650, "Lưu file MP4 & Gửi API", size=10)
    p.draw_arrow(715, 430, 710, 600, text="Hết 3 giây", text_size=9)

    # Cooldown
    p.draw_header_box(300, 600, 510, 680, rx=12)
    p.draw_text(405, 615, "Cooldown (Khóa 5s)", font_type="bold", size=12)
    p.draw_text(405, 650, "Tránh spam gửi cảnh báo", size=10)
    p.draw_arrow(600, 640, 510, 640, text="Hoàn tất", text_size=9)

    # Return to Idle
    p.draw_arrow(300, 640, 135, 280, text="Hết 5 giây khóa", text_size=9)

    p.save("state_diagram.png")

def main():
    print("=================================================================")
    print(" Khởi động chương trình vẽ sơ đồ offline bằng Pillow")
    print("=================================================================")
    generate_system_architecture()
    generate_database_erd()
    generate_use_case_diagram()
    generate_class_diagram()
    generate_activity_diagram()
    generate_state_diagram()
    print("=================================================================")
    print(" Hoàn tất kết xuất và lưu 6 sơ đồ PNG offline thành công!")
    print("=================================================================")

if __name__ == "__main__":
    main()
