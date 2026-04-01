"""
Database Module — จัดเก็บข้อมูลสุขภาพและพิกัดผู้ใช้
เริ่มต้นด้วย JSON file (ง่ายและฟรี)
สามารถเปลี่ยนเป็น Firebase / Supabase / PostgreSQL ภายหลัง
"""

import json
import os
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

RECORDS_FILE = DATA_DIR / "health_records.json"
LOCATIONS_FILE = DATA_DIR / "locations.json"


# In-memory store (โหลดจาก disk ตอนเริ่ม)
db = {
    "records": _load_json(RECORDS_FILE, default=[]),
    "locations": _load_json(LOCATIONS_FILE, default={}),
}


def _load_json(path: Path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def _save_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


async def save_record(record: dict):
    """บันทึกผลการวัดสุขภาพ"""
    db["records"].append(record)
    _save_json(RECORDS_FILE, db["records"])


async def get_history(user_id: str, limit: int = 10) -> list:
    """ดึงประวัติการวัดของผู้ใช้ล่าสุด"""
    user_records = [r for r in db["records"] if r["user_id"] == user_id]
    return sorted(user_records, key=lambda x: x["timestamp"], reverse=True)[:limit]


async def get_all_records(date_from: str = None, date_to: str = None) -> list:
    """ดึงข้อมูลทั้งหมด — สำหรับ Dashboard เจ้าหน้าที่"""
    records = db["records"]
    if date_from:
        records = [r for r in records if r["timestamp"] >= date_from]
    if date_to:
        records = [r for r in records if r["timestamp"] <= date_to]
    return records


async def get_risk_summary() -> dict:
    """สรุปจำนวนตามระดับความเสี่ยง"""
    from collections import Counter
    levels = [r["risk_level"] for r in db["records"]]
    return dict(Counter(levels))
