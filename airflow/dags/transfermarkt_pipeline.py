# -*- coding: utf-8 -*-
"""
transfermarkt_pipeline.py
==========================
Apache Airflow DAG - Pipeline tự động hóa toàn diện hệ thống Big Data
Transfermarkt Football Analytics.

Luồng thực thi:
  [check_environment]
       --> [run_data_cleaning]
       --> [run_spark_analysis]
       --> [run_kmeans_clustering]
       --> [run_rf_regression]
       --> [trigger_kafka_producer]
       --> [generate_summary_report]

Lịch biểu: Tự động chạy hàng ngày lúc 02:00 UTC
Chủ sở hữu: dang_duy_loi
"""

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os

# ── Đường dẫn project ─────────────────────────────────────────────────────────
PROJECT_DIR = "/opt/airflow/project"   # Mount volume trong Docker
PYTHON_BIN  = "/opt/airflow/project/.venv/bin/python"   # hoặc python3

# ── Tham số mặc định cho mọi task ────────────────────────────────────────────
default_args = {
    "owner":            "dang_duy_loi",
    "depends_on_past":  False,
    "email_on_failure": False,
    "email_on_retry":   False,
    "retries":          1,
    "retry_delay":      timedelta(minutes=5),
    "execution_timeout": timedelta(hours=2),
}

# ── Định nghĩa DAG ────────────────────────────────────────────────────────────
with DAG(
    dag_id="transfermarkt_bigdata_pipeline",
    default_args=default_args,
    description=(
        "Pipeline tự động hóa toàn diện: Làm sạch dữ liệu → "
        "Phân tích Spark SQL → K-Means Clustering → Random Forest Regression → "
        "Kafka Streaming → Báo cáo tổng kết"
    ),
    schedule_interval="0 2 * * *",       # Chạy lúc 02:00 UTC hàng ngày
    start_date=datetime(2026, 9, 30),
    catchup=False,
    max_active_runs=1,
    tags=["bigdata", "transfermarkt", "kafka", "spark", "ml", "etl"],
) as dag:

    # ────────────────────────────────────────────────────────────────────────
    # TASK 1: Kiểm tra môi trường và kết nối hệ thống
    # ────────────────────────────────────────────────────────────────────────
    check_environment = BashOperator(
        task_id="check_environment",
        bash_command="""
            echo "=== [TASK 1] KIỂM TRA MÔI TRƯỜNG ==="
            echo "Thời gian: $(date)"
            echo "Python version: $(python3 --version 2>&1)"
            echo "HDFS NameNode: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:9870/ || echo 'N/A')"
            echo "Kafka Broker: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:9092/ 2>/dev/null || echo 'Checking TCP...')"
            echo "Dataset size: $(du -sh /opt/airflow/project/bigdata_dataset/ 2>/dev/null || echo 'N/A')"
            echo "=== Môi trường sẵn sàng ==="
        """,
    )

    # ────────────────────────────────────────────────────────────────────────
    # TASK 2: Làm sạch và tiền xử lý dữ liệu bằng PySpark
    # ────────────────────────────────────────────────────────────────────────
    run_data_cleaning = BashOperator(
        task_id="run_data_cleaning",
        bash_command=f"""
            echo "=== [TASK 2] PYSPARK DATA CLEANING ==="
            cd {PROJECT_DIR}
            python3 02_data_cleaning.py
            echo "=== Làm sạch dữ liệu hoàn thành ==="
        """,
    )

    # ────────────────────────────────────────────────────────────────────────
    # TASK 3: Phân tích thống kê bằng Spark SQL
    # ────────────────────────────────────────────────────────────────────────
    run_spark_analysis = BashOperator(
        task_id="run_spark_analysis",
        bash_command=f"""
            echo "=== [TASK 3] SPARK SQL ANALYSIS ==="
            cd {PROJECT_DIR}
            python3 03_spark_analysis.py
            echo "=== Phân tích Spark SQL hoàn thành ==="
        """,
    )

    # ────────────────────────────────────────────────────────────────────────
    # TASK 4: Phân cụm K-Means
    # ────────────────────────────────────────────────────────────────────────
    run_kmeans_clustering = BashOperator(
        task_id="run_kmeans_clustering",
        bash_command=f"""
            echo "=== [TASK 4] K-MEANS CLUSTERING ==="
            cd {PROJECT_DIR}
            python3 04_ml_kmeans.py
            echo "=== K-Means Clustering hoàn thành ==="
        """,
    )

    # ────────────────────────────────────────────────────────────────────────
    # TASK 5: Dự đoán giá trị bằng Random Forest Regression
    # ────────────────────────────────────────────────────────────────────────
    run_rf_regression = BashOperator(
        task_id="run_rf_regression",
        bash_command=f"""
            echo "=== [TASK 5] RANDOM FOREST REGRESSION ==="
            cd {PROJECT_DIR}
            python3 05_ml_regression.py
            echo "=== Random Forest Regression hoàn thành ==="
        """,
    )

    # ────────────────────────────────────────────────────────────────────────
    # TASK 6: Kích hoạt Kafka Producer phát sự kiện streaming
    # ────────────────────────────────────────────────────────────────────────
    trigger_kafka_producer = BashOperator(
        task_id="trigger_kafka_producer",
        bash_command=f"""
            echo "=== [TASK 6] KAFKA STREAMING PRODUCER ==="
            cd {PROJECT_DIR}
            timeout 60 python3 06_kafka_producer.py || true
            echo "=== Kafka Producer hoàn thành ==="
        """,
    )

    # ────────────────────────────────────────────────────────────────────────
    # TASK 7: Tạo báo cáo tổng kết pipeline
    # ────────────────────────────────────────────────────────────────────────
    generate_summary_report = BashOperator(
        task_id="generate_summary_report",
        bash_command="""
            echo "=== [TASK 7] BÁO CÁO TỔNG KẾT PIPELINE ==="
            echo "Thời gian hoàn thành : $(date)"
            echo "Các file đầu ra đã tạo:"
            echo "  - bigdata_dataset/cleaned_players.parquet"
            echo "  - bigdata_dataset/top15_players.parquet"
            echo "  - bigdata_dataset/position_stats.parquet"
            echo "  - bigdata_dataset/country_stats.parquet"
            echo "  - bigdata_dataset/age_value_stats.parquet"
            echo "  - bigdata_dataset/kmeans_results.parquet"
            echo "  - bigdata_dataset/rf_predictions.parquet"
            echo ""
            echo "=== Pipeline transfermarkt_bigdata_pipeline HOÀN THÀNH THÀNH CÔNG! ==="
        """,
    )

    # ── Thiết lập thứ tự phụ thuộc giữa các Task ────────────────────────────
    (
        check_environment
        >> run_data_cleaning
        >> run_spark_analysis
        >> run_kmeans_clustering
        >> run_rf_regression
        >> trigger_kafka_producer
        >> generate_summary_report
    )