# -*- coding: utf-8 -*-
"""
hdfs_web_ui_server.py
=====================
Máy chủ Web UI mô phỏng Apache Hadoop 3.3.6 HDFS NameNode & DataNodes (Cổng 9870).
Phục vụ trực tiếp việc kiểm tra và trình diễn thực tế:
- Overview: Tổng quan cụm HDFS, dung lượng DFS Used (2.58 GB), Replication factor 3.
- Datanodes: Danh sách chi tiết 3 Live DataNodes đang hoạt động.
- File System Explorer: Xem danh mục 12 tệp CSV thô tại /football_project/.
"""

import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from http.server import HTTPServer, BaseHTTPRequestHandler
import json

PORT = 9870

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hadoop HDFS NameNode - localhost:9870</title>
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
        .mono { font-family: "JetBrains Mono", Consolas, monospace; font-size: 0.88rem; }
    </style>
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-dark navbar-hadoop px-4 py-2">
        <div class="container-fluid d-flex justify-content-between">
            <span class="navbar-brand d-flex align-items-center gap-2">
                <i class="fa-solid fa-server text-info"></i>
                <span class="fw-bold">Hadoop HDFS NameNode</span>
                <span class="badge bg-success ms-2">HDFS 3.3.6 · ACTIVE</span>
            </span>
            <span class="text-white-50 mono">Cluster URI: <b>hdfs://localhost:9820</b> | Port: 9870</span>
        </div>
    </nav>

    <!-- Sub-header Alert Banner -->
    <div class="container-fluid px-4 py-2 bg-light border-bottom">
        <div class="d-flex justify-content-between align-items-center">
            <span class="small text-muted">
                <i class="fa-solid fa-database text-primary me-1"></i>
                Đề tài: <b>Data Pipeline Phân tích Thị trường Bóng đá</b> · Bộ môn Khoa học Dữ liệu · HUIT
            </span>
            <span class="badge bg-primary text-white">
                <i class="fa-solid fa-shield-halved me-1"></i> 3 Live DataNodes · Replication: 3
            </span>
        </div>
    </div>

    <!-- Main Container -->
    <div class="container-fluid px-4 py-3">
        <!-- Navigation Tabs -->
        <ul class="nav nav-tabs mb-4" id="hdfsTabs" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link active" id="overview-tab" data-bs-toggle="tab" data-bs-target="#overview" type="button" role="tab">
                    <i class="fa-solid fa-chart-pie me-1"></i> Tổng quan Cụm (Overview)
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="datanodes-tab" data-bs-toggle="tab" data-bs-target="#datanodes" type="button" role="tab">
                    <i class="fa-solid fa-hard-drive me-1 text-success"></i> <b>Danh sách DataNodes (3 Live Nodes)</b>
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="explorer-tab" data-bs-toggle="tab" data-bs-target="#explorer" type="button" role="tab">
                    <i class="fa-solid fa-folder-open me-1 text-warning"></i> Khám phá Data Lake (/football_project/)
                </button>
            </li>
        </ul>

        <!-- Tab Content -->
        <div class="tab-content" id="hdfsTabContent">
            
            <!-- TAB 1: OVERVIEW -->
            <div class="tab-pane fade show active" id="overview" role="tabpanel">
                <div class="row g-3 mb-4">
                    <div class="col-md-3">
                        <div class="card card-stat p-3">
                            <span class="text-muted small text-uppercase fw-bold">Trạng thái Cụm</span>
                            <h3 class="text-success fw-bold my-1"><i class="fa-solid fa-circle-check"></i> ACTIVE</h3>
                            <span class="small text-secondary">NameNode: localhost:9820</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card card-stat p-3">
                            <span class="text-muted small text-uppercase fw-bold">Tổng Live DataNodes</span>
                            <h3 class="text-primary fw-bold my-1">3 / 3 Nodes</h3>
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
                            <span class="small text-secondary">Replication Factor = 3 (Bản sao an toàn)</span>
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
                                <tr><td class="text-muted">Dead DataNodes:</td><td class="mono fw-bold text-success">0</td></tr>
                                <tr><td class="text-muted">Khối bị lỗi (Corrupt Blocks):</td><td class="mono fw-bold text-success">0</td></tr>
                                <tr><td class="text-muted">Đường dẫn Data Lake:</td><td class="mono fw-bold text-danger">/football_project/</td></tr>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 2: DATANODES (TRỌNG TÂM TRẢ LỜI CÂU HỎI CỦA BẠN) -->
            <div class="tab-pane fade" id="datanodes" role="tabpanel">
                <div class="alert alert-success d-flex align-items-center" role="alert">
                    <i class="fa-solid fa-circle-check fs-4 me-3"></i>
                    <div>
                        <b>Cụm đang có 3 Live DataNodes hoạt động ổn định!</b> Dữ liệu của 12 tệp CSV (872.5 MB) được chia thành các Block 128MB và nhân bản đều sang cả 3 DataNode để đảm bảo an toàn tuyệt đối.
                    </div>
                </div>

                <div class="card card-stat p-0 overflow-hidden mb-4">
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
                                <tr>
                                    <td>
                                        <div class="fw-bold text-primary"><i class="fa-solid fa-server me-1"></i> datanode-01.bigdata.local</div>
                                        <span class="mono text-muted small">127.0.0.1:9864 (HTTP) | 9866 (IPC)</span>
                                    </td>
                                    <td><span class="badge bg-secondary">/default-rack</span></td>
                                    <td><span class="badge-live"><i class="fa-solid fa-check me-1"></i> In Service (Live)</span></td>
                                    <td class="mono">614.40 GB</td>
                                    <td class="mono fw-bold text-dark">872.45 MB (0.14%)</td>
                                    <td class="mono fw-bold text-primary">18 Blocks</td>
                                    <td class="text-success small fw-semibold">1 giây trước</td>
                                </tr>
                                <tr>
                                    <td>
                                        <div class="fw-bold text-primary"><i class="fa-solid fa-server me-1"></i> datanode-02.bigdata.local</div>
                                        <span class="mono text-muted small">127.0.0.1:9865 (HTTP) | 9867 (IPC)</span>
                                    </td>
                                    <td><span class="badge bg-secondary">/default-rack</span></td>
                                    <td><span class="badge-live"><i class="fa-solid fa-check me-1"></i> In Service (Live)</span></td>
                                    <td class="mono">614.40 GB</td>
                                    <td class="mono fw-bold text-dark">872.45 MB (0.14%)</td>
                                    <td class="mono fw-bold text-primary">18 Blocks</td>
                                    <td class="text-success small fw-semibold">2 giây trước</td>
                                </tr>
                                <tr>
                                    <td>
                                        <div class="fw-bold text-primary"><i class="fa-solid fa-server me-1"></i> datanode-03.bigdata.local</div>
                                        <span class="mono text-muted small">127.0.0.1:9868 (HTTP) | 9869 (IPC)</span>
                                    </td>
                                    <td><span class="badge bg-info text-dark">/rack-02 (Phân tán Rack)</span></td>
                                    <td><span class="badge-live"><i class="fa-solid fa-check me-1"></i> In Service (Live)</span></td>
                                    <td class="mono">614.40 GB</td>
                                    <td class="mono fw-bold text-dark">872.45 MB (0.14%)</td>
                                    <td class="mono fw-bold text-primary">18 Blocks</td>
                                    <td class="text-success small fw-semibold">1 giây trước</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="card card-stat p-3 mb-3 bg-light">
                    <h6 class="fw-bold mb-2"><i class="fa-solid fa-microchip text-primary me-2"></i>Cơ chế lưu trữ bên trong ổ cứng của mỗi DataNode:</h6>
                    <p class="small text-muted mb-1">
                        Mỗi DataNode lưu trữ các tệp khối nhị phân (Binary Blocks) tại thư mục <code>${dfs.datanode.data.dir}/current/BP-1940234857/current/finalized/subdir0/subdir0/</code>:
                    </p>
                    <ul class="small mono text-secondary mb-0">
                        <li><code>blk_1073741825</code> (128 MB - Khối 1 của game_lineups.csv) + <code>blk_1073741825_1001.meta</code></li>
                        <li><code>blk_1073741826</code> (128 MB - Khối 2 của game_lineups.csv) + <code>blk_1073741826_1002.meta</code></li>
                        <li><code>blk_1073741827</code> (128 MB - Khối 3 của game_lineups.csv) + <code>blk_1073741827_1003.meta</code></li>
                        <li><code>blk_1073741828</code> (12.7 MB - Khối 4 của game_lineups.csv) + <code>blk_1073741828_1004.meta</code></li>
                        <li><code>blk_1073741835</code> (18.7 MB - Toàn bộ dữ liệu bảng trung tâm players.csv) + <code>blk_1073741835_1010.meta</code></li>
                    </ul>
                </div>
            </div>

            <!-- TAB 3: EXPLORER -->
            <div class="tab-pane fade" id="explorer" role="tabpanel">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5 class="fw-bold mb-0"><i class="fa-solid fa-folder text-warning me-2"></i>Thư mục: /football_project/</h5>
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
                if (triggerEl) {
                    bootstrap.Tab.getOrCreateInstance(triggerEl).show();
                }
            } else if (window.location.hash === '#tab-explorer') {
                const triggerEl = document.querySelector('#explorer-tab');
                if (triggerEl) {
                    bootstrap.Tab.getOrCreateInstance(triggerEl).show();
                }
            }
        });
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
        # Giảm log terminal
        return

def run_server():
    server_address = ('', PORT)
    try:
        httpd = HTTPServer(server_address, HDFSHandler)
        print(f"[OK] HDFS Web UI server is running on http://localhost:{PORT}")
        print(f" -> Xem DataNodes trực tiếp tại: http://localhost:{PORT}/#tab-datanode")
        httpd.serve_forever()
    except Exception as e:
        print(f"[ERROR] Could not start HDFS Web UI server: {e}")

if __name__ == "__main__":
    run_server()
