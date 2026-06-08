from fastapi import FastAPI, Request
import uvicorn
from datetime import datetime
import json
import os
import threading
import subprocess
import sys
import time
import requests
from urllib import request as urlrequest
from urllib.error import URLError, HTTPError

import numpy as np
import pandas as pd

app = FastAPI(title="Thermal Receiver API")

SAVE_DIR = "received_data"
DATA_DIR = "data"
RAW_HISTORY_CSV = os.path.join(DATA_DIR, "live_thermal_history.csv")
PREDICTIONS_CSV = os.path.join(DATA_DIR, "live_predictions.csv")
EVALUATIONS_CSV = os.path.join(DATA_DIR, "live_evaluations.csv")
DEFAULT_PREDICTION_CALLBACK_URL = "http://192.168.10.102:8100/api/prediction"
PREDICTION_CALLBACK_URL = os.getenv(
    "PREDICTION_CALLBACK_URL",
    DEFAULT_PREDICTION_CALLBACK_URL,
).strip()
CALLBACK_TIMEOUT_SECONDS = float(os.getenv("PREDICTION_CALLBACK_TIMEOUT", "5"))

# ==========================================
# MIGRATION & MULTI-CAMERA PATH UTILITIES
# ==========================================
MODEL_DIR = "model"

def migrate_existing_files():
    default_cam = "192_168_10_152"
    
    # Files in DATA_DIR
    data_files = [
        ("live_thermal_history.csv", f"{default_cam}_live_thermal_history.csv"),
        ("live_predictions.csv", f"{default_cam}_live_predictions.csv"),
        ("live_evaluations.csv", f"{default_cam}_live_evaluations.csv"),
        ("thermal_points.json", f"{default_cam}_thermal_points.json"),
    ]
    for old_name, new_name in data_files:
        old_path = os.path.join(DATA_DIR, old_name)
        new_path = os.path.join(DATA_DIR, new_name)
        if os.path.exists(old_path) and not os.path.exists(new_path):
            try:
                os.rename(old_path, new_path)
                print(f"[MIGRATION] Đã chuyển đổi file dữ liệu: {old_path} -> {new_path}")
            except Exception as e:
                print(f"[MIGRATION-ERROR] Lỗi chuyển đổi {old_name}: {e}")

    # Files in MODEL_DIR
    model_files = [
        ("config.json", f"{default_cam}_config.json"),
        ("linear_reg.pkl", f"{default_cam}_linear_reg.pkl"),
        ("scaler_X.pkl", f"{default_cam}_scaler_X.pkl"),
        ("scaler_y.pkl", f"{default_cam}_scaler_y.pkl"),
    ]
    for old_name, new_name in model_files:
        old_path = os.path.join(MODEL_DIR, old_name)
        new_path = os.path.join(MODEL_DIR, new_name)
        if os.path.exists(old_path) and not os.path.exists(new_path):
            try:
                os.rename(old_path, new_path)
                print(f"[MIGRATION] Đã chuyển đổi file model: {old_path} -> {new_path}")
            except Exception as e:
                print(f"[MIGRATION-ERROR] Lỗi chuyển đổi {old_name}: {e}")

# Chạy di chuyển dữ liệu lúc khởi tạo module
migrate_existing_files()

def get_camera_id(data: dict, request: Request = None) -> str:
    cam_id = data.get("camera_ip") or data.get("device_id") or data.get("stream_id")
    if cam_id:
        return str(cam_id).replace(".", "_").replace("-", "_").replace(":", "_")
    
    if request:
        qp = request.query_params.get("camera_ip") or request.query_params.get("device_id")
        if qp:
            return str(qp).replace(".", "_").replace("-", "_").replace(":", "_")
        
        client_ip = request.client.host
        if client_ip and client_ip not in ("127.0.0.1", "localhost"):
            return str(client_ip).replace(".", "_")
            
    return "192_168_10_152"

# Cache cấu hình và Dataframe cho từng camera
camera_configs = {}
_cached_history_dfs = {}
_cached_predictions_dfs = {}

# Biến toàn cục duy trì tương thích ngược
TARGETS = []
TARGET_COLS = []
HORIZON = 5
TARGET_TO_PRED_COL = {}
ID_TO_LABEL = {}

def get_camera_config(camera_id: str):
    if camera_id in camera_configs:
        return camera_configs[camera_id]
        
    cfg = {
        "targets": [],
        "target_cols": [],
        "horizon": 5,
        "target_to_pred_col": {},
        "id_to_label": {}
    }
    
    config_path = f"model/{camera_id}_config.json"
    if not os.path.exists(config_path):
        config_path = "model/config.json"
        
    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                c = json.load(f)
            cfg["targets"] = c.get("targets", [])
            cfg["target_cols"] = c.get("target_cols", [])
            cfg["horizon"] = c.get("horizon", 5)
            cfg["target_to_pred_col"] = dict(zip(cfg["targets"], cfg["target_cols"]))
    except Exception as e:
        print(f"[CONFIG-ERROR] Không thể đọc config cho {camera_id}: {e}")
        
    pts_config_path = os.path.join(DATA_DIR, f"{camera_id}_thermal_points.json")
    if not os.path.exists(pts_config_path):
        pts_config_path = os.path.join(DATA_DIR, "thermal_points.json")
        
    try:
        if os.path.exists(pts_config_path):
            with open(pts_config_path, "r", encoding="utf-8") as f:
                pts_data = json.load(f)
            for p in pts_data.get("points", []):
                p_id = p.get("id")
                p_label = p.get("label")
                if p_id and p_label:
                    cfg["id_to_label"][str(p_id).replace(":", "_")] = str(p_label)
    except Exception as e:
        print(f"[CONFIG-ERROR] Không thể đọc nhãn điểm cho {camera_id}: {e}")
        
    camera_configs[camera_id] = cfg
    return cfg

def reload_config(camera_id: str = "192_168_10_152"):
    global TARGETS, TARGET_COLS, HORIZON, TARGET_TO_PRED_COL, ID_TO_LABEL
    
    if camera_id in camera_configs:
        del camera_configs[camera_id]
    if camera_id in _cached_history_dfs:
        del _cached_history_dfs[camera_id]
    if camera_id in _cached_predictions_dfs:
        del _cached_predictions_dfs[camera_id]
        
    cfg = get_camera_config(camera_id)
    TARGETS = cfg["targets"]
    TARGET_COLS = cfg["target_cols"]
    HORIZON = cfg["horizon"]
    TARGET_TO_PRED_COL = cfg["target_to_pred_col"]
    ID_TO_LABEL = cfg["id_to_label"]
    
    print(f"[CONFIG] Đã tải cấu hình cho camera {camera_id}. Targets: {TARGETS}")

# Load ban đầu
reload_config()


os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

state_lock = threading.Lock()


# Global variables to cache data for performance
_cached_history_df = None
_cached_predictions_df = None


def to_timestamp_text(value):
    ts = pd.to_datetime(value)
    return ts.strftime("%Y-%m-%d %H:%M:%S")


def prune_received_data(camera_id: str, max_files: int = 50):
    try:
        cam_save_dir = os.path.join(SAVE_DIR, camera_id)
        if not os.path.exists(cam_save_dir):
            return
        files = [os.path.join(cam_save_dir, f) for f in os.listdir(cam_save_dir) if f.endswith(".json")]
        if len(files) > max_files:
            files.sort(key=os.path.getmtime, reverse=True)
            for old_file in files[max_files:]:
                try:
                    os.remove(old_file)
                except Exception:
                    pass
    except Exception as e:
        print(f"[CLEANUP-WARNING] Lỗi khi dọn dẹp received_data cho {camera_id}: {e}")


def thermal_json_to_row(data: dict, camera_id: str = "192_168_10_152") -> dict:
    timestamp = data.get("timestamp") or data.get("Timestamp")
    if not timestamp:
        raise ValueError("Thiếu timestamp trong dữ liệu gửi lên.")

    cfg = get_camera_config(camera_id)
    targets = cfg["targets"]
    id_to_label = cfg["id_to_label"]

    row = {"Timestamp": to_timestamp_text(timestamp)}
    for point in data.get("points", []):
        raw_id = str(point.get("id", "")).replace(":", "_")
        point_id = id_to_label.get(raw_id, raw_id)
        
        # Chỉ ghi nhận các điểm nằm trong danh sách TARGETS được cấu hình
        if point_id in targets:
            row[point_id] = point.get("temperature")

    # Điền giá trị None cho các target bị thiếu (ví dụ: chưa có tọa độ hoặc lỗi cảm biến)
    for target in targets:
        if target not in row:
            row[target] = None

    return row


def read_csv_if_exists(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)


def sync_csv_headers(path: str, expected_headers: list) -> None:
    if not os.path.exists(path):
        pd.DataFrame(columns=expected_headers).to_csv(path, index=False)
        return
    try:
        df = pd.read_csv(path)
        needed = [col for col in expected_headers if col not in df.columns]
        if needed:
            for col in needed:
                df[col] = None
            df.to_csv(path, index=False)
            print(f"[CSV-ALIGN] Added new columns {needed} to {path} to maintain existing data.")
    except Exception as e:
        print(f"[CSV-ALIGN-ERROR] Failed to sync headers for {path}: {e}")


def save_history_row(row: dict, camera_id: str = "192_168_10_152") -> pd.DataFrame:
    global _cached_history_dfs
    
    cfg = get_camera_config(camera_id)
    targets = cfg["targets"]
    history_csv = os.path.join(DATA_DIR, f"{camera_id}_live_thermal_history.csv")
    
    file_exists = os.path.exists(history_csv)
    if file_exists:
        try:
            df = pd.read_csv(history_csv)
        except Exception:
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

    headers = ["Timestamp"] + targets
    for col in headers:
        if col not in df.columns:
            df[col] = None

    is_merged = False
    if not df.empty:
        last_time_str = df.iloc[-1]["Timestamp"]
        try:
            last_time = pd.to_datetime(last_time_str)
            curr_time = pd.to_datetime(row["Timestamp"])
            time_diff = abs((curr_time - last_time).total_seconds())
        except Exception:
            time_diff = 999.0
            
        if time_diff <= 5.0:
            last_idx = df.index[-1]
            for col, val in row.items():
                if col != "Timestamp" and pd.notna(val) and val is not None:
                    df.at[last_idx, col] = val
            is_merged = True
            print(f"[MERGE] Merged split payload for {row['Timestamp']} into last row {last_time_str} ({camera_id})")

    if not is_merged:
        row_df = pd.DataFrame([row])
        for col in headers:
            if col not in row_df.columns:
                row_df[col] = None
        row_df = row_df[headers]
        df = pd.concat([df, row_df], ignore_index=True)

    df.to_csv(history_csv, index=False)
    _cached_history_dfs[camera_id] = df.tail(200)
    return _cached_history_dfs[camera_id]


def append_rows(path: str, rows: list[dict]) -> None:
    if not rows:
        return

    new_df = pd.DataFrame(rows)
    old_df = read_csv_if_exists(path)
    out_df = pd.concat([old_df, new_df], ignore_index=True)
    out_df.to_csv(path, index=False)


def evaluate_due_predictions(actual_row: dict, camera_id: str = "192_168_10_152") -> dict | None:
    global _cached_predictions_dfs
    
    cfg = get_camera_config(camera_id)
    targets = cfg["targets"]
    predictions_csv = os.path.join(DATA_DIR, f"{camera_id}_live_predictions.csv")
    evaluations_csv = os.path.join(DATA_DIR, f"{camera_id}_live_evaluations.csv")

    if camera_id not in _cached_predictions_dfs:
        _cached_predictions_dfs[camera_id] = read_csv_if_exists(predictions_csv).tail(100)
        
    pred_df = _cached_predictions_dfs[camera_id]
    if pred_df.empty:
        return None

    actual_ts = pd.to_datetime(actual_row["Timestamp"])
    df = pred_df.copy()
    df["forecast_timestamp_dt"] = pd.to_datetime(
        df["forecast_timestamp"], errors="coerce"
    )
    due_df = df[df["forecast_timestamp_dt"] == actual_ts].copy()
    if due_df.empty:
        return None

    existing_eval_df = read_csv_if_exists(evaluations_csv)
    existing_keys = set()
    if not existing_eval_df.empty:
        for _, row in existing_eval_df.iterrows():
            key = (str(row.get("issued_at")), str(row.get("forecast_timestamp")), str(row.get("target")))
            existing_keys.add(key)

    eval_rows = []
    for _, pred_row in due_df.iterrows():
        for target in targets:
            pred_col = f"{target}_pred"
            key = (str(pred_row["issued_at"]), str(pred_row["forecast_timestamp"]), target)
            if key in existing_keys:
                continue

            predicted = float(pred_row[pred_col])
            actual = float(actual_row[target])
            error = actual - predicted
            eval_rows.append({
                "evaluated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "issued_at": pred_row["issued_at"],
                "input_timestamp": pred_row["input_timestamp"],
                "forecast_timestamp": pred_row["forecast_timestamp"],
                "target": target,
                "predicted": predicted,
                "actual": actual,
                "error": error,
                "abs_error": abs(error),
                "squared_error": error ** 2,
            })

    append_rows(evaluations_csv, eval_rows)
    if not eval_rows:
        return None

    abs_errors = [row["abs_error"] for row in eval_rows]
    squared_errors = [row["squared_error"] for row in eval_rows]
    return {
        "forecast_timestamp": to_timestamp_text(actual_ts),
        "count": len(eval_rows),
        "mae": float(np.mean(abs_errors)),
        "rmse": float(np.sqrt(np.mean(squared_errors))),
        "details": eval_rows,
    }


def save_prediction(history_df: pd.DataFrame, camera_id: str = "192_168_10_152", active_targets: list = None) -> dict:
    global _cached_predictions_dfs
    from src.predict import predict_last

    cfg = get_camera_config(camera_id)
    targets = cfg["targets"]
    target_cols = cfg["target_cols"]
    horizon = cfg["horizon"]
    target_to_pred_col = cfg["target_to_pred_col"]
    predictions_csv = os.path.join(DATA_DIR, f"{camera_id}_live_predictions.csv")

    pred_df = predict_last(history_df, camera_id=camera_id)
    input_timestamp = pd.to_datetime(pred_df.iloc[0]["Timestamp"])
    forecast_timestamp = input_timestamp + pd.Timedelta(minutes=horizon)

    record = {
        "camera_ip": camera_id.replace("_", "."),
        "issued_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input_timestamp": to_timestamp_text(input_timestamp),
        "forecast_timestamp": to_timestamp_text(forecast_timestamp),
    }

    # Luôn tính toán và trả về toàn bộ targets trong cấu hình để đảm bảo Server trung tâm đầy đủ thông tin
    targets_to_process = active_targets if active_targets is not None else targets
    for target in targets_to_process:
        try:
            pred_col = target_to_pred_col.get(target, f"{target}_t5")
            if not pred_df.empty and pred_col in pred_df.columns:
                record[f"{target}_pred"] = float(pred_df.iloc[0][pred_col])
            else:
                # Fallback: lấy giá trị nhiệt độ hiện tại từ history_df nếu không có dự báo
                last_val = 30.0
                if target in history_df.columns:
                    val = history_df[target].iloc[-1]
                    last_val = float(val) if pd.notna(val) else 30.0
                record[f"{target}_pred"] = last_val
        except Exception as e:
            print(f"[PREDICT-ERROR] Lỗi khi trích xuất dự báo cho {target} ({camera_id}): {e}")
            record[f"{target}_pred"] = 30.0

    # 1. Fast append to CSV or overwrite last row if split payload
    file_exists = os.path.exists(predictions_csv)
    if file_exists:
        try:
            df = pd.read_csv(predictions_csv)
        except Exception:
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

    pred_headers = ["issued_at", "input_timestamp", "forecast_timestamp"] + [f"{t}_pred" for t in targets]
    for col in pred_headers:
        if col not in df.columns:
            df[col] = None

    is_merged = False
    if not df.empty:
        last_input_time_str = df.iloc[-1]["input_timestamp"]
        try:
            last_time = pd.to_datetime(last_input_time_str)
            curr_time = pd.to_datetime(record["input_timestamp"])
            time_diff = abs((curr_time - last_time).total_seconds())
        except Exception:
            time_diff = 999.0
            
        if time_diff <= 5.0:
            last_idx = df.index[-1]
            for col, val in record.items():
                if pd.notna(val) and val is not None:
                    df.at[last_idx, col] = val
            is_merged = True
            print(f"[MERGE] Overwrote split prediction for {record['input_timestamp']} in last row ({camera_id})")

    if not is_merged:
        row_df = pd.DataFrame([record])
        for col in pred_headers:
            if col not in row_df.columns:
                row_df[col] = None
        row_df = row_df[pred_headers]
        df = pd.concat([df, row_df], ignore_index=True)

    df.to_csv(predictions_csv, index=False)
    _cached_predictions_dfs[camera_id] = df.tail(100)

    return record


def send_prediction_callback(prediction: dict, target_url: str = None) -> dict:
    url = target_url or PREDICTION_CALLBACK_URL
    if not url:
        return {
            "sent": False,
            "reason": "URL callback chưa được cấu hình",
        }

    payload = prediction
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    
    max_retries = 3
    last_error = "Unknown"
    
    for attempt in range(max_retries):
        try:
            req = urlrequest.Request(
                url,
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlrequest.urlopen(req, timeout=CALLBACK_TIMEOUT_SECONDS) as resp:
                response_body = resp.read().decode("utf-8", errors="replace")
                return {
                    "sent": True,
                    "status_code": resp.status,
                    "response": response_body,
                }
        except HTTPError as e:
            last_error = f"HTTP {e.code}"
        except URLError as e:
            last_error = str(e.reason)
        except Exception as e:
            last_error = str(e)
            
        print(f"[CALLBACK] Lần thử {attempt+1}/{max_retries} tới {url} thất bại: {last_error}")
        if attempt < max_retries - 1:
            time.sleep(1) # Chờ 1 giây trước khi thử lại

    return {
        "sent": False,
        "error": last_error,
    }


def get_latest_prediction() -> dict | None:
    predictions_df = read_csv_if_exists(PREDICTIONS_CSV)
    if predictions_df.empty:
        return None

    predictions_df["issued_at_dt"] = pd.to_datetime(
        predictions_df["issued_at"], errors="coerce"
    )
    predictions_df = predictions_df.sort_values("issued_at_dt").reset_index(drop=True)
    latest = predictions_df.iloc[-1].drop(labels=["issued_at_dt"]).to_dict()

    for key, value in latest.items():
        if pd.isna(value):
            latest[key] = None
        elif key.endswith("_pred"):
            latest[key] = float(value)
        else:
            latest[key] = str(value)

    return latest


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/latest-prediction")
@app.get("/api/prediction")
def latest_prediction():
    prediction = get_latest_prediction()
    if not prediction:
        return {
            "success": False,
            "message": "Chưa có prediction nào.",
            "prediction": None,
        }

    return {
        "success": True,
        "prediction": prediction,
    }


@app.post("/api/send-latest-prediction")
def send_latest_prediction():
    prediction = get_latest_prediction()
    if not prediction:
        return {
            "success": False,
            "message": "Chưa có prediction nào để gửi.",
        }

    callback_result = send_prediction_callback(prediction)
    return {
        "success": callback_result.get("sent", False),
        "callback_url": PREDICTION_CALLBACK_URL,
        "prediction": prediction,
        "prediction_callback": callback_result,
    }


# ==========================================
# AUTOMATIC BACKGROUND RETRAINING DAEMON
# ==========================================
training_lock = threading.Lock()
is_training = False

def trigger_background_training(camera_id: str = "192_168_10_152"):
    global is_training
    with training_lock:
        if is_training:
            print(f"[AUTOTRAIN] Một tiến trình huấn luyện đang chạy, bỏ qua kích hoạt trùng lặp cho {camera_id}.", flush=True)
            return
        is_training = True

    def train_job():
        global is_training
        print(f"[AUTOTRAIN] Bắt đầu tự động huấn luyện lại model cho camera {camera_id} (Fine-tuning)...", flush=True)
        try:
            cwd = os.path.dirname(os.path.abspath(__file__))
            venv_python = os.path.join(cwd, "tf_env", "bin", "python")
            if not os.path.exists(venv_python):
                venv_python = sys.executable

            p = subprocess.Popen(
                [venv_python, "train.py", "--camera_id", camera_id],
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            # Đọc liên tục log để tránh đầy buffer ống dẫn
            for line in iter(p.stdout.readline, ''):
                if line:
                    print(f"[AUTOTRAIN-LOG] {line.strip()}", flush=True)
            p.wait()
            print(f"[AUTOTRAIN] Đã hoàn thành tự động huấn luyện lại model cho {camera_id}. Exit code: {p.returncode}", flush=True)
            
            if p.returncode == 0:
                # Nạp lại trọng số mới vào RAM trực tiếp không cần khởi động lại
                from src.predict import reload_model_weights
                reload_model_weights(camera_id)
                
                # Ghi nhận mốc thời gian huấn luyện thành công
                meta_path = os.path.join(cwd, "model", f"{camera_id}_training_meta.json")
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump({"last_trained": time.time()}, f, ensure_ascii=False, indent=4)
                    
        except Exception as e:
            print(f"[AUTOTRAIN-ERROR] Lỗi khi chạy huấn luyện ngầm cho {camera_id}: {e}", flush=True)
        finally:
            with training_lock:
                is_training = False

    threading.Thread(target=train_job, daemon=True).start()


def check_and_trigger_autotrain(camera_id: str = "192_168_10_152"):
    """Tự động kiểm tra xem đã qua 2 ngày (172800 giây) kể từ lần train cuối cùng chưa."""
    cwd = os.path.dirname(os.path.abspath(__file__))
    meta_path = os.path.join(cwd, "model", f"{camera_id}_training_meta.json")
    should_train = False
    
    # 2 ngày = 2 * 24 * 3600 = 172800 giây
    INTERVAL_SECONDS = 172800
    
    if not os.path.exists(meta_path):
        # Chưa từng train tự động -> Đánh dấu mốc ban đầu (không train ngay lập tức để tránh overload lúc mới chạy)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({"last_trained": time.time()}, f, ensure_ascii=False, indent=4)
        return

    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        last_trained = meta.get("last_trained", 0)
        if time.time() - last_trained >= INTERVAL_SECONDS:
            should_train = True
    except Exception:
        should_train = True

    if should_train:
        trigger_background_training(camera_id)


@app.post("/api/thermal-data")
async def receive_thermal_data(request: Request):
    try:
        data = await request.json()

        # Lấy camera_id
        camera_id = get_camera_id(data, request)
        cfg = get_camera_config(camera_id)
        targets = cfg["targets"]
        id_to_label = cfg["id_to_label"]

        # Tạo thư mục lưu log riêng cho từng camera
        cam_save_dir = os.path.join(SAVE_DIR, camera_id)
        os.makedirs(cam_save_dir, exist_ok=True)

        # lưu raw json ra file để kiểm tra
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(cam_save_dir, f"thermal_{now_str}.json")

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        # Tự động dọn dẹp để giữ tối đa 50 file log mới nhất cho camera này
        prune_received_data(camera_id, max_files=50)

        print(f"=== NHẬN DỮ LIỆU THÀNH CÔNG TỪ CAMERA {camera_id} ===")
        print(json.dumps(data, ensure_ascii=False, indent=2))

        row = thermal_json_to_row(data, camera_id=camera_id)
        
        # Xác định các điểm thực sự có dữ liệu trong lượt này (chỉ giữ các điểm được cấu hình)
        active_points = [p.get("id") for p in data.get("points", [])]
        active_targets = []
        for p_id in active_points:
            raw_id = str(p_id).replace(":", "_")
            lbl = id_to_label.get(raw_id, raw_id)
            if lbl in targets:
                active_targets.append(lbl)

        # Nếu không có target nào hoạt động trong gói tin này (ví dụ: chỉ chứa điểm đã bị xoá/không theo dõi), bỏ qua hoàn toàn để tránh lưu dòng trống
        if not active_targets:
            print(f"[THERMAL] Gói tin từ {camera_id} không chứa bất kỳ điểm/vùng nào trong cấu hình TARGETS. Bỏ qua không xử lý.")
            return {"status": "skipped", "message": "No active targets in payload, skipping history and prediction"}

        prediction = None
        prediction_status = "not_started"
        callback_result = None

        with state_lock:
            history_df = save_history_row(row, camera_id=camera_id)
            evaluation = evaluate_due_predictions(row, camera_id=camera_id)

            print(f"Dữ liệu hiện có: {len(history_df)} dòng trong lịch sử. Active: {active_targets}")
            try:
                prediction = save_prediction(history_df, camera_id=camera_id, active_targets=active_targets)
                prediction_status = "created"
                print("Dự đoán thành công!")
            except ValueError as e:
                prediction_status = f"not_ready: {e}"
                print(f"Chưa thể dự đoán: {e}")
            except Exception as e:
                prediction_status = f"failed: {e}"
                print(f"Lỗi khi dự đoán: {e}")
        # Thực hiện cơ chế PUSH dự báo sang Server trung tâm (hoặc bên thứ 3)
        if prediction:
            target_url = PREDICTION_CALLBACK_URL
            if not target_url:
                client_ip = request.client.host
                target_url = f"http://{client_ip}:8080/api/prediction"
            
            print(f"Đang gửi dự đoán tới {target_url}...")
            callback_result = send_prediction_callback(prediction, target_url=target_url)
            
            if callback_result.get("sent"):
                print(f"Gửi thành công tới {target_url}")
            else:
                print(f"Gửi thất bại tới {target_url}: {callback_result.get('error') or callback_result.get('reason')}")

        print(f"Đã lưu history: {len(history_df)} dòng")
        if evaluation:
            print(
                "Đã đánh giá prediction cũ: "
                f"forecast_timestamp={evaluation['forecast_timestamp']}, "
                f"MAE={evaluation['mae']:.4f}, RMSE={evaluation['rmse']:.4f}"
            )
        else:
            print("Chưa có prediction cũ đến hạn để so sánh")

        print(f"Trạng thái dự đoán mới: {prediction_status}")
        if prediction:
            print(json.dumps(prediction, ensure_ascii=False, indent=2))
        # Tự động kiểm tra và kích hoạt huấn luyện lại model sau mỗi 2 ngày
        try:
            check_and_trigger_autotrain(camera_id)
        except Exception as ex:
            print(f"[AUTOTRAIN-ERROR] Lỗi khi kiểm tra tự động huấn luyện cho {camera_id}: {ex}", flush=True)

        return {
            "success": True,
            "message": f"Đã nhận dữ liệu nhiệt cho {camera_id}",
            "received_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "actual_row": row,
            "history_rows": len(history_df),
            "evaluation": evaluation,
            "prediction_status": prediction_status,
            "prediction": prediction,
            "prediction_callback": callback_result,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/v1/config/thermal")
@app.post("/config/thermal")
async def save_thermal_config(request: Request, forward: bool = True):
    """
    1. API cập nhật tọa độ hình ảnh (Thermal Analyzer Configuration):
    """
    try:
        data = await request.json()
        
        # Bỏ qua nếu đây thực tế là gói tin đo nhiệt độ từ camera gửi nhầm tới endpoint cấu hình
        is_measurement = any("temperature" in p for p in data.get("points", []))
        if is_measurement:
            print("[CONFIG-WARNING] Nhận gói tin đo nhiệt tại endpoint /config/thermal. Bỏ qua cấu hình.", flush=True)
            return {"success": False, "error": "Endpoint dành cho cấu hình tọa độ, không phải dữ liệu đo nhiệt."}

        camera_id = get_camera_id(data, request)
        config_path = os.path.join(DATA_DIR, f"{camera_id}_thermal_points.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"[CONFIG] Đã nhận và lưu cấu hình điểm đo nhiệt mới cho {camera_id} vào: {config_path}")

        # 1a. Forward cấu hình sang Server trung tâm (192.168.10.102:8100)
        if forward:
            try:
                central_url = "http://192.168.10.102:8100/config/thermal"
                print(f"[CONFIG] Forwarding config/thermal to central server: {central_url}")
                requests.post(central_url, json=data, timeout=5)
            except Exception as e:
                print(f"[CONFIG-ERROR] Failed to forward config/thermal to central server: {e}")

        # 1b. Tự động đồng bộ targets từ các points và zones vừa nhận vào config.json
        targets = []
        if "points" in data:
            targets.extend([p.get("label") or p.get("id") for p in data["points"] if p.get("label") or p.get("id")])
        if "zones" in data:
            targets.extend([z.get("label") or z.get("id") for z in data["zones"] if z.get("label") or z.get("id")])
        if targets:
                config_path_json = f"model/{camera_id}_config.json"
                if os.path.exists(config_path_json):
                    with open(config_path_json, "r", encoding="utf-8") as f:
                        model_config = json.load(f)
                else:
                    model_config = {"window_size": 5, "horizon": 5, "seasonal_period": 60}

                model_config["targets"] = targets
                
                # Tạo động feature_cols và target_cols
                horizon = model_config.get("horizon", 5)
                feature_cols = []
                target_cols = []
                for t in targets:
                    feature_cols.extend([t, f"{t}_trend", f"{t}_seasonal", f"{t}_residual"])
                    target_cols.append(f"{t}_t{horizon}")
                    
                model_config["feature_cols"] = feature_cols
                model_config["target_cols"] = target_cols

                with open(config_path_json, "w", encoding="utf-8") as f:
                    json.dump(model_config, f, ensure_ascii=False, indent=4)

                # Đồng bộ và thêm cột mới (giữ lại dữ liệu cũ)
                headers = ["Timestamp"] + targets
                history_csv = os.path.join(DATA_DIR, f"{camera_id}_live_thermal_history.csv")
                sync_csv_headers(history_csv, headers)

                # Đồng bộ cấu trúc dự báo mới
                pred_headers = ["issued_at", "input_timestamp", "forecast_timestamp"] + [f"{t}_pred" for t in targets]
                predictions_csv = os.path.join(DATA_DIR, f"{camera_id}_live_predictions.csv")
                sync_csv_headers(predictions_csv, pred_headers)
                
                eval_headers = ["evaluated_at", "issued_at", "input_timestamp", "forecast_timestamp", "target", "predicted", "actual", "error", "abs_error", "squared_error"]
                evaluations_csv = os.path.join(DATA_DIR, f"{camera_id}_live_evaluations.csv")
                sync_csv_headers(evaluations_csv, eval_headers)

                # Nạp lại cấu hình vào bộ nhớ RAM
                reload_config(camera_id)

                print(f"[CONFIG] Đã tự động đồng bộ targets từ points mới cho {camera_id}: {targets}. Kích hoạt Retrain...")
                trigger_background_training(camera_id)

        return {"status": "ok"}
    except Exception as e:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=500, content={"status": "error", "error": str(e)})

@app.post("/api/config/update")
async def update_forecasting_targets(request: Request, forward: bool = True):
    """
    2. API cập nhật danh sách dự báo (Forecasting Targets):
    """
    try:
        data = await request.json()
        targets = data.get("targets")
        if not targets:
            return {"success": False, "error": "Thiếu danh sách targets"}

        camera_id = get_camera_id(data, request)

        # 2a. Forward cấu hình sang Server trung tâm (192.168.10.102:8100)
        if forward:
            try:
                central_url = "http://192.168.10.102:8100/api/config/update"
                print(f"[CONFIG] Forwarding api/config/update to central server: {central_url}")
                requests.post(central_url, json=data, timeout=5)
            except Exception as e:
                print(f"[CONFIG-ERROR] Failed to forward api/config/update to central server: {e}")

        # Đọc config.json hiện tại
        config_path = f"model/{camera_id}_config.json"
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                model_config = json.load(f)
        else:
            model_config = {"window_size": 5, "horizon": 5, "seasonal_period": 60}

        model_config["targets"] = targets
        
        # Tạo động feature_cols và target_cols
        horizon = model_config.get("horizon", 5)
        feature_cols = []
        target_cols = []
        for t in targets:
            feature_cols.extend([t, f"{t}_trend", f"{t}_seasonal", f"{t}_residual"])
            target_cols.append(f"{t}_t{horizon}")
            
        model_config["feature_cols"] = feature_cols
        model_config["target_cols"] = target_cols

        # Ghi đè targets vào file config
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(model_config, f, ensure_ascii=False, indent=4)

        # Đồng bộ và thêm cột mới (giữ lại dữ liệu cũ)
        headers = ["Timestamp"] + targets
        history_csv = os.path.join(DATA_DIR, f"{camera_id}_live_thermal_history.csv")
        sync_csv_headers(history_csv, headers)

        # Đồng bộ cấu trúc dự báo mới
        pred_headers = ["issued_at", "input_timestamp", "forecast_timestamp"] + [f"{t}_pred" for t in targets]
        predictions_csv = os.path.join(DATA_DIR, f"{camera_id}_live_predictions.csv")
        sync_csv_headers(predictions_csv, pred_headers)
        
        eval_headers = ["evaluated_at", "issued_at", "input_timestamp", "forecast_timestamp", "target", "predicted", "actual", "error", "abs_error", "squared_error"]
        evaluations_csv = os.path.join(DATA_DIR, f"{camera_id}_live_evaluations.csv")
        sync_csv_headers(evaluations_csv, eval_headers)

        # Nạp lại cấu hình vào bộ nhớ RAM
        reload_config(camera_id)

        print(f"[CONFIG] Đã cập nhật targets dự báo mới cho {camera_id}: {targets}. Làm sạch dữ liệu cũ và kích hoạt Retrain...")

        # Kích hoạt tiến trình Retrain ngầm
        trigger_background_training(camera_id)
        
        # --- TRIGGER DỰ ĐOÁN NGAY LẬP TỨC SAU KHI ĐỔI CẤU HÌNH ---
        try:
            current_history = _cached_history_dfs.get(camera_id)
            if current_history is None and os.path.exists(history_csv):
                current_history = pd.read_csv(history_csv).tail(100)
            
            if current_history is not None and not current_history.empty:
                print(f"[CONFIG] Đang chạy dự báo tức thì sau khi cập nhật danh sách targets cho {camera_id}...")
                with state_lock:
                    prediction = save_prediction(current_history, camera_id=camera_id, active_targets=targets)
                    if prediction:
                        send_prediction_callback(prediction)
                        print(f"[CONFIG] Đã gửi dự báo cập nhật thành công cho {camera_id}!")
        except Exception as pred_ex:
            print(f"[CONFIG-ERROR] Không thể chạy dự báo tức thì cho {camera_id}: {pred_ex}")

        return {"success": True, "message": f"Cấu hình targets mới thành công cho {camera_id} và đang retrain ngầm"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/prediction/history")
def get_prediction_history(camera_id: str = "192_168_10_152"):
    """
    Trả về dữ liệu lịch sử thực tế song song với dữ liệu dự báo cho từng mốc thời gian.
    Format: { "history": [ { "timestamp": "HH:MM", "Nhãn_1_actual": 31.5, "Nhãn_1_pred": 32.0, ... } ] }
    """
    try:
        camera_id = camera_id.replace(".", "_")
        history_csv = os.path.join(DATA_DIR, f"{camera_id}_live_thermal_history.csv")
        predictions_csv = os.path.join(DATA_DIR, f"{camera_id}_live_predictions.csv")

        history_df = read_csv_if_exists(history_csv)
        predictions_df = read_csv_if_exists(predictions_csv)

        timestamps = set()
        if not history_df.empty and "Timestamp" in history_df.columns:
            timestamps.update(history_df["Timestamp"].dropna().tolist())
        if not predictions_df.empty and "forecast_timestamp" in predictions_df.columns:
            timestamps.update(predictions_df["forecast_timestamp"].dropna().tolist())

        sorted_timestamps = sorted(list(timestamps))

        history_lookup = {}
        if not history_df.empty:
            for _, r in history_df.iterrows():
                ts = r.get("Timestamp")
                if ts:
                    history_lookup[str(ts)] = r.to_dict()

        pred_lookup = {}
        if not predictions_df.empty:
            for _, r in predictions_df.iterrows():
                ts = r.get("forecast_timestamp")
                if ts:
                    pred_lookup[str(ts)] = r.to_dict()

        history_list = []
        cfg = get_camera_config(camera_id)
        targets = cfg["targets"]

        # Lấy tối đa 50 mốc thời gian gần nhất để vẽ biểu đồ
        for ts in sorted_timestamps[-50:]:
            try:
                dt = pd.to_datetime(ts)
                time_str = dt.strftime("%H:%M")
            except Exception:
                time_str = str(ts)

            entry = {"timestamp": time_str}
            hist_row = history_lookup.get(ts, {})
            pred_row = pred_lookup.get(ts, {})

            for target in targets:
                # Actual
                val_act = hist_row.get(target)
                if pd.isna(val_act) or val_act is None:
                    val_act = None
                else:
                    val_act = float(val_act)
                entry[f"{target}_actual"] = val_act

                # Predicted
                val_pred = pred_row.get(f"{target}_pred")
                if pd.isna(val_pred) or val_pred is None:
                    val_pred = None
                else:
                    val_pred = float(val_pred)
                entry[f"{target}_pred"] = val_pred

            history_list.append(entry)

        return {"history": history_list}
    except Exception as e:
        return {"history": [], "error": str(e)}

@app.get("/api/training-status")
def get_training_status(camera_id: str = "192_168_10_152"):
    """
    Trả về trạng thái tiến trình huấn luyện model ngầm
    """
    global is_training
    camera_id = camera_id.replace(".", "_")
    cwd = os.path.dirname(os.path.abspath(__file__))
    meta_path = os.path.join(cwd, "model", f"{camera_id}_training_meta.json")
    last_trained_str = None
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            last_trained_time = meta.get("last_trained", 0)
            last_trained_str = datetime.fromtimestamp(last_trained_time).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass

    return {
        "status": "training" if is_training else "idle",
        "last_trained": last_trained_str
    }


if __name__ == "__main__":
    uvicorn.run("thermal_receiver:app", host="0.0.0.0", port=8080, reload=True)
    # Trigger config reload check
