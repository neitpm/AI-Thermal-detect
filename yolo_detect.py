import os
import cv2
import time
import requests
import json
import threading
import signal
import sys
import numpy as np
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit
from concurrent.futures import ThreadPoolExecutor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =========================
# SOURCE CONFIG
# =========================
SOURCE = "rtsp://admin:Demo%402024@192.168.10.152:554/Streaming/Channels/102"
ENGINE_PATH = "models/yolov8n.engine"

# =========================
# DETECTION CONFIG
# =========================
INPUT_W = 640
INPUT_H = 640
CONF_THRES = 0.55  # Lọc nhận diện sai triệt để
IOU_THRES = 0.45   # Giảm chồng lấn box trùng
PERSON_CLASS_ID = 0
SKIP_FRAMES = 2

MIN_BOX_W = 20
MIN_BOX_H = 40
MIN_BOX_AREA = 800
MIN_ASPECT_RATIO = 0.20
MAX_ASPECT_RATIO = 1.20

# =========================
# API CONFIG
# =========================
API_URL = "http://192.168.10.102:5000/api/person-detection"
CAMERA_IP = "192.168.10.152"
MIN_API_INTERVAL = 5
API_TIMEOUT = 5
API_MAX_WORKERS = 1
JPEG_QUALITY = 85

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
    "rtsp_transport;tcp|max_delay;500000|fflags;nobuffer"
)

# =========================
# SYSTEM SIGNALS FOR HEADLESS DAEMON
# =========================
running = True
def handle_exit_signal(signum, frame):
    global running
    print(f"\n[SYSTEM] Nhan tin hieu dung (signal {signum}). Dang shutdown he thong...")
    running = False

signal.signal(signal.SIGINT, handle_exit_signal)
signal.signal(signal.SIGTERM, handle_exit_signal)

# =========================
# LOAD TENSORRT ENGINE
# =========================
TRT_LOGGER = trt.Logger(trt.Logger.ERROR)
print(f"[TRT] Loading engine: {ENGINE_PATH}")
with open(ENGINE_PATH, "rb") as f:
    runtime = trt.Runtime(TRT_LOGGER)
    engine = runtime.deserialize_cuda_engine(f.read())

if engine is None:
    raise RuntimeError("Khong load duoc TensorRT engine.")

context = engine.create_execution_context()

input_name, output_name = None, None
for i in range(engine.num_io_tensors):
    name = engine.get_tensor_name(i)
    mode = engine.get_tensor_mode(name)
    if mode == trt.TensorIOMode.INPUT:
        input_name = name
    elif mode == trt.TensorIOMode.OUTPUT:
        output_name = name

input_shape = tuple(context.get_tensor_shape(input_name))
if -1 in input_shape:
    input_shape = (1, 3, INPUT_H, INPUT_W)
    context.set_input_shape(input_name, input_shape)
output_shape = tuple(context.get_tensor_shape(output_name))

d_input  = cuda.mem_alloc(int(np.prod(input_shape))  * np.dtype(np.float32).itemsize)
d_output = cuda.mem_alloc(int(np.prod(output_shape)) * np.dtype(np.float32).itemsize)
trt_output = np.empty(output_shape, dtype=np.float32)
stream = cuda.Stream()

context.set_tensor_address(input_name,  int(d_input))
context.set_tensor_address(output_name, int(d_output))
print("[TRT] Engine loaded OK. Dang chay o che do headless (ngam)...")


# =========================
# HELPER FUNCTIONS
# =========================
def preprocess(frame):
    h0, w0 = frame.shape[:2]
    img = cv2.resize(frame, (INPUT_W, INPUT_H))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.transpose(2, 0, 1).astype(np.float32) / 255.0
    img = np.ascontiguousarray(np.expand_dims(img, 0))
    return img, h0, w0


def is_valid_person_box(x1, y1, x2, y2):
    bw, bh = x2 - x1, y2 - y1
    if bw < MIN_BOX_W or bh < MIN_BOX_H:
        return False
    if bw * bh < MIN_BOX_AREA:
        return False
    r = bw / (bh + 1e-6)
    return MIN_ASPECT_RATIO <= r <= MAX_ASPECT_RATIO


def detect_persons(frame):
    """TensorRT inference, decode cho class 0 (person)."""
    img, h0, w0 = preprocess(frame)
    cuda.memcpy_htod_async(d_input, img, stream)
    context.execute_async_v3(stream_handle=stream.handle)
    cuda.memcpy_dtoh_async(trt_output, d_output, stream)
    stream.synchronize()

    preds = trt_output[0]  # (84, 8400)
    if preds.shape[0] != 84:
        preds = preds.T

    boxes_raw = preds[0:4, :]
    scores = preds[4, :]

    keep_indices = np.where(scores >= CONF_THRES)[0]

    img_draw = frame.copy()
    boxes = []
    count = 0

    if len(keep_indices) > 0:
        cx = boxes_raw[0, keep_indices]
        cy = boxes_raw[1, keep_indices]
        w = boxes_raw[2, keep_indices]
        h = boxes_raw[3, keep_indices]

        x1s = (cx - w / 2) * (w0 / INPUT_W)
        y1s = (cy - h / 2) * (h0 / INPUT_H)
        x2s = (cx + w / 2) * (w0 / INPUT_W)
        y2s = (cy + h / 2) * (h0 / INPUT_H)
        confidences = scores[keep_indices]

        nms_boxes = []
        for i in range(len(keep_indices)):
            nms_boxes.append([
                float(x1s[i]),
                float(y1s[i]),
                float(x2s[i] - x1s[i]),
                float(y2s[i] - y1s[i])
            ])

        indices = cv2.dnn.NMSBoxes(nms_boxes, confidences.tolist(), CONF_THRES, IOU_THRES)

        if len(indices) > 0:
            indices = np.array(indices).flatten()
            for idx in indices:
                box = nms_boxes[idx]
                score = float(confidences[idx])
                x1 = int(max(0, min(w0 - 1, box[0])))
                y1 = int(max(0, min(h0 - 1, box[1])))
                x2 = int(max(0, min(w0 - 1, box[0] + box[2])))
                y2 = int(max(0, min(h0 - 1, box[1] + box[3])))

                if x2 <= x1 or y2 <= y1:
                    continue
                if not is_valid_person_box(x1, y1, x2, y2):
                    continue

                count += 1
                boxes.append({
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                    "score": round(score, 4)
                })
                cv2.rectangle(img_draw, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(img_draw, f"person: {score:.2f}", (x1, max(20, y1 - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    return img_draw, count, boxes


def send_detection_api(person_count, boxes, frame_bgr):
    payload = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "camera_ip": CAMERA_IP,
        "person_count": person_count,
        "alert_type": "person_detected",
        "boxes": boxes,
    }
    success, encoded_img = cv2.imencode(".jpg", frame_bgr,
                                        [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY])
    if not success:
        print("[API] Loi encode anh")
        return
    try:
        response = requests.post(
            API_URL,
            data={"metadata": json.dumps(payload, ensure_ascii=False)},
            files={"image": (f"person_{int(time.time())}.jpg", encoded_img.tobytes(), "image/jpeg")},
            timeout=API_TIMEOUT,
        )
        print(f"[API] status={response.status_code} | {response.text}")
    except Exception as e:
        print(f"[API] Loi gui API: {e}")


def send_video_api(video_path):
    if not os.path.exists(video_path):
        return
    payload = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "camera_ip": CAMERA_IP,
        "alert_type": "person_detection_video",
    }
    try:
        print(f"[API-VIDEO] Dang gui video {video_path}...")
        with open(video_path, "rb") as f:
            response = requests.post(
                API_URL,
                data={"metadata": json.dumps(payload, ensure_ascii=False)},
                files={"video": (os.path.basename(video_path), f, "video/mp4")},
                timeout=30,
            )
        print(f"[API-VIDEO] Ket qua: status={response.status_code} | response={response.text}")
    except Exception as e:
        print(f"[API-VIDEO] Loi gui video API: {e}")
    finally:
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
                print(f"[API-VIDEO] Da xoa file tam local: {video_path}")
        except Exception as ex:
            print(f"[API-VIDEO] Khong xoa duoc file tam {video_path}: {ex}")


# =========================
# THREADED FRAME READER
# =========================
class FrameReader(threading.Thread):
    def __init__(self, src):
        super().__init__(daemon=True)
        self.cap = cv2.VideoCapture(src, cv2.CAP_FFMPEG)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        if not self.cap.isOpened():
            raise RuntimeError(f"Khong mo duoc nguon: {src}")
        self.frame = None
        self.ret = False
        self._lock = threading.Lock()
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            ret, frame = self.cap.read()
            with self._lock:
                self.ret = ret
                self.frame = frame

    def read(self):
        with self._lock:
            if self.frame is None:
                return False, None
            return self.ret, self.frame.copy()

    def stop(self):
        self._stop_event.set()
        self.join(timeout=2)
        self.cap.release()


# =========================
# MAIN LOOP
# =========================
reader = FrameReader(SOURCE)
reader.start()

prev_time = time.time()
last_api_sent_time = 0
last_has_person = False
api_executor = ThreadPoolExecutor(max_workers=API_MAX_WORKERS)
api_future = None

# Video recording state variables
is_recording = False
video_writer = None
temp_video_path = None
last_person_seen_time = 0
event_grace_period = 3.0  # seconds
event_alert_sent = True

cached_draw = None
cached_count = 0
cached_boxes = []
frame_idx = 0

try:
    while running:
        ret, frame = reader.read()
        if not ret or frame is None:
            time.sleep(0.005)
            continue

        frame_idx += 1

        # Chỉ inference định kỳ
        if frame_idx % SKIP_FRAMES == 0:
            cached_draw, cached_count, cached_boxes = detect_persons(frame)

        img_draw = cached_draw if cached_draw is not None else frame
        count = cached_count

        curr_time = time.time()
        fps = 1.0 / (curr_time - prev_time + 1e-6)
        prev_time = curr_time

        has_person = count > 0
        
        # LOGGING CHO DETECTION
        if has_person and not last_has_person:
            print(f"[YOLO-EVENT] Phat hien {count} nguoi trong khung hinh.")
        elif not has_person and last_has_person:
            print(f"[YOLO-EVENT] Het nguoi trong khung hinh.")

        # --- EVENT VIDEO RECORDING LOGIC ---
        if has_person:
            last_person_seen_time = curr_time
            if not is_recording:
                is_recording = True
                event_alert_sent = False  # Reset the alert flag for the new event!
                h, w = frame.shape[:2]
                temp_video_path = os.path.join(BASE_DIR, f"event_{int(curr_time)}.mp4")
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                video_writer = cv2.VideoWriter(temp_video_path, fourcc, 10.0, (w, h))
                print(f"[YOLO-VIDEO] Bat dau ghi hinh su kien nguoi: {temp_video_path}")
            
        if is_recording:
            video_writer.write(img_draw)
            
            if not has_person and (curr_time - last_person_seen_time >= event_grace_period):
                is_recording = False
                video_writer.release()
                print(f"[YOLO-VIDEO] Ket thuc su kien ghi hinh. Dang gui video ngam...")
                api_executor.submit(send_video_api, temp_video_path)

        # --- INSTANT ALERT LOGIC (ALARM IMMEDIATELY ON FIRST SPOT) ---
        if has_person and not event_alert_sent:
            api_busy = api_future is not None and not api_future.done()
            if not api_busy:
                api_future = api_executor.submit(
                    send_detection_api, count, list(cached_boxes), img_draw.copy()
                )
                event_alert_sent = True  # Mark as sent so we don't send again during this event!

        last_has_person = has_person
        time.sleep(0.002)

finally:
    reader.stop()
    if is_recording and video_writer is not None:
        try:
            video_writer.release()
            print(f"[YOLO-VIDEO] Dong file video truoc khi dung.")
            send_video_api(temp_video_path)
        except Exception:
            pass
    api_executor.shutdown(wait=False, cancel_futures=True)
    print("[SYSTEM] Da dung tat ca tien trinh thanh cong.")
