# -*- coding: utf-8 -*-
"""
03_spark_analysis.py
====================
Phân tích thống kê đa chiều dữ liệu bóng đá bằng Apache Spark & Spark SQL.
- Sử dụng SparkSession và Spark SQL TempView để truy vấn trực tiếp trên DataFrame.
- Phân tích 5 góc độ chuyên sâu:
  1. Top 15 cầu thủ đắt giá nhất hành tinh
  2. Thống kê theo vị trí thi đấu (Forward, Midfield, Defender, Goalkeeper)
  3. Top 10 quốc gia sở hữu cầu thủ có định giá bình quân cao nhất
  4. Tương quan độ tuổi và giá trị chuyển nhượng
- Xuất các bảng chỉ số ra tệp Parquet phục vụ Streamlit Dashboard.
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

# 1. Cấu hình UTF-8 cho Windows Console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# 2. Cấu hình Java 17 Temurin cho Spark
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
import pandas as pd
import numpy as np

def run_analysis():
    print("=" * 75)
    print(" [SPARK SQL & STATS] PHAN TICH THONG KE DA CHIEU VOI APACHE SPARK")
    print("=" * 75)

    parquet_path = "bigdata_dataset/cleaned_players.parquet"
    if not os.path.exists(parquet_path):
        print(f"[CANH BAO] Chua tim thay {parquet_path}. Dang khoi chay 02_data_cleaning.py...")
        import importlib
        cleaner = importlib.import_module("02_data_cleaning")
        cleaner.run_cleaning()

    # Khởi tạo Spark Session
    print("\n[STEP 1] Khoi tao Apache Spark Session & Dang ky Spark SQL TempView...")
    spark = SparkSession.builder \
        .appName("Transfermarkt_Spark_SQL_Analysis") \
        .master("local[*]") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    # Đọc Parquet vào Spark DataFrame
    df_raw = pd.read_parquet(parquet_path)
    df_spark = spark.createDataFrame(df_raw)
    df_spark.createOrReplaceTempView("players")
    print(f"  * Da nap {df_spark.count():,} cau thu vao Spark SQL view 'players'.")

    # 1. TOP 15 CẦU THỦ CÓ GIÁ TRỊ CAO NHẤT THẾ GIỚI
    print("\n" + "-" * 75)
    print("TRUY VAN SPARK SQL 1: TOP 15 CAU THU CO GIA TRI CHUYEN NHUONG CAO NHAT")
    print("-" * 75)
    query_top15 = """
        SELECT player_id, name, country_of_citizenship, position, current_club_name, market_value_in_eur
        FROM players
        ORDER BY market_value_in_eur DESC
        LIMIT 15
    """
    top15_df = spark.sql(query_top15).toPandas()
    top15_df.to_parquet("bigdata_dataset/top15_players.parquet", index=False)
    print(top15_df.to_string(index=False))

    # 2. THỐNG KÊ THEO VỊ TRÍ THI ĐẤU
    print("\n" + "-" * 75)
    print("TRUY VAN SPARK SQL 2: GIA TRI TRUNG BINH & THE HINH THEO VI TRI THI DAU")
    print("-" * 75)
    query_pos = """
        SELECT 
            position,
            COUNT(player_id) AS so_luong_cau_thu,
            ROUND(AVG(market_value_in_eur), 1) AS gia_trung_binh_eur,
            MAX(market_value_in_eur) AS gia_cao_nhat_eur,
            ROUND(AVG(height_in_cm), 1) AS chieu_cao_tb_cm
        FROM players
        GROUP BY position
        ORDER BY gia_trung_binh_eur DESC
    """
    pos_stats = spark.sql(query_pos).toPandas()
    pos_stats.to_parquet("bigdata_dataset/position_stats.parquet", index=False)
    print(pos_stats.to_string(index=False))

    # 3. THỐNG KÊ THEO QUỐC GIA
    print("\n" + "-" * 75)
    print("TRUY VAN SPARK SQL 3: TOP 10 QUOC GIA CO GIA TRI BINH QUAN CAO NHAT (>= 50 cau thu)")
    print("-" * 75)
    query_country = """
        SELECT 
            country_of_citizenship,
            COUNT(player_id) AS so_cau_thu,
            ROUND(AVG(market_value_in_eur), 0) AS gia_trung_binh_eur,
            SUM(market_value_in_eur) AS tong_gia_tri_eur
        FROM players
        GROUP BY country_of_citizenship
        HAVING COUNT(player_id) >= 50
        ORDER BY gia_trung_binh_eur DESC
        LIMIT 10
    """
    country_stats = spark.sql(query_country).toPandas()
    country_stats.to_parquet("bigdata_dataset/country_stats.parquet", index=False)
    print(country_stats.to_string(index=False))

    # 4. TƯƠNG QUAN ĐỘ TUỔI VÀ GIÁ TRỊ
    print("\n" + "-" * 75)
    print("TRUY VAN SPARK SQL 4: BIEN DONG GIA TRI TRUNG BINH THEO DO TUOI (18 - 38)")
    print("-" * 75)
    query_age = """
        SELECT 
            age,
            COUNT(player_id) AS so_cau_thu,
            ROUND(AVG(market_value_in_eur), 0) AS gia_tb_eur
        FROM players
        WHERE age BETWEEN 18 AND 38
        GROUP BY age
        ORDER BY age ASC
    """
    age_stats = spark.sql(query_age).toPandas()
    age_stats.to_parquet("bigdata_dataset/age_value_stats.parquet", index=False)
    print(age_stats.head(10).to_string(index=False))
    print("  ... (hien thi 10 dong dau, tong cong", len(age_stats), "do tuoi)")

    spark.stop()
    print("\n[HOAN THANH] Toan bo ket qua Spark SQL da duoc luu ra Parquet thanh cong!")

if __name__ == "__main__":
    run_analysis()
