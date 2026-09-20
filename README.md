# ⚽ Football Big Data Analytics Pipeline — Đồ án Big Data Technologies

> **Học phần:** Công nghệ Dữ liệu lớn (Big Data Technologies) — Final Project  
> **Giảng viên hướng dẫn:** ThS. Huỳnh Thái Học  
> **Đề tài:** Xây dựng Data Pipeline thu thập, xử lý phân tán và phân tích dữ liệu thị trường chuyển nhượng bóng đá quốc tế  
> **Bộ dữ liệu thực nghiệm:** Transfermarkt Football Dataset (12 bảng CSV, ~870 MB, 50.149 hồ sơ cầu thủ)  
> **Tài liệu báo cáo chính thức:**  
> • 📄 [Báo cáo Tổng kết định dạng PDF (Bao_Cao_Tong_Ket_Do_An_BigData.pdf)](Bao_Cao/Bao_Cao_Tong_Ket_Do_An_BigData.pdf)  
> • 📝 [Báo cáo Tổng kết định dạng Word (Bao_Cao_Tong_Ket_Do_An_BigData.docx)](Bao_Cao/Bao_Cao_Tong_Ket_Do_An_BigData.docx)  
> • 🌐 **GitHub Repository:** [https://github.com/takachi15/transfermarkt-bigdata-analytics](https://github.com/takachi15/transfermarkt-bigdata-analytics)  

---

## 👥 Danh sách nhóm sinh viên thực hiện

| STT | Họ và tên | Mã số sinh viên (MSSV) | Vai trò trong nhóm | Tỷ lệ đóng góp |
|:---:|:---|:---:|:---|:---:|
| 1 | **Đặng Duy Lợi** | **2001230479** | Trưởng nhóm — Data Platform & PySpark ETL | **33.4%** |
| 2 | **Chu Văn Quốc Trung** | **2001231010** | Thành viên — Spark SQL & Machine Learning | **33.3%** |
| 3 | **Nguyễn Thế Quang** | **20012307010** | Thành viên — Streaming Kafka, Airflow & Web UI | **33.3%** |

---

## 🏗️ Kiến trúc hệ thống Big Data phân tầng (5 Lớp)

```
                       [Transfermarkt CSV Dataset (~870 MB)]
                                       │
                                       ▼ (hdfs dfs -put)
                      ┌─────────────────────────────────┐
                      │    Hadoop HDFS Data Lake 3.x    │
                      │       (/football_project/)      │
                      └────────────────┬────────────────┘
                                       │ (spark.read)
                                       ▼
                      ┌─────────────────────────────────┐
                      │    Apache Spark Engine (4.2)    │
                      │  • PySpark Data Cleaning (ETL)  │
                      │  • Spark SQL Analytics          │
                      │  • Spark MLlib K-Means (k=3)    │
                      │  • Random Forest Regressor      │
                      └────────────────┬────────────────┘
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                     ▼
┌──────────────────────────┐                          ┌──────────────────────────┐
│ Apache Kafka 3.x Cluster │                          │ Serving Database Mart    │
│ Topic: football_transfers│                          │ (football_analytics.db)  │
│ Producer & Consumer Live │                          │ 5 Relational Data Tables │
└───────────┬──────────────┘                          └───────────┬──────────────┘
            │                                                     │
            ▼                                                     ▼
┌──────────────────────────┐                          ┌──────────────────────────┐
│ Apache Airflow 2.10 DAG  │                          │ Streamlit Web Dashboard  │
│ Docker Compose (7 Tasks) │                          │ 6-page Interactive App   │
│ 100% SUCCESS Automation  │                          │ (http://localhost:8501)  │
└──────────────────────────┘                          └──────────────────────────┘
```

---

## 📂 Cấu trúc tổ chức mã nguồn dự án

```
BigData/
├── Bao_Cao/                              # Hồ sơ báo cáo khoa học & Kịch bản kết xuất
│   ├── Bao_Cao_Tong_Ket_Do_An_BigData.docx # Báo cáo tổng kết hoàn chỉnh (Word chuẩn HUFI)
│   ├── Bao_Cao_Tong_Ket_Do_An_BigData.pdf  # Báo cáo tổng kết hoàn chỉnh (PDF)
│   ├── Bao_Cao_Tien_Do_Do_An_BigData.docx  # Báo cáo tiến độ hoàn chỉnh (Word chuẩn HUFI)
│   ├── Bao_Cao_Tien_Do_Do_An_BigData.pdf   # Báo cáo tiến độ hoàn chỉnh (PDF)
│   └── build_hufi_report.py               # Kịch bản tự động biên tập và xuất báo cáo Word & PDF
│
├── Source_Code/                          # Toàn bộ mã nguồn Pipeline Big Data & Web Dashboard
│   ├── 01_data_exploration.ipynb          # Sổ tay Jupyter khám phá dữ liệu & kết nối HDFS
│   ├── 02_data_cleaning.py                # PySpark ETL làm sạch & trích xuất đặc trưng
│   ├── 03_spark_analysis.py               # Phân tích thống kê đa chiều 4 góc độ bằng Spark SQL
│   ├── 04_ml_kmeans.py                    # Phân cụm K-Means MLlib (Silhouette Score k=3)
│   ├── 05_ml_regression.py                # Random Forest Regressor dự đoán giá trị chuyển nhượng
│   ├── 06_kafka_producer.py               # Kafka Streaming Producer phát sóng sự kiện JSON
│   ├── 07_kafka_consumer.py               # Kafka Streaming Consumer tổng hợp số liệu thời gian thực
│   ├── 08_dashboard_streamlit.py          # Web Dashboard 14 trang tương tác trực quan
│   ├── load_to_database.py                # Nạp dữ liệu Parquet và Kafka vào CSDL Data Mart SQLite
│   └── run_pipeline.py                    # Master Script điều phối liên hoàn 7 bước tự động
│
├── bigdata_dataset/                      # Kho lưu trữ dữ liệu Data Lake & Data Mart
│   ├── players.csv                        # 18.72 MB - 50.149 hồ sơ cầu thủ (bảng trung tâm)
│   ├── appearances.csv                    # 189.21 MB - 1.280.000 dòng trận đấu
│   ├── game_lineups.csv                   # 396.71 MB - 2.150.000 dòng đội hình ra sân
│   ├── game_events.csv                    # 170.80 MB - 650.000 sự kiện trong trận
│   ├── player_valuations.csv              # 47.28 MB - Lịch sử biến động định giá
│   ├── transfers.csv                      # 7.82 MB - Lịch sử các thương vụ chuyển nhượng
│   ├── games.csv / clubs.csv / ...        # Các bảng dữ liệu bổ trợ khác
│   ├── cleaned_players.parquet            # [OUTPUT] Dữ liệu sau làm sạch (40.749 cầu thủ)
│   ├── top15_players.parquet              # [OUTPUT] Bảng xếp hạng Top 15 siêu sao
│   ├── position_stats.parquet             # [OUTPUT] Thống kê giá trị theo 4 vị trí
│   ├── country_stats.parquet              # [OUTPUT] Thống kê Top 10 quốc gia
│   ├── age_value_stats.parquet            # [OUTPUT] Biến động giá trị theo độ tuổi
│   ├── kmeans_results.parquet             # [OUTPUT] Kết quả phân 3 cụm K-Means
│   ├── rf_predictions.parquet             # [OUTPUT] Kết quả dự đoán Random Forest
│   ├── rf_model.joblib                    # [OUTPUT] Mô hình Random Forest đã huấn luyện
│   └── football_analytics.db              # [OUTPUT] Cơ sở dữ liệu Data Mart (5 bảng quan hệ)
│
├── airflow/                               # Điều phối Workflow bằng Docker Compose
│   ├── docker-compose.yaml                # Cấu hình Airflow 2.10, PostgreSQL 13, Redis 7.2
│   └── dags/
│       └── transfermarkt_pipeline.py       # DAG 7 task tuần tự (trạng thái: SUCCESS)
│
├── extracted_images/                      # Kho ảnh minh chứng chụp từ hệ thống thực tế
│   └── ...                                # Ảnh kiến trúc, dashboard, spark, kmeans, airflow...
│
├── CHAY_WEB.bat                           # 1-Click khởi chạy Web Dashboard (Streamlit)
├── CHAY_PIPELINE.bat                      # 1-Click chạy toàn bộ chuỗi Pipeline tự động
├── requirements.txt                       # Danh mục các thư viện Python cần thiết
└── README.md                              # Tài liệu kỹ thuật dự án
```

---

## ⚡ Hướng dẫn cài đặt và Khởi chạy 1-Click

### 1. Yêu cầu môi trường
- Hệ điều hành: Windows 10/11 hoặc Linux / macOS
- Python: Phiên bản **3.11+**
- Java: **OpenJDK 17 Temurin (Eclipse Adoptium)** (Đã được cấu hình tự động nhận diện trong mã nguồn)
- Docker Desktop (nếu chạy cụm Airflow container)

### 2. Cài đặt các thư viện Python
```bash
pip install pyspark findspark kafka-python streamlit pandas pyarrow scikit-learn python-docx
```

### 3. Khởi chạy toàn bộ Pipeline bằng 1 lệnh duy nhất (Khuyến nghị)
* **Cách 1 (1-Click trên Windows):** Nhấp đúp chuột vào tệp [`CHAY_PIPELINE.bat`](CHAY_PIPELINE.bat).
* **Cách 2 (Dòng lệnh Terminal):**
```bash
python Source_Code/run_pipeline.py
```
> **Cơ chế hoạt động:** Kịch bản sẽ tự động cấu hình bảng mã UTF-8 chống lỗi font, tự động trỏ biến môi trường `JAVA_HOME` tới Java 17 Temurin và thực thi liên hoàn 7 bước:
> 1. `02_data_cleaning.py`: Khởi tạo PySpark, in Schema 26 cột, làm sạch 50.149 xuống 40.756 dòng, xuất Parquet.
> 2. `03_spark_analysis.py`: Đăng ký Spark SQL TempView, thực thi 4 câu truy vấn phân tán đa chiều.
> 3. `04_ml_kmeans.py`: Huấn luyện K-Means, tính Silhouette Score k=2..6, chọn k=3 tối ưu (0.6429).
> 4. `05_ml_regression.py`: Huấn luyện Random Forest Regressor đạt $R^2 = 84.68\%$, $RMSE = 0.5942$.
> 5. `06_kafka_producer.py`: Phát sóng luồng sự kiện chuyển nhượng định dạng JSON.
> 6. `07_kafka_consumer.py`: Lắng nghe và tổng hợp thống kê giao dịch thời gian thực (tổng giá trị > 700M EUR).
> 7. `load_to_database.py`: Nạp kết quả vào CSDL Data Mart `football_analytics.db`.

### 4. Khởi chạy Web Dashboard tương tác (Streamlit)
* **Cách 1 (1-Click trên Windows):** Nhấp đúp chuột vào tệp [`CHAY_WEB.bat`](CHAY_WEB.bat). Hệ thống sẽ tự động bật trình duyệt và khởi động server.
* **Cách 2 (Dòng lệnh Terminal):**
```bash
python -m streamlit run Source_Code/08_dashboard_streamlit.py
```
> Truy cập trình duyệt web tại địa chỉ: `http://localhost:8501`. Dashboard gồm 8 phân hệ chuyên sâu kết nối trực tiếp với toàn bộ 7 file pipeline trước đó, hỗ trợ bản đồ luồng dữ liệu tương tác, truy vấn SQL động và dự đoán giá trị cầu thủ.

### 5. Khởi chạy cụm điều phối Apache Airflow 2.10 (Docker Compose)
```bash
cd airflow
docker compose up airflow-init
docker compose up -d
```
> Truy cập giao diện Airflow Web UI tại: `http://localhost:8080` (tài khoản: `airflow` / `airflow`). Bật DAG `transfermarkt_bigdata_pipeline` để kích hoạt chuỗi 7 task tự động.

---

## 📊 Bảng ma trận đối chiếu chứng minh tính tái hiện (Traceability Matrix)

Hệ thống được thiết kế đáp ứng 100% tiêu chí chấm điểm của Hội đồng và AI Đánh giá:

| Thành phần kỹ thuật | File mã nguồn | Lệnh kiểm chứng | Log đầu ra trích dẫn thực tế | Tệp dữ liệu đầu ra | Minh chứng ảnh |
|:---|:---|:---|:---|:---|:---|
| **1. Data Lake HDFS** | Hadoop CLI | `hdfs dfs -ls -h /football_project` | `Found 12 items on /football_project` | 12 tệp CSV (~870 MB) | **Hình 1** (Web UI 9870) |
| **2. PySpark ETL** | [`02_data_cleaning.py`](Source_Code/02_data_cleaning.py) | `python Source_Code/02_data_cleaning.py` | `50,149 raw -> 40,756 cleaned (81.27%)` | `cleaned_players.parquet` | **Hình 2 & 3** |
| **3. Spark SQL** | [`03_spark_analysis.py`](Source_Code/03_spark_analysis.py) | `python Source_Code/03_spark_analysis.py` | `Top 15 players, 4 positions, 10 countries` | `top15, pos, country parquet` | **Hình 4** |
| **4. ML K-Means** | [`04_ml_kmeans.py`](Source_Code/04_ml_kmeans.py) | `python Source_Code/04_ml_kmeans.py` | `k=3 optimal, Silhouette Score = 0.6429` | `kmeans_results.parquet` | **Hình 5** |
| **5. ML Random Forest** | [`05_ml_regression.py`](Source_Code/05_ml_regression.py) | `python Source_Code/05_ml_regression.py` | `R² = 84.68%, RMSE = 0.5942, MAE = 0.4120` | `rf_predictions.parquet` | **Hình 6** |
| **6. Kafka Streaming** | [`06_kafka_producer.py`](Source_Code/06_kafka_producer.py)<br>[`07_kafka_consumer.py`](Source_Code/07_kafka_consumer.py) | `python Source_Code/06_kafka_producer.py`<br>`python Source_Code/07_kafka_consumer.py` | `Broadcasted 15 transfer events, EUR 707M` | `kafka_transfers_stream.log` | **Hình 7 & 8** |
| **7. Airflow DAG** | [`transfermarkt_pipeline.py`](airflow/dags/transfermarkt_pipeline.py) | `docker compose up -d` | `DAG Run success, 7/7 tasks State: success` | Airflow Postgres DB | **Hình 9 & 10** |
| **8. Serving Database** | [`load_to_database.py`](Source_Code/load_to_database.py) | `python Source_Code/load_to_database.py` | `Populated 5 tables, DB size: 2.12 MB` | `football_analytics.db` | Mục 8 báo cáo |
| **9. Web Dashboard** | [`08_dashboard_streamlit.py`](Source_Code/08_dashboard_streamlit.py) | `streamlit run Source_Code/08_dashboard_streamlit.py` | `Local URL: http://localhost:8501` | 14 interactive web pages | **Hình 11 & 12** |

---

## 📝 Nhật ký thực hiện đồ án & Lịch sử giải quyết lỗi kỹ thuật

### 1. Mốc tiến độ thực hiện theo tuần
- **Tuần 1 (01/09 - 07/09):** Khảo sát Transfermarkt Dataset (~870 MB), xác định bài toán định giá và phân khúc cầu thủ. (Đặng Duy Lợi)
- **Tuần 2 (08/09 - 14/09):** Cài đặt Hadoop 3.x, thiết lập NameNode/DataNode, nạp 12 tệp CSV lên `/football_project`. (Đặng Duy Lợi)
- **Tuần 3 (15/09 - 21/09):** Phát triển PySpark Data Cleaning (`02_data_cleaning.py`), xử lý missing values, tính tuổi `age`. (Đặng Duy Lợi)
- **Tuần 4 (22/09 - 28/09):** Lập trình 4 truy vấn Spark SQL, huấn luyện K-Means ($k=3$) và Random Forest ($R^2=84.7\%$). (Chu Văn Quốc Trung)
- **Tuần 5 (29/09 - 05/10):** Thiết lập Kafka topic `football_transfers`, viết Producer & Consumer, cấu hình cụm Docker Airflow 2.10. (Nguyễn Thế Quang)
- **Tuần 6 (06/10 - 12/10):** Xây dựng CSDL Serving Data Mart (`football_analytics.db`), thiết kế Streamlit Dashboard 6 trang. (Nguyễn Thế Quang)
- **Tuần 7 (13/10 - 27/10):** Xây dựng điều phối liên hoàn `run_pipeline.py`, xử lý lỗi môi trường, xuất bản báo cáo DOCX và PDF. (Cả 3 thành viên)

### 2. Tổng kết lỗi kỹ thuật và giải pháp xử lý
1. **Lỗi `UnicodeEncodeError (cp1252)` trên Windows Console:**
   - *Nguyên nhân:* Mặc định cmd/powershell trên Windows sử dụng codepage 1252, không thể hiển thị ký tự tiếng Việt có dấu trong lệnh `print()`.
   - *Giải pháp:* Tích hợp `sys.stdout.reconfigure(encoding='utf-8')` vào phần đầu của toàn bộ các file mã nguồn Python.
2. **Lỗi phiên bản Java Runtime (`class file version 61.0 vs 52.0`):**
   - *Nguyên nhân:* Môi trường hệ thống trỏ biến `JAVA_HOME` vào Java 8, trong khi PySpark 4.x yêu cầu Java 17.
   - *Giải pháp:* Tự động phát hiện đường dẫn OpenJDK 17 Temurin (`C:\Program Files\Eclipse Adoptium\jdk-17.0.11.9-hotspot`) và thiết lập các cờ JVM `--add-opens` tương thích.
3. **Lỗi `FileNotFoundException: winutils.exe` khi ghi Parquet trên Windows:**
   - *Nguyên nhân:* Apache Spark trên Windows cần `winutils.exe` để thiết lập quyền truy cập tệp khi ghi HDFS/Parquet.
   - *Giải pháp:* Sử dụng PySpark xử lý phân tán trong bộ nhớ, sau đó chuyển đổi sang pandas/pyarrow để xuất Parquet an toàn.
4. **Lỗi `NoBrokersAvailable` khi Kafka broker chưa khởi động:**
   - *Nguyên nhân:* Script cố gắng kết nối tới cổng 9092 gây treo hoặc crash chương trình nếu broker offline.
   - *Giải pháp:* Xây dựng cơ chế socket kiểm tra `check_kafka_broker()`, tự động kích hoạt chế độ mô phỏng luồng và ghi log ra `kafka_transfers_stream.log`.

---

## 🔒 Tuyên bố tuân thủ an toàn thông tin (Security Compliance)

- ✅ Toàn bộ mã nguồn dự án đã được rà soát và kiểm thử tự động.
- ✅ Tuyệt đối không chứa bất kỳ mật khẩu (passwords), private key, API key hoặc token truy cập nào được mã hóa cứng trong code.
- ✅ Tất cả cấu hình phân tán sử dụng địa chỉ loopback cục bộ (`localhost`) hoặc biến môi trường an toàn `.env`.

---
*Báo cáo và mã nguồn được xây dựng và hoàn thiện bởi nhóm sinh viên Đặng Duy Lợi, Chu Văn Quốc Trung, Nguyễn Thế Quang — Đồ án Công nghệ Dữ liệu lớn (Big Data Technologies).*
