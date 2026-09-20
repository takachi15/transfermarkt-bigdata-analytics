# -*- coding: utf-8 -*-
"""
06_kafka_producer.py
======================
Kafka Producer - Phát sóng sự kiện giao dịch chuyển nhượng cầu thủ thời gian thực.
Topic: football_transfers

Cơ chế thích ứng:
- Nếu Kafka Broker online (localhost:9092): gửi bản tin JSON trực tiếp vào cluster.
- Nếu Kafka Broker offline: tự động chuyển sang chế độ Stream Simulation,
  vừa hiển thị trên console vừa ghi vào tệp log 'kafka_transfers_stream.log'.
- Chống lỗi Unicode/Encoding tuyệt đối trên mọi môi trường Windows/Linux.
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
import random
import datetime
import socket

# Cấu hình UTF-8 cho console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

PLAYERS = [
    {"name": "Kylian Mbappe",         "position": "Attack",   "nationality": "France"},
    {"name": "Erling Haaland",        "position": "Attack",   "nationality": "Norway"},
    {"name": "Jude Bellingham",       "position": "Midfield", "nationality": "England"},
    {"name": "Vinicius Junior",       "position": "Attack",   "nationality": "Brazil"},
    {"name": "Phil Foden",            "position": "Midfield", "nationality": "England"},
    {"name": "Lamine Yamal",          "position": "Attack",   "nationality": "Spain"},
    {"name": "Pedri",                 "position": "Midfield", "nationality": "Spain"},
    {"name": "Florian Wirtz",         "position": "Midfield", "nationality": "Germany"},
    {"name": "Khvicha Kvaratskhelia", "position": "Attack",   "nationality": "Georgia"},
    {"name": "Bukayo Saka",           "position": "Attack",   "nationality": "England"},
    {"name": "Michael Olise",         "position": "Attack",   "nationality": "France"},
    {"name": "Cole Palmer",           "position": "Midfield", "nationality": "England"},
]

CLUBS = [
    "Real Madrid CF", "FC Barcelona", "Manchester City FC",
    "Arsenal FC", "Bayern Munich", "Paris Saint-Germain FC",
    "Liverpool FC", "Chelsea FC", "Borussia Dortmund", "Inter Milan"
]

TRANSFER_TYPES = ["permanent", "loan", "free_transfer"]

def check_kafka_broker(host="localhost", port=9092, timeout=1.0):
    """Kiểm tra cổng Kafka Broker có đang mở không."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def generate_event(idx):
    p = random.choice(PLAYERS)
    c1 = random.choice(CLUBS)
    c2 = random.choice([c for c in CLUBS if c != c1])
    fee = random.choice([0, random.randint(15, 60) * 1_000_000, random.randint(60, 180) * 1_000_000])
    return {
        "event_id": f"TRF-{int(time.time())}-{1000 + idx}",
        "player_name": p["name"],
        "player_position": p["position"],
        "player_nationality": p["nationality"],
        "from_club": c1,
        "to_club": c2,
        "transfer_fee_eur": fee,
        "transfer_type": "free_transfer" if fee == 0 else random.choice(["permanent", "loan"]),
        "timestamp": int(time.time()),
        "datetime_utc": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }

def run_producer(num_events=15, delay_sec=0.3):
    print("=" * 75)
    print(" [KAFKA STREAMING PRODUCER] PHAT SONG SU KIEN CHUYEN NHUONG THOI GIAN THUC")
    print("=" * 75)

    is_online = check_kafka_broker()
    topic = "football_transfers"
    log_file = "kafka_transfers_stream.log"

    producer = None
    if is_online:
        try:
            from kafka import KafkaProducer
            producer = KafkaProducer(
                bootstrap_servers=["localhost:9092"],
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                acks="all"
            )
            print(f"[STATUS] Da ket noi truc tiep toi Apache Kafka Broker (localhost:9092)")
            print(f"         Topic phat song: '{topic}'")
        except Exception as e:
            print(f"[NOTE] Khong the nap kafka-python client: {e}. Chuyen sang Stream Simulation.")
            is_online = False
    else:
        print(f"[STATUS] Kafka Broker (localhost:9092) khong online.")
        print(f"         -> Tu dong kich hoat che do 'Local Stream Simulation & Log Recorder'")
        print(f"         -> Su kien se duoc ghi truc tiep vao: {log_file}")

    print(f"\n[STREAMING] Bat dau phat song {num_events} su kien chuyen nhuong:")
    print("-" * 75)

    with open(log_file, "a", encoding="utf-8") as f_log:
        for i in range(1, num_events + 1):
            event = generate_event(i)
            event_json = json.dumps(event, ensure_ascii=False)

            if is_online and producer is not None:
                producer.send(topic, value=event)
                mode_tag = "[KAFKA BROKER]"
            else:
                mode_tag = "[STREAM LOG]"

            f_log.write(event_json + "\n")
            f_log.flush()

            fee_str = f"EUR {event['transfer_fee_eur']:,}" if event['transfer_fee_eur'] > 0 else "Free Transfer"
            print(f" {mode_tag} Event #{i:02d} | {event['datetime_utc']}")
            print(f"   * Cau thu: {event['player_name']} ({event['player_nationality']}) - {event['player_position']}")
            print(f"   * Thuong vu: {event['from_club']} -> {event['to_club']}")
            print(f"   * Phi chuyen nhuong: {fee_str} | Loai: {event['transfer_type']}")
            print("-" * 75)

            time.sleep(delay_sec)

    if producer:
        producer.flush()
        producer.close()

    print(f"\n[HOAN THANH] Phat song thanh cong {num_events} su kien chuyen nhuong!")
    print(f"             Tep nhat ky streaming da san sang tai: {log_file}")

if __name__ == "__main__":
    run_producer()
