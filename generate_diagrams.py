import os
import base64
import urllib.request
import urllib.parse
import time

DIAGRAMS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagrams")
os.makedirs(DIAGRAMS_DIR, exist_ok=True)

# Định nghĩa các sơ đồ dưới dạng Mermaid
DIAGRAMS = {
    "system_architecture": """graph TB
    subgraph EdgeNode["Thiết bị biên (Jetson Edge Node)"]
        subgraph YOLO_Process["Module Phát hiện Xâm nhập"]
            yolo["yolo_detect.py (TensorRT YOLOv8n)"]
            reader["FrameReader (Multi-thread, non-blocking)"]
            rec["Dynamic Event Recorder (MP4 Event)"]
            reader --> yolo
            yolo --> rec
        end
        
        subgraph Thermal_Process["Module Giám sát Nhiệt độ"]
            sender["thermal_sender.py (ISAPI Polling & Extract)"]
            receiver["timeseries_service/thermal_receiver.py (FastAPI, Port 8080)"]
            pre["preprocess.py (STL Decomposition & Interpolation)"]
            pred["predict_all.py / model_builder.py (MTKAN Model)"]
            train["train.py (Autotrain background thread)"]
            
            sender -->|HTTP POST JSON Matrix| receiver
            receiver -->|Write Raw Data| pre
            pre -->|Prepare CSV Features| pred
            receiver -.->|Trigger Dynamic Sync & Retrain| train
        end
    end
    
    subgraph External["Thiết bị Ngoại vi"]
        cam_opt["Camera IP Quang (RTSP Port 554)"]
        cam_therm["Camera Nhiệt Hikvision (ISAPI API)"]
    end
    
    subgraph Central["Máy chủ Trung tâm (Central Station)"]
        server["central_station.py (FastAPI Port 5000)"]
        ui["Web Dashboard (Plotly, Streams, Alerts)"]
        server --> ui
    end
    
    cam_opt -->|RTSP H.264/H.265 Stream| reader
    cam_therm -->|Multipart JPEG + Temp Matrix| sender
    
    rec -->|HTTP POST Alert & MP4 Video| server
    receiver -->|HTTP POST Forecast Callback| server""",

    "database_erd": """erDiagram
    THERMAL_POINTS_JSON {
        string camera_ip PK
        list points
    }
    POINT_OBJECT {
        string id PK
        string label
        float x
        float y
    }
    THERMAL_HISTORY_CSV {
        datetime timestamp PK
        float target_1 "Dynamic column maps to Point.label"
        float target_2 "Dynamic column maps to Point.label"
        float target_N "Dynamic column maps to Point.label"
    }
    CONFIG_JSON {
        string camera_ip PK
        int window_size
        int horizon
        int seasonal_period
        list targets "Reference to point labels"
        list feature_cols "Raw + STL decomposed column names"
        list target_cols "Predicted column names (e.g. label_t5)"
    }
    TRAINING_META_JSON {
        string camera_ip PK
        datetime last_trained
        float train_loss
        float val_loss
        list training_columns
    }
    LIVE_PREDICTIONS_CSV {
        datetime timestamp PK
        float target_1_pred
        float target_2_pred
        float target_N_pred
    }

    THERMAL_POINTS_JSON ||--o{ POINT_OBJECT : "defines"
    POINT_OBJECT ||--o{ THERMAL_HISTORY_CSV : "maps to column header"
    CONFIG_JSON ||--o{ THERMAL_HISTORY_CSV : "selects targets & features"
    CONFIG_JSON ||--|| TRAINING_META_JSON : "tracks training context"
    THERMAL_HISTORY_CSV ||--|| LIVE_PREDICTIONS_CSV : "leads to predictions" """,

    "use_case_diagram": """graph TD
    subgraph Actors["Tác nhân"]
        Operator["Nhân viên Vận hành"]
        Guard["Nhân viên Bảo vệ"]
        EdgeSys["Hệ thống Biên (Edge AI)"]
        CentralServer["Máy chủ Trung tâm"]
    end
    
    subgraph UseCases["Hộp Use Case"]
        UC1["Cấu hình điểm đo nhiệt độ"]
        UC2["Xem trực tiếp luồng video & nhiệt độ"]
        UC3["Nhận cảnh báo xâm nhập người"]
        UC4["Truy xuất & xem video sự kiện MP4"]
        UC5["Dự báo cảnh báo sớm quá nhiệt"]
        UC6["Tự động huấn luyện lại mô hình AI"]
    end
    
    Operator --> UC1
    Operator --> UC2
    Guard --> UC3
    Guard --> UC4
    
    EdgeSys --> UC3
    EdgeSys --> UC5
    EdgeSys --> UC6
    
    CentralServer --> UC1
    CentralServer --> UC2
    CentralServer --> UC3""",

    "class_diagram": """classDiagram
    class FrameReader {
        +string rtsp_url
        +queue frame_queue
        +bool running
        +thread reader_thread
        +start()
        +read()
        +stop()
    }
    class YoloDetector {
        +string engine_path
        +float conf_threshold
        +float min_aspect_ratio
        +float max_aspect_ratio
        +detect_persons(frame) list
    }
    class EventRecorder {
        +string output_dir
        +int grace_period
        +bool is_recording
        +write_frame(frame)
        +start_recording()
        +stop_recording()
    }
    class ThermalSender {
        +string camera_ip
        +string isapi_url
        +poll_isapi()
        +parse_multipart()
        +send_payload()
    }
    class ThermalReceiver {
        +app FastAPI
        +receive_thermal_data()
        +get_config()
        +update_config()
    }
    class CSVDataManager {
        +string csv_path
        +sync_csv_headers(targets)
        +append_row(timestamp, data_dict)
        +interpolate_missing_data(df) DataFrame
    }
    class STLPreprocessor {
        +int seasonal_period
        +build_features(df) DataFrame
    }
    class MTKANForecastingModel {
        +string model_path
        +int window_size
        +int horizon
        +predict(X) ndarray
        +train(data_path, targets)
    }

    FrameReader --> YoloDetector : "feeds frames"
    YoloDetector --> EventRecorder : "triggers"
    ThermalSender --> ThermalReceiver : "sends HTTP POST"
    ThermalReceiver --> CSVDataManager : "uses to save"
    CSVDataManager --> STLPreprocessor : "prepares data"
    STLPreprocessor --> MTKANForecastingModel : "feeds features" """,

    "activity_diagram": """graph TD
    Start([Bắt đầu vòng lặp]) --> Poll[Đọc luồng dữ liệu camera nhiệt ISAPI]
    Poll --> Parse[Phân tích Multipart & Trích xuất ma trận nhiệt Float32]
    Parse --> Send[HTTP POST gửi dữ liệu lên Thermal Receiver API]
    
    subgraph API_Processing["Xử lý tại API Biên (FastAPI)"]
        Send --> CheckSchema{Cấu hình targets thay đổi?}
        CheckSchema -- Có --> SyncHeaders[Cập nhật schema CSV - Không mất dữ liệu cũ]
        CheckSchema -- Không --> AppendCSV[Ghi thêm dòng dữ liệu mới vào CSV]
        SyncHeaders --> AppendCSV
        
        AppendCSV --> FillNaN[Nội suy dữ liệu bị khuyết thiếu - Interpolate]
        FillNaN --> STL[Phân rã STL: Trend, Seasonal, Residual]
        STL --> Predict[Dự báo nhiệt độ 5 phút tới qua mô hình MTKAN]
        Predict --> Compare{Nhiệt độ dự báo > Ngưỡng?}
    end
    
    Compare -- Có --> TriggerAlert[Gửi cảnh báo quá nhiệt tức thời về Máy chủ trung tâm]
    Compare -- Không --> End([Kết thúc chu kỳ])
    TriggerAlert --> End""",

    "state_diagram": """stateDiagram-v2
    [*] --> Idle : Trạng thái giám sát bình thường
    
    Idle --> Intrusion_Detected : Bounding box con người & vượt qua bộ lọc Aspect Ratio
    
    state Intrusion_Detected {
        [*] --> Start_Record : Khởi tạo Event Recorder & tạo file MP4
        Start_Record --> Writing_Frames : Ghi hình luồng video liên tục
        Writing_Frames --> Check_Frame : Nhận diện frame tiếp theo
        
        Check_Frame --> Writing_Frames : Vẫn thấy người
        Check_Frame --> Grace_Period : Không thấy người (Grace Period 3s)
        
        state Grace_Period {
            [*] --> Countdown : Bắt đầu đếm ngược 3 giây
            Countdown --> Person_Reappears : Người xuất hiện lại?
            Countdown --> Timeout : Hết 3 giây không có người
        }
    }
    
    Person_Reappears --> Writing_Frames : Tiếp tục ghi hình
    Timeout --> Save_And_Alert : Lưu file MP4 & Gửi cảnh báo về Central Server
    
    Save_And_Alert --> Cooldown : Khởi động trạng thái khóa chống spam (Cooldown 5s)
    Cooldown --> Idle : Hết thời gian cooldown"""
}

def generate_png_diagrams():
    print("[INFO] Bắt đầu kết xuất và tải sơ đồ thiết kế...")
    for name, code in DIAGRAMS.items():
        print(f"[INFO] Đang xử lý sơ đồ: {name}...")
        
        # Mã hóa Base64
        # mermaid.ink mong muốn chuỗi được mã hóa base64 chuẩn URL không chứa padding =
        # hoặc mã hóa base64 thông thường sau đó urlencode
        # Hãy dùng urlsafe_b64encode
        encoded = base64.urlsafe_b64encode(code.encode("utf-8")).decode("utf-8")
        url = f"https://mermaid.ink/img/{encoded}"
        
        output_path = os.path.join(DIAGRAMS_DIR, f"{name}.png")
        
        # Gửi request với User-Agent để tránh lỗi 403 Forbidden
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        
        success = False
        retries = 3
        for attempt in range(retries):
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    with open(output_path, "wb") as f:
                        f.write(response.read())
                print(f"[SUCCESS] Đã tải thành công: {output_path}")
                success = True
                break
            except Exception as e:
                print(f"[WARNING] Lỗi khi tải sơ đồ {name} (Lần thử {attempt + 1}/{retries}): {e}")
                time.sleep(2)
        
        if not success:
            print(f"[ERROR] Không thể kết xuất sơ đồ {name} sau {retries} lần thử.")
            # Tạo một hình ảnh trống/lỗi giả nếu muốn, hoặc bỏ qua để người dùng kiểm tra lại mạng

if __name__ == "__main__":
    generate_png_diagrams()
