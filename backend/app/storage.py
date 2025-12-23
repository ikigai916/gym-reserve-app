"""
データ永続化（JSONファイル操作）
"""
import json
import os
from typing import List, Dict, Optional
from datetime import datetime

# データファイルのパス
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
RESERVATIONS_FILE = os.path.join(DATA_DIR, "reservations.json")

def ensure_data_dir():
    """データディレクトリが存在しない場合は作成"""
    os.makedirs(DATA_DIR, exist_ok=True)

def load_users() -> List[Dict]:
    """ユーザーデータを読み込む"""
    ensure_data_dir()
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_users(users: List[Dict]):
    """ユーザーデータを保存"""
    ensure_data_dir()
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def load_reservations() -> List[Dict]:
    """予約データを読み込む"""
    ensure_data_dir()
    if os.path.exists(RESERVATIONS_FILE):
        try:
            with open(RESERVATIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_reservations(reservations: List[Dict]):
    """予約データを保存"""
    ensure_data_dir()
    with open(RESERVATIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(reservations, f, ensure_ascii=False, indent=2)

