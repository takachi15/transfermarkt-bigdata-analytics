# -*- coding: utf-8 -*-
"""
07_kafka_consumer.py
======================
Kafka Consumer - Lắng nghe và thống kê luồng sự kiện chuyển nhượng cầu thủ thời gian thực.
Topic: football_transfers

Cơ chế thích ứng:
- Nếu Kafka Broker online (localhost:9092): kết nối và consume message trực tiếp từ cluster.
- Nếu Kafka Broker offline: tự động đọc và replay các sự kiện từ 'kafka_transfers_stream.log'
  được sinh ra bởi 06_kafka_producer.py, tổng hợp thống kê trực tiếp.
- Chống lỗi Unicode/Encoding tuyệt đối.
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
import json
import time
import socket
from collections import defaultdict

# Cấu hình UTF-8 cho console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

stats = {
    "total_events":    0,
    "total_fee_eur":   0,
    "clubs_involved":  set(),
    "players_seen":    set(),
    "by_type":         defaultdict(int),
    "top_fee":         {"player": "", "fee": 0},
}

def check_kafka_broker(host="localhost", port=9092, timeout=1.0):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def process_event(data: dict):
    stats["total_events"]  += 1
    stats["total_fee_eur"] += data.get("transfer_fee_eur", 0)
    if data.get("from_club"):
        stats["clubs_involved"].add(data.get("from_club"))
    if data.get("to_club"):
        stats["clubs_involved"].add(data.get("to_club"))
    if data.get("player_name"):
        stats["players_seen"].add(data.get("player_name"))
    stats["by_type"][data.get("transfer_type", "unknown")] += 1

    fee = data.get("transfer_fee_eur", 0)
    if fee > stats["top_fee"]["fee"]:
        stats["top_fee"] = {"player": data.get("player_name"), "fee": fee}

def print_live_stats():
    print("\n" + "=" * 70)
    print("       BANG THONG KE LUONG CHUYEN NHUONG THOI GIAN THUC")
    print("=" * 70)
    print(f"  * Tong so su kien da nhan:     {stats['total_events']}")
    print(f"  * Tong gia tri giao dich:      EUR {stats['total_fee_eur']:,}")
    print(f"  * So cau lac bo lien quan:     {len(stats['clubs_involved'])}")
    print(f"  * So cau thu xuat hien:        {len(stats['players_seen'])}")
    print(f"  * Thuong vu cao nhat:          {stats['top_fee']['player']} - EUR {stats['top_fee']['fee']:,}")
    print("  * Phan bo loai giao dich:")
    for t, cnt in sorted(stats["by_type"].items()):
        print(f"      - {t:22s}: {cnt} thuong vu")
    print("=" * 70 + "\n")

def run_consumer():
    print("=" * 75)
    print(" [KAFKA STREAMING CONSUMER] LANG NGHE & XU LY LUONG CHUYEN NHUONG")
    print("=" * 75)

    is_online = check_kafka_broker()
    topic = "football_transfers"
    log_file = "kafka_transfers_stream.log"

    if is_online:
        print(f"[STATUS] Ket noi toi Apache Kafka Broker (localhost:9092)...")
        print(f"         Topic dang lang nghe: '{topic}'")
        try:
            from kafka import KafkaConsumer
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=["localhost:9092"],
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                group_id="football_pipeline_group",
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                consumer_timeout_ms=10_000,
            )
            for msg in consumer:
                data = msg.value
                process_event(data)
                fee_str = f"EUR {data.get('transfer_fee_eur', 0):,}" if data.get('transfer_fee_eur', 0) > 0 else "Free Transfer"
                print(f"  [RECV] #{stats['total_events']:02d} | {data.get('player_name')} | {data.get('from_club')} -> {data.get('to_club')} ({fee_str})")
                if stats["total_events"] % 5 == 0:
                    print_live_stats()
            consumer.close()
        except Exception as e:
            print(f"[NOTE] Loi ket noi client Kafka: {e}. Chuyen sang doc log stream.")
            is_online = False

    if not is_online:
        print(f"[STATUS] Kafka Broker offline. Kich hoat che do doc Stream Log Simulator.")
        if not os.path.exists(log_file):
            print(f"[INFO] Chua co {log_file}. Khoi chay producer de tao luong du lieu...")
            import importlib
            prod = importlib.import_module("06_kafka_producer")
            prod.run_producer(num_events=10, delay_sec=0.1)

        print(f"\n[READING] Dang doc va phan tich luong su kien tu: {log_file}")
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    process_event(data)
                    fee_str = f"EUR {data.get('transfer_fee_eur', 0):,}" if data.get('transfer_fee_eur', 0) > 0 else "Free Transfer"
                    print(f"  [STREAM-EVENT] #{stats['total_events']:02d} | {data.get('player_name')} | {data.get('from_club')} -> {data.get('to_club')} ({fee_str})")
                except Exception:
                    pass

    print_live_stats()
    print("[HOAN THANH] Kafka Consumer da hoan tat phan tich luong du lieu!")

if __name__ == "__main__":
    run_consumer()
