# -*- coding: utf-8 -*-
"""
02_data_cleaning.py
====================
Pipeline tiền xử lý và làm sạch dữ liệu lớn bằng Apache Spark (PySpark).
- Tự động cấu hình Java 17 Temurin & JVM options tương thích Windows.
- Đọc dữ liệu từ HDFS / Local dataset vào PySpark DataFrame.
- Làm sạch Missing Values, tính tuổi cầu thủ (age), lọc Outlier.
- Xuất dữ liệu Parquet chuẩn hóa phục vụ các tầng phân tích và Machine Learning.
"""

import os
import sys

# Đồng bộ thư mục làm việc về Project Root
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR) if os.path.basename(_SCRIPT_DIR) == "Source_Code" else _SCRIPT_DIR
if os.path.exists(_PROJECT_ROOT):
    try:
        os.chdir(_PROJECT_ROOT)
    except Exception:
        pass

# 1. Cấu hình UTF-8 cho Windows Console chống lỗi UnicodeEncodeError
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# 2. Cấu hình Java 17 cho Apache Spark
java_17_paths = [
    r"C:\Program Files\Eclipse Adoptium\jdk-17.0.11.9-hotspot",
    r"C:\Program Files\Eclipse Adoptium\jre-17.0.19.10-hotspot"
]
for p in java_17_paths:
    if os.path.exists(p):
        os.environ["JAVA_HOME"] = p
        os.environ["PATH"] = os.path.join(p, "bin") + os.pathsep + os.environ.get("PATH", "")
        break

os.environ["_JAVA_OPTIONS"] = (
    "--add-opens=java.base/java.lang=ALL-UNNAMED "
    "--add-opens=java.base/java.lang.invoke=ALL-UNNAMED "
    "--add-opens=java.base/java.lang.reflect=ALL-UNNAMED "
    "--add-opens=java.base/java.io=ALL-UNNAMED "
    "--add-opens=java.base/java.net=ALL-UNNAMED "
    "--add-opens=java.base/java.nio=ALL-UNNAMED "
    "--add-opens=java.base/java.util=ALL-UNNAMED "
    "--add-opens=java.base/java.util.concurrent=ALL-UNNAMED "
    "--add-opens=java.base/sun.nio.ch=ALL-UNNAMED"
)

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit
import pandas as pd
import numpy as np

def run_cleaning():
    print("=" * 75)
    print(" [ETL PIPELINE] TIEN XU LY & LAM SACH DU LIEU CAU THU (APACHE SPARK)")
    print("=" * 75)

    # Khởi tạo Spark Session Local Cluster
    print("\n[STEP 1] Khoi tao Apache Spark Session...")
    spark = SparkSession.builder \
        .appName("Transfermarkt_Data_Cleaning") \
        .master("local[*]") \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    print("  * Spark Session da san sang (PySpark 4.2 / Java 17 Temurin).")

    # Kiểm tra nguồn dữ liệu
    local_path = "bigdata_dataset/players.csv"
    hdfs_url = "hdfs://localhost:9820/football_project/players.csv"
    data_source = local_path if os.path.exists(local_path) else hdfs_url
    print(f"\n[STEP 2] Nap du lieu vao PySpark DataFrame tu: {data_source}")

    df_spark = spark.read.option("header", "true").option("inferSchema", "true").csv(local_path)
    total_raw = df_spark.count()
    print(f"  * Tong so ban ghi tho: {total_raw:,} cau thu | {len(df_spark.columns)} thuoc tinh")
    print("\n[SCHEMA DU LIEU THO TU SPARK]")
    df_spark.printSchema()

    # 3. Làm sạch missing value và chuyển đổi đặc trưng
    print("\n[STEP 3] Xu ly Missing Values & Feature Engineering...")
    # Lọc bỏ cầu thủ thiếu định giá
    df_filtered = df_spark.filter(col("market_value_in_eur").isNotNull())
    after_mv = df_filtered.count()
    dropped_count = total_raw - after_mv
    print(f"  * Loai bo {dropped_count:,} ban ghi thieu market_value_in_eur")
    print(f"  * So luong ban ghi giu lai: {after_mv:,}")

    # Chuyển đổi sang pandas để trích xuất tuổi và lưu parquet an toàn trên Windows
    print("\n[STEP 4] Tinh toan dac trung Tuoi (age) va loc ngoai le (Outliers)...")
    pdf = df_filtered.toPandas()
    
    # Tính tuổi
    pdf["date_of_birth"] = pd.to_datetime(pdf["date_of_birth"], errors="coerce")
    pdf["age"] = ((pd.Timestamp.now() - pdf["date_of_birth"]).dt.days / 365.25).fillna(25).astype(int)

    # Điền thiếu chiều cao & chân thuận
    avg_height = int(pdf["height_in_cm"].mean()) if pdf["height_in_cm"].notna().any() else 180
    pdf["height_in_cm"] = pdf["height_in_cm"].fillna(avg_height).astype(int)
    pdf["foot"] = pdf["foot"].fillna("right")
    pdf["position"] = pdf["position"].fillna("Unknown")
    pdf["sub_position"] = pdf["sub_position"].fillna("Unknown")

    # Lọc ngoại lệ
    pdf = pdf[
        (pdf["market_value_in_eur"] > 0) &
        (pdf["age"].between(15, 45)) &
        (pdf["height_in_cm"].between(150, 220))
    ]
    total_clean = len(pdf)
    print(f"  * Du lieu sau khi loc ngoai le: {total_clean:,} cau thu")
    print(f"  * Ty le du lieu hop le: {(total_clean / total_raw * 100):.2f}%")

    # Loại bỏ các cột dư thừa
    cols_to_drop = [
        "first_name", "last_name", "player_code", "city_of_birth",
        "url", "image_url", "agent_name", "contract_expiration_date"
    ]
    pdf = pdf.drop(columns=[c for c in cols_to_drop if c in pdf.columns])

    # 4. Xuất Parquet
    out_parquet = "bigdata_dataset/cleaned_players.parquet"
    pdf.to_parquet(out_parquet, index=False)
    print(f"\n[STEP 5] Xuat tep Parquet chuan hoa: {out_parquet}")
    print(f"  * Kich thuoc tep Parquet: {os.path.getsize(out_parquet) / 1024 / 1024:.2f} MB")

    print("\n[5 DONG DU LIEU MAU SAU KHI LAM SACH]")
    cols_preview = ["name", "country_of_citizenship", "position", "foot", "height_in_cm", "age", "market_value_in_eur"]
    print(pdf[cols_preview].head(5).to_string(index=False))

    spark.stop()
    print("\n[HOAN THANH] Module 02_data_cleaning.py da thuc thi thanh cong 100%!")

if __name__ == "__main__":
    run_cleaning()
