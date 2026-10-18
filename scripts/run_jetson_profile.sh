#!/bin/bash
# ==============================================================================
# Jetson Hardware Profiling & Benchmark Runner
# Usage:
#   chmod +x run_jetson_profile.sh
#   ./run_jetson_profile.sh
# ==============================================================================

set -e

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_DIR="./benchmark_results_${TIMESTAMP}"
mkdir -p "${OUTPUT_DIR}"

echo "=========================================================="
echo " Starting Jetson In-Situ Hardware Profiling & Benchmark"
echo " Destination: ${OUTPUT_DIR}"
echo "=========================================================="

SYS_FILE="${OUTPUT_DIR}/jetson_system_info.txt"
LOG_FILE="${OUTPUT_DIR}/jetson_inference.log"

echo "=== JETSON SYSTEM AUDIT ===" > "${SYS_FILE}"
date >> "${SYS_FILE}"

echo "[1/7] Querying Device Tree Model..."
if [ -f /proc/device-tree/model ]; then
    cat /proc/device-tree/model >> "${SYS_FILE}"
    echo "" >> "${SYS_FILE}"
else
    echo "Unknown / Not Tegra device-tree" >> "${SYS_FILE}"
fi

echo "[2/7] Querying L4T Release (/etc/nv_tegra_release)..."
if [ -f /etc/nv_tegra_release ]; then
    cat /etc/nv_tegra_release >> "${SYS_FILE}"
else
    echo "nv_tegra_release not found" >> "${SYS_FILE}"
fi

echo "[3/7] Querying Python & TensorRT Versions..."
python3 --version >> "${SYS_FILE}" 2>&1 || true
if command -v trtexec >/dev/null 2>&1; then
    trtexec --version >> "${SYS_FILE}" 2>&1 || true
else
    echo "trtexec: command not found in PATH" >> "${SYS_FILE}"
fi

echo "[4/7] Querying GPU Driver / nvidia-smi / tegrastats..."
if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi >> "${SYS_FILE}" 2>&1 || true
else
    echo "nvidia-smi not available on this Tegra architecture" >> "${SYS_FILE}"
fi

echo "[5/7] Querying NVPModel and Jetson Clocks..."
if command -v nvpmodel >/dev/null 2>&1; then
    echo "--- nvpmodel -q ---" >> "${SYS_FILE}"
    sudo nvpmodel -q >> "${SYS_FILE}" 2>&1 || nvpmodel -q >> "${SYS_FILE}" 2>&1 || true
fi

echo "[6/7] Querying Thermal Zones..."
echo "--- Thermal Zones ---" >> "${SYS_FILE}"
for zone in /sys/devices/virtual/thermal/thermal_zone*; do
    if [ -f "$zone/type" ] && [ -f "$zone/temp" ]; then
        echo "$(cat $zone/type): $(awk '{printf "%.1f C", $1/1000}' $zone/temp)" >> "${SYS_FILE}"
    fi
done

echo "[7/7] Running Python Benchmark Suite..."
python3 ./scripts/jetson_benchmark_collector.py || true

# Copy generated files to output dir if created locally
if [ -f jetson_benchmark.json ]; then
    mv jetson_benchmark.json "${OUTPUT_DIR}/"
fi
if [ -f jetson_system_info.txt ]; then
    cp jetson_system_info.txt "${OUTPUT_DIR}/"
fi
if [ -f jetson_inference.log ]; then
    mv jetson_inference.log "${OUTPUT_DIR}/"
fi

echo "=========================================================="
echo " Benchmark profiling completed."
echo " Artifacts saved in: ${OUTPUT_DIR}"
echo " Files:"
ls -lh "${OUTPUT_DIR}"
echo "=========================================================="
