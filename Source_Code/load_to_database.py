# -*- coding: utf-8 -*-
"""
load_to_database.py
===================
Module tải dữ liệu phân tích và kết quả học máy vào Cơ sở dữ liệu phục vụ báo cáo (Serving Database).
- Công nghệ: Relational Database (SQLite / PostgreSQL compatible)
- Tạo cấu trúc Data Mart gồm các bảng:
    1. dim_players              (Hồ sơ cầu thủ sạch, cụm K-Means và giá trị định giá dự đoán)
    2. fact_top15_players        (Bảng xếp hạng Top 15 cầu thủ giá trị nhất thế giới)
    3. fact_position_analytics   (Chỉ số phân tích tổng hợp theo 4 vị trí thi đấu)
    4. fact_country_analytics    (Chỉ số phân tích theo Top 10 quốc gia hàng đầu)
    5. fact_transfer_events      (Nhật ký sự kiện chuyển nhượng thu nhận từ Kafka)
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
import sqlite3
import pandas as pd
import json

# Cấu hình UTF-8 cho console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

DB_PATH = "bigdata_dataset/football_analytics.db"

def run_database_export():
    print("=" * 75)
    print(" [DATABASE SERVING LAYER] NAP DU LIEU VAO DATABASE DATA MART")
    print("=" * 75)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Nạp bảng dim_players từ kmeans và regression
    print("\n[STEP 1] Nap bang 'dim_players' (Ho so cau thu & ket qua ML)...")
    rf_path = "bigdata_dataset/rf_predictions.parquet"
    km_path = "bigdata_dataset/kmeans_results.parquet"
    if os.path.exists(rf_path) and os.path.exists(km_path):
        df_rf = pd.read_parquet(rf_path)
        df_km = pd.read_parquet(km_path)[["player_id", "prediction"]]
        df_players = pd.merge(df_rf, df_km, on="player_id", how="left")
        df_players.to_sql("dim_players", conn, if_exists="replace", index=False)
        print(f"  * Da nap {len(df_players):,} cau thu vao bang 'dim_players'.")

    # 2. Nạp bảng fact_top15_players
    print("\n[STEP 2] Nap bang 'fact_top15_players' (Top 15 sieu sao the gioi)...")
    top15_path = "bigdata_dataset/top15_players.parquet"
    if os.path.exists(top15_path):
        df_top15 = pd.read_parquet(top15_path)
        df_top15.to_sql("fact_top15_players", conn, if_exists="replace", index=False)
        print(f"  * Da nap {len(df_top15):,} ban ghi vao bang 'fact_top15_players'.")

    # 3. Nạp bảng fact_position_analytics
    print("\n[STEP 3] Nap bang 'fact_position_analytics' (Thong ke vi tri)...")
    pos_path = "bigdata_dataset/position_stats.parquet"
    if os.path.exists(pos_path):
        df_pos = pd.read_parquet(pos_path)
        df_pos.to_sql("fact_position_analytics", conn, if_exists="replace", index=False)
        print(f"  * Da nap {len(df_pos):,} vi tri vao bang 'fact_position_analytics'.")

    # 4. Nạp bảng fact_country_analytics
    print("\n[STEP 4] Nap bang 'fact_country_analytics' (Thong ke quoc gia)...")
    country_path = "bigdata_dataset/country_stats.parquet"
    if os.path.exists(country_path):
        df_country = pd.read_parquet(country_path)
        df_country.to_sql("fact_country_analytics", conn, if_exists="replace", index=False)
        print(f"  * Da nap {len(df_country):,} quoc gia vao bang 'fact_country_analytics'.")

    # 5. Nạp bảng fact_transfer_events từ log Kafka
    print("\n[STEP 5] Nap bang 'fact_transfer_events' (Luong giao dich tu Kafka)...")
    log_path = "kafka_transfers_stream.log"
    events = []
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except Exception:
                        pass
        if events:
            df_events = pd.DataFrame(events)
            df_events.to_sql("fact_transfer_events", conn, if_exists="replace", index=False)
            print(f"  * Da nap {len(df_events):,} su kien chuyen nhuong vao 'fact_transfer_events'.")

    conn.commit()

    # Truy vấn kiểm tra
    print("\n[KIEM TRA TRUY VAN SQL TRUC TIEP TREN DATABASE]")
    cursor.execute("SELECT name, market_value_in_eur, predicted_value_eur FROM dim_players ORDER BY market_value_in_eur DESC LIMIT 3")
    sample_rows = cursor.fetchall()
    for row in sample_rows:
        print(f"  * {row[0]}: Thuc te = EUR {row[1]:,}, Du doan = EUR {row[2]:,}")

    conn.close()
    print(f"\n[HOAN THANH] Co so du lieu Serving Database da san sang tai: {DB_PATH}")
    print(f"             Kich thuoc tep CSDL: {os.path.getsize(DB_PATH) / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    run_database_export()
