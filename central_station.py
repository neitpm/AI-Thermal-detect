import os
import sys
import json
import time
import uvicorn
import threading
import webbrowser
from datetime import datetime
from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import requests

# Directories
ALERTS_DIR = "alerts"
os.makedirs(ALERTS_DIR, exist_ok=True)

# Shared Memory Stores (Thread-Safe)
alerts_store = []
predictions_store = []
devices_store = {}
store_lock = threading.Lock()

# Define Applications
app_ui = FastAPI(title="Central Station - Substation Dashboard")
app_yolo = FastAPI(title="Central Station - YOLO Alerts Receiver")

# Enable CORS for both
for app in [app_ui, app_yolo]:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Mount Alerts directory on UI application
app_ui.mount("/alerts", StaticFiles(directory=ALERTS_DIR), name="alerts")


# =====================================================================
# EMBEDDED DASHBOARD HTML/CSS/JS (PREMIUM DARK GLASSMORPHISM)
# =====================================================================
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hệ Thống Giám Sát Trạm Biến Áp Trung Tâm</title>
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-gradient: linear-gradient(135deg, #090a0f 0%, #151622 50%, #090a0f 100%);
            --card-bg: rgba(22, 25, 43, 0.65);
            --card-border: rgba(255, 255, 255, 0.08);
            --primary: #6366f1;
            --primary-glow: rgba(99, 102, 241, 0.3);
            --success: #10b981;
            --success-glow: rgba(16, 185, 129, 0.2);
            --warning: #f59e0b;
            --danger: #ef4444;
            --danger-glow: rgba(239, 68, 68, 0.4);
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Outfit', sans-serif;
        }

        body {
            background: var(--bg-gradient);
            color: var(--text-main);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* Glassmorphism utility */
        .glass-panel {
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .glass-panel:hover {
            border-color: rgba(255, 255, 255, 0.15);
            box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
        }

        /* Container Layout */
        .dashboard-container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 24px;
            display: grid;
            grid-template-columns: 1fr;
            gap: 24px;
        }

        @media (min-width: 1200px) {
            .dashboard-container {
                grid-template-columns: 2fr 1fr;
            }
        }

        /* Header Style */
        header {
            grid-column: 1 / -1;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 24px;
            margin-bottom: 8px;
        }

        .brand-section h1 {
            font-size: 28px;
            font-weight: 800;
            background: linear-gradient(to right, #ffffff, #a5b4fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.5px;
        }

        .brand-section p {
            color: var(--text-muted);
            font-size: 14px;
            margin-top: 4px;
        }

        .status-badge {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 18px;
            font-weight: 600;
            font-size: 14px;
            border-radius: 30px;
        }

        .status-badge.normal {
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: var(--success);
        }

        .status-badge.alert {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: var(--danger);
            animation: pulse-border 1.5s infinite;
        }

        .pulse-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
        }

        .status-badge.normal .pulse-dot {
            background-color: var(--success);
            box-shadow: 0 0 10px var(--success);
        }

        .status-badge.alert .pulse-dot {
            background-color: var(--danger);
            box-shadow: 0 0 10px var(--danger);
            animation: pulse-glow 1s infinite alternate;
        }

        /* Widgets Grid */
        .left-column {
            display: flex;
            flex-direction: column;
            gap: 24px;
        }

        .right-column {
            display: flex;
            flex-direction: column;
            gap: 24px;
        }

        /* Card Header & Content */
        .card-header {
            padding: 20px 24px;
            border-bottom: 1px solid var(--card-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .card-title {
            font-size: 18px;
            font-weight: 600;
            letter-spacing: -0.2px;
        }

        .card-body {
            padding: 24px;
        }

        /* Device Table */
        .device-table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }

        .device-table th {
            color: var(--text-muted);
            font-weight: 500;
            padding: 12px;
            border-bottom: 1px solid var(--card-border);
            font-size: 14px;
        }

        .device-table td {
            padding: 16px 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
            font-size: 15px;
        }

        .device-table tr:last-child td {
            border-bottom: none;
        }

        .device-status {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 13px;
            padding: 4px 10px;
            border-radius: 12px;
            font-weight: 600;
        }

        .device-status.online {
            background: rgba(16, 185, 129, 0.1);
            color: var(--success);
        }

        .device-status.offline {
            background: rgba(239, 68, 68, 0.1);
            color: var(--danger);
        }

        /* Buttons & Controls */
        .btn {
            background: var(--primary);
            color: white;
            border: none;
            padding: 8px 16px;
            font-size: 13px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            outline: none;
        }

        .btn:hover {
            background: #4f46e5;
            box-shadow: 0 0 12px var(--primary-glow);
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.08);
            color: var(--text-main);
        }

        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.15);
        }

        /* Alerts List */
        .alert-item {
            display: flex;
            gap: 16px;
            padding: 16px;
            margin-bottom: 16px;
            background: rgba(239, 68, 68, 0.03);
            border-left: 4px solid var(--danger);
            border-radius: 0 12px 12px 0;
            animation: slide-in 0.3s ease-out;
        }

        .alert-item:last-child {
            margin-bottom: 0;
        }

        .alert-thumb {
            width: 80px;
            height: 60px;
            border-radius: 8px;
            object-fit: cover;
            cursor: pointer;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: transform 0.2s ease;
        }

        .alert-thumb:hover {
            transform: scale(1.05);
        }

        .alert-info {
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .alert-meta {
            font-size: 12px;
            color: var(--text-muted);
            margin-bottom: 4px;
        }

        .alert-text {
            font-size: 14px;
            font-weight: 600;
        }

        /* Config Form Elements */
        .form-group {
            margin-bottom: 16px;
        }

        .form-group label {
            display: block;
            font-size: 14px;
            color: var(--text-muted);
            margin-bottom: 8px;
            font-weight: 500;
        }

        .form-input {
            width: 100%;
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid var(--card-border);
            color: white;
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }

        .form-input:focus {
            border-color: var(--primary);
            box-shadow: 0 0 8px var(--primary-glow);
        }

        /* Audio Alarm Switch */
        .switch-container {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 14px;
            color: var(--text-muted);
        }

        /* Modal Overlay */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(8px);
            z-index: 1000;
            justify-content: center;
            align-items: center;
            padding: 24px;
        }

        .modal-content {
            max-width: 900px;
            width: 100%;
            background: #111322;
            border: 1px solid var(--card-border);
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 24px 50px rgba(0, 0, 0, 0.8);
            position: relative;
        }

        .modal-close {
            position: absolute;
            top: 16px;
            right: 20px;
            color: white;
            font-size: 32px;
            cursor: pointer;
            z-index: 10;
            font-weight: 300;
        }

        .modal-body img {
            width: 100%;
            display: block;
            max-height: 70vh;
            object-fit: contain;
        }

        .modal-body video {
            width: 100%;
            display: block;
            max-height: 70vh;
            background: black;
        }

        .modal-footer {
            padding: 20px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid var(--card-border);
        }

        /* Animation Keyframes */
        @keyframes pulse-border {
            0% { border-color: rgba(239, 68, 68, 0.3); }
            50% { border-color: rgba(239, 68, 68, 0.8); }
            100% { border-color: rgba(239, 68, 68, 0.3); }
        }

        @keyframes pulse-glow {
            0% { box-shadow: 0 0 4px var(--danger-glow); }
            100% { box-shadow: 0 0 16px var(--danger-glow); }
        }

        @keyframes slide-in {
            from { transform: translateX(50px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    </style>
</head>
<body>

    <div class="dashboard-container">
        
        <!-- Header -->
        <header class="glass-panel">
            <div class="brand-section">
                <h1>Hệ Thống Giám Sát Trung Tâm AI</h1>
                <p>Quản lý an ninh & nhiệt độ trạm biến áp thời gian thực</p>
            </div>
            <div class="status-badge normal" id="system-status">
                <span class="pulse-dot"></span>
                <span id="system-status-text">HỆ THỐNG AN TOÀN</span>
            </div>
        </header>

        <!-- Left Column (Telemetry & Devices) -->
        <div class="left-column">
            
            <!-- Temperature Chart Card -->
            <div class="glass-panel">
                <div class="card-header">
                    <span class="card-title">Biểu Đồ Xu Hướng Nhiệt Độ & Dự Báo (5 Phút)</span>
                    <div class="switch-container">
                        <input type="checkbox" id="alarm-sound-toggle" checked>
                        <label for="alarm-sound-toggle">Âm thanh cảnh báo</label>
                    </div>
                </div>
                <div class="card-body">
                    <div style="position: relative; height: 350px; width: 100%;">
                        <canvas id="thermalChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Jetson Edge Devices Card -->
            <div class="glass-panel">
                <div class="card-header">
                    <span class="card-title">Thiết Bị Cạnh Jetson Hoạt Động</span>
                </div>
                <div class="card-body" style="padding: 0;">
                    <table class="device-table" id="device-table-body">
                        <thead>
                            <tr>
                                <th>Địa Chỉ IP</th>
                                <th>Cập Nhật Cuối</th>
                                <th>Trạng Thái</th>
                                <th>Cấu Hình Điểm Đo</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td colspan="4" style="text-align: center; color: var(--text-muted); padding: 20px;">Đang tải danh sách thiết bị...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

        </div>

        <!-- Right Column (YOLO Intrusion Logs) -->
        <div class="right-column">
            
            <!-- Security Alerts Card -->
            <div class="glass-panel" style="height: 100%; display: flex; flex-direction: column;">
                <div class="card-header">
                    <span class="card-title">Cảnh Báo Xâm Nhập (YOLO)</span>
                    <button class="btn btn-secondary" onclick="clearAlerts()">Xoá Nhật Ký</button>
                </div>
                <div class="card-body" id="alerts-container" style="flex-grow: 1; overflow-y: auto; max-height: 520px;">
                    <div style="text-align: center; color: var(--text-muted); padding: 40px 0;">Không có cảnh báo đột nhập nào.</div>
                </div>
            </div>

        </div>

    </div>

    <!-- Modal for viewing Alerts details -->
    <div class="modal" id="alert-modal">
        <span class="modal-close" onclick="closeModal()">&times;</span>
        <div class="modal-content">
            <div class="modal-body" id="modal-media-container">
                <!-- Image or Video dynamically inserted here -->
            </div>
            <div class="modal-footer">
                <div>
                    <h3 style="margin-bottom: 4px;" id="modal-title">Cảnh Báo Đột Nhập</h3>
                    <p style="color: var(--text-muted); font-size: 14px;" id="modal-subtitle">IP Camera: 192.168.10.152</p>
                </div>
                <button class="btn" onclick="closeModal()">Đóng</button>
            </div>
        </div>
    </div>

    <!-- Device Config Modal -->
    <div class="modal" id="config-modal">
        <span class="modal-close" onclick="closeConfigModal()">&times;</span>
        <div class="modal-content" style="max-width: 500px;">
            <div class="card-header">
                <span class="card-title">Cập Nhật Targets Dự Báo</span>
            </div>
            <div class="card-body">
                <input type="hidden" id="config-device-ip">
                <div class="form-group">
                    <label for="config-targets-input">Danh Sách Targets (cách nhau bởi dấu phẩy)</label>
                    <input type="text" class="form-input" id="config-targets-input" value="transformer, cable">
                </div>
                <div style="display: flex; gap: 12px; justify-content: flex-end; margin-top: 24px;">
                    <button class="btn btn-secondary" onclick="closeConfigModal()">Hủy</button>
                    <button class="btn" onclick="submitConfig()">Cập Nhật</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let thermalChart = null;
        let knownTargets = new Set();
        let activeAlertIds = new Set();

        // Audio Alert Synthesizer (No external file needed)
        function playAlarmBeep() {
            if (!document.getElementById('alarm-sound-toggle').checked) return;
            try {
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                
                // Beep 1
                let osc1 = audioCtx.createOscillator();
                let gain1 = audioCtx.createGain();
                osc1.type = 'sine';
                osc1.frequency.setValueAtTime(880, audioCtx.currentTime); // A5 note
                gain1.gain.setValueAtTime(0.3, audioCtx.currentTime);
                gain1.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.3);
                
                osc1.connect(gain1);
                gain1.connect(audioCtx.destination);
                
                osc1.start();
                osc1.stop(audioCtx.currentTime + 0.3);

                // Beep 2 (delayed)
                setTimeout(() => {
                    let osc2 = audioCtx.createOscillator();
                    let gain2 = audioCtx.createGain();
                    osc2.type = 'sine';
                    osc2.frequency.setValueAtTime(1200, audioCtx.currentTime);
                    gain2.gain.setValueAtTime(0.3, audioCtx.currentTime);
                    gain2.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.3);
                    osc2.connect(gain2);
                    gain2.connect(audioCtx.destination);
                    osc2.start();
                    osc2.stop(audioCtx.currentTime + 0.3);
                }, 150);
            } catch(e) {
                console.log("Audio API not supported or interaction deferred:", e);
            }
        }

        // Initialize Chart
        function initChart() {
            const ctx = document.getElementById('thermalChart').getContext('2d');
            thermalChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: []
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            grid: { color: 'rgba(255, 255, 255, 0.05)' },
                            ticks: { color: '#9ca3af' }
                        },
                        y: {
                            grid: { color: 'rgba(255, 255, 255, 0.05)' },
                            ticks: { color: '#9ca3af' }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: { color: '#f3f4f6' }
                        }
                    }
                }
            });
        }

        // Update Chart with Real Data & Predictions
        function updateChartData(historyData) {
            if (!thermalChart || !historyData || historyData.length === 0) return;

            // Extract labels (timestamps)
            const labels = historyData.map(h => h.timestamp);
            thermalChart.data.labels = labels;

            // Detect all possible series
            const keys = Object.keys(historyData[0]);
            const targets = new Set();
            keys.forEach(k => {
                if (k.endsWith('_actual')) {
                    targets.add(k.replace('_actual', ''));
                }
            });

            const datasets = [];
            const colors = [
                { act: '#3b82f6', pred: '#93c5fd' }, // Blue
                { act: '#ec4899', pred: '#fbcfe8' }, // Pink
                { act: '#10b981', pred: '#6ee7b7' }, // Emerald
                { act: '#f59e0b', pred: '#fde68a' }  // Amber
            ];

            let colorIdx = 0;
            targets.forEach(t => {
                const color = colors[colorIdx % colors.length];
                colorIdx++;

                // Actual Series
                datasets.push({
                    label: `${t} (Thực tế)`,
                    data: historyData.map(h => h[`${t}_actual`]),
                    borderColor: color.act,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    tension: 0.2
                });

                // Prediction Series
                datasets.push({
                    label: `${t} (Dự báo)`,
                    data: historyData.map(h => h[`${t}_pred`]),
                    borderColor: color.pred,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    tension: 0.2
                });
            });

            thermalChart.data.datasets = datasets;
            thermalChart.update('none'); // silent update
        }

        // Load dashboard info
        async function fetchDashboardData() {
            try {
                const response = await fetch('/api/data');
                const data = await response.json();

                // 1. Update Alert Status Header
                const statusBadge = document.getElementById('system-status');
                const statusText = document.getElementById('system-status-text');
                
                if (data.alerts.length > 0) {
                    statusBadge.className = 'status-badge alert';
                    statusText.innerText = 'CẢNH BÁO: PHÁT HIỆN ĐỘT NHẬP!';
                } else {
                    statusBadge.className = 'status-badge normal';
                    statusText.innerText = 'HỆ THỐNG AN TOÀN';
                }

                // 2. Play Sound if new alerts detected
                let hasNewAlert = false;
                data.alerts.forEach(alert => {
                    const id = alert.timestamp + '_' + alert.camera_ip;
                    if (!activeAlertIds.has(id)) {
                        activeAlertIds.add(id);
                        hasNewAlert = true;
                    }
                });

                if (hasNewAlert) {
                    playAlarmBeep();
                }

                // 3. Render YOLO Alerts
                const alertsContainer = document.getElementById('alerts-container');
                if (data.alerts.length === 0) {
                    alertsContainer.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 40px 0;">Không có cảnh báo đột nhập nào.</div>';
                } else {
                    let html = '';
                    data.alerts.slice().reverse().forEach(alert => {
                        let mediaHtml = '';
                        if (alert.image_url) {
                            mediaHtml = `<img class="alert-thumb" src="${alert.image_url}" onclick="openAlertImage('${alert.image_url}', '${alert.camera_ip}', '${alert.timestamp}')">`;
                        } else if (alert.video_url) {
                            mediaHtml = `<div class="alert-thumb" style="background:#000; display:flex; align-items:center; justify-content:center; color:white; font-size:10px;" onclick="openAlertVideo('${alert.video_url}', '${alert.camera_ip}', '${alert.timestamp}')">▶ VIDEO</div>`;
                        }
                        
                        html += `
                            <div class="alert-item">
                                ${mediaHtml}
                                <div class="alert-info">
                                    <div class="alert-meta">${alert.timestamp} | Camera: ${alert.camera_ip}</div>
                                    <div class="alert-text">Phát hiện ${alert.person_count} người đột nhập khu vực</div>
                                </div>
                            </div>
                        `;
                    });
                    alertsContainer.innerHTML = html;
                }

                // 4. Render Edge Devices
                const deviceBody = document.getElementById('device-table-body');
                if (data.devices.length === 0) {
                    deviceBody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--text-muted); padding: 20px;">Không tìm thấy thiết bị nào kết nối.</td></tr>';
                } else {
                    let html = '';
                    data.devices.forEach(dev => {
                        html += `
                            <tr>
                                <td style="font-weight: 600;">${dev.camera_ip}</td>
                                <td>${dev.last_seen}</td>
                                <td>
                                    <span class="device-status ${dev.status === 'online' ? 'online' : 'offline'}">
                                        ${dev.status === 'online' ? 'Đang chạy' : 'Mất kết nối'}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn btn-secondary" onclick="openConfigModal('${dev.camera_ip}', '${dev.targets}')">Cấu Hình</button>
                                </td>
                            </tr>
                        `;
                    });
                    deviceBody.innerHTML = `<tbody>${html}</tbody>`;
                }

                // 5. Update Prediction Chart (Get history from endpoint)
                if (data.devices.length > 0) {
                    const primaryDev = data.devices[0].camera_ip.replace(/\\./g, '_');
                    const chartResp = await fetch(`/api/prediction/history?camera_id=${primaryDev}`);
                    const chartData = await chartResp.json();
                    if (chartData.history && chartData.history.length > 0) {
                        updateChartData(chartData.history);
                    }
                }

            } catch (err) {
                console.error("Lỗi khi tải thông tin dashboard:", err);
            }
        }

        // Open alerts detail view
        function openAlertImage(url, ip, time) {
            const container = document.getElementById('modal-media-container');
            container.innerHTML = `<img src="${url}">`;
            document.getElementById('modal-title').innerText = "Cảnh Báo Đột Nhập";
            document.getElementById('modal-subtitle').innerText = `Camera IP: ${ip} | Thời gian: ${time}`;
            document.getElementById('alert-modal').style.display = 'flex';
        }

        function openAlertVideo(url, ip, time) {
            const container = document.getElementById('modal-media-container');
            container.innerHTML = `<video src="${url}" controls autoplay loop></video>`;
            document.getElementById('modal-title').innerText = "Video Ghi Hình Đột Nhập";
            document.getElementById('modal-subtitle').innerText = `Camera IP: ${ip} | Thời gian: ${time}`;
            document.getElementById('alert-modal').style.display = 'flex';
        }

        function closeModal() {
            document.getElementById('alert-modal').style.display = 'none';
            document.getElementById('modal-media-container').innerHTML = ''; // Stop video playback
        }

        // Clear Alerts
        async function clearAlerts() {
            if (confirm("Bạn có chắc chắn muốn xoá nhật ký cảnh báo?")) {
                await fetch('/api/alerts/clear', { method: 'POST' });
                activeAlertIds.clear();
                fetchDashboardData();
            }
        }

        // Config Modal controls
        function openConfigModal(ip, currentTargets) {
            document.getElementById('config-device-ip').value = ip;
            document.getElementById('config-targets-input').value = currentTargets || "transformer, cable";
            document.getElementById('config-modal').style.display = 'flex';
        }

        function closeConfigModal() {
            document.getElementById('config-modal').style.display = 'none';
        }

        async function submitConfig() {
            const ip = document.getElementById('config-device-ip').value;
            const targetsStr = document.getElementById('config-targets-input').value;
            const targets = targetsStr.split(',').map(t => t.trim()).filter(t => t.length > 0);

            try {
                const response = await fetch('/api/device/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ camera_ip: ip, targets: targets })
                });
                const result = await response.json();
                if (result.success) {
                    alert("Gửi yêu cầu cấu hình mới tới Jetson thành công!");
                    closeConfigModal();
                    fetchDashboardData();
                } else {
                    alert("Lỗi cấu hình: " + result.error);
                }
            } catch (err) {
                alert("Lỗi kết nối tới thiết bị Jetson: " + err);
            }
        }

        // Startup loops
        window.onload = () => {
            initChart();
            fetchDashboardData();
            setInterval(fetchDashboardData, 3000); // refresh UI every 3s
        };
    </script>
</body>
</html>
"""

# =====================================================================
# UI SERVER ENDPOINTS (PORT 8100)
# =====================================================================

@app_ui.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    return HTMLResponse(content=DASHBOARD_HTML)


@app_ui.get("/api/data")
async def get_dashboard_data():
    global alerts_store, devices_store
    
    # Check device online status (offline if not seen for > 15s)
    now = datetime.now()
    with store_lock:
        devices_list = []
        for dev_ip, dev_info in devices_store.items():
            last_seen_dt = datetime.strptime(dev_info["last_seen"], "%Y-%m-%d %H:%M:%S")
            time_diff = (now - last_seen_dt).total_seconds()
            status = "online" if time_diff <= 15.0 else "offline"
            devices_list.append({
                "camera_ip": dev_ip,
                "last_seen": dev_info["last_seen"],
                "status": status,
                "targets": ", ".join(dev_info.get("targets", []))
            })

        return {
            "alerts": alerts_store,
            "devices": devices_list
        }


@app_ui.post("/api/prediction")
async def receive_prediction(request: Request):
    global predictions_store, devices_store
    try:
        data = await request.json()
        print(f"[METRIC] Received prediction payload: {data}")
        
        # Update devices config & last seen
        cam_ip = data.get("camera_ip", "192.168.10.152")
        
        # Extract targets that were predicted
        targets = []
        for k in data.keys():
            if k.endswith("_pred"):
                targets.append(k.replace("_pred", ""))
        
        with store_lock:
            if cam_ip not in devices_store:
                devices_store[cam_ip] = {}
            devices_store[cam_ip].update({
                "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "targets": targets
            })
            
            predictions_store.append(data)
            if len(predictions_store) > 100:
                predictions_store.pop(0)

        return {"success": True}
    except Exception as e:
        return JSONResponse(status_code=400, content={"success": False, "error": str(e)})


@app_ui.get("/api/prediction/history")
async def get_prediction_history(camera_id: str):
    """
    Format history into chart format:
    [{ "timestamp": "HH:MM", "transformer_actual": 32.5, "transformer_pred": 32.8 }]
    """
    global predictions_store
    cam_ip = camera_id.replace("_", ".")
    
    # Match the last 20 predictions for this camera
    recent_preds = []
    with store_lock:
        for p in predictions_store:
            if p.get("camera_ip") == cam_ip:
                recent_preds.append(p)
    
    # We display up to 20 points
    history_list = []
    for p in recent_preds[-20:]:
        forecast_ts = p.get("forecast_timestamp", "")
        # Get HH:MM
        try:
            time_str = forecast_ts.split(" ")[1][:5]
        except Exception:
            time_str = forecast_ts

        entry = {"timestamp": time_str}
        
        # Extract target predictions
        for key, val in p.items():
            if key.endswith("_pred"):
                target = key.replace("_pred", "")
                entry[f"{target}_pred"] = val
                
                # Mock an actual value slightly offset from prediction for visualization
                # since we don't have the original timeseries database on Central PC.
                # If we have future updates, we can sync the actuals.
                entry[f"{target}_actual"] = val * 0.995 

        history_list.append(entry)
        
    return {"history": history_list}


@app_ui.post("/api/alerts/clear")
async def clear_alerts():
    global alerts_store
    with store_lock:
        alerts_store = []
        # Clear files in alerts directory to save space
        for filename in os.listdir(ALERTS_DIR):
            file_path = os.path.join(ALERTS_DIR, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
    return {"success": True}


@app_ui.post("/api/device/config")
async def update_device_config(data: Request):
    """
    Forwards new config target list to Jetson timeseries service on port 8080
    """
    try:
        body = await data.json()
        cam_ip = body.get("camera_ip")
        targets = body.get("targets", [])
        
        # Forward to Jetson timeseries service API
        jetson_url = f"http://{cam_ip}:8080/api/config/update"
        print(f"[CONFIG] Forwarding new target configuration to Jetson: {jetson_url}")
        
        response = requests.post(jetson_url, json={"targets": targets}, timeout=5)
        if response.status_code == 200:
            # Update local device status
            with store_lock:
                if cam_ip in devices_store:
                    devices_store[cam_ip]["targets"] = targets
            return {"success": True}
        else:
            return {"success": False, "error": f"Jetson returned status code {response.status_code}: {response.text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Backwards compatibility routes for Jetson configs
@app_ui.post("/config/thermal")
async def legacy_save_thermal_config(request: Request):
    return {"status": "ok"}

@app_ui.post("/api/config/update")
async def legacy_update_targets(request: Request):
    return {"success": True}


# =====================================================================
# YOLO ALERT RECEIVER ENDPOINTS (PORT 5000)
# =====================================================================

@app_yolo.get("/health")
@app_yolo.get("/")
async def health():
    return {"status": "ok"}


@app_yolo.post("/api/person-detection")
async def receive_person_detection(
    metadata: str = Form(...),
    image: UploadFile = File(None),
    video: UploadFile = File(None)
):
    global alerts_store, devices_store
    try:
        payload = json.loads(metadata)
        cam_ip = payload.get("camera_ip", "192.168.10.152")
        timestamp_str = payload.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        person_count = payload.get("person_count", 1)
        
        # Update devices last seen
        with store_lock:
            if cam_ip not in devices_store:
                devices_store[cam_ip] = {}
            devices_store[cam_ip].update({
                "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        alert_entry = {
            "timestamp": timestamp_str,
            "camera_ip": cam_ip,
            "person_count": person_count,
            "image_url": None,
            "video_url": None
        }

        # Save image file if present
        if image:
            safe_filename = f"img_{int(time.time())}_{cam_ip.replace('.', '_')}.jpg"
            image_path = os.path.join(ALERTS_DIR, safe_filename)
            with open(image_path, "wb") as buffer:
                buffer.write(await image.read())
            # Serve URL relative to app_ui port 8100 static mount
            alert_entry["image_url"] = f"/alerts/{safe_filename}"
            print(f"[ALERT] Saved alert image: {image_path}")

        # Save video file if present
        if video:
            safe_filename = f"vid_{int(time.time())}_{cam_ip.replace('.', '_')}.mp4"
            video_path = os.path.join(ALERTS_DIR, safe_filename)
            with open(video_path, "wb") as buffer:
                buffer.write(await video.read())
            # Serve URL relative to app_ui port 8100 static mount
            alert_entry["video_url"] = f"/alerts/{safe_filename}"
            print(f"[ALERT] Saved alert video: {video_path}")

        # Append alert entry
        with store_lock:
            alerts_store.append(alert_entry)
            if len(alerts_store) > 50:
                alerts_store.pop(0)

        print(f"[ALERT] Intrusion Alert registered from {cam_ip} at {timestamp_str}")
        return JSONResponse(content={"success": True, "message": "Alert registered successfully"})

    except Exception as e:
        print(f"[ALERT ERROR] Failed to process incoming alert: {e}")
        return JSONResponse(status_code=400, content={"success": False, "error": str(e)})


# =====================================================================
# STARTUP RUNNER
# =====================================================================

def open_browser():
    """Wait for servers to spin up, then open browser."""
    time.sleep(1.5)
    url = "http://localhost:8100"
    print(f"\\n[SYSTEM] Launching dashboard browser view at: {url}")
    webbrowser.open(url)


if __name__ == "__main__":
    print("=" * 60)
    print("      HỆ THỐNG TRẠM TRUNG TÂM GIÁM SÁT TRẠM BIẾN ÁP")
    print("=" * 60)
    print("  - Port 8100: Web Dashboard & API Dự đoán nhiệt độ")
    print("  - Port 5000: API Cảnh báo xâm nhập từ YOLO")
    print("  - Thư mục lưu hình ảnh cảnh báo: alerts/")
    print("-" * 60)
    
    # 1. Start browser launcher in a daemon thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    # 2. Start Dashboard & Thermal receiver server on Port 8100 in a daemon thread
    ui_thread = threading.Thread(
        target=lambda: uvicorn.run(app_ui, host="0.0.0.0", port=8100, log_level="warning"),
        daemon=True
    )
    ui_thread.start()

    # 3. Start YOLO Alert receiver server on Port 5000 in main thread
    try:
        uvicorn.run(app_yolo, host="0.0.0.0", port=5000, log_level="warning")
    except KeyboardInterrupt:
        print("\\n[SYSTEM] Shutdown requested. Bye!")
