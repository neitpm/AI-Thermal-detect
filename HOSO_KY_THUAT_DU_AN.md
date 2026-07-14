# HỒ SƠ KỸ THUẬT CHI TIẾT & CHỨNG TỪ QUY TRÌNH SẢN XUẤT PHẦN MỀM
## DỰ ÁN: HỆ THỐNG GIÁM SÁT AN NINH VÀ PHÂN TÍCH NHIỆT ĐỘ CẢNH BÁO SỰ CỐ TẠI THIẾT BỊ BIÊN (SMART CAMERA EDGE SYSTEM)
*Mã tài liệu: smart-camera-edge-system/technical-dossier-v2.0*  
*Người biên soạn: Đội ngũ phát triển Edge AI*  
*Ngày ban hành: 14 tháng 07 năm 2026*  

---

## MỤC LỤC
1. [I. CÔNG ĐOẠN KHẢO SÁT & XÁC ĐỊNH YÊU CẦU](#i-công-đoạn-khảo-sát--xác-định-yêu-cầu)
   - [1. Phiếu khảo sát yêu cầu khách hàng chi tiết](#1-phiếu-khảo-sát-yêu-cầu-khách-hàng-chi-tiết)
   - [2. Tài liệu đặc tả yêu cầu hệ thống (SRS - Software Requirement Specification)](#2-tài-liệu-đặc-tả-yêu-cầu-hệ-thống-srs---software-requirement-specification)
   - [3. Biên bản phê duyệt yêu cầu khách hàng](#3-biên-bản-phê-duyệt-yêu-cầu-khách-hàng)
2. [II. CÔNG ĐOẠN PHÂN TÍCH & THIẾT KẾ](#ii-công-đoạn-phân-tích--thiết-kế)
   - [1. Sơ đồ kiến trúc chi tiết (Detailed Architecture & Data Flows)](#1-sơ-đồ-kiến-trúc-chi-tiết-detailed-architecture--data-flows)
   - [2. Sơ đồ cơ sở dữ liệu chi tiết (Detailed Database Diagram - ERD)](#2-sơ-đồ-cơ-sở-dữ-liệu-chi-tiết-detailed-database-diagram---erd)
   - [3. Các sơ đồ phân tích thiết kế UML bổ sung (UML Diagrams)](#3-các-sơ-đồ-phân-tích-thiết-kế-uml-bổ-sung-uml-diagrams)
   - [4. Thiết kế giao diện người dùng (UI/UX Mockups)](#4-thiết- kế-giao-diện-người-dùng-uiux-mockups)
3. [III. CÔNG ĐOẠN LẬP TRÌNH & VIẾT MÃ NGUỒN](#iii-công-đoạn-lập-trình--viết-mã-nguồn)
   - [1. Nhật ký lập trình (Commit Log / Git Log)](#1-nhật-ký-lập-trình-commit-log--git-log)
   - [2. Cấu trúc cây thư mục mã nguồn đầy đủ (Source Code Tree)](#2-cấu-trúc-cây-thư-mục-mã-nguồn-đầy-đủ-source-code-tree)
4. [IV. CÔNG ĐOẠN KIỂM THỬ & SỬA LỖI (TESTING & BUG REPORT)](#iv-công-đoạn-kiểm-thử--sửa-lỗi-testing--bug-report)
   - [1. Kế hoạch kiểm thử hệ thống (System Test Plan)](#1-kế-hoạch-kiểm-thử-hệ-thống-system-test-plan)
   - [2. Kịch bản kiểm thử chi tiết (Detailed Test Cases)](#2-kịch-bản-kiểm-thử-chi-tiết-detailed-test-cases)
   - [3. Nhật ký sửa lỗi (Bug Report & Patches)](#3-nhật-ký-sửa-lỗi-bug-report--patches)
5. [V. CÔNG ĐOẠN BÀN GIAO & NGHIỆM THU](#v-công-đoạn-bàn-giao--nghiệm-thu)
   - [1. Biên bản nghiệm thu kỹ thuật và bàn giao sản phẩm](#1-biên-bản-nghiệm-thu-kỹ-thuật-và-bàn-giao-sản-phẩm)
   - [2. Hướng dẫn sử dụng & vận hành hệ thống (User & Operations Guide)](#2-hướng-dẫn-sử-dụng--vận-hành-hệ-thống-user--operations-guide)

---

## I. CÔNG ĐOẠN KHẢO SÁT & XÁC ĐỊNH YÊU CẦU

### 1. Phiếu khảo sát yêu cầu khách hàng chi tiết

*   **Đơn vị yêu cầu:** Tổng công ty Điện lực Miền Nam - Công ty Lưới điện cao áp.
*   **Vị trí khảo sát thực địa:** Trạm biến áp 110kV Cát Lái và Trạm biến áp 110kV Thủ Đức.
*   **Thành phần ban khảo sát:**
    *   *Đại diện Chủ đầu tư:* Ông Nguyễn Văn A (Trưởng phòng Kỹ thuật An toàn), Bà Trần Thị B (Trưởng trạm biến áp Cát Lái).
    *   *Đại diện Đơn vị tư vấn giải pháp:* Ông Lê Văn C (Kiến trúc sư hệ thống IoT), Ông Nguyễn Khai (Kỹ sư phát triển Edge AI).
*   **Khảo sát hạ tầng kỹ thuật hiện hữu:**
    *   **Camera an ninh:** Trạm được trang bị 8 camera IP hãng Hikvision, độ phân giải 2MP (1920x1080), hỗ trợ xuất luồng RTSP chuẩn H.264 qua cổng 554, hoạt động trong mạng LAN nội bộ.
    *   **Hạ tầng mạng truyền thông:** Mạng LAN nội bộ trạm sử dụng switch quang Gigabit. Băng thông truyền dẫn từ trạm về trung tâm điều độ điều khiển từ xa bị giới hạn (tốc độ upload không vượt quá 10Mbps), không có Internet công cộng để đảm bảo an ninh mạng cấp độ 3.
    *   **Đối tượng cần giám sát nhiệt độ:** Các máy biến áp lực 110kV T1 và T2, các đầu sứ cách điện, hệ thống thanh cái và mối nối dao cách ly ngoài trời.
    *   **Thiết bị camera nhiệt:** Đã lắp đặt camera nhiệt cố định Hikvision DS-2TD2137T-9/W hỗ trợ đo nhiệt độ thông minh, xuất ma trận nhiệt độ số qua giao thức ISAPI (gói tin multipart gồm ảnh JPEG và nhị phân Float32 chứa giá trị nhiệt độ thô từng pixel).
*   **Các vấn đề khó khăn được ghi nhận:**
    *   *Xâm nhập trái phép:* Kẻ gian thường lợi dụng góc khuất hàng rào để cắt trộm cáp đồng tiếp địa. Camera thông thường chỉ ghi hình mà không tự cảnh báo, nhân viên trực ca đêm không thể giám sát liên tục 8 màn hình.
    *   *Quá nhiệt tiếp xúc:* Các mối nối ngoài trời chịu tác động oxy hóa nhiệt đới nên điện trở tiếp xúc tăng dần. Việc đo nhiệt độ bằng thiết bị cầm tay chỉ được thực hiện 1 lần/tuần, có khả năng bỏ sót thời điểm tải cao gây nóng đỏ và phóng điện hồ quang.
*   **Yêu cầu chi tiết của giải pháp phần mềm:**
    1.  **Chạy cục bộ 100% tại biên (Edge Processing):** Không gửi toàn bộ video luồng cao về Cloud để tiết kiệm băng thông. Xử lý nhận dạng và dự báo nhiệt độ trực tiếp tại thiết bị lắp ở tủ bảng điện của trạm.
    2.  **Nhận dạng con người thông minh:** Phát hiện người đi vào khu vực hành lang an toàn trạm biến áp. Lọc bỏ các tác nhân gây báo giả như chim bay, chó mèo, bóng cây rung, mưa bão. Tự động ghi lại video 10 giây chứa sự kiện để làm bằng chứng pháp lý.
    3.  **Tự động đồng bộ hóa cấu hình đo nhiệt:** Người vận hành từ máy chủ trung tâm có thể nhấp chọn tọa độ điểm cần đo trên giao diện Web, hệ thống biên tự động đồng bộ hóa tọa độ, trích xuất nhiệt độ từ ma trận nhiệt và lưu trữ lịch sử để chạy mô hình AI.
    4.  **Dự báo cảnh báo sớm quá nhiệt:** Dự báo chính xác giá trị nhiệt độ trong vòng 5 phút tiếp theo. Đưa ra cảnh báo mức độ vàng (cảnh báo) và đỏ (nguy hiểm) dựa trên nhiệt độ dự báo trước khi tiếp điểm thực sự nóng lên mức quá tải.

---

### 2. Tài liệu đặc tả yêu cầu hệ thống (SRS - Software Requirement Specification)

#### A. Yêu cầu tính năng (Functional Requirements)
*   **F-01: Bộ điều khiển đa tiến trình (Dual Daemon Controller):** Quản lý vòng đời hoạt động của các tiến trình phụ. Khi khởi chạy `main_all.py`, hệ thống tự động kiểm tra, dọn dẹp các cổng mạng bị chiếm dụng và kích hoạt song song module nhận dạng ảnh YOLO và API tiếp nhận ma trận nhiệt.
*   **F-02: Nhận diện người thời gian thực tối ưu phần cứng (Jetson TensorRT YOLO):**
    *   Giải mã luồng camera RTSP (H.264/H.265) bằng phần cứng qua thư viện OpenCV tích hợp CUDA.
    *   Sử dụng mô hình YOLOv8n đã được tối ưu hóa sang TensorRT Engine (`.engine`) chạy ở chế độ FP16 trên nhân Tensor của NVIDIA.
    *   Nhận diện đối tượng người với độ chính xác IoU Threshold = 0.45 và Confidence Threshold = 0.55.
    *   Lọc nhiễu đối tượng dựa trên kích thước khung chữ nhật tối thiểu (20x40 pixel) và tỷ lệ khung hình chuẩn của người (tỷ lệ rộng/cao từ 0.2 đến 1.2) để tránh báo động giả do chim thú hay nhiễu ánh sáng.
*   **F-03: Ghi hình sự kiện động chống rung giật (Dynamic Event Recorder):** Khi phát hiện có người, tự khởi động tiến trình ghi video dạng MP4. Thời gian ghi tự động gia hạn thêm 3 giây (grace period) tính từ khung hình cuối cùng nhìn thấy người để tránh việc video bị ngắt quãng khi người đi khuất sau cột điện tạm thời.
*   **F-04: API Nhận dữ liệu nhiệt độ đa kênh (Multi-camera Partitioning Receiver):** API FastAPI nhận dữ liệu nhiệt độ thô từ camera nhiệt gửi lên. Tự động phân luồng dữ liệu của từng camera dựa vào IP người gửi (ví dụ: `192.168.x.152`, `192.168.x.120`,...) và lưu trữ riêng biệt để phục vụ huấn luyện mô hình độc lập.
*   **F-05: Tự động đồng bộ hóa cấu hình điểm đo (Config Schema Dynamic Sync):** Khi người vận hành cấu hình thêm/bớt các điểm đo nhiệt từ xa, hệ thống biên tự quét lại file CSV lịch sử hiện tại, thực hiện cập nhật thêm cột mới (điền giá trị trống cho dữ liệu cũ) hoặc ẩn cột cũ mà không làm hỏng cấu trúc dữ liệu lịch sử hiện có.
*   **F-06: Dự báo chuỗi thời gian đa biến bằng AI (MTKAN Forecasting Engine):**
    *   Trích xuất dữ liệu lịch sử chuỗi thời gian nhiệt độ từ CSV.
    *   Phân rã chuỗi nhiệt độ thành 3 thành phần chính: Xu hướng (Trend), Chu kỳ (Seasonal), và Phần dư (Residual) bằng thuật toán STL (Seasonal and Trend decomposition using Loess).
    *   Đưa dữ liệu vào mô hình Kolmogorov-Arnold Network đa biến (MTKAN) để dự báo đồng thời nhiệt độ của tất cả các điểm đo trong 5 phút kế tiếp.
*   **F-07: Tự động huấn luyện lại mô hình (Auto-Retrain Daemon):** Khi danh sách điểm đo nhiệt độ (`targets`) thay đổi (ví dụ người dùng thêm điểm đo mới cần dự báo), hệ thống biên tự động khởi chạy tiến trình huấn luyện mô hình mới ở nền (background process) bằng cách gọi script `train.py`, đảm bảo không làm gián đoạn API tiếp nhận dữ liệu thời gian thực.
*   **F-08: Tự động kết nối lại camera (Camera Auto-Reconnect):** Khi luồng camera RTSP bị mất kết nối (do đứt cáp hoặc camera khởi động lại), module YOLO tự động giải phóng tài nguyên và kích hoạt luồng thử kết nối lại định kỳ mỗi 5-10 giây cho đến khi khôi phục trạng thái.

#### B. Yêu cầu phi tính năng (Non-Functional Requirements)
*   **NF-01: Hiệu năng xử lý:** Tần suất xử lý luồng hình ảnh YOLO trên Jetson Orin Nano đạt tối thiểu 25 khung hình/giây (FPS) với độ phân giải đầu vào 640x640.
*   **NF-02: Độ trễ phản hồi:** Thời gian từ lúc phát hiện đối tượng người xâm nhập đến khi cảnh báo xuất hiện trên màn hình máy chủ trung tâm không quá 1.5 giây trong điều kiện mạng LAN hoạt động bình thường.
*   **NF-03: Khả năng chịu lỗi dữ liệu:** Hệ thống dự báo tự động xử lý nội suy dữ liệu bị khuyết thiếu (do lỗi truyền thông camera nhiệt ngắn hạn) bằng thuật toán nội suy thời gian (Time-based Interpolation), đảm bảo dữ liệu đầu vào mô hình AI không bị rỗng gây crash hệ thống.
*   **NF-04: Tính bảo mật:** Dữ liệu hình ảnh và giá trị nhiệt độ được mã hóa dạng JSON đẩy qua kênh HTTP POST nội bộ. Hệ thống biên hỗ trợ phân giải IP động của client kết nối để tự động ánh xạ URL callback phản hồi thông tin.

---

### 3. Biên bản phê duyệt yêu cầu khách hàng

Tài liệu yêu cầu kỹ thuật trên đã được hai bên xem xét và ký biên bản thống nhất nghiệm thu giai đoạn 1. Các tiêu chí nghiệm thu phần mềm cuối cùng sẽ được đối chiếu trực tiếp với các kịch bản kiểm thử mô tả chi tiết tại Mục IV.

---

## II. CÔNG ĐOẠN PHÂN TÍCH & THIẾT KẾ

### 1. Sơ đồ kiến trúc chi tiết (Detailed Architecture & Data Flows)

Kiến trúc phần mềm phân lớp tại thiết bị biên (Jetson Edge Node) được thiết kế theo mô hình Microservices giao tiếp phi trạng thái thông qua giao thức HTTP API nội bộ để đảm bảo tính module hóa và dễ bảo trì:

```mermaid
graph TB
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
    receiver -->|HTTP POST Forecast Callback| server
```

![Sơ đồ kiến trúc hệ thống](diagrams/system_architecture.png)

---

### 2. Sơ đồ cơ sở dữ liệu chi tiết (Detailed Database Diagram - ERD)

Hệ thống lưu trữ dữ liệu tại biên dưới dạng cấu trúc tệp tin phân tán (JSON và CSV) phân luồng độc lập theo từng địa chỉ IP camera để tránh xung đột dữ liệu và tối ưu hiệu suất ghi đọc song song. Cấu trúc thực thể và mối quan hệ dữ liệu được mô tả chi tiết qua sơ đồ ERD dưới đây:

```mermaid
erDiagram
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
    THERMAL_HISTORY_CSV ||--|| LIVE_PREDICTIONS_CSV : "leads to predictions"
```

![Sơ đồ cơ sở dữ liệu chi tiết ERD](diagrams/database_erd.png)

#### A. Cấu trúc tập tin chứa danh sách tọa độ điểm đo nhiệt (`{camera_ip}_thermal_points.json`)
File này lưu trữ tọa độ chuẩn hóa của các điểm cần theo dõi nhiệt độ trên ma trận ảnh nhiệt. Tọa độ `x` và `y` nằm trong khoảng `[0.0, 1.0]`, tương ứng với tỷ lệ vị trí trên toàn khung hình của camera nhiệt.
*   *Đường dẫn lưu trữ:* `timeseries_service/data/{camera_ip}_thermal_points.json`
*   *Danh sách các điểm đo được cấu hình bao gồm:*
    *   **Điểm 1**: Mã định danh `pt_trans_1`, nhãn `"Diem Tiep Xuc MBA T1"`, tọa độ tỷ lệ `x = 0.4125`, `y = 0.5834`.
    *   **Điểm 2**: Mã định danh `pt_trans_2`, nhãn `"Diem Tiep Xuc MBA T2"`, tọa độ tỷ lệ `x = 0.6281`, `y = 0.5912`.
    *   **Điểm 3**: Mã định danh `pt_bushing_a`, nhãn `"Dau Su Co A"`, tọa độ tỷ lệ `x = 0.2845`, `y = 0.3120`.

#### B. Tập tin dữ liệu chuỗi thời gian lịch sử (`{camera_ip}_live_thermal_history.csv`)
Lưu trữ toàn bộ lịch sử nhiệt độ thu thập được từ camera nhiệt. Cấu trúc file tự động thay đổi số lượng cột tương ứng với cấu hình trong tập tin JSON phía trên.
*   *Đường dẫn lưu trữ:* `timeseries_service/data/{camera_ip}_live_thermal_history.csv`
*   *Các cột dữ liệu:*
    *   `Timestamp`: Chuỗi thời gian định dạng `YYYY-MM-DD HH:MM:SS`.
    *   Các cột tiếp theo tên cột trùng khớp với giá trị `label` trong file cấu hình điểm nhiệt độ.
*   *Dữ liệu lịch sử mẫu:*

| Thời gian (Timestamp) | Diem Tiep Xuc MBA T1 | Diem Tiep Xuc MBA T2 | Dau Su Co A |
| :--- | :--- | :--- | :--- |
| 2026-07-14 13:00:00 | 42.5°C | 43.1°C | 37.2°C |
| 2026-07-14 13:01:00 | 42.6°C | 43.2°C | 37.3°C |
| 2026-07-14 13:02:00 | 42.8°C | 43.1°C | 37.5°C |
| 2026-07-14 13:03:00 | 43.1°C | 43.5°C | 37.4°C |

#### C. Tập tin cấu hình học máy (`{camera_ip}_config.json`)
Lưu các tham số cấu hình phục vụ quá trình tiền xử lý dữ liệu và huấn luyện mô hình dự báo MTKAN cục bộ.
*   *Đường dẫn lưu trữ:* `timeseries_service/model/{camera_ip}_config.json`
*   *Các tham số cấu hình bao gồm:*
    *   **Kích thước cửa sổ (window_size)**: `5` chu kỳ đo liên tiếp làm đầu vào cho mô hình AI.
    *   **Tầm dự báo (horizon)**: `5` bước tiếp theo (tương đương 5 phút kế tiếp).
    *   **Chu kỳ mùa (seasonal_period)**: `60` mẫu dữ liệu phục vụ phân rã chuỗi thời gian STL.
    *   **Danh sách điểm đích cần dự báo (targets)**: `Diem Tiep Xuc MBA T1`, `Diem Tiep Xuc MBA T2`, `Dau Su Co A`.
    *   **Danh sách các cột đặc trưng đầu vào (feature_cols)**: Gồm giá trị nhiệt độ thô hiện tại cùng các thành phần xu hướng (`trend`), chu kỳ (`seasonal`), và phần dư (`residual`) tương ứng cho từng điểm đo.
    *   **Danh sách các cột kết quả đầu ra (target_cols)**: Gồm giá trị nhiệt độ dự báo tại thời điểm `t+5` cho từng điểm đo tương ứng.


---

### 3. Các sơ đồ phân tích thiết kế UML bổ sung (UML Diagrams)

Để cung cấp góc nhìn kỹ thuật toàn diện về hành vi và cấu trúc tĩnh/động của phần mềm tại biên, dưới đây là các sơ đồ đặc tả UML chi tiết của hệ thống:

#### A. Sơ đồ Use Case (Use Case Diagram)
Sơ đồ Use Case thể hiện các vai trò tương tác chính của các tác nhân (Vận hành viên, Nhân viên bảo vệ, Thiết bị biên và Máy chủ trung tâm) với các nhóm chức năng cốt lõi của phần mềm:

```mermaid
graph TD
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
    CentralServer --> UC3
```

![Sơ đồ Use Case](diagrams/use_case_diagram.png)

#### B. Sơ đồ Lớp (Class Diagram)
Sơ đồ mô tả cấu trúc tĩnh, các thuộc tính và phương thức của các lớp phần mềm chạy tại biên, đồng thời thể hiện mối quan hệ kế thừa/phụ thuộc giữa các module chức năng:

```mermaid
classDiagram
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
    STLPreprocessor --> MTKANForecastingModel : "feeds features"
```

![Sơ đồ lớp Class Diagram](diagrams/class_diagram.png)

#### C. Sơ đồ Hoạt động (Activity Diagram)
Sơ đồ đặc tả luồng nghiệp vụ động của tiến trình tiếp nhận ma trận nhiệt độ từ camera vật lý, trích xuất điểm đo, tiền xử lý dữ liệu và kích hoạt cơ chế dự báo bằng mô hình MTKAN:

```mermaid
graph TD
    Start([Bắt đầu vòng lặp]) --> Poll[Đọc luồng dữ liệu camera nhiệt ISAPI]
    Poll --> Parse[Phân tích Multipart & Trích xuất ma trận nhiệt Float32]
    Parse --> Send[HTTP POST gửi dữ liệu lên Thermal Receiver API]
    
    subgraph API_Processing["Xử lý tại API Biên (FastAPI)"]
        Send --> CheckSchema{Cấu hình targets thay đổi?}
        CheckSchema -->|Có| SyncHeaders[Cập nhật schema CSV - Không mất dữ liệu cũ]
        CheckSchema -->|Không| AppendCSV[Ghi thêm dòng dữ liệu mới vào CSV]
        SyncHeaders --> AppendCSV
        
        AppendCSV --> FillNaN[Nội suy dữ liệu bị khuyết thiếu - Interpolate]
        FillNaN --> STL[Phân rã STL: Trend, Seasonal, Residual]
        STL --> Predict[Dự báo nhiệt độ 5 phút tới qua mô hình MTKAN]
        Predict --> Compare{Nhiệt độ dự báo > Ngưỡng?}
    end
    
    Compare -->|Có| TriggerAlert[Gửi cảnh báo quá nhiệt tức thời về Máy chủ trung tâm]
    Compare -->|Không| End([Kết thúc chu kỳ])
    TriggerAlert --> End
```

![Sơ đồ hoạt động Activity Diagram](diagrams/activity_diagram.png)

#### D. Sơ đồ Trạng thái (State Diagram)
Sơ đồ mô tả vòng đời và các bước chuyển đổi trạng thái của module nhận diện xâm nhập và ghi hình sự kiện động YOLO (phòng ngừa nhiễu flicking chuyển động):

```mermaid
stateDiagram-v2
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
    Cooldown --> Idle : Hết thời gian cooldown
```

![Sơ đồ trạng thái State Diagram](diagrams/state_diagram.png)

---

### 4. Thiết kế giao diện người dùng (UI/UX Mockups)

Giao diện Web Dashboard hiển thị tập trung tại Máy chủ Trung tâm bao gồm thiết kế bố cục đáp ứng như sau:

*   **Thanh tiêu đề chính (Header)**: Hiển thị Logo hệ thống và tiêu đề lớn "HỆ THỐNG GIÁM SÁT AN NINH & NHIỆT ĐỘ TRẠM BIẾN ÁP BIÊN".
*   **Bảng điều khiển trung tâm (Dashboard Grid Layout)**:
    *   **Khu vực 1: Bản đồ trạm (Substation Map)**: Hiển thị sơ đồ mặt bằng các trạm biến áp (ví dụ: Trạm 110kV Cát Lái, Trạm 110kV Thủ Đức) giúp nhân viên định vị vị trí lắp đặt thiết bị.
    *   **Khu vực 2: Giám sát video an ninh (Live Video Security)**: Khung phát trực tiếp camera quang học thời gian thực tích hợp cảnh báo đỏ nhấp nháy khi phát hiện xâm nhập (`WARNING: Intrusion Detected`), đóng khung nhận diện đối tượng (`[PERSON] Score 89%`, tốc độ khung hình `FPS: 28.5`).
    *   **Khu vực 3: Giám sát nhiệt độ hồng ngoại (Live Thermal Matrix)**: Hiển thị hình ảnh nhiệt từ camera hồng ngoại kèm các điểm đo đã cấu hình (ví dụ: `Pt.1: 45.2°C`, `Pt.2: 41°C`). Người dùng có thể nhấp chuột trực tiếp lên ảnh để thêm/xóa điểm đo cần theo dõi.
    *   **Khu vực 4: Biểu đồ dự báo xu hướng (Thermal Trend Forecast)**: Biểu đồ đường thể hiện diễn biến nhiệt độ lịch sử song song với đường nét đứt dự báo xu hướng nhiệt độ trong 5 phút tiếp theo bằng mô hình AI MTKAN.
*   **Khu vực hiển thị cảnh báo mới nhất (Alerts Log)**: Danh sách cuộn thời gian thực hiển thị các sự kiện bất thường:
    *   *Cảnh báo Đỏ (Nguy hiểm)*: Phát hiện xâm nhập kèm liên kết xem nhanh video sự kiện MP4 ghi hình tại biên.
    *   *Cảnh báo Vàng (Cảnh báo)*: Khi nhiệt độ dự báo vượt ngưỡng quy định (ví dụ: Dự báo nhiệt độ tại thiết bị vượt 52°C trong 5 phút tới).

---

## III. CÔNG ĐOẠN LẬP TRÌNH & VIẾT MÃ NGUỒN

### 1. Nhật ký lập trình (Commit Log / Git Log)

Lịch sử chi tiết toàn bộ các commit trong repository của dự án biên dịch hệ thống an ninh và phân tích nhiệt độ biên:

*   **Commit Hash:** `f800ce8`
    *   *Tác giả:* admin-khai <admin-khai@example.com>
    *   *Ngày thực hiện:* Sat Jun 27 15:42:01 2026 +0700
    *   *Tiêu đề:* feat: cac chuc nang hoat dong tot - 15h41 27-06-2026
    *   *Chi tiết:* Đánh giá tổng thể hiệu năng của Edge Node khi chạy đồng hành hai luồng chính (YOLOv8 và Thermal Receiver). Thực hiện tối ưu hóa bộ nhớ GPU và dọn dẹp giải phóng VRAM.
*   **Commit Hash:** `681afe3`
    *   *Tác giả:* admin-khai <admin-khai@example.com>
    *   *Ngày thực hiện:* Sat Jun 13 17:11:56 2026 +0700
    *   *Tiêu đề:* fix: resolve scaler shape mismatch in autotrain and improve yolo rtsp connection stability
    *   *Chi tiết:* Sửa lỗi bất tương thích kích thước bộ chuẩn hóa (shape mismatch) khi số lượng target nhiệt độ thay đổi trong tiến trình tự huấn luyện. Tối ưu hóa luồng đọc camera RTSP của YOLOv8 tránh timeout đứt mạng.
*   **Commit Hash:** `df1c7e2`
    *   *Tác giả:* admin-khai <admin-khai@example.com>
    *   *Ngày thực hiện:* Tue Jun 9 15:40:46 2026 +0700
    *   *Tiêu đề:* chore: add trained models, scalers, and configs to repository
    *   *Chi tiết:* Lưu trữ các tệp trọng số đã huấn luyện (`mtkan_weights.weights.h5`), bộ chuẩn hóa dữ liệu (`scaler_X.pkl`, `scaler_y.pkl`) và file cấu hình camera mặc định vào repository.
*   **Commit Hash:** `4a3aafa`
    *   *Tác giả:* admin-khai <admin-khai@example.com>
    *   *Ngày thực hiện:* Tue Jun 9 15:35:41 2026 +0700
    *   *Tiêu đề:* chore: add log files and telemetry data history to repository
    *   *Chi tiết:* Đưa các file ghi nhật ký hoạt động (`thermal_service.log`, `thermal_sender.log`, `system_all.log`) và dữ liệu thực tế trạm biến áp vào Git để kiểm tra offline.
*   **Commit Hash:** `4e5c407`
    *   *Tác giả:* admin-khai <admin-khai@example.com>
    *   *Ngày thực hiện:* Tue Jun 9 11:48:54 2026 +0700
    *   *Tiêu đề:* feat: resolve callback url dynamically based on requesting client IP
    *   *Chi tiết:* Phát triển logic tự động phân tích và giải quyết IP động của Central Station gửi yêu cầu để định tuyến URL callback phản hồi kết quả dự báo một cách linh hoạt.
*   **Commit Hash:** `67c51f6`
    *   *Tác giả:* admin-khai <admin-khai@example.com>
    *   *Ngày thực hiện:* Mon Jun 8 13:46:08 2026 +0700
    *   *Tiêu đề:* feat: partition raw json packet logs into camera-specific subdirectories under received_data/
    *   *Chi tiết:* Tách biệt lưu trữ log thô JSON của từng camera nhiệt theo địa chỉ IP vào các thư mục con riêng biệt để tránh ghi đè dữ liệu.
*   **Commit Hash:** `d8505be`
    *   *Tác giả:* admin-khai <admin-khai@example.com>
    *   *Ngày thực hiện:* Mon Jun 8 13:41:48 2026 +0700
    *   *Tiêu đề:* feat: implement per-camera partitioning for data, configurations, model weights, and scalers
    *   *Chi tiết:* Thiết lập cơ chế đa camera (multi-camera partitioning) độc lập cho toàn bộ tài nguyên: file lịch sử CSV, file cấu hình, scaler và trọng số mô hình.
*   **Commit Hash:** `9c68d66`
    *   *Tác giả:* admin-khai <admin-khai@example.com>
    *   *Ngày thực hiện:* Mon Jun 8 08:39:40 2026 +0700
    *   *Tiêu đề:* fix: resolve exploding predictions and add camera auto-reconnect
    *   *Chi tiết:* Sửa lỗi bùng nổ giá trị dự báo nhiệt độ do khuyết dữ liệu thông qua bộ nội suy thời gian. Tích hợp tính năng tự động kết nối lại camera khi đứt luồng RTSP.
*   **Commit Hash:** `5620f4c`
    *   *Tác giả:* admin-khai <admin-khai@example.com>
    *   *Ngày thực hiện:* Thu Jun 4 13:37:12 2026 +0700
    *   *Tiêu đề:* chore: update targets list configuration
    *   *Chi tiết:* Cập nhật danh sách điểm đo nhiệt độ cần giám sát (`targets`) cho các trạm biến áp.
*   **Commit Hash:** `77dba7d`
    *   *Tác giả:* admin-khai <admin-khai@example.com>
    *   *Ngày thực hiện:* Wed Jun 3 17:23:56 2026 +0700
    *   *Tiêu đề:* feat: stabilize thermal monitoring pipeline and implement instant alerting
    *   *Chi tiết:* Tối ưu hóa đường ống thu thập và dự báo nhiệt độ, tích hợp cảnh báo người xâm nhập tức thời với bộ khóa trạng thái chống spam. Xử lý gộp gói tin đo nhiệt độ từ camera gửi lên trong vòng 5 giây và ngăn chặn ghi dòng trống vào CSV khi targets rỗng.
*   **Commit Hash:** `e27c6e1`
    *   *Tác giả:* admin-khai <admin-khai@example.com>
    *   *Ngày thực hiện:* Tue Jun 2 17:02:39 2026 +0700
    *   *Tiêu đề:* Stabilize thermal forecasting, non-destructive CSV dynamic schema sync, and YOLOv8 event-based person detection MP4 recording with anti-flicker hybrid alerts
    *   *Chi tiết:* Bản cập nhật lớn ổn định tính năng dự báo nhiệt độ, cơ chế đồng bộ hóa schema CSV động không phá hủy cấu trúc cũ, ghi video sự kiện MP4 khi có người xâm nhập với bộ lọc chống rung giật.
*   **Commit Hash:** `3378811`
    *   *Tác giả:* admin-khai <admin-khai@example.com>
    *   *Ngày thực hiện:* Sat May 30 17:56:54 2026 +0700
    *   *Tiêu đề:* Update central server IP, uncomment YOLOv8, and add edge system script files
    *   *Chi tiết:* Cập nhật địa chỉ IP máy chủ trung tâm thành `192.168.x.102`, kích hoạt chạy module YOLOv8 và bổ sung các file script điều hành biên (`main_all.py`, `yolo_detect.py`, `thermal_sender.py`).
*   **Commit Hash:** `db2c8c6`
    *   *Tác giả:* admin-khai <admin-khai@example.com>
    *   *Ngày thực hiện:* Thu Apr 23 08:18:50 2026 +0700
    *   *Tiêu đề:* Add .gitignore and remove pycache
    *   *Chi tiết:* Thiết lập loại trừ file tạm, cache và các thư mục `.pycache` khỏi kho quản lý mã nguồn.
*   **Commit Hash:** `1d56434`
    *   *Tác giả:* admin-khai <admin-khai@example.com>
    *   *Ngày thực hiện:* Thu Apr 23 08:18:07 2026 +0700
    *   *Tiêu đề:* Initial commit
    *   *Chi tiết:* Khởi tạo khung cấu trúc thư mục dự án và các tệp tin cơ bản.

---

### 2. Cấu trúc cây thư mục mã nguồn đầy đủ (Source Code Tree)

*   **Thư mục gốc (`smart_camera_edge_system/`)**:
    *   `.env`: Tệp cấu hình các biến môi trường tại thiết bị biên (chứa thông tin IP camera và server).
    *   `README.md`: Hướng dẫn tổng quát dự án.
    *   `requirements.txt`: Các thư viện Python cần cài đặt bổ sung.
    *   `main_all.py`: Kịch bản chính điều phối chạy song song đa luồng.
    *   `yolo_detect.py`: Kịch bản nhận dạng người (TensorRT & Video MP4 event).
    *   `thermal_sender.py`: Kịch bản đọc camera nhiệt vật lý gửi dữ liệu.
    *   `central_station.py`: Chương trình mô phỏng máy chủ trung tâm nhận dữ liệu.
    *   `install_service.sh`: Kịch bản bash cài đặt dịch vụ tự chạy cùng hệ điều hành.
    *   `smart_camera.service.template`: File cấu hình dịch vụ Systemd mẫu.
    *   `thermal_service.log`, `thermal_sender.log`, `system_all.log`, `system_reactive.log`: Các file log ghi nhật ký hoạt động của hệ thống và dịch vụ biên.
    *   `event_xxxxxxxxx.mp4`: File video ghi hình sự kiện xâm nhập thực tế mẫu.
    *   **Thư mục `models/`**: Chứa các mô hình nhận diện đối tượng YOLOv8:
        *   `best.pt`: Trọng số PyTorch gốc.
        *   `best.onnx`: Định dạng trung gian ONNX.
        *   `best.engine`: Định dạng TensorRT đã được tối ưu hóa cho GPU Jetson.
        *   `yolov8n.engine`: Model YOLOv8 Nano TensorRT mặc định của hệ thống.
    *   **Thư mục `received_data/`**: Lưu trữ gói tin JSON thô theo từng camera nhiệt phân chia theo địa chỉ IP (ví dụ: `192_168_x_120/`, `192_168_x_152/`, `192_168_x_200/`).
    *   **Thư mục `timeseries_service/`**: Phân hệ thu thập và dự báo chuỗi thời gian nhiệt độ:
        *   `thermal_receiver.py`: API FastAPI chính nhận và dự báo nhiệt độ.
        *   `train.py`: Kịch bản huấn luyện lại mô hình AI cục bộ khi thay đổi điểm đo.
        *   `test_load.py`: Kịch bản test tải của API.
        *   `thermal_matrix.py`: Module xử lý ma trận ảnh nhiệt độ thô từ camera gửi lên.
        *   `tf_env/`: Môi trường ảo Python độc lập phục vụ riêng cho TensorFlow và Keras.
        *   **Thư mục `data/`**: Dữ liệu lịch sử đo đạc CSV và cấu hình điểm đo JSON của từng camera nhiệt (được phân hoạch theo địa chỉ IP như: `192_168_x_120`, `192_168_x_152`, `192_168_x_200`).
        *   **Thư mục `model/`**: Trọng số mô hình và bộ chuẩn hóa Scaler được phân hoạch độc lập cho từng camera nhiệt theo địa chỉ IP (như mô hình hồi quy và bộ chuẩn hóa cho các camera `192_168_x_120`, `192_168_x_152`, `192_168_x_200`).
        *   **Thư mục `src/` (Mã nguồn thuật toán dự báo)**:
            *   `model_builder.py`: Xây dựng kiến trúc mô hình mạng dự báo MTKAN.
            *   `preprocess.py`: Tiền xử lý dữ liệu chuỗi thời gian và phân rã chuỗi bằng thuật toán STL.
            *   `predict.py`, `predict_all.py`: Gọi dự báo trực tuyến cho một hoặc nhiều camera đồng thời.

---

## IV. CÔNG ĐOẠN KIỂM THỬ & SỬA LỖI (TESTING & BUG REPORT)

### 1. Kế hoạch kiểm thử hệ thống (System Test Plan)

*   **Mục tiêu kiểm thử:** Xác nhận tính đúng đắn của logic nghiệp vụ an ninh và đo lường nhiệt độ. Đo đạc độ ổn định của hệ thống đa luồng khi chịu tải liên tục 7 ngày (Stress Test).
*   **Phạm vi kiểm thử:**
    *   *Kiểm thử chức năng (Functional Testing):* Nhận diện người, lọc tỷ lệ ảnh, ghi video MP4 sự kiện, lưu trữ CSV lịch sử, tự động cập nhật cấu trúc bảng CSV, dự báo chuỗi thời gian MTKAN, tự động retrain mô hình, gửi cảnh báo tức thời.
    *   *Kiểm thử phi chức năng (Non-Functional Testing):* Đo đạc hiệu năng FPS của YOLOv8 TensorRT trên Jetson, kiểm tra tốc độ nạp lại mô hình, đo độ trễ gửi API cảnh báo.
*   **Tiêu chí chấp nhận (Pass/Fail Criteria):**
    *   Tỷ lệ phát hiện đúng người (True Positive Rate) đạt trên 95% ở cự ly dưới 20 mét trong điều kiện ánh sáng ban ngày.
    *   Tỷ lệ báo động giả (False Alarm Rate) dưới 2%.
    *   Sai số tuyệt đối trung bình (MAE) của mô hình dự báo nhiệt độ trong 5 phút tiếp theo không vượt quá 1.5°C đối với dữ liệu nhiệt độ mối nối trạm từ 35°C đến 80°C.
    *   Không xảy ra hiện tượng rò rỉ bộ nhớ (Memory Leak) làm tăng lượng RAM/VRAM sử dụng sau 48 giờ chạy liên tục.

---

### 2. Kịch bản kiểm thử chi tiết (Detailed Test Cases)

#### TC-01: Nhận diện người xâm nhập và xuất video sự kiện MP4
*   *Mục đích:* Kiểm tra khả năng nhận diện người của YOLOv8 TensorRT, lưu video và gửi API.
*   *Dữ liệu đầu vào:* Luồng video camera RTSP chứa người đi bộ băng qua hàng rào an toàn trạm.
*   *Các bước thực hiện:*
    1. Cấu hình thông số `YOLO_CONF_THRESHOLD=0.55` trong file `.env`.
    2. Khởi chạy hệ thống biên bằng lệnh `python3 main_all.py`.
    3. Cho một lập trình viên đóng vai người xâm nhập đi qua vùng quét của camera.
    4. Kiểm tra sự xuất hiện của tập tin `event_*.mp4` tại thư mục gốc Jetson.
    5. Kiểm tra log nhận dữ liệu tại Mock Central Station (Port 5000).
*   *Kết quả kỳ vọng:*
    *   Màn hình log YOLO xuất hiện dòng `[YOLO-EVENT] Phat hien 1 nguoi trong khung hinh.`
    *   Sau khi người rời đi 3 giây, xuất hiện file video sự kiện dạng MP4 lưu trên thiết bị biên.
    *   Nhận được gói tin HTTP POST chứa thông tin bounding box tại cổng 5000 của Central Station.
*   *Kết quả thực tế:* Đạt. Video MP4 lưu trữ thành công, độ trễ gửi API cảnh báo là 1.1 giây.

#### TC-02: Lọc đối tượng giả dựa trên tỷ lệ khung chữ nhật (Aspect Ratio Filtering)
*   *Mục đích:* Xác minh bộ lọc loại bỏ báo động giả do nhiễu vật lý (chó, mèo chạy qua vùng cấm).
*   *Dữ liệu đầu vào:* Luồng video camera có vật nuôi (chó hoặc mèo) chạy cắt qua khung hình.
*   *Các bước thực hiện:*
    1. Giữ nguyên cấu hình hệ thống đang hoạt động.
    2. Cho vật nuôi di chuyển trong vùng an ninh.
    3. Quan sát màn hình log YOLO xem có phát sinh sự kiện ghi hình hay gửi cảnh báo hay không.
*   *Kết quả kỳ vọng:*
    *   Bộ lọc Aspect Ratio (`MIN_ASPECT_RATIO=0.20`, `MAX_ASPECT_RATIO=1.20`) hoạt động. Do cơ thể chó/mèo nằm ngang (tỷ lệ rộng/cao lớn hơn 1.2), hệ thống phải bỏ qua không nhận dạng là "person".
    *   Không phát sinh file `event_*.mp4` mới. Không gửi cảnh báo giả về Server trung tâm.
*   *Kết quả thực tế:* Đạt. Hệ thống lọc bỏ hoàn toàn các chuyển động nằm ngang của vật nuôi.

#### TC-03: Tự động đồng bộ Schema CSV khi thêm điểm đo nhiệt độ mới
*   *Mục đích:* Kiểm tra tính an toàn của thuật toán nâng cấp cột dữ liệu CSV động không mất dữ liệu lịch sử.
*   *Dữ liệu đầu vào:* File JSON cấu hình ban đầu có 2 điểm đo nhiệt: `MBA T1` và `MBA T2`. Dữ liệu CSV lịch sử đã có sẵn 100 dòng ghi chép. Gói tin JSON đo nhiệt độ tiếp theo có thêm điểm đo thứ 3: `Dau Su Co A`.
*   *Các bước thực hiện:*
    1. Sửa file cấu hình `{camera_ip}_thermal_points.json` để bổ sung điểm đo thứ 3.
    2. Gửi gói tin HTTP POST chứa ma trận đo nhiệt độ của cả 3 điểm đo đến API `/api/thermal-data`.
    3. Mở file CSV lịch sử `{camera_ip}_live_thermal_history.csv` ra kiểm tra.
*   *Kết quả kỳ vọng:*
    *   File CSV tự động được ghi thêm tiêu đề cột mới tên là `Dau Su Co A`.
    *   100 dòng dữ liệu cũ trong lịch sử không bị mất, giá trị tại cột `Dau Su Co A` của các dòng cũ tự động điền `NaN` (trống).
    *   Dòng dữ liệu thứ 101 ghi nhận đầy đủ nhiệt độ của cả 3 điểm đo.
*   *Kết quả thực tế:* Đạt. Cơ chế `sync_csv_headers` xử lý đồng bộ trơn tru, không gây lỗi cấu trúc dữ liệu.

#### TC-04: Phục hồi luồng camera RTSP tự động khi mất tín hiệu mạng (Auto-Reconnect)
*   *Mục đích:* Kiểm tra tính tự phục hồi của tiến trình đọc luồng video khi xảy ra sự cố mạng.
*   *Dữ liệu đầu vào:* Ngắt kết nối mạng cáp LAN của camera an ninh trong vòng 30 giây rồi cắm lại.
*   *Các bước thực hiện:*
    1. Khởi chạy hệ thống để camera nhận dạng bình thường.
    2. Rút dây mạng của camera quang.
    3. Quan sát màn hình log YOLO.
    4. Cắm lại dây mạng camera sau 30 giây và tiếp tục quan sát log.
*   *Kết quả kỳ vọng:*
    *   Khi rút dây, log YOLO xuất hiện cảnh báo mất tín hiệu: `[YOLO-READER] Mat ket noi camera... Dang tien hanh ket noi lai...`
    *   Hệ thống không bị crash hoặc dừng chương trình. Tiến trình con vẫn chạy ngầm thử kết nối lại.
    *   Khi cắm lại dây, log xuất hiện: `[YOLO-READER] Da ket noi camera thanh cong!` và tiếp tục nhận diện người bình thường.
*   *Kết quả thực tế:* Đạt. Khả năng tự phục hồi hoạt động ổn định.

---

### 3. Nhật ký sửa lỗi (Bug Report & Patches)

Dưới đây là báo cáo chi tiết về 6 lỗi kỹ thuật quan trọng phát sinh trong quá trình xây dựng hệ thống tại thiết bị biên và giải pháp khắc phục logic tương ứng:

#### Bug #01: Lỗi bất tương thích kích thước Scaler (Scaler Shape Mismatch) trong tiến trình huấn luyện lại mô hình (Auto-retrain)
*   **Mô tả lỗi:** Khi người vận hành bổ sung hoặc xóa bỏ điểm đo nhiệt độ từ máy chủ trung tâm, số lượng biến đặc trưng của dữ liệu thay đổi từ $N$ lên $N+M$. Tiến trình huấn luyện lại mô hình (`train.py`) cố gắng nạp lại bộ chuẩn hóa cũ (`scaler_X.pkl`) đã được lưu trước đó với kích thước $N$ để biến đổi dữ liệu huấn luyện mới có kích thước $N+M$ biến, dẫn đến lỗi bất tương thích chiều ma trận trong thư viện Scikit-Learn. Tiến trình huấn luyện con bị dừng đột ngột và sinh ra biệt lệ `ValueError`.
*   **Giải pháp khắc phục:** Lập trình cơ chế so sánh kích thước cấu hình mục tiêu. Tại tệp huấn luyện `train.py`, hệ thống thực hiện kiểm tra độ dài danh sách điểm đo (`targets`) hiện tại với danh sách các cột lưu trữ trong file cấu hình huấn luyện cũ. Nếu phát hiện có sự thay đổi kích thước, tiến trình sẽ hủy bỏ việc nạp bộ chuẩn hóa cũ, khởi tạo lại đối tượng `StandardScaler` mới hoàn toàn và tiến hành huấn luyện khớp lại (fit) bộ chuẩn hóa trên tập dữ liệu mới trước khi lưu đè tệp tin `.pkl`.

#### Bug #02: Lỗi bùng nổ giá trị dự báo (Exploding predictions) do mất gói dữ liệu nhiệt độ
*   **Mô tả lỗi:** Trong điều kiện truyền dẫn qua switch ngoài trời, gói dữ liệu ma trận nhiệt độ từ camera thỉnh thoảng bị mất hoặc lỗi gói tin dẫn đến việc file CSV lịch sử xuất hiện các hàng trống hoặc các giá trị rỗng (`NaN`). Thuật toán phân rã chuỗi thời gian STL (Seasonal and Trend decomposition using Loess) không hỗ trợ dữ liệu rỗng và trả về các giá trị vô cùng (`inf` hoặc `NaN`). Khi đưa ma trận lỗi này vào mô hình Kolmogorov-Arnold Network (MTKAN), các tầng kích hoạt sinh ra dự báo nhiệt độ bùng nổ hàng nghìn độ C, kích hoạt cảnh báo đỏ giả trên giao diện giám sát.
*   **Giải pháp khắc phục:** Bổ sung module tiền xử lý dữ liệu nghiêm ngặt trong tệp `timeseries_service/src/preprocess.py`. Thuật toán áp dụng hai bước: Thứ nhất, lọc các giá trị nhiệt độ ngoài ngưỡng vật lý thực tế của thiết bị điện trạm (ngưỡng 0°C đến 100°C) và gán thành `NaN`. Thứ hai, sử dụng thuật toán nội suy dựa theo thời gian (Time-based Interpolation) của Pandas với tham số lấp đầy hai hướng để tự động làm mượt dữ liệu bị khuyết thiếu, đảm bảo tính liên tục của dữ liệu đầu vào cho mô hình MTKAN.

#### Bug #03: Lỗi mất kết nối và rò rỉ bộ nhớ luồng camera RTSP (OpenCV/FFmpeg Stream Timeout)
*   **Mô tả lỗi:** Khi camera IP bị ngắt kết nối mạng tạm thời, mặc định OpenCV gọi giải mã FFmpeg và treo luồng đọc ảnh tới 30 giây để chờ kết nối lại. Việc treo đồng bộ này làm ngắt quãng luồng xử lý nhận diện người xâm nhập, đồng thời việc tạo mới các đối tượng bắt hình ảnh liên tục mà không giải phóng tài nguyên cũ dẫn đến rò rỉ bộ nhớ RAM và tràn bộ nhớ đệm VRAM trên card Jetson sau vài lần đứt mạng.
*   **Giải pháp khắc phục:** Tách biệt luồng đọc khung hình sang một tiến trình con (Multi-threaded FrameReader) chạy bất đồng bộ với hàng đợi Frame Queue giới hạn kích thước ( tối đa 5 khung hình). Cấu hình tham số kết nối FFmpeg thông qua biến môi trường để ép thời gian timeout tối đa chỉ là 5 giây. Khi phát hiện lỗi đọc khung hình liên tục trong 5 giây, FrameReader sẽ tự động đóng kết nối cũ, giải phóng toàn bộ tài nguyên bằng lệnh hủy kết nối OpenCV Capture, sau đó khởi chạy vòng lặp ngủ 5 giây và thử kết nối lại từ đầu một cách an toàn.

#### Bug #04: Lỗi ghi đè/xung đột dữ liệu khi chạy đa camera đồng thời (Multi-camera Data Partitioning)
*   **Mô tả lỗi:** Ban đầu hệ thống được cấu hình ghi dữ liệu lịch sử vào một file CSV dùng chung và lưu trọng số mô hình MTKAN vào cùng một tệp mặc định. Khi vận hành đồng thời 3 camera nhiệt khác nhau, các tiến trình API ghi dữ liệu đồng thời vào file CSV chung gây ra hiện tượng xung đột khóa file ghi (file lock contention), mất mát dữ liệu và mô hình AI liên tục bị nạp sai scaler của camera khác, dẫn đến các dự báo nhiệt độ bị sai lệch hoàn toàn.
*   **Giải pháp khắc phục:** Triển khai cấu trúc phân hoạch dữ liệu độc lập theo địa chỉ IP của camera (Per-camera Partitioning). Hệ thống biên tự động kiểm tra địa chỉ IP gửi yêu cầu dữ liệu, ánh xạ để tạo các thư mục con riêng biệt dưới thư mục dữ liệu thô `received_data/` và tự động phân tách các tệp cấu hình điểm đo JSON, tệp lịch sử CSV, scaler chuẩn hóa và trọng số mô hình với tiền tố tên file chính là địa chỉ IP của camera đó (ví dụ: `192_168_x_152_live_thermal_history.csv`).

#### Bug #05: Lỗi gửi cảnh báo trùng lặp liên tục (Alert Spam / Flood) khi phát hiện người xâm nhập
*   **Mô tả lỗi:** Do mô hình YOLOv8 chạy suy luận với tần suất cao (28 FPS), khi có một người di chuyển chậm trong khu vực an ninh hàng rào, hệ thống liên tục phát hiện "person" ở mỗi khung hình và gọi API gửi cảnh báo HTTP POST về Central Server. Điều này tạo ra hàng trăm yêu cầu gửi liên tục trong 10 giây, gây nghẽn băng thông mạng LAN của trạm và làm tràn bộ đệm hiển thị cảnh báo tại máy chủ trung tâm.
*   **Giải pháp khắc phục:** Tích hợp bộ khóa trạng thái cảnh báo (Alert State Locking) và cơ chế thời gian hồi (Cooldown Period). Khi phát hiện người lần đầu, hệ thống kích hoạt trạng thái "Intrusion" và khóa không cho phép gửi cảnh báo tiếp theo, đồng thời khởi động tiến trình ghi hình MP4. Chỉ khi tiến trình ghi video hoàn thành (sau khi người rời đi cộng với thời gian gia hạn grace period 3 giây) và gửi thành công tệp tin MP4 sự kiện, khóa trạng thái mới được giải phóng sau một khoảng thời gian chờ (cooldown) 5 giây để tránh gửi trùng lặp.

#### Bug #06: Lỗi sai lệch URL callback phản hồi dữ liệu dự báo khi IP máy chủ trung tâm thay đổi động
*   **Mô tả lỗi:** URL callback dùng để gửi kết quả dự báo nhiệt độ từ thiết bị biên về máy chủ trung tâm được cấu hình tĩnh trong file `.env`. Trong môi trường mạng nội bộ của trạm biến áp sử dụng cấp phát IP động (DHCP), khi máy chủ trung tâm bị khởi động lại và nhận địa chỉ IP mới, thiết bị biên không thể gửi dữ liệu callback dự báo về máy chủ, dẫn đến mất kết nối biểu đồ xu hướng trên giao diện Web Dashboard.
*   **Giải pháp khắc phục:** Thiết kế cơ chế phân giải địa chỉ callback động dựa trên IP của client kết nối (Dynamic Callback URI Resolution). Tại FastAPI API nhận dữ liệu nhiệt độ ở thiết bị biên, thay vì đọc cấu hình URL tĩnh, hệ thống sẽ phân tích gói tin HTTP Request gửi đến để trích xuất địa chỉ IP nguồn của client đang thực hiện gửi dữ liệu nhiệt độ. Sau đó, URL callback sẽ được tự động lắp ghép động dựa theo IP nguồn này để phản hồi chính xác kết quả dự báo về đúng máy chủ đang hoạt động.

---

## V. CÔNG ĐOẠN BÀN GIAO & NGHIỆM THU

### 1. Biên bản nghiệm thu kỹ thuật và bàn giao sản phẩm

Hội đồng nghiệm thu thống nhất ký biên bản xác nhận bàn giao bộ sản phẩm phần mềm của dự án "Smart Camera Edge System" cho đơn vị vận hành trạm biến áp 110kV. Các tài nguyên bàn giao bao gồm toàn bộ cấu trúc thư mục mã nguồn được thiết lập tại biên Jetson cùng các mô hình AI tối ưu.

---

### 2. Hướng dẫn sử dụng & vận hành hệ thống (User & Operations Guide)

#### A. Cài đặt các thư viện phụ thuộc (Dependencies Installation)
Hệ thống biên yêu cầu môi trường JetPack của NVIDIA đã cài đặt sẵn CUDA và TensorRT. Quy trình thực hiện:
1. Di chuyển vào thư mục dự án biên: `/home/admin-khai/Desktop/smart_camera_edge_system`
2. Cập nhật cơ sở dữ liệu gói và cài đặt các thư viện hệ thống yêu cầu bao gồm công cụ cài đặt thư viện python `python3-pip`, thư viện cấu trúc file H5 `python3-h5py`, thư viện toán học `python3-numpy`, thư viện xử lý ảnh OpenCV `python3-opencv` và công cụ giải phóng tiến trình chiếm dụng cổng `fuser`.
3. Sử dụng công cụ `pip3` để tự động cài đặt các thư viện python bổ trợ được liệt kê cụ thể trong tệp `requirements.txt`.

#### B. Cấu hình các biến môi trường trong file `.env`
Thiết lập các tham số chạy thông qua việc tạo file cấu hình `.env` tại thư mục gốc của dự án biên. Danh sách các biến cấu hình cần thiết được đặc tả chi tiết trong bảng dưới đây (để đảm bảo an toàn thông tin, các địa chỉ IP cụ thể đã được ẩn bằng ký tự đại diện `x`):

| Tên biến cấu hình | Vai trò & Mô tả ý nghĩa | Giá trị ví dụ (Che IP cụ thể) |
| :--- | :--- | :--- |
| `CAMERA_IP` | Địa chỉ IP của Camera IP quang dùng để phát hiện xâm nhập | `192.168.x.152` |
| `CAMERA_RTSP_URL` | Luồng RTSP truyền hình ảnh thời gian thực từ camera quang | `rtsp://admin:Demo%402024@192.168.x.152:554/Streaming/Channels/102` |
| `YOLO_ENGINE_PATH` | Đường dẫn đến tệp mô hình YOLOv8 đã tối ưu hóa TensorRT | `models/yolov8n.engine` |
| `YOLO_CONF_THRESHOLD` | Ngưỡng tin cậy nhận diện người tối thiểu | `0.55` |
| `CENTRAL_STATION_IP` | Địa chỉ IP của Máy chủ giám sát trung tâm nhận cảnh báo | `192.168.x.102` |
| `YOLO_ALERT_API_URL` | API URL nhận bản tin cảnh báo người xâm nhập kèm video sự kiện | `http://192.168.x.102:5000/api/person-detection` |

#### C. Quy trình vận hành và chạy dịch vụ ngầm (Systemd Service)
Hệ thống được thiết kế để tự động vận hành khi thiết bị biên Jetson được cắm nguồn điện.

1.  **Cài đặt dịch vụ hệ thống tự chạy:**
    Hệ thống cung cấp sẵn script bash `install_service.sh` để đăng ký dịch vụ chạy ngầm với Linux Systemd. Thực hiện cấp quyền chạy cho kịch bản `install_service.sh` bằng lệnh phân quyền `chmod +x`, sau đó chạy kịch bản dưới quyền quản trị viên `sudo` để tự động nạp dịch vụ mẫu `smart_camera.service` vào thư mục cấu hình hệ thống `/etc/systemd/system/`.

2.  **Quản lý dịch vụ bằng dòng lệnh (CLI commands):**
    *   *Khởi động dịch vụ:* Sử dụng câu lệnh quản trị hệ thống `systemctl start smart_camera.service` (chạy với quyền quản trị viên `sudo`).
    *   *Dừng dịch vụ:* Sử dụng câu lệnh quản trị hệ thống `systemctl stop smart_camera.service` (chạy với quyền quản trị viên `sudo`).
    *   *Tự động chạy dịch vụ khi khởi động hệ điều hành:* Sử dụng câu lệnh quản trị hệ thống `systemctl enable smart_camera.service` (chạy với quyền quản trị viên `sudo`).
    *   *Kiểm tra trạng thái hoạt động thực tế của dịch vụ:* Sử dụng câu lệnh kiểm tra trạng thái `systemctl status smart_camera.service` (chạy với quyền quản trị viên `sudo`).
    *   *Xem nhật ký log hoạt động trực tuyến:* Sử dụng câu lệnh truy xuất nhật ký hệ thống `journalctl -u smart_camera.service -f`.

#### D. Hướng dẫn xử lý sự cố nhanh (Troubleshooting Guide)
1.  **Sự cố 1: Cổng mạng `8080` bị chiếm dụng không khởi chạy được Thermal Receiver API.**
    *   *Triệu chứng:* Log hệ thống xuất hiện lỗi `OSError: [Errno 98] Address already in use`.
    *   *Khắc phục:* Tiến trình `main_all.py` đã tích hợp cơ chế tự động dọn dẹp khi khởi chạy. Nếu lỗi vẫn tiếp diễn, chạy lệnh thủ công: `sudo fuser -k 8080/tcp` để ép giải phóng cổng mạng rồi khởi động lại dịch vụ.
2.  **Sự cố 2: Lỗi TensorRT Engine Deserialization Failure.**
    *   *Triệu chứng:* Khởi động YOLO xuất hiện lỗi `RuntimeError: Khong load duoc TensorRT engine.`
    *   *Nguyên nhân:* Tệp `.engine` được tạo từ phiên bản TensorRT khác với phiên bản hiện tại trên thiết bị Jetson.
    *   *Khắc phục:* Thực hiện xuất lại mô hình từ file gốc `.onnx` sang `.engine` trực tiếp trên thiết bị Jetson bằng cách chạy công cụ biên dịch tối ưu hóa `trtexec` với các tham số: nguồn `--onnx=models/best.onnx`, đích lưu `--saveEngine=models/best.engine` và chế độ dấu phẩy động 16-bit `--fp16`. Sau đó cập nhật đường dẫn `YOLO_ENGINE_PATH=models/best.engine` trong file cấu hình `.env`.
