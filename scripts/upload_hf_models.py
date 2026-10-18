#!/usr/bin/env python3
"""
Upload Artifacts to Hugging Face Hub (Public Repo: neitpm/ai-thermal-detect-models)
Reads HF_TOKEN strictly from environment ($env:HF_TOKEN).
Never prints token, never writes token to disk.
"""

import os
import sys
import shutil
import tempfile
from huggingface_hub import HfApi, create_repo

REPO_ID = "neitpm/ai-thermal-detect-models"

ARTIFACT_MAPPING = {
    # Detection
    "models/best.onnx": "models/yolo_uniform.onnx",
    "models/best.pt": "models/yolo_uniform.pt",
    "models/yolov8n.engine": "models/yolov8n.engine",
    # Forecasting
    "timeseries_service/model/linear_reg.pkl": "forecasting/linear_reg.pkl",
    "timeseries_service/model/scaler_X.pkl": "forecasting/scaler_X.pkl",
    "timeseries_service/model/scaler_y.pkl": "forecasting/scaler_y.pkl",
    "timeseries_service/model/mtkan_model.keras": "forecasting/mtkan_model.keras",
    "timeseries_service/model/mtkan_weights.weights.h5": "forecasting/mtkan_weights.weights.h5",
    "timeseries_service/model/config.json": "forecasting/config.json",
    "timeseries_service/model/metrics_test.csv": "forecasting/metrics_test.csv",
    # Inference scripts
    "scripts/infer_yolo.py": "scripts/infer_yolo.py",
    "scripts/forecast_temperature.py": "scripts/forecast_temperature.py",
    # Metadata
    "metadata/model_manifest.json": "metadata/model_manifest.json",
    "metadata/checksums.sha256": "metadata/checksums.sha256",
    "metadata/HF_MODEL_CARD.md": "README.md"
}

def main():
    token = os.environ.get("HF_TOKEN")
    if not token or not token.strip():
        print("ERROR: Environment variable HF_TOKEN is not set or empty.", file=sys.stderr)
        print("Please set it in PowerShell: $env:HF_TOKEN = 'your_hf_token'", file=sys.stderr)
        sys.exit(1)

    print("Authenticating with Hugging Face Hub...")
    api = HfApi(token=token.strip())

    try:
        user_info = api.whoami()
        print(f"Authenticated as user: {user_info.get('name', 'Unknown')}")
    except Exception as e:
        print(f"Authentication failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Ensuring repository exists: {REPO_ID} (public)...")
    try:
        create_repo(repo_id=REPO_ID, repo_type="model", token=token.strip(), exist_ok=True, private=False)
        print("Repository is ready.")
    except Exception as e:
        print(f"Failed to create/access repo: {e}", file=sys.stderr)
        sys.exit(1)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    with tempfile.TemporaryDirectory() as staging_dir:
        print(f"Staging validated artifacts in temporary directory: {staging_dir}")
        uploaded_count = 0
        
        for local_rel, hub_rel in ARTIFACT_MAPPING.items():
            local_full = os.path.join(base_dir, local_rel)
            if not os.path.exists(local_full):
                print(f"[SKIP] File does not exist locally: {local_rel}")
                continue

            dest_full = os.path.join(staging_dir, hub_rel)
            os.makedirs(os.path.dirname(dest_full), exist_ok=True)
            shutil.copy2(local_full, dest_full)
            size_kb = os.path.getsize(dest_full) / 1024.0
            print(f"  + Prepared: {hub_rel} ({size_kb:.1f} KB)")
            uploaded_count += 1

        print(f"\nUploading {uploaded_count} artifacts to {REPO_ID}...")
        api.upload_folder(
            folder_path=staging_dir,
            repo_id=REPO_ID,
            repo_type="model",
            commit_message="feat: upload verified thermal detection and forecasting models with manifest",
            token=token.strip()
        )
        print(f"\nSuccessfully published {uploaded_count} artifacts to: https://huggingface.co/{REPO_ID}")

if __name__ == "__main__":
    main()
