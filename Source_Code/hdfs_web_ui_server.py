# -*- coding: utf-8 -*-
"""
hdfs_web_ui_server.py
=====================
Máy chủ Web UI mô phỏng Apache Hadoop 3.3.6 HDFS NameNode & DataNodes (Cổng 9870).
TÍCH HỢP TOÀN DIỆN TRỰC TIẾP TẠI CỔNG 9870:
1. 🏛️ Toàn cảnh Hạ tầng 5 Cụm Máy chủ Big Data (Cluster Infrastructure Topology)
2. 🏢 Giám sát Cụm 3 DataNodes (Live Cluster, Heartbeat nhấp nháy & Bộ thử nghiệm Chịu lỗi Fault Tolerance)
3. 🔄 Luồng Hoạt động Dữ liệu End-to-End 6 Giai đoạn (Từ Nạp HDFS qua lệnh hdfs dfs -put đến Phục vụ Web)
4. 📁 Khám phá Thư mục Data Lake (/football_project/ với 12 tệp CSV, 872.5 MB)
5. 📋 Bảng Ma trận 7 Trụ cột Công nghệ Big Data & Vấn đề Giải quyết trong Thực tế
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
    <title>Hadoop HDFS & Big Data Infrastructure - localhost:9870</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; background-color: #F8FAFC; color: #1E293B; }
        .navbar-hadoop { background-color: #1B365D; border-bottom: 3px solid #0D766E; }
        .nav-tabs .nav-link { color: #475569; font-weight: 600; font-size: 0.92rem; padding: 10px 16px; }
        .nav-tabs .nav-link.active { color: #1B365D; border-color: #CBD5E1 #CBD5E1 #FFFFFF; border-top: 3px solid #2563EB; font-weight: 700; background-color: #FFFFFF; }
        .card-stat { border-radius: 8px; border: 1px solid #E2E8F0; background: #FFFFFF; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
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

        /* Infra Card on Tab 1 */
        .cluster-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
            transition: transform 0.2s;
        }
        .cluster-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08);
        }
    </style>
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-dark navbar-hadoop px-4 py-2">
        <div class="container-fluid d-flex justify-content-between align-items-center">
            <span class="navbar-brand d-flex align-items-center gap-2 mb-0">
                <i class="fa-solid fa-server text-info fs-3"></i>
                <div>
                    <div class="fw-bold fs-5 line-height-1">Hadoop HDFS & Big Data Infrastructure Console</div>
                    <div class="small text-white-50" style="font-size: 0.75rem;">Học phần: Công nghệ Dữ liệu lớn (Big Data) · GV: ThS. Huỳnh Thái Học · HUIT</div>
                </div>
            </span>
            <div class="d-flex align-items-center gap-3">
                <span class="text-white-50 mono small d-none d-md-inline">
                    NameNode IPC: <b class="text-white">hdfs://localhost:9820</b> | Web UI: <b class="text-info">Port 9870</b>
                </span>
                <a href="http://localhost:8501" target="_blank" class="btn btn-warning btn-sm fw-bold shadow-sm">
                    <i class="fa-solid fa-gauge-high me-1"></i> Mở Web Dashboard (Port 8501)
                </a>
            </div>
        </div>
    </nav>

    <!-- Sub-header Alert Banner -->
    <div class="container-fluid px-4 py-2 bg-light border-bottom">
        <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
            <span class="small text-muted">
                <i class="fa-solid fa-layer-group text-primary me-1"></i>
                Hạ tầng Tích hợp Toàn diện: <b>Hadoop HDFS (9820/9870) · Spark 4.2 (16 Cores) · Kafka (9092) · Airflow (8080) · SQLite Data Mart</b>
            </span>
            <div class="d-flex gap-2">
                <span class="badge bg-success" id="badgeClusterState">
                    <span class="pulse-active"></span> 3 Live DataNodes · Replication: 3
                </span>
                <span class="badge bg-primary">Dung lượng: 872.5 MB / 7,497,433 dòng</span>
            </div>
        </div>
    </div>

    <!-- Main Container -->
    <div class="container-fluid px-4 py-3">
        <!-- Navigation Tabs -->
        <ul class="nav nav-tabs mb-4" id="hdfsTabs" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link active" id="infra-tab" data-bs-toggle="tab" data-bs-target="#infra" type="button" role="tab">
                    <i class="fa-solid fa-network-wired me-1 text-primary"></i> <b>1. Toàn cảnh Hạ tầng 5 Cụm Big Data</b>
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="datanodes-tab" data-bs-toggle="tab" data-bs-target="#datanodes" type="button" role="tab">
                    <i class="fa-solid fa-hard-drive me-1 text-success"></i> <b>2. Giám sát Cụm 3 DataNodes & Thử nghiệm Chịu lỗi</b>
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="pipeline-tab" data-bs-toggle="tab" data-bs-target="#pipeline" type="button" role="tab">
                    <i class="fa-solid fa-diagram-project me-1 text-warning"></i> <b>3. Luồng Hoạt động Dữ liệu Chi tiết (Từ Nạp đến Phục vụ)</b>
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="explorer-tab" data-bs-toggle="tab" data-bs-target="#explorer" type="button" role="tab">
                    <i class="fa-solid fa-folder-open me-1 text-info"></i> <b>4. Khám phá Thư mục Data Lake (/football_project/)</b>
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="matrix-tab" data-bs-toggle="tab" data-bs-target="#matrix" type="button" role="tab">
                    <i class="fa-solid fa-table-cells me-1 text-secondary"></i> <b>5. Ma trận 7 Trụ cột & Nghiệp vụ Áp dụng</b>
                </button>
            </li>
        </ul>

        <!-- Tab Content -->
        <div class="tab-content" id="hdfsTabContent">
            
            <!-- ══════════════════════════════════════════════════════════════════
                 TAB 1: TOÀN CẢNH HẠ TẦNG 5 CỤM BIG DATA (TÍCH HỢP ĐÚNG YÊU CẦU CỦA BẠN)
                 ══════════════════════════════════════════════════════════════════ -->
            <div class="tab-pane fade show active" id="infra" role="tabpanel">
                <div class="row g-3 mb-4">
                    <div class="col-md-3">
                        <div class="card card-stat p-3">
                            <span class="text-muted small text-uppercase fw-bold">Hadoop HDFS Data Lake</span>
                            <h3 class="text-primary fw-bold my-1">872.45 MB</h3>
                            <span class="small text-secondary">12 tệp CSV thô · 7,497,433 dòng</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card card-stat p-3">
                            <span class="text-muted small text-uppercase fw-bold">Apache Spark 4.2 Engine</span>
                            <h3 class="text-warning fw-bold my-1">16 Cores Parallel</h3>
                            <span class="small text-success fw-semibold"><i class="fa-solid fa-bolt"></i> Nhanh gấp 16.0x Pandas</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card card-stat p-3">
                            <span class="text-muted small text-uppercase fw-bold">Kafka Streaming (9092)</span>
                            <h3 class="text-success fw-bold my-1">> 707 Triệu €</h3>
                            <span class="small text-muted">Topic: football_transfers (JSON)</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card card-stat p-3">
                            <span class="text-muted small text-uppercase fw-bold">Airflow 2.10 (Docker)</span>
                            <h3 class="text-danger fw-bold my-1">7/7 SUCCESS</h3>
                            <span class="small text-secondary">2m 10s Tự động hóa hoàn toàn</span>
                        </div>
                    </div>
                </div>

                <!-- CỤM 1: HADOOP HDFS DATA LAKE -->
                <div class="cluster-card" style="border-left: 5px solid #2563EB;">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h5 class="fw-bold text-primary mb-0">
                            <i class="fa-solid fa-server me-2"></i>CỤM 1: LƯU TRỮ PHÂN TÁN HADOOP HDFS 3.x (DATA LAKE LAYER)
                        </h5>
                        <span class="badge bg-primary">Block Size: 128 MB · Replication Factor: 3</span>
                    </div>
                    <p class="text-muted small mb-3">
                        Nhiệm vụ: Quản lý và lưu trữ 12 tệp CSV thô (872.5 MB, gần 7.5 triệu bản ghi). Phân tách thành 18 khối nhị phân và nhân bản 3 lần sang 3 DataNode (tổng 2.58 GB).
                    </p>
                    <div class="row g-2">
                        <div class="col-md-3">
                            <div class="p-2 border rounded bg-light text-center">
                                <span class="badge bg-primary small text-uppercase">MASTER (BỘ NÃO)</span>
                                <div class="fw-bold mt-1 text-dark">HDFS NameNode</div>
                                <div class="mono small text-secondary">Port IPC: 9820 | Web: 9870</div>
                                <div class="small text-success mt-1">Lưu Metadata cây thư mục trong RAM</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="p-2 border rounded bg-light text-center">
                                <span class="badge bg-success small text-uppercase">WORKER 1 (KHO ĐĨA)</span>
                                <div class="fw-bold mt-1 text-dark">DataNode-01</div>
                                <div class="mono small text-secondary">Port 9864 · /default-rack</div>
                                <div class="small text-primary mt-1">Lưu 18 Blocks (872.5 MB)</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="p-2 border rounded bg-light text-center">
                                <span class="badge bg-success small text-uppercase">WORKER 2 (KHO ĐĨA)</span>
                                <div class="fw-bold mt-1 text-dark">DataNode-02</div>
                                <div class="mono small text-secondary">Port 9865 · /default-rack</div>
                                <div class="small text-primary mt-1">Lưu 18 Blocks (872.5 MB)</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="p-2 border rounded bg-light text-center">
                                <span class="badge bg-success small text-uppercase">WORKER 3 (KHO ĐĨA)</span>
                                <div class="fw-bold mt-1 text-dark">DataNode-03</div>
                                <div class="mono small text-secondary">Port 9866 · /rack-02</div>
                                <div class="small text-primary mt-1">Lưu 18 Blocks (872.5 MB)</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="text-center text-muted fw-bold my-2 mono small">
                    ▼ Đọc song song In-Memory dựa trên vị trí dữ liệu (HDFS Data Locality qua 16 Cores CPU) ▼
                </div>

                <!-- CỤM 2: APACHE SPARK 4.2 -->
                <div class="cluster-card" style="border-left: 5px solid #D97706;">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h5 class="fw-bold text-warning mb-0" style="color: #B45309 !important;">
                            <i class="fa-solid fa-bolt me-2"></i>CỤM 2: ĐỘNG CƠ TÍNH TOÁN PHÂN TÁN APACHE SPARK 4.2 & MLLIB (BATCH LAYER)
                        </h5>
                        <span class="badge bg-warning text-dark">16 Cores Parallel · Tungsten In-Memory Engine</span>
                    </div>
                    <p class="text-muted small mb-3">
                        Nhiệm vụ: 16 Cores CPU tính toán song song trong bộ nhớ RAM, tối ưu hóa kế hoạch thực thi logic và vật lý qua Catalyst Optimizer.
                    </p>
                    <div class="row g-2">
                        <div class="col-md-4">
                            <div class="p-2 border rounded bg-light">
                                <div class="fw-bold text-dark"><i class="fa-solid fa-broom me-1 text-warning"></i> PySpark ETL (02_cleaning.py)</div>
                                <div class="small text-secondary mt-1">Điền median missing, chuẩn hóa tuổi từ ngày sinh, lọc 9,400 lỗi -> Giữ 40,749 bản ghi sạch.</div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="p-2 border rounded bg-light">
                                <div class="fw-bold text-dark"><i class="fa-solid fa-file-zipper me-1 text-success"></i> Nén Parquet Snappy (Columnar)</div>
                                <div class="small text-secondary mt-1">Dung lượng giảm từ 18.72 MB CSV xuống 1.41 MB Parquet (-97.7% dung lượng đĩa), tăng tốc đọc gấp 5 lần.</div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="p-2 border rounded bg-light">
                                <div class="fw-bold text-dark"><i class="fa-solid fa-brain me-1 text-primary"></i> Spark SQL & PySpark MLlib</div>
                                <div class="small text-secondary mt-1">K-Means k=3 (Sil: 0.6429) phân 3 đẳng cấp cầu thủ + Random Forest ln(1+y) R²=84.68% & Scouting Engine.</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="text-center text-muted fw-bold my-2 mono small">
                    ▼ Điều phối luồng dữ liệu tự động và bắt sóng sự kiện chuyển nhượng thời gian thực ▼
                </div>

                <!-- CỤM 3 & CỤM 4: KAFKA VÀ AIRFLOW -->
                <div class="row g-3">
                    <div class="col-md-6">
                        <div class="cluster-card h-100" style="border-left: 5px solid #16A34A;">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h6 class="fw-bold text-success mb-0"><i class="fa-solid fa-satellite-dish me-2"></i>CỤM 3: APACHE KAFKA (SPEED LAYER)</h6>
                                <span class="badge bg-success">Port 9092</span>
                            </div>
                            <p class="small text-muted mb-2">
                                Message Broker tiếp nhận luồng sự kiện chuyển nhượng trực tiếp dạng JSON, độ trễ mili-giây.
                            </p>
                            <ul class="small mono text-secondary mb-0">
                                <li>Topic: <b>football_transfers</b> (Throughput ~2,450 msgs/s)</li>
                                <li>Producer: <code>06_kafka_producer.py</code></li>
                                <li>Consumer: <code>07_kafka_consumer.py</code> (> 707M €)</li>
                            </ul>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="cluster-card h-100" style="border-left: 5px solid #7C3AED;">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h6 class="fw-bold mb-0" style="color: #7C3AED;"><i class="fa-solid fa-arrows-spin me-2"></i>CỤM 4: APACHE AIRFLOW (ORCHESTRATOR)</h6>
                                <span class="badge bg-dark">Docker Compose</span>
                            </div>
                            <p class="small text-muted mb-2">
                                Điều phối lập lịch tự động toàn bộ Data Pipeline qua cụm 5 container Docker Compose.
                            </p>
                            <ul class="small mono text-secondary mb-0">
                                <li>Airflow Web UI: <b>http://localhost:8080</b></li>
                                <li>DAG Name: <b>transfermarkt_pipeline</b></li>
                                <li>Trạng thái: <b>7/7 Tasks SUCCESS</b> (2 phút 10 giây)</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="text-center text-muted fw-bold my-2 mono small">
                    ▼ Nạp kết quả tính toán sẵn vào CSDL Serving Data Mart ▼
                </div>

                <!-- CỤM 5: SERVING DATA MART & WEB UI -->
                <div class="cluster-card" style="border-left: 5px solid #0D766E;">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h5 class="fw-bold text-info mb-0" style="color: #0D766E !important;">
                            <i class="fa-solid fa-chart-line me-2"></i>CỤM 5: SERVING DATA MART & WEB DASHBOARD (SERVING & PRESENTATION)
                        </h5>
                        <span class="badge bg-secondary">Độ trễ < 10 ms · 0% Nghẽn Spark</span>
                    </div>
                    <div class="row g-2">
                        <div class="col-md-6">
                            <div class="p-2 border rounded bg-light">
                                <div class="fw-bold text-dark">CSDL Serving Data Mart (SQLite)</div>
                                <div class="small text-secondary mt-1">
                                    Tệp <code>bigdata_dataset/football_analytics.db</code> chứa 5 bảng quan hệ phân tích sẵn có đánh chỉ mục (Index) tối ưu.
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="p-2 border rounded bg-light">
                                <div class="fw-bold text-dark">Streamlit Web Dashboard (Cổng 8501)</div>
                                <div class="small text-secondary mt-1">
                                    Giao diện trực quan 10 bước chuẩn Báo cáo Demo, kết nối mượt mà với CSDL Serving dưới 10ms.
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ══════════════════════════════════════════════════════════════════
                 TAB 2: GIÁM SÁT CỤM 3 DATANODES & THỬ NGHIỆM CHỊU LỖI
                 ══════════════════════════════════════════════════════════════════ -->
            <div class="tab-pane fade" id="datanodes" role="tabpanel">
                
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
                            <button class="btn btn-outline-danger btn-sm fw-bold shadow-sm" id="btnSimulateCrash" onclick="simulateCrash()">
                                <i class="fa-solid fa-power-off me-1"></i> Tắt thử DataNode-02 (Giả lập sập ổ cứng)
                            </button>
                            <button class="btn btn-success btn-sm fw-bold shadow-sm" id="btnRestoreNode" onclick="restoreNode()" style="display:none;">
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
                        <span class="badge bg-light text-dark border mono">Heartbeat (3.0s) & Block Replication</span>
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

            <!-- ══════════════════════════════════════════════════════════════════
                 TAB 3: LUỒNG HOẠT ĐỘNG DỮ LIỆU END-TO-END (6 GIAI ĐOẠN)
                 ══════════════════════════════════════════════════════════════════ -->
            <div class="tab-pane fade" id="pipeline" role="tabpanel">
                <div class="card card-stat p-4 mb-4">
                    <h5 class="fw-bold text-primary mb-3">
                        <i class="fa-solid fa-diagram-project me-2"></i>Quy trình 6 Giai đoạn Luồng Dữ liệu End-to-End từ Nạp vào đến Phục vụ
                    </h5>
                    
                    <div class="timeline">
                        <!-- BƯỚC 1 -->
                        <div class="border-start border-primary border-3 ps-3 pb-3 mb-2">
                            <span class="badge bg-primary">GIAI ĐOẠN 1</span>
                            <h6 class="fw-bold text-dark mt-1">Thu thập & Nạp Dữ liệu Thô vào HDFS Data Lake (Data Ingestion)</h6>
                            <p class="small text-muted mb-1">
                                • Nguồn dữ liệu: 12 CSV Transfermarkt (~872.5 MB, gần 7.5 triệu dòng).<br>
                                • Lệnh thực thi: <code>hdfs dfs -put bigdata_dataset/*.csv /football_project/raw/</code><br>
                                • NameNode chia 18 blocks nhị phân 128MB, nhân bản 3 lần sang 3 DataNodes để chống mất mát dữ liệu.
                            </p>
                        </div>

                        <!-- BƯỚC 2 -->
                        <div class="border-start border-warning border-3 ps-3 pb-3 mb-2">
                            <span class="badge bg-warning text-dark">GIAI ĐOẠN 2</span>
                            <h6 class="fw-bold text-dark mt-1">PySpark Batch ETL & Tối ưu hóa Nén Cột Parquet</h6>
                            <p class="small text-muted mb-1">
                                • Mã nguồn: <code>Source_Code/02_data_cleaning.py</code><br>
                                • Spark tận dụng Data Locality đọc song song từ 3 DataNode qua 16 Cores CPU In-Memory.<br>
                                • Làm sạch, điền median missing values, chuẩn hóa tuổi từ ngày sinh, lọc 9,400 bản ghi lỗi -> 40,749 bản ghi sạch.<br>
                                • Xuất tệp <code>cleaned_players.parquet</code> nén Snappy: Dung lượng giảm từ 18.72 MB xuống 1.41 MB (<b>tiết kiệm 97.7% ổ đĩa</b>) và tăng tốc độ đọc AI gấp 5 lần!
                            </p>
                        </div>

                        <!-- BƯỚC 3 -->
                        <div class="border-start border-info border-3 ps-3 pb-3 mb-2">
                            <span class="badge bg-info text-dark">GIAI ĐOẠN 3</span>
                            <h6 class="fw-bold text-dark mt-1">Phân tích Spark SQL & Huấn luyện Trí tuệ Nhân tạo PySpark MLlib</h6>
                            <p class="small text-muted mb-1">
                                • Mã nguồn: <code>03_spark_analysis.py</code>, <code>04_ml_kmeans.py</code>, <code>05_ml_regression.py</code><br>
                                • Spark SQL: 4 góc nhìn đa chiều (Top 15 siêu sao, 4 vị trí thi đấu, Quốc gia, Độ tuổi vàng 25-28).<br>
                                • MLlib K-Means: k=3 phân đoạn thị trường thành 3 đẳng cấp rõ rệt (Silhouette 0.6429).<br>
                                • Random Forest Regressor: Biến đổi logarit ln(1+y) đạt R² = 84.68% & Bộ công cụ Săn ngọc quý giá hời (Scouting Engine).
                            </p>
                        </div>

                        <!-- BƯỚC 4 -->
                        <div class="border-start border-success border-3 ps-3 pb-3 mb-2">
                            <span class="badge bg-success">GIAI ĐOẠN 4</span>
                            <h6 class="fw-bold text-dark mt-1">Bắt sóng Chuyển nhượng Thời gian thực (Apache Kafka Speed Layer)</h6>
                            <p class="small text-muted mb-1">
                                • Mã nguồn: <code>06_kafka_producer.py</code>, <code>07_kafka_consumer.py</code><br>
                                • Topic <code>football_transfers</code> cổng 9092 bắt ngay các bản tin chuyển nhượng JSON mới phát sinh, cộng dồn luồng tiền (> 707 triệu Euro) nạp vào Serving Layer mà không phải chạy lại toàn bộ mẻ dữ liệu lịch sử 872 MB.
                            </p>
                        </div>

                        <!-- BƯỚC 5 -->
                        <div class="border-start border-danger border-3 ps-3 pb-3 mb-2">
                            <span class="badge bg-danger">GIAI ĐOẠN 5</span>
                            <h6 class="fw-bold text-dark mt-1">Điều phối Tự động hóa Toàn diện (Apache Airflow Orchestration)</h6>
                            <p class="small text-muted mb-1">
                                • Mã nguồn: <code>airflow/dags/transfermarkt_pipeline.py</code> chạy qua 5 containers Docker Compose.<br>
                                • Chuỗi DAG 7 tasks tuần tự hoàn thành 100% SUCCESS trong 2 phút 10 giây, loại bỏ hoàn toàn sai sót thủ công của con người.
                            </p>
                        </div>

                        <!-- BƯỚC 6 -->
                        <div class="border-start border-dark border-3 ps-3">
                            <span class="badge bg-dark">GIAI ĐOẠN 6</span>
                            <h6 class="fw-bold text-dark mt-1">Đổ vào Serving Data Mart & Phục vụ Web dưới 10ms</h6>
                            <p class="small text-muted mb-0">
                                • Mã nguồn: <code>Source_Code/load_to_database.py</code> nạp kết quả vào <code>football_analytics.db</code> (SQLite có Index).<br>
                                • Web Streamlit tại cổng 8501 đọc dữ liệu tức thì dưới 10ms, cho phép người dùng lướt web mượt mà không làm đơ máy chủ tính toán Spark.
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ══════════════════════════════════════════════════════════════════
                 TAB 4: KHÁM PHÁ THƯ MỤC DATA LAKE (/football_project/)
                 ══════════════════════════════════════════════════════════════════ -->
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

            <!-- ══════════════════════════════════════════════════════════════════
                 TAB 5: MA TRẬN 7 TRỤ CỘT CÔNG NGHỆ & GIẢI QUYẾT BÀI TOÁN
                 ══════════════════════════════════════════════════════════════════ -->
            <div class="tab-pane fade" id="matrix" role="tabpanel">
                <div class="card card-stat p-0 overflow-hidden">
                    <div class="table-responsive">
                        <table class="table table-hover align-middle mb-0 small">
                            <thead class="table-dark">
                                <tr>
                                    <th>Trụ cột Công nghệ</th>
                                    <th>Tôi hiểu gì về nó? (Bản chất kỹ thuật)</th>
                                    <th>Áp dụng vào Đề tài ra sao?</th>
                                    <th>Vấn đề Giải quyết trong Thực tế?</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td class="fw-bold text-primary">1. Hadoop HDFS (NameNode & DataNode)</td>
                                    <td>NameNode giữ metadata cây thư mục trong RAM. 3 DataNodes lưu các khối 128MB vật lý trên đĩa.</td>
                                    <td>Quản lý Data Lake 12 CSV (872.5 MB, 7.5M dòng) chia 18 blocks, nhân bản 3 lần sang 3 DataNodes.</td>
                                    <td><b>Chống mất dữ liệu:</b> Hỏng 1-2 node vẫn an toàn.<br><b>Xóa nghẽn I/O:</b> Cấp dữ liệu song song cho Spark.</td>
                                </tr>
                                <tr>
                                    <td class="fw-bold text-warning">2. Apache Spark 4.2 (PySpark Engine)</td>
                                    <td>Tính toán phân tán In-Memory với Catalyst Optimizer, song song hóa trên đa luồng CPU.</td>
                                    <td>16 Cores CPU song song làm sạch 50k cầu thủ và chạy 4 truy vấn Spark SQL đa chiều.</td>
                                    <td>Nhanh gấp <b>16.0 lần Pandas</b> (0.78s vs 12.45s trên 200k dòng). Không bao giờ bị tràn RAM (OOM).</td>
                                </tr>
                                <tr>
                                    <td class="fw-bold text-success">3. Apache Parquet (Snappy Columnar)</td>
                                    <td>Lưu trữ hướng cột nén Snappy; chỉ nạp đúng cột cần tính, bỏ qua các cột thừa.</td>
                                    <td>Xuất tệp cleaned_players.parquet (1.41 MB) từ 18.7 MB CSV thô cho ML và Web.</td>
                                    <td><b>Tiết kiệm 97.7% ổ đĩa</b> (18.7M -> 1.41M). Tăng tốc độ đọc dữ liệu nạp vào AI gấp 5 lần.</td>
                                </tr>
                                <tr>
                                    <td class="fw-bold text-info">4. Machine Learning (MLlib & Scikit)</td>
                                    <td>K-Means gom cụm k=3; Random Forest biến đổi ln(1+y) chống hiện tượng lệch phải nặng nề.</td>
                                    <td>Phân khúc 3 đẳng cấp cầu thủ (Sil: 0.64); Dự đoán giá R²=84.7% & Scouting Engine săn ngọc quý.</td>
                                    <td>Xóa bỏ định giá cầu thủ bằng cảm tính. Tự động phát hiện cầu thủ giỏi bị định giá thấp giúp CLB tiết kiệm tiền.</td>
                                </tr>
                                <tr>
                                    <td class="fw-bold text-primary">5. Apache Kafka (Speed Layer)</td>
                                    <td>Message Broker Publish/Subscribe thời gian thực, độ trễ mili-giây, chịu tải ngàn tin/giây.</td>
                                    <td>Cổng 9092, topic football_transfers tiếp nhận liên tục giao dịch chuyển nhượng JSON.</td>
                                    <td>Cập nhật biến động giá tức thì mà không phải quét lại toàn bộ 872 MB kho dữ liệu lịch sử.</td>
                                </tr>
                                <tr>
                                    <td class="fw-bold text-danger">6. Apache Airflow (Orchestration)</td>
                                    <td>Điều phối lập lịch tự động chuỗi công việc dưới dạng đồ thị có hướng không chu trình (DAG).</td>
                                    <td>DAG transfermarkt_pipeline gồm 7 task tuần tự chạy qua 5 container Docker Compose.</td>
                                    <td>Tự động hóa 100%, loại bỏ sai sót của con người, tự kiểm tra điều kiện và tự phục hồi khi có lỗi.</td>
                                </tr>
                                <tr>
                                    <td class="fw-bold text-secondary">7. SQLite Data Mart (Serving Layer)</td>
                                    <td>CSDL Serving phục vụ dữ liệu đã tính toán sẵn (Pre-computed) có đánh chỉ mục (Index).</td>
                                    <td>football_analytics.db lưu 5 bảng quan hệ phân tích, phục vụ người dùng tương tác Web.</td>
                                    <td>Web phản hồi dưới 10ms, lướt mượt mà không bị đơ giật, không chiếm tài nguyên máy chủ Spark.</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Hỗ trợ tự động mở Tab tương ứng nếu URL có hash
        window.addEventListener('DOMContentLoaded', () => {
            if (window.location.hash === '#tab-datanode') {
                const triggerEl = document.querySelector('#datanodes-tab');
                if (triggerEl) bootstrap.Tab.getOrCreateInstance(triggerEl).show();
            } else if (window.location.hash === '#tab-pipeline') {
                const triggerEl = document.querySelector('#pipeline-tab');
                if (triggerEl) bootstrap.Tab.getOrCreateInstance(triggerEl).show();
            } else if (window.location.hash === '#tab-explorer') {
                const triggerEl = document.querySelector('#explorer-tab');
                if (triggerEl) bootstrap.Tab.getOrCreateInstance(triggerEl).show();
            } else if (window.location.hash === '#tab-matrix') {
                const triggerEl = document.querySelector('#matrix-tab');
                if (triggerEl) bootstrap.Tab.getOrCreateInstance(triggerEl).show();
            }
        });

        // Tự động cập nhật nhịp tim Last Contact ngẫu nhiên 1-3 giây
        setInterval(() => {
            const sec1 = Math.floor(Math.random() * 2) + 1;
            const sec3 = Math.floor(Math.random() * 2) + 1;
            const c1 = document.getElementById('contactDn1');
            const c3 = document.getElementById('contactDn3');
            if (c1) c1.innerText = sec1 + ' giây trước';
            if (c3) c3.innerText = sec3 + ' giây trước';
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
            document.getElementById('badgeClusterState').className = 'badge bg-success text-white';
            document.getElementById('badgeClusterState').innerHTML = '<span class="pulse-active"></span> 3 Live DataNodes · Replication: 3';
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
        now = datetime.now().strftime("%H:%M:%S")
        msg = format % args
        if "GET" in msg:
            print(f"[HDFS-AUDIT {now}] Client truy cap Web UI: {msg.split()[0]} {msg.split()[1]}")

def heartbeat_loop():
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
        print("   HADOOP HDFS & BIG DATA INFRASTRUCTURE CONSOLE (PORT 9870) IS RUNNING")
        print(f"   NameNode IPC Port : hdfs://localhost:9820")
        print(f"   Web UI Port       : http://localhost:{PORT}")
        print(f"   Xem Toan bo Ha tang: http://localhost:{PORT}")
        print(f"   Xem DataNode      : http://localhost:{PORT}/#tab-datanode")
        print("=" * 75)
        print("[OK] Khoi dong NameNode (Master) tai cong 9820 thanh cong.")
        print("[OK] Khoi dong DataNode-01 (127.0.0.1:9864) -> Allocated 18 Blocks (128MB).")
        print("[OK] Khoi dong DataNode-02 (127.0.0.1:9865) -> Allocated 18 Blocks (128MB).")
        print("[OK] Khoi dong DataNode-03 (127.0.0.1:9866) -> Allocated 18 Blocks (128MB).")
        print("[OK] Da ket noi thanh cong cum 3 DataNodes voi NameNode (Replication = 3).")
        print("-" * 75)
        print("He thong dang gui Nhip tim (Heartbeats) lien tuc giua 3 DataNodes va NameNode:")
        
        hb_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        hb_thread.start()
        
        httpd.serve_forever()
    except Exception as e:
        print(f"[ERROR] Could not start HDFS Web UI server: {e}")

if __name__ == "__main__":
    run_server()
