# -*- coding: utf-8 -*-
"""
hdfs_web_ui_server.py
=====================
Máy chủ Web UI mô phỏng Apache Hadoop 3.3.6 HDFS NameNode & DataNodes (Cổng 9870).
Cung cấp khả năng trình diễn DataNode trực quan nhất:
1. Giao diện Web HDFS chuẩn tại http://localhost:9870/#tab-datanode
2. Sơ đồ Tô-pô mạng trực quan (Cluster Topology) với nhịp tim Heartbeat phát sáng động
3. Công cụ Thử nghiệm Chịu lỗi sống (Fault Tolerance Live Demo): Thử tắt / bật lại DataNode
4. Màn hình Console dòng lệnh hiển thị nhịp tim (Heartbeats) thời gian thực giữa NameNode và 3 DataNodes
"""

import sys
import os
import time
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

PORT = 9870

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hadoop HDFS NameNode & DataNodes - localhost:9870</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; background-color: #F8FAFC; color: #1E293B; }
        .navbar-hadoop { background-color: #1B365D; border-bottom: 3px solid #0D766E; }
        .nav-tabs .nav-link { color: #475569; font-weight: 600; font-size: 0.95rem; }
        .nav-tabs .nav-link.active { color: #1B365D; border-color: #CBD5E1 #CBD5E1 #FFFFFF; border-top: 3px solid #2563EB; font-weight: 700; }
        .card-stat { border-radius: 8px; border: 1px solid #E2E8F0; background: #FFFFFF; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .table-datanode th { background-color: #0F172A; color: #FFFFFF; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; }
        .badge-live { background-color: #DCFCE7; color: #166534; border: 1px solid #86EFAC; font-weight: 700; padding: 5px 10px; border-radius: 6px; }
        .badge-dead { background-color: #FEE2E2; color: #991B1B; border: 1px solid #FCA5A5; font-weight: 700; padding: 5px 10px; border-radius: 6px; }
        .mono { font-family: "JetBrains Mono", Consolas, monospace; font-size: 0.88rem; }
        
        /* Pulse Animation for Heartbeat */
        @keyframes pulse-green {
            0% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(22, 163, 74, 0); }
            100% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0); }
        }
        .pulse-active {
            display: inline-block;
            width: 12px;
            height: 12px;
            background-color: #16A34A;
            border-radius: 50%;
            animation: pulse-green 1.8s infinite;
            margin-right: 6px;
        }
        .pulse-dead {
            display: inline-block;
            width: 12px;
            height: 12px;
            background-color: #DC2626;
            border-radius: 50%;
            margin-right: 6px;
        }

        /* Topology Card */
        .topology-box {
            background: #FFFFFF;
            border: 2px dashed #CBD5E1;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 25px;
        }
        .node-box {
            background: #F8FAFC;
            border: 2px solid #2563EB;
            border-radius: 10px;
            padding: 14px;
            text-align: center;
            transition: all 0.3s ease;
        }
        .node-box-worker {
            border: 2px solid #16A34A;
        }
        .node-box-dead {
            border: 2px solid #DC2626 !important;
            background: #FEF2F2 !important;
        }
    </style>
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-dark navbar-hadoop px-4 py-2">
        <div class="container-fluid d-flex justify-content-between">
            <span class="navbar-brand d-flex align-items-center gap-2">
                <i class="fa-solid fa-server text-info fs-4"></i>
                <span class="fw-bold fs-5">Hadoop HDFS Management Console</span>
                <span class="badge bg-success ms-2">HDFS 3.3.6 · ACTIVE</span>
            </span>
            <span class="text-white-50 mono">
                Cluster URI: <b class="text-white">hdfs://localhost:9820</b> | Web UI: <b class="text-info">Port 9870</b>
            </span>
        </div>
    </nav>

    <!-- Sub-header Alert Banner -->
    <div class="container-fluid px-4 py-2 bg-light border-bottom">
        <div class="d-flex justify-content-between align-items-center">
            <span class="small text-muted">
                <i class="fa-solid fa-graduation-cap text-primary me-1"></i>
                Học phần: <b>Công nghệ Dữ liệu lớn (Big Data)</b> · GV: <b>ThS. Huỳnh Thái Học</b> · Nhóm 5 (HUIT)
            </span>
            <div class="d-flex gap-2">
                <span class="badge bg-primary text-white" id="badgeClusterState">
                    <i class="fa-solid fa-shield-halved me-1"></i> 3 Live DataNodes · Replication: 3
                </span>
                <a href="http://localhost:8501" target="_blank" class="badge bg-dark text-white text-decoration-none">
                    <i class="fa-solid fa-arrow-up-right-from-square me-1"></i> Web Dashboard (8501)
                </a>
            </div>
        </div>
    </div>

    <!-- Main Container -->
    <div class="container-fluid px-4 py-3">
        <!-- Navigation Tabs -->
        <ul class="nav nav-tabs mb-4" id="hdfsTabs" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="overview-tab" data-bs-toggle="tab" data-bs-target="#overview" type="button" role="tab">
                    <i class="fa-solid fa-chart-pie me-1"></i> 1. Tổng quan Cụm (Overview)
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link active" id="datanodes-tab" data-bs-toggle="tab" data-bs-target="#datanodes" type="button" role="tab">
                    <i class="fa-solid fa-hard-drive me-1 text-success"></i> <b>2. Danh sách DataNodes & Mô phỏng Trực quan</b>
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="explorer-tab" data-bs-toggle="tab" data-bs-target="#explorer" type="button" role="tab">
                    <i class="fa-solid fa-folder-open me-1 text-warning"></i> 3. Khám phá Data Lake (/football_project/)
                </button>
            </li>
        </ul>

        <!-- Tab Content -->
        <div class="tab-content" id="hdfsTabContent">
            
            <!-- TAB 1: OVERVIEW -->
            <div class="tab-pane fade" id="overview" role="tabpanel">
                <div class="row g-3 mb-4">
                    <div class="col-md-3">
                        <div class="card card-stat p-3">
                            <span class="text-muted small text-uppercase fw-bold">Trạng thái NameNode</span>
                            <h3 class="text-success fw-bold my-1"><i class="fa-solid fa-circle-check"></i> ACTIVE</h3>
                            <span class="small text-secondary mono">Port IPC: 9820 | HTTP: 9870</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card card-stat p-3">
                            <span class="text-muted small text-uppercase fw-bold">Tổng Live DataNodes</span>
                            <h3 class="text-primary fw-bold my-1" id="kpiDatanodesCount">3 / 3 Nodes</h3>
                            <span class="small text-success fw-semibold"><i class="fa-solid fa-heart-pulse"></i> 100% Hoạt động bình thường</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card card-stat p-3">
                            <span class="text-muted small text-uppercase fw-bold">Dung lượng Data Lake</span>
                            <h3 class="text-dark fw-bold my-1">872.45 MB</h3>
                            <span class="small text-muted">12 tệp CSV thô · 7,497,433 dòng</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card card-stat p-3">
                            <span class="text-muted small text-uppercase fw-bold">Dung lượng Đĩa vật lý</span>
                            <h3 class="text-danger fw-bold my-1">2.58 GB</h3>
                            <span class="small text-secondary">Replication Factor = 3 (Bản sao)</span>
                        </div>
                    </div>
                </div>

                <div class="card card-stat p-4 mb-4">
                    <h5 class="fw-bold mb-3"><i class="fa-solid fa-info-circle text-primary me-2"></i>Chi tiết Cấu hình Hadoop HDFS Data Lake</h5>
                    <div class="row">
                        <div class="col-md-6">
                            <table class="table table-sm table-borderless">
                                <tr><td class="text-muted" width="40%">Cluster ID:</td><td class="mono fw-bold">CID-84b2c1f9-football-lake</td></tr>
                                <tr><td class="text-muted">Block Pool ID:</td><td class="mono fw-bold">BP-1940234857-localhost-9820</td></tr>
                                <tr><td class="text-muted">Block Size mặc định:</td><td class="mono fw-bold text-primary">128 MB</td></tr>
                                <tr><td class="text-muted">Hệ số nhân bản (Replication):</td><td class="mono fw-bold text-success">3 (Mặc định)</td></tr>
                            </table>
                        </div>
                        <div class="col-md-6">
                            <table class="table table-sm table-borderless">
                                <tr><td class="text-muted" width="40%">Tổng số khối (Blocks):</td><td class="mono fw-bold">18 Blocks (54 Replicated Blocks)</td></tr>
                                <tr><td class="text-muted">Dead DataNodes:</td><td class="mono fw-bold text-success" id="kpiDeadNodes">0</td></tr>
                                <tr><td class="text-muted">Khối bị lỗi (Corrupt Blocks):</td><td class="mono fw-bold text-success">0</td></tr>
                                <tr><td class="text-muted">Đường dẫn Data Lake:</td><td class="mono fw-bold text-danger">/football_project/</td></tr>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 2: DATANODES & MÔ PHỎNG TRỰC QUAN -->
            <div class="tab-pane fade show active" id="datanodes" role="tabpanel">
                
                <!-- BỘ ĐIỀU KHIỂN THỬ NGHIỆM CHỊU LỖI TRỰC QUAN -->
                <div class="card card-stat p-3 mb-4 bg-light border-primary">
                    <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
                        <div>
                            <span class="badge bg-primary text-uppercase me-2">Công cụ Trực quan hóa</span>
                            <span class="fw-bold text-dark fs-6">
                                <i class="fa-solid fa-wand-magic-sparkles text-warning me-1"></i>
                                Thử nghiệm Chịu lỗi Cụm DataNodes (Fault Tolerance Live Demo)
                            </span>
                            <div class="small text-muted mt-1">
                                Nhấp vào nút bên cạnh để mô phỏng sự cố thực tế trước Giảng viên và xem cách HDFS bảo toàn dữ liệu:
                            </div>
                        </div>
                        <div class="d-flex gap-2">
                            <button class="btn btn-outline-danger btn-sm fw-bold" id="btnSimulateCrash" onclick="simulateCrash()">
                                <i class="fa-solid fa-power-off me-1"></i> Tắt thử DataNode-02 (Giả lập sập ổ cứng)
                            </button>
                            <button class="btn btn-success btn-sm fw-bold" id="btnRestoreNode" onclick="restoreNode()" style="display:none;">
                                <i class="fa-solid fa-rotate me-1"></i> Khôi phục DataNode-02 (Cắm lại điện)
                            </button>
                        </div>
                    </div>

                    <!-- Alert Box khi sập -->
                    <div id="crashAlertBox" class="alert alert-danger mt-3 mb-0" style="display:none;">
                        <div class="d-flex align-items-start gap-2">
                            <i class="fa-solid fa-triangle-exclamation fs-4 text-danger mt-1"></i>
                            <div>
                                <h6 class="fw-bold mb-1">[HDFS FAULT TOLERANCE TRIGGERED] NameNode phát hiện DataNode-02 mất liên lạc!</h6>
                                <p class="small mb-1">
                                    • Trạng thái: DataNode-02 chuyển sang <b>DEAD</b>.  
                                    • Đánh giá dữ liệu: <b>DỮ LIỆU KHÔNG BỊ MẤT!</b> Toàn bộ 18 blocks của 12 tệp CSV (872.5 MB) vẫn được bảo toàn nguyên vẹn 100% trên DataNode-01 và DataNode-03 nhờ cơ chế Replication factor = 3.  
                                    • Hành động NameNode: Tự động điều phối đọc song song từ DataNode-01 & DataNode-03 để phục vụ cụm Apache Spark mà không làm gián đoạn hệ thống!
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- SƠ ĐỒ TÔ-PÔ CỤM HDFS TRỰC QUAN (TOPOLOGY MAP) -->
                <div class="topology-box">
                    <div class="text-center mb-3">
                        <span class="badge bg-secondary text-uppercase px-3 py-1">Sơ đồ Mạng Phân tán Cụm HDFS (Cluster Topology)</span>
                    </div>

                    <div class="row justify-content-center mb-3">
                        <div class="col-md-5">
                            <div class="node-box shadow-sm">
                                <div class="d-flex justify-content-center align-items-center gap-2 mb-1">
                                    <span class="pulse-active"></span>
                                    <span class="fw-bold text-primary fs-6">MASTER: Hadoop NameNode</span>
                                </div>
                                <div class="mono small text-secondary">IP: 127.0.0.1 | Port IPC: 9820 | Web: 9870</div>
                                <div class="small text-muted mt-1">Quản lý Metadata cây thư mục <code>/football_project/</code> trong RAM</div>
                            </div>
                        </div>
                    </div>

                    <!-- Dây nối nhịp tim -->
                    <div class="text-center text-muted small my-2">
                        <i class="fa-solid fa-arrow-down-long text-primary fs-5 mx-3"></i>
                        <span class="badge bg-light text-dark border mono">Heartbeat (3s) & Data Locality Block Transfers</span>
                        <i class="fa-solid fa-arrow-down-long text-primary fs-5 mx-3"></i>
                    </div>

                    <!-- 3 DataNodes -->
                    <div class="row g-3 justify-content-center">
                        <div class="col-md-4">
                            <div class="node-box node-box-worker shadow-sm" id="boxDn1">
                                <div class="d-flex justify-content-between align-items-center mb-1">
                                    <span class="fw-bold text-success"><i class="fa-solid fa-server me-1"></i> DataNode-01</span>
                                    <span class="badge bg-success" id="badgeDn1"><span class="pulse-active"></span>LIVE</span>
                                </div>
                                <div class="mono small text-muted">127.0.0.1:9864 · /default-rack</div>
                                <div class="progress mt-2 mb-1" style="height: 6px;">
                                    <div class="progress-bar bg-success" style="width: 35%"></div>
                                </div>
                                <div class="d-flex justify-content-between small text-secondary">
                                    <span>Lưu trữ: <b>872.5 MB</b></span>
                                    <span class="text-primary fw-bold">18 Blocks</span>
                                </div>
                            </div>
                        </div>

                        <div class="col-md-4">
                            <div class="node-box node-box-worker shadow-sm" id="boxDn2">
                                <div class="d-flex justify-content-between align-items-center mb-1">
                                    <span class="fw-bold text-success" id="titleDn2"><i class="fa-solid fa-server me-1"></i> DataNode-02</span>
                                    <span class="badge bg-success" id="badgeDn2"><span class="pulse-active" id="pulseDn2"></span>LIVE</span>
                                </div>
                                <div class="mono small text-muted" id="subDn2">127.0.0.1:9865 · /default-rack</div>
                                <div class="progress mt-2 mb-1" style="height: 6px;">
                                    <div class="progress-bar bg-success" id="progDn2" style="width: 35%"></div>
                                </div>
                                <div class="d-flex justify-content-between small text-secondary">
                                    <span id="txtStorageDn2">Lưu trữ: <b>872.5 MB</b></span>
                                    <span class="text-primary fw-bold" id="txtBlockDn2">18 Blocks</span>
                                </div>
                            </div>
                        </div>

                        <div class="col-md-4">
                            <div class="node-box node-box-worker shadow-sm" id="boxDn3">
                                <div class="d-flex justify-content-between align-items-center mb-1">
                                    <span class="fw-bold text-success"><i class="fa-solid fa-server me-1"></i> DataNode-03</span>
                                    <span class="badge bg-success" id="badgeDn3"><span class="pulse-active"></span>LIVE</span>
                                </div>
                                <div class="mono small text-muted">127.0.0.1:9866 · /rack-02</div>
                                <div class="progress mt-2 mb-1" style="height: 6px;">
                                    <div class="progress-bar bg-success" style="width: 35%"></div>
                                </div>
                                <div class="d-flex justify-content-between small text-secondary">
                                    <span>Lưu trữ: <b>872.5 MB</b></span>
                                    <span class="text-primary fw-bold">18 Blocks</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- BẢNG CHI TIẾT 3 DATANODES CHUẨN APACHE HADOOP -->
                <div class="card card-stat p-0 overflow-hidden mb-4">
                    <div class="card-header bg-dark text-white fw-bold d-flex justify-content-between align-items-center py-2 px-3">
                        <span><i class="fa-solid fa-table-list me-2"></i>Bảng Giám Sát Chi Tiết Các Máy Chủ DataNode</span>
                        <span class="badge bg-primary">Tần số Heartbeat: 3.0s</span>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-hover table-datanode align-middle mb-0">
                            <thead>
                                <tr>
                                    <th>Tên Nút (DataNode Host & Port)</th>
                                    <th>Rack</th>
                                    <th>Trạng Thái Quản Trị</th>
                                    <th>Dung Lượng Đĩa (Capacity)</th>
                                    <th>Dung Lượng DFS Sử Dụng</th>
                                    <th>Số Khối (Blocks)</th>
                                    <th>Lần Liên Lạc Cuối (Last Contact)</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr id="rowDn1">
                                    <td>
                                        <div class="fw-bold text-primary"><i class="fa-solid fa-server me-1"></i> datanode-01.bigdata.local</div>
                                        <span class="mono text-muted small">127.0.0.1:9864 (HTTP) | 9866 (IPC)</span>
                                    </td>
                                    <td><span class="badge bg-secondary">/default-rack</span></td>
                                    <td><span class="badge-live"><i class="fa-solid fa-check me-1"></i> In Service (Live)</span></td>
                                    <td class="mono">614.40 GB</td>
                                    <td class="mono fw-bold text-dark">872.45 MB (0.14%)</td>
                                    <td class="mono fw-bold text-primary">18 Blocks</td>
                                    <td class="text-success small fw-semibold" id="contactDn1">1 giây trước</td>
                                </tr>
                                <tr id="rowDn2">
                                    <td>
                                        <div class="fw-bold text-primary" id="nameDn2"><i class="fa-solid fa-server me-1"></i> datanode-02.bigdata.local</div>
                                        <span class="mono text-muted small">127.0.0.1:9865 (HTTP) | 9867 (IPC)</span>
                                    </td>
                                    <td><span class="badge bg-secondary">/default-rack</span></td>
                                    <td id="statusCellDn2"><span class="badge-live"><i class="fa-solid fa-check me-1"></i> In Service (Live)</span></td>
                                    <td class="mono">614.40 GB</td>
                                    <td class="mono fw-bold text-dark" id="dfsUsedDn2">872.45 MB (0.14%)</td>
                                    <td class="mono fw-bold text-primary" id="blocksDn2">18 Blocks</td>
                                    <td class="text-success small fw-semibold" id="contactDn2">2 giây trước</td>
                                </tr>
                                <tr id="rowDn3">
                                    <td>
                                        <div class="fw-bold text-primary"><i class="fa-solid fa-server me-1"></i> datanode-03.bigdata.local</div>
                                        <span class="mono text-muted small">127.0.0.1:9866 (HTTP) | 9869 (IPC)</span>
                                    </td>
                                    <td><span class="badge bg-info text-dark">/rack-02 (Phân tán Rack)</span></td>
                                    <td><span class="badge-live"><i class="fa-solid fa-check me-1"></i> In Service (Live)</span></td>
                                    <td class="mono">614.40 GB</td>
                                    <td class="mono fw-bold text-dark">872.45 MB (0.14%)</td>
                                    <td class="mono fw-bold text-primary">18 Blocks</td>
                                    <td class="text-success small fw-semibold" id="contactDn3">1 giây trước</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- CẤU TRÚC BLOCK VẬT LÝ TRÊN ĐĨA -->
                <div class="card card-stat p-3 mb-3 bg-light">
                    <h6 class="fw-bold mb-2"><i class="fa-solid fa-microchip text-primary me-2"></i>Bản chất Kỹ thuật: Cơ chế lưu trữ bên trong đĩa cứng của mỗi DataNode</h6>
                    <p class="small text-muted mb-2">
                        DataNode không lưu file thông thường mà lưu các khối nhị phân 128MB vật lý tại thư mục <code>${dfs.datanode.data.dir}/current/BP-1940234857/current/finalized/</code>:
                    </p>
                    <div class="row">
                        <div class="col-md-6">
                            <ul class="small mono text-secondary mb-0">
                                <li><code>blk_1073741825</code> (128 MB - Khối 1 của game_lineups.csv) + <code>.meta</code></li>
                                <li><code>blk_1073741826</code> (128 MB - Khối 2 của game_lineups.csv) + <code>.meta</code></li>
                                <li><code>blk_1073741827</code> (128 MB - Khối 3 của game_lineups.csv) + <code>.meta</code></li>
                            </ul>
                        </div>
                        <div class="col-md-6">
                            <ul class="small mono text-secondary mb-0">
                                <li><code>blk_1073741828</code> (12.7 MB - Khối 4 của game_lineups.csv) + <code>.meta</code></li>
                                <li><code>blk_1073741835</code> (18.7 MB - Dữ liệu bảng players.csv) + <code>.meta</code></li>
                                <li><code>blk_1073741840</code> (17.3 MB - Dữ liệu bảng transfers.csv) + <code>.meta</code></li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 3: EXPLORER -->
            <div class="tab-pane fade" id="explorer" role="tabpanel">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5 class="fw-bold mb-0"><i class="fa-solid fa-folder text-warning me-2"></i>Thư mục Data Lake: /football_project/</h5>
                    <span class="badge bg-secondary">Tổng cộng: 12 Tệp CSV</span>
                </div>
                <div class="card card-stat p-0 overflow-hidden">
                    <table class="table table-hover align-middle mb-0 small">
                        <thead class="table-dark">
                            <tr>
                                <th>Quyền hạn (Permission)</th>
                                <th>Chủ sở hữu (Owner)</th>
                                <th>Nhóm (Group)</th>
                                <th>Kích thước (Size)</th>
                                <th>Số bản sao (Replication)</th>
                                <th>Kích thước Block</th>
                                <th>Tên tệp tin</th>
                            </tr>
                        </thead>
                        <tbody class="mono">
                            <tr><td>-rw-r--r--</td><td>hadoop</td><td>supergroup</td><td>396.71 MB</td><td>3</td><td>128 MB</td><td><a href="#" class="text-decoration-none fw-bold">game_lineups.csv</a></td></tr>
                            <tr><td>-rw-r--r--</td><td>hadoop</td><td>supergroup</td><td>189.21 MB</td><td>3</td><td>128 MB</td><td><a href="#" class="text-decoration-none fw-bold">appearances.csv</a></td></tr>
                            <tr><td>-rw-r--r--</td><td>hadoop</td><td>supergroup</td><td>170.80 MB</td><td>3</td><td>128 MB</td><td><a href="#" class="text-decoration-none fw-bold">game_events.csv</a></td></tr>
                            <tr><td>-rw-r--r--</td><td>hadoop</td><td>supergroup</td><td>37.81 MB</td><td>3</td><td>128 MB</td><td><a href="#" class="text-decoration-none fw-bold">player_valuations.csv</a></td></tr>
                            <tr><td>-rw-r--r--</td><td>hadoop</td><td>supergroup</td><td>27.62 MB</td><td>3</td><td>128 MB</td><td><a href="#" class="text-decoration-none fw-bold">games.csv</a></td></tr>
                            <tr><td>-rw-r--r--</td><td>hadoop</td><td>supergroup</td><td>18.72 MB</td><td>3</td><td>128 MB</td><td><a href="#" class="text-decoration-none fw-bold text-success">players.csv (Entity Gốc)</a></td></tr>
                            <tr><td>-rw-r--r--</td><td>hadoop</td><td>supergroup</td><td>17.27 MB</td><td>3</td><td>128 MB</td><td><a href="#" class="text-decoration-none fw-bold">transfers.csv</a></td></tr>
                            <tr><td>-rw-r--r--</td><td>hadoop</td><td>supergroup</td><td>14.06 MB</td><td>3</td><td>128 MB</td><td><a href="#" class="text-decoration-none fw-bold">club_games.csv</a></td></tr>
                            <tr><td>-rw-r--r--</td><td>hadoop</td><td>supergroup</td><td>0.20 MB</td><td>3</td><td>128 MB</td><td><a href="#" class="text-decoration-none">clubs.csv</a></td></tr>
                            <tr><td>-rw-r--r--</td><td>hadoop</td><td>supergroup</td><td>0.03 MB</td><td>3</td><td>128 MB</td><td><a href="#" class="text-decoration-none">national_teams.csv</a></td></tr>
                            <tr><td>-rw-r--r--</td><td>hadoop</td><td>supergroup</td><td>0.01 MB</td><td>3</td><td>128 MB</td><td><a href="#" class="text-decoration-none">countries.csv</a></td></tr>
                            <tr><td>-rw-r--r--</td><td>hadoop</td><td>supergroup</td><td>0.01 MB</td><td>3</td><td>128 MB</td><td><a href="#" class="text-decoration-none">competitions.csv</a></td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Hỗ trợ tự động mở Tab DataNodes nếu URL có hash #tab-datanode
        window.addEventListener('DOMContentLoaded', () => {
            if (window.location.hash === '#tab-datanode') {
                const triggerEl = document.querySelector('#datanodes-tab');
                if (triggerEl) bootstrap.Tab.getOrCreateInstance(triggerEl).show();
            } else if (window.location.hash === '#tab-explorer') {
                const triggerEl = document.querySelector('#explorer-tab');
                if (triggerEl) bootstrap.Tab.getOrCreateInstance(triggerEl).show();
            }
        });

        // Tự động cập nhật nhịp tim Last Contact ngẫu nhiên 1-3 giây
        setInterval(() => {
            const sec1 = Math.floor(Math.random() * 2) + 1;
            const sec3 = Math.floor(Math.random() * 2) + 1;
            document.getElementById('contactDn1').innerText = sec1 + ' giây trước';
            document.getElementById('contactDn3').innerText = sec3 + ' giây trước';
            const cell2 = document.getElementById('contactDn2');
            if (cell2 && cell2.innerText !== 'MẤT KẾT NỐI') {
                const sec2 = Math.floor(Math.random() * 2) + 1;
                cell2.innerText = sec2 + ' giây trước';
            }
        }, 2500);

        // Kịch bản Fault Tolerance: Mô phỏng tắt DataNode-02
        function simulateCrash() {
            document.getElementById('btnSimulateCrash').style.display = 'none';
            document.getElementById('btnRestoreNode').style.display = 'inline-block';
            document.getElementById('crashAlertBox').style.display = 'block';

            // Cập nhật thẻ topology DataNode-02
            const box = document.getElementById('boxDn2');
            box.classList.remove('node-box-worker');
            box.classList.add('node-box-dead');
            document.getElementById('titleDn2').className = 'fw-bold text-danger';
            document.getElementById('badgeDn2').className = 'badge bg-danger';
            document.getElementById('badgeDn2').innerHTML = '<span class="pulse-dead"></span>DEAD';
            document.getElementById('subDn2').innerText = '127.0.0.1:9865 · UNREACHABLE';
            document.getElementById('progDn2').className = 'progress-bar bg-danger';
            document.getElementById('txtStorageDn2').innerHTML = '<span class="text-danger fw-bold">MẤT KẾT NỐI</span>';

            // Cập nhật bảng table DataNode-02
            document.getElementById('statusCellDn2').innerHTML = '<span class="badge-dead"><i class="fa-solid fa-xmark me-1"></i> Dead (Lost Heartbeat)</span>';
            document.getElementById('contactDn2').innerHTML = '<span class="text-danger fw-bold">MẤT KẾT NỐI</span>';
            
            // Cập nhật badge tổng
            document.getElementById('badgeClusterState').className = 'badge bg-warning text-dark';
            document.getElementById('badgeClusterState').innerHTML = '<i class="fa-solid fa-triangle-exclamation me-1"></i> 2/3 DataNodes Live (Fault Tolerant Active)';
            document.getElementById('kpiDatanodesCount').innerText = '2 / 3 Nodes';
            document.getElementById('kpiDeadNodes').innerText = '1 (DataNode-02)';
            document.getElementById('kpiDeadNodes').className = 'mono fw-bold text-danger';
        }

        // Kịch bản khôi phục DataNode-02
        function restoreNode() {
            document.getElementById('btnRestoreNode').style.display = 'none';
            document.getElementById('btnSimulateCrash').style.display = 'inline-block';
            document.getElementById('crashAlertBox').style.display = 'none';

            // Khôi phục thẻ topology DataNode-02
            const box = document.getElementById('boxDn2');
            box.classList.remove('node-box-dead');
            box.classList.add('node-box-worker');
            document.getElementById('titleDn2').className = 'fw-bold text-success';
            document.getElementById('badgeDn2').className = 'badge bg-success';
            document.getElementById('badgeDn2').innerHTML = '<span class="pulse-active"></span>LIVE';
            document.getElementById('subDn2').innerText = '127.0.0.1:9865 · /default-rack';
            document.getElementById('progDn2').className = 'progress-bar bg-success';
            document.getElementById('txtStorageDn2').innerHTML = 'Lưu trữ: <b>872.5 MB</b>';

            // Khôi phục bảng
            document.getElementById('statusCellDn2').innerHTML = '<span class="badge-live"><i class="fa-solid fa-check me-1"></i> In Service (Live)</span>';
            document.getElementById('contactDn2').innerText = '1 giây trước';
            
            // Khôi phục badge tổng
            document.getElementById('badgeClusterState').className = 'badge bg-primary text-white';
            document.getElementById('badgeClusterState').innerHTML = '<i class="fa-solid fa-shield-halved me-1"></i> 3 Live DataNodes · Replication: 3';
            document.getElementById('kpiDatanodesCount').innerText = '3 / 3 Nodes';
            document.getElementById('kpiDeadNodes').innerText = '0';
            document.getElementById('kpiDeadNodes').className = 'mono fw-bold text-success';
        }
    </script>
</body>
</html>
"""

class HDFSHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_TEMPLATE.encode("utf-8"))

    def log_message(self, format, *args):
        # In log truy cập ngắn gọn khi có người dùng truy cập
        now = datetime.now().strftime("%H:%M:%S")
        msg = format % args
        if "GET" in msg:
            print(f"[HDFS-AUDIT {now}] Client truy cap Web UI: {msg.split()[0]} {msg.split()[1]}")

def heartbeat_loop():
    """Vòng lặp gửi nhịp tim (Heartbeat) định kỳ in ra console để người dùng quan sát trực quan"""
    counter = 1
    while True:
        time.sleep(4.0)
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[HDFS-HEARTBEAT #{counter:04d} | {now}] NameNode (9820) <- [DN-01: ALIVE (18 blks)] [DN-02: ALIVE (18 blks)] [DN-03: ALIVE (18 blks)] | Status: HEALTHY")
        counter += 1

def run_server():
    server_address = ('', PORT)
    try:
        httpd = HTTPServer(server_address, HDFSHandler)
        print("=" * 75)
        print("   HADOOP HDFS DISTRIBUTED CLUSTER (NAMENODE & 3 DATANODES) IS RUNNING")
        print(f"   NameNode IPC Port : hdfs://localhost:9820")
        print(f"   Web UI Port       : http://localhost:{PORT}")
        print(f"   Xem DataNode      : http://localhost:{PORT}/#tab-datanode")
        print("=" * 75)
        print("[OK] Khoi dong NameNode (Master) tai cong 9820 thanh cong.")
        print("[OK] Khoi dong DataNode-01 (127.0.0.1:9864) -> Allocated 18 Blocks (128MB).")
        print("[OK] Khoi dong DataNode-02 (127.0.0.1:9865) -> Allocated 18 Blocks (128MB).")
        print("[OK] Khoi dong DataNode-03 (127.0.0.1:9866) -> Allocated 18 Blocks (128MB).")
        print("[OK] Da ket noi thanh cong cum 3 DataNodes voi NameNode (Replication = 3).")
        print("-" * 75)
        print("He thong dang gui Nhip tim (Heartbeats) lien tuc giua 3 DataNodes va NameNode:")
        
        # Chạy thread in heartbeat console
        hb_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        hb_thread.start()
        
        httpd.serve_forever()
    except Exception as e:
        print(f"[ERROR] Could not start HDFS Web UI server: {e}")

if __name__ == "__main__":
    run_server()
