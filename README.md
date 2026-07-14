# 🌟 Hệ thống Camera Biên Thông minh (Smart Camera Edge System)

Hệ thống tích hợp đa luồng hiệu năng cao chạy trên **Jetson Orin Nano**, kết hợp bộ phát hiện người chuyên dụng bằng **TensorRT** và dịch vụ dự báo chuỗi thời gian nhiệt độ tự động tối ưu **FastAPI & TensorFlow (MTKAN)**.

---

## 🛠️ Kiến trúc hệ thống (System Architecture)

Dự án bao gồm 2 dịch vụ chính chạy song song dưới sự điều phối của một **Master Daemon Control** (`main_all.py`):

1. **YOLOv8n TensorRT Detector (Bộ Phát hiện Người)**:
   - Tối ưu hóa GPU biên thông qua việc biên dịch file ONNX sang TensorRT Engine (`yolov8n.engine`) chạy ở tốc độ cực cao (~251 FPS).
   - Thiết kế dạng chạy ngầm không màn hình (Headless Daemon), bắt giữ các luồng video RTSP bất đồng bộ và đẩy cảnh báo qua Thread Pool lên máy chủ trung tâm.
2. **FastAPI Thermal Service (Dịch vụ Nhận dữ liệu & Dự báo Nhiệt)**:
   - Nhận dữ liệu nhiệt độ trực tiếp qua API, lưu lịch sử tối ưu và đưa ra dự đoán trước 5 phút (Horizon = 5) bằng mạng Nơ-ron.
   - **Tự động huấn luyện lại ngầm (Background Auto-Retraining)**: Sau mỗi 2 ngày (172.800 giây), dịch vụ tự động kích hoạt train lại mô hình trên luồng phụ độc lập.
   - **Cập nhật nóng không gián đoạn (Zero-Downtime Hot-Swapping)**: Tự động nạp (hot-swap) trọng số mô hình mới vào RAM ngay sau khi train xong mà không cần khởi động lại server.

---

## 📋 Yêu cầu hệ thống (Prerequisites)

* **Thiết bị**: Jetson Orin Nano (hoặc dòng Jetson tương đương).
* **Hệ điều hành**: JetPack (5.x hoặc 6.x) đã tích hợp sẵn **CUDA**, **cuDNN**, và **TensorRT**.
* **Python**: Phiên bản 3.10.

---

## 🚀 Hướng dẫn cài đặt & Chạy tự động (Quick Start)

Hệ thống hỗ trợ script cài đặt tự động `install_service.sh` giúp chuẩn bị môi trường ảo, cài đặt tất cả dependencies và đăng ký dịch vụ chạy nền Systemd chỉ với **1 câu lệnh duy nhất**.

### Bước 1: Clone dự án và truy cập thư mục gốc
```bash
git clone <url-cua-ban> smart_camera_edge_system
cd smart_camera_edge_system
```

### Bước 2: Chạy kịch bản cài đặt tự động
```bash
chmod +x install_service.sh
sudo ./install_service.sh
```
*Lệnh này sẽ tự động thực hiện:*
1. Cài đặt các gói thư viện hệ thống cần thiết qua `apt`.
2. Tạo môi trường ảo Python độc lập (`tf_env`) cho module xử lý chuỗi thời gian nhiệt độ.
3. Tự động cài đặt các dependencies Python cần thiết cho cả YOLOv8 và Thermal Receiver.
4. Tự động tạo tệp cấu hình `.env` mặc định (nếu chưa tồn tại).
5. Đăng ký, kích hoạt và khởi chạy dịch vụ chạy nền `smart_camera.service` với Systemd.

---

## ⚙️ Cấu hình Hệ thống (Configuration)

Trước khi vận hành thực tế, hãy cấu hình các tham số tại file `.env` ở thư mục gốc:
```env
# Địa chỉ IP của Camera IP quang dùng để phát hiện xâm nhập
CAMERA_IP=192.168.10.152
# Luồng RTSP truyền hình ảnh thời gian thực từ camera quang
CAMERA_RTSP_URL=rtsp://admin:Demo%402024@192.168.10.152:554/Streaming/Channels/102

# Đường dẫn đến tệp mô hình YOLOv8 đã tối ưu hóa TensorRT (.engine)
YOLO_ENGINE_PATH=models/yolov8n.engine
# Ngưỡng tin cậy nhận diện người (Confidence Threshold)
YOLO_CONF_THRESHOLD=0.55

# Địa chỉ IP của Máy chủ giám sát trung tâm (Central Station) nhận cảnh báo
CENTRAL_STATION_IP=192.168.10.102
```

---

## 🎯 Điều khiển & Quản lý Dịch vụ (Service Management)

Sau khi cài đặt thành công bằng script, dịch vụ sẽ chạy tự động ở nền. Bạn có thể quản lý dịch vụ bằng các lệnh sau:

* **Xem trạng thái hoạt động**:
  ```bash
  sudo systemctl status smart_camera.service
  ```

* **Xem nhật ký hoạt động thời gian thực (Real-time logs)**:
  ```bash
  sudo journalctl -u smart_camera.service -f
  ```

* **Dừng dịch vụ**:
  ```bash
  sudo systemctl stop smart_camera.service
  ```

* **Khởi động lại dịch vụ**:
  ```bash
  sudo systemctl restart smart_camera.service
  ```

* **Chạy thủ công ở chế độ thử nghiệm (Foreground)**:
  Nếu muốn dừng dịch vụ nền và chạy trực tiếp để kiểm tra log ra màn hình:
  ```bash
  sudo systemctl stop smart_camera.service
  python3 main_all.py
  ```

---

## ⚠️ Lưu ý quan trọng khi thay đổi điểm nhiệt độ

Khi người dùng **thêm điểm nhiệt mới** hoặc **đổi tên/vị trí điểm nhiệt** trên camera:
1. **Cập nhật Cấu hình**: Truy cập file `timeseries_service/model/config.json` và cập nhật lại danh sách điểm nhiệt mới trong mục `"targets"`.
2. **Huấn luyện lại**: Do kích thước ma trận đầu vào của mô hình AI thay đổi, bạn cần thực hiện huấn luyện lại mô hình từ đầu bằng lệnh:
   ```bash
   cd timeseries_service
   ./tf_env/bin/python train.py
   ```
   *Sau khi chương trình train xong và tạo ra trọng số mới, dịch vụ sẽ tự động nạp nóng và hoạt động ổn định bình thường.*
