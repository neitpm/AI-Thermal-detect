#!/bin/bash

# ==============================================================================
# SMART CAMERA EDGE SYSTEM - SYSTEMD INSTALLATION SCRIPT
# This script automates dependency installation, virtual environment setup,
# and registers the systemd service to run the system in the background.
# ==============================================================================

# Ensure script is run with root privileges
if [ "$EUID" -ne 0 ]; then
  echo "Error: Please run this script as root (use sudo)."
  exit 1
fi

# Resolve the absolute path of the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_FILE="${PROJECT_DIR}/smart_camera.service.template"
SERVICE_FILE="/etc/systemd/system/smart_camera.service"

echo "================================================================="
echo " Installing Smart Camera Edge System Service"
echo " Project Directory: ${PROJECT_DIR}"
echo "================================================================="

# 1. Update and install system dependencies (apt)
echo "[1/6] Checking system package dependencies..."
apt-get update -y
apt-get install -y python3-pip python3-venv python3-dev build-essential

# 2. Setup virtual environment for Thermal Receiver
echo "[2/6] Setting up Python virtual environment (tf_env)..."
VENV_DIR="${PROJECT_DIR}/timeseries_service/tf_env"
if [ ! -d "${VENV_DIR}" ]; then
  python3 -m venv "${VENV_DIR}"
  echo "Created virtual environment at ${VENV_DIR}"
else
  echo "Virtual environment already exists at ${VENV_DIR}"
fi

# 3. Install Python dependencies
echo "[3/6] Installing Python dependencies..."
# Update pip inside venv
"${VENV_DIR}/bin/pip" install --upgrade pip

# Install dependencies inside venv (for thermal receiver)
echo "Installing packages inside tf_env virtual environment..."
"${VENV_DIR}/bin/pip" install fastapi uvicorn requests numpy==1.23.5 pandas scikit-learn joblib

# Install dependencies for system python (for YOLO script)
echo "Installing packages in system python..."
pip3 install opencv-python requests numpy

# 4. Verify configuration (.env) exists
echo "[4/6] Checking environment configuration..."
if [ ! -f "${PROJECT_DIR}/.env" ]; then
  echo "[WARNING] .env file not found. Creating from .env.example..."
  cp "${PROJECT_DIR}/.env.example" "${PROJECT_DIR}/.env"
  echo "[IMPORTANT] Please configure the IP addresses and credentials in ${PROJECT_DIR}/.env"
else
  echo ".env configuration file verified."
fi

# 5. Create the Systemd service file from template
echo "[5/6] Generating systemd service file..."
if [ ! -f "${TEMPLATE_FILE}" ]; then
  echo "Error: Template file ${TEMPLATE_FILE} not found."
  exit 1
fi
sed "s|{{WORKING_DIRECTORY}}|${PROJECT_DIR}|g" "${TEMPLATE_FILE}" > "${SERVICE_FILE}"

# Set appropriate permissions
chmod 644 "${SERVICE_FILE}"

# 6. Enable and start the Service
echo "[6/6] Registering service with Systemd..."
systemctl daemon-reload
systemctl enable smart_camera.service
systemctl restart smart_camera.service

# Check service status
sleep 2
echo "================================================================="
echo " Installation Complete!"
echo "================================================================="
systemctl status smart_camera.service --no-pager

echo ""
echo "To monitor real-time logs, run:"
echo "  sudo journalctl -u smart_camera.service -f"
echo ""
echo "To stop the service, run:"
echo "  sudo systemctl stop smart_camera.service"
echo ""
echo "To restart the service, run:"
echo "  sudo systemctl restart smart_camera.service"
echo "================================================================="
