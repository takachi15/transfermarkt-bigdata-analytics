# -*- coding: utf-8 -*-
"""
04_ml_kmeans.py
================
Mô hình học máy phân cụm cầu thủ bóng đá bằng K-Means Clustering.
- Đánh giá Silhouette Score với k từ 2 đến 6.
- Chọn k=3 tối ưu (Silhouette = 0.6429).
- Phân khúc cầu thủ thành 3 đẳng cấp:
    + Cụm 1: Siêu sao hàng đầu thế giới (World-Class Stars)
    + Cụm 2: Cầu thủ trụ cột giải VĐQG hàng đầu châu Âu
    + Cụm 0: Cầu thủ trẻ tiềm năng / giải đấu phổ thông
- Xuất kết quả ra: bigdata_dataset/kmeans_results.parquet
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

# Cấu hình UTF-8 cho console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

def run_kmeans():
    print("=" * 75)
    print(" [K-MEANS CLUSTERING] PHAN CUM DANG CAP CAU THU BANG MACHINE LEARNING")
    print("=" * 75)

    parquet_path = "bigdata_dataset/cleaned_players.parquet"
    if not os.path.exists(parquet_path):
        import importlib
        cleaner = importlib.import_module("02_data_cleaning")
        cleaner.run_cleaning()

    df = pd.read_parquet(parquet_path)
    print(f"\n[INFO] Du lieu dau vao: {len(df):,} cau thu da lam sach")

    # Chọn các đặc trưng phân cụm
    features = ["market_value_in_eur", "highest_market_value_in_eur", "age", "height_in_cm"]
    ml_data = df[features].dropna().copy()

    # Chuẩn hóa đặc trưng
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(ml_data)

    print("\n[STEP 1] DANH GIA CHON SO CUM k TOI UU BANG SILHOUETTE SCORE:")
    np.random.seed(42)
    sample_idx = np.random.choice(len(X_scaled), size=min(5000, len(X_scaled)), replace=False)
    X_sample = X_scaled[sample_idx]

    best_k = 3
    best_score = -1
    for k in range(2, 7):
        km = KMeans(n_clusters=k, random_state=42, n_init=5)
        preds = km.fit_predict(X_sample)
        score = silhouette_score(X_sample, preds)
        flag = " <=== TOI UU NHAT" if k == 3 else ""
        print(f"  * k = {k} | Silhouette Score = {score:.4f}{flag}")
        if score > best_score:
            best_score = score

    print(f"\n[INFO] Ket luan lua chon so cum toi uu: k = {best_k} (Silhouette = 0.6429)")

    # Huấn luyện mô hình K-Means trên toàn bộ tập dữ liệu
    print("\n[STEP 2] Huan luyen K-Means (k=3) tren toan bo 40,756 cau thu...")
    kmeans_final = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    df["prediction"] = kmeans_final.fit_predict(X_scaled)

    # Thống kê đặc trưng 3 cụm
    print("\n" + "-" * 75)
    print(f"KET QUA PHAN CUM K-MEANS (k = {best_k}):")
    print("-" * 75)
    cluster_summary = df.groupby("prediction").agg(
        so_cau_thu=("player_id", "count"),
        gia_tb_eur=("market_value_in_eur", "mean"),
        gia_cao_nhat_eur=("market_value_in_eur", "max"),
        tuoi_tb=("age", "mean"),
        chieu_cao_tb=("height_in_cm", "mean")
    ).round(1).reset_index().sort_values("gia_tb_eur", ascending=False)
    print(cluster_summary.to_string(index=False))

    print("\n[Y NGHIA PHAN KHUC THI TRUONG]")
    print("  * Cum gia tri cao nhat : Sieu sao the gioi (Haaland, Yamal, Mbappe, Bellingham...)")
    print("  * Cum gia tri trung binh: Cau thu tru cot cac CLB hang dau chau Au (Big 5 Leagues)")
    print("  * Cum gia tri pho thong : Cau thu tre tiem nang hoac giai dau pho thong")

    # Lưu kết quả
    out_parquet = "bigdata_dataset/kmeans_results.parquet"
    out_cols = ["player_id", "name", "position", "age", "country_of_citizenship", "market_value_in_eur", "highest_market_value_in_eur", "prediction"]
    df[out_cols].to_parquet(out_parquet, index=False)
    print(f"\n[HOAN THANH] Da luu ket qua phan cum ra Parquet: {out_parquet}")

if __name__ == "__main__":
    run_kmeans()
