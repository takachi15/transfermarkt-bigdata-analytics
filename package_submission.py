# -*- coding: utf-8 -*-
"""
package_submission.py
=====================
Tự động đóng gói toàn bộ hồ sơ nộp đồ án Big Data thành tệp:
"DoAn_BigData_Nhom5_Final.zip"
Bao gồm:
- Báo cáo (AI Verification PDF, Báo cáo Tổng kết 50 trang, Kịch bản Demo)
- Mã nguồn đầy đủ (Source_Code/)
- Toàn bộ 9 tệp Terminal Execution Logs (logs/)
- Toàn bộ các tệp đầu ra (bigdata_dataset/*.parquet, rf_model.joblib, football_analytics.db)
- Airflow DAG & Docker Compose (airflow/)
- README.md, requirements.txt, CHAY_WEB.bat, CHAY_PIPELINE.bat
"""

import os
import sys
import zipfile

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ZIP_OUTPUT = os.path.join(BASE_DIR, "DoAn_BigData_Nhom5_Final.zip")

# Danh mục các tệp và thư mục đưa vào gói nộp
INCLUDE_ITEMS = [
    # Thư mục Báo Cáo
    ("Bao_Cao/Bao_Cao_Tong_Ket_Do_An_BigData.pdf", "Bao_Cao/Bao_Cao_Tong_Ket_Do_An_BigData.pdf"),
    ("Bao_Cao/Bao_Cao_Tong_Ket_Do_An_BigData.docx", "Bao_Cao/Bao_Cao_Tong_Ket_Do_An_BigData.docx"),
    ("Bao_Cao/Bao_Cao_Tong_Ket_Do_An_BigData_Chuan_AI_10Diem.pdf", "Bao_Cao/Bao_Cao_Tong_Ket_Do_An_BigData_Chuan_AI_10Diem.pdf"),
    ("Bao_Cao/Bao_Cao_Tong_Ket_Do_An_BigData_Chuan_AI_10Diem.docx", "Bao_Cao/Bao_Cao_Tong_Ket_Do_An_BigData_Chuan_AI_10Diem.docx"),
    ("Bao_Cao/Kich_Ban_Demo_Bao_Cao_Cuoi_Ky_BigData.pdf", "Bao_Cao/Kich_Ban_Demo_Bao_Cao_Cuoi_Ky_BigData.pdf"),
    ("Bao_Cao/Kich_Ban_Demo_Bao_Cao_Cuoi_Ky_BigData.docx", "Bao_Cao/Kich_Ban_Demo_Bao_Cao_Cuoi_Ky_BigData.docx"),
    ("Bao_Cao/Bao_Cao_Tien_Do_Do_An_BigData.docx", "Bao_Cao/Bao_Cao_Tien_Do_Do_An_BigData.docx"),
    ("Bao_Cao/Bao_Cao_Tien_Do_Do_An_BigData.pdf", "Bao_Cao/Bao_Cao_Tien_Do_Do_An_BigData.pdf"),

    # Mã nguồn
    ("Source_Code/01_data_exploration.ipynb", "Source_Code/01_data_exploration.ipynb"),
    ("Source_Code/02_data_cleaning.py", "Source_Code/02_data_cleaning.py"),
    ("Source_Code/03_spark_analysis.py", "Source_Code/03_spark_analysis.py"),
    ("Source_Code/04_ml_kmeans.py", "Source_Code/04_ml_kmeans.py"),
    ("Source_Code/05_ml_regression.py", "Source_Code/05_ml_regression.py"),
    ("Source_Code/06_kafka_producer.py", "Source_Code/06_kafka_producer.py"),
    ("Source_Code/07_kafka_consumer.py", "Source_Code/07_kafka_consumer.py"),
    ("Source_Code/08_dashboard_streamlit.py", "Source_Code/08_dashboard_streamlit.py"),
    ("Source_Code/load_to_database.py", "Source_Code/load_to_database.py"),
    ("Source_Code/run_pipeline.py", "Source_Code/run_pipeline.py"),

    # Logs thực thi thực tế
    ("logs/hdfs_execution.log", "logs/hdfs_execution.log"),
    ("logs/spark_etl_cleaning.log", "logs/spark_etl_cleaning.log"),
    ("logs/spark_sql_analysis.log", "logs/spark_sql_analysis.log"),
    ("logs/ml_kmeans_training.log", "logs/ml_kmeans_training.log"),
    ("logs/ml_regression_training.log", "logs/ml_regression_training.log"),
    ("logs/kafka_streaming.log", "logs/kafka_streaming.log"),
    ("logs/airflow_pipeline_run.log", "logs/airflow_pipeline_run.log"),
    ("logs/dashboard_audit.log", "logs/dashboard_audit.log"),
    ("logs/git_commit_history.log", "logs/git_commit_history.log"),

    # Airflow
    ("airflow/docker-compose.yaml", "airflow/docker-compose.yaml"),
    ("airflow/dags/transfermarkt_pipeline.py", "airflow/dags/transfermarkt_pipeline.py"),

    # Tệp điều phối và tài liệu gốc
    ("README.md", "README.md"),
    ("requirements.txt", "requirements.txt"),
    ("CHAY_WEB.bat", "CHAY_WEB.bat"),
    ("CHAY_PIPELINE.bat", "CHAY_PIPELINE.bat"),

    # Output dataset cốt lõi
    ("bigdata_dataset/cleaned_players.parquet", "bigdata_dataset/cleaned_players.parquet"),
    ("bigdata_dataset/rf_model.joblib", "bigdata_dataset/rf_model.joblib"),
    ("bigdata_dataset/football_analytics.db", "bigdata_dataset/football_analytics.db"),
    ("bigdata_dataset/kmeans_results.parquet", "bigdata_dataset/kmeans_results.parquet"),
    ("bigdata_dataset/rf_predictions.parquet", "bigdata_dataset/rf_predictions.parquet"),
    ("bigdata_dataset/top15_players.parquet", "bigdata_dataset/top15_players.parquet"),
    ("bigdata_dataset/position_stats.parquet", "bigdata_dataset/position_stats.parquet"),
    ("bigdata_dataset/country_stats.parquet", "bigdata_dataset/country_stats.parquet"),
    ("bigdata_dataset/age_value_stats.parquet", "bigdata_dataset/age_value_stats.parquet"),
    ("bigdata_dataset/yearly_market_trends.parquet", "bigdata_dataset/yearly_market_trends.parquet"),
    ("bigdata_dataset/transfers_2020_2025.parquet", "bigdata_dataset/transfers_2020_2025.parquet"),

    # Các bảng CSV thực thể mẫu trong Data Lake
    ("bigdata_dataset/players.csv", "bigdata_dataset/players.csv"),
    ("bigdata_dataset/transfers.csv", "bigdata_dataset/transfers.csv"),
    ("bigdata_dataset/club_games.csv", "bigdata_dataset/club_games.csv"),
    ("bigdata_dataset/clubs.csv", "bigdata_dataset/clubs.csv"),
    ("bigdata_dataset/competitions.csv", "bigdata_dataset/competitions.csv"),
    ("bigdata_dataset/countries.csv", "bigdata_dataset/countries.csv"),
    ("bigdata_dataset/national_teams.csv", "bigdata_dataset/national_teams.csv"),
    ("bigdata_dataset/player_valuations.csv", "bigdata_dataset/player_valuations.csv"),
    ("bigdata_dataset/games.csv", "bigdata_dataset/games.csv"),
]

def create_zip():
    print(f"Bắt đầu đóng gói hồ sơ nộp bài vào: {ZIP_OUTPUT}")
    count = 0
    with zipfile.ZipFile(ZIP_OUTPUT, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
        for src, arc in INCLUDE_ITEMS:
            src_path = os.path.join(BASE_DIR, src)
            if os.path.exists(src_path):
                zipf.write(src_path, arc)
                count += 1
                size_kb = os.path.getsize(src_path) / 1024
                print(f" [+] Thêm: {arc} ({size_kb:.1f} KB)")
            else:
                print(f" [!] Cảnh báo không tìm thấy: {src_path}")
    
    zip_size_mb = os.path.getsize(ZIP_OUTPUT) / (1024 * 1024)
    print(f"\n[THÀNH CÔNG] Đã tạo gói nộp bài hoàn chỉnh: {ZIP_OUTPUT}")
    print(f"  * Tổng số tệp đóng gói: {count} tệp")
    print(f"  * Dung lượng gói ZIP: {zip_size_mb:.2f} MB")

if __name__ == "__main__":
    create_zip()
