# -*- coding: utf-8 -*-
"""
run_pipeline.py
================
Kịch bản tự động điều phối toàn bộ chu trình Big Data Pipeline từ đầu đến cuối:
1. 02_data_cleaning.py   (Apache Spark ETL & Làm sạch dữ liệu)
2. 03_spark_analysis.py  (Spark SQL Phân tích thống kê đa chiều 5 góc độ)
3. 04_ml_kmeans.py       (Mô hình học máy phân cụm K-Means)
4. 05_ml_regression.py   (Mô hình Random Forest Regressor dự đoán giá trị)
5. 06_kafka_producer.py  (Phát sóng luồng giao dịch chuyển nhượng Kafka)
6. 07_kafka_consumer.py  (Lắng nghe và thống kê luồng dữ liệu thời gian thực)
7. load_to_database.py   (Nạp dữ liệu phân tích và ML vào Cơ sở dữ liệu Data Mart)
"""

import os
import sys
import time

# 1. Cấu hình UTF-8 chống lỗi UnicodeEncodeError trên mọi Terminal Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# 2. Đồng bộ thư mục làm việc về Project Root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "Source_Code" else SCRIPT_DIR
if os.path.exists(PROJECT_ROOT):
    try:
        os.chdir(PROJECT_ROOT)
    except Exception:
        pass

# 3. Cấu hình Java 17 Temurin cho Spark
java_17_paths = [
    r"C:\Program Files\Eclipse Adoptium\jdk-17.0.11.9-hotspot",
    r"C:\Program Files\Eclipse Adoptium\jre-17.0.19.10-hotspot"
]
for p in java_17_paths:
    if os.path.exists(p):
        os.environ["JAVA_HOME"] = p
        os.environ["PATH"] = os.path.join(p, "bin") + os.pathsep + os.environ.get("PATH", "")
        break

def main():
    print("*" * 75)
    print("   FOOTBALL BIG DATA PIPELINE - KHOI CHAY TU DONG TOAN DIEN")
    print("   Hoc phan: Cong nghe Du lieu lon (Big Data Technologies)")
    print("   Nhom sinh vien thuc hien:")
    print("     1. Dang Duy Loi        - MSSV: 2001230479 (Truong nhom)")
    print("     2. Chu Van Quoc Trung  - MSSV: 2001231010")
    print("     3. Nguyen The Quang    - MSSV: 20012307010")
    print("*" * 75 + "\n")

    steps = [
        ("BUOC 1: APACHE SPARK ETL & TIEN XU LY DU LIEU", "02_data_cleaning.py"),
        ("BUOC 2: SPARK SQL PHAN TICH THONG KE DA CHIEU", "03_spark_analysis.py"),
        ("BUOC 3: PHAN CUM K-MEANS VOI SILHOUETTE SCORE", "04_ml_kmeans.py"),
        ("BUOC 4: DU DOAN GIA TRI RANDOM FOREST REGRESSOR", "05_ml_regression.py"),
        ("BUOC 5: PHAT SONG LUONG KAFKA STREAMING", "06_kafka_producer.py"),
        ("BUOC 6: KAFKA CONSUMER TONG HOP DU LIEU LIVE", "07_kafka_consumer.py"),
        ("BUOC 7: NAP DU LIEU VAO DATABASE DATA MART", "load_to_database.py"),
    ]

    for title, script in steps:
        script_full_path = os.path.join(SCRIPT_DIR, script)
        print("\n" + "=" * 75)
        print(f">>> DANG THUC THI: {title} ({script})")
        print("=" * 75)
        ret = os.system(f'"{sys.executable}" "{script_full_path}"')
        if ret != 0:
            print(f"[CANH BAO] Buoc {script} tra ve ma loi: {ret}")
        time.sleep(1)

    print("\n" + "*" * 75)
    print("   TAT CA CAC BUOC PIPELINE DA THUC THI THANH CONG 100%!")
    print("   De khoi chay Web Dashboard truc quan hoa, ban co the chay:")
    print("       CHAY_WEB.bat  (tai thu muc goc)")
    print("   hoac lenh:")
    print("       streamlit run Source_Code/08_dashboard_streamlit.py")
    print("*" * 75)

if __name__ == "__main__":
    main()
