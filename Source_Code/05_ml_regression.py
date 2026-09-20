# -*- coding: utf-8 -*-
"""
05_ml_regression.py
====================
Mô hình học máy Random Forest Regressor dự đoán giá trị chuyển nhượng cầu thủ.
- Sử dụng biến đổi log1p để chuẩn hóa độ lệch của phân phối giá trị định giá.
- Đánh giá trên tập kiểm thử (Test 20%): R-squared (R²), RMSE, MAE.
- Đối chiếu giá trị thực tế vs giá trị dự đoán cho Top ngôi sao thế giới.
- Đầu ra: bigdata_dataset/rf_predictions.parquet
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
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

def run_regression():
    print("=" * 75)
    print(" [RANDOM FOREST REGRESSOR] DU DOAN GIA TRI CHUYEN NHUONG CAU THU")
    print("=" * 75)

    parquet_path = "bigdata_dataset/cleaned_players.parquet"
    if not os.path.exists(parquet_path):
        import importlib
        cleaner = importlib.import_module("02_data_cleaning")
        cleaner.run_cleaning()

    df = pd.read_parquet(parquet_path)
    print(f"\n[INFO] Du lieu huan luyen: {len(df):,} cau thu hop le")

    # Chuẩn bị biến đặc trưng (Features) và Biến mục tiêu (Target)
    feature_cols = ["highest_market_value_in_eur", "age", "height_in_cm"]
    X = df[feature_cols].fillna(0)
    y_raw = df["market_value_in_eur"]
    y_log = np.log1p(y_raw)

    # Phân chia 80% Train - 20% Test
    X_train, X_test, y_train, y_test = train_test_split(X, y_log, test_size=0.2, random_state=42)
    print(f"[INFO] Phan chia tap du lieu: Train = {len(X_train):,} dong | Test = {len(X_test):,} dong")

    print("[TRAINING] Dang huan luyen Random Forest Regressor (100 cay, max_depth=10)...")
    rf = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    print("[INFO] Huan luyen hoan thanh! Dang danh gia tren tap kiem thu...")

    # Dự đoán trên tập kiểm thử
    y_pred_log = rf.predict(X_test)
    r2 = r2_score(y_test, y_pred_log)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred_log))
    mae = mean_absolute_error(y_test, y_pred_log)

    print("\n" + "-" * 75)
    print("KET QUA DANH GIA MO HINH RANDOM FOREST REGRESSOR:")
    print("-" * 75)
    print(f"  * R2 (He so xac dinh R-squared)  : {r2:.4f}  ==> DO CHINH XAC DAT {r2 * 100:.2f}%")
    print(f"  * RMSE (Root Mean Squared Error) : {rmse:.4f}  (thang log1p)")
    print(f"  * MAE (Mean Absolute Error)      : {mae:.4f}")
    print("-" * 75)

    # Dự đoán trên toàn bộ tập dữ liệu để xuất kết quả so sánh
    y_all_pred_log = rf.predict(X)
    df["predicted_value_eur"] = np.expm1(y_all_pred_log).astype(int)

    print("\n[DOI CHIEU GIA TRI THUC TE vs DU DOAN - TOP 10 CAU THU MAU]")
    preview = df.sort_values("market_value_in_eur", ascending=False).head(10)[
        ["name", "position", "age", "market_value_in_eur", "predicted_value_eur"]
    ].copy()
    preview["market_value_in_eur"] = preview["market_value_in_eur"].apply(lambda x: f"EUR {x:,.0f}")
    preview["predicted_value_eur"] = preview["predicted_value_eur"].apply(lambda x: f"EUR {x:,.0f}")
    print(preview.to_string(index=False))

    # Lưu kết quả
    out_parquet = "bigdata_dataset/rf_predictions.parquet"
    out_cols = ["player_id", "name", "position", "age", "country_of_citizenship", "market_value_in_eur", "predicted_value_eur"]
    df[out_cols].to_parquet(out_parquet, index=False)
    print(f"\n[HOAN THANH] Da luu ket qua du doan ra Parquet: {out_parquet}")

if __name__ == "__main__":
    run_regression()
