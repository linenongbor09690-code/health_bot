"""
จำแนกระดับความเสี่ยงจากค่าความดันและน้ำตาลในเลือด
อ้างอิงเกณฑ์: แนวทางเวชปฏิบัติ กรมการแพทย์ / JNC8 / ADA
"""

from enum import Enum


class RiskLevel(Enum):
    GREEN = "🟢 ปกติ"
    YELLOW = "🟡 กลุ่มเสี่ยง"
    ORANGE = "🟠 ป่วย/คุมไม่ได้"
    RED = "🔴 วิกฤต"


def classify_risk(systolic: int, diastolic: int, glucose: int) -> RiskLevel:
    """
    จำแนกระดับความเสี่ยงจากความดันและน้ำตาล

    ความดัน (mmHg):
    ───────────────
    ปกติ        : < 130/80
    เสี่ยง      : 130-139 / 80-89
    ป่วย        : 140-179 / 90-109
    วิกฤต       : ≥ 180 / ≥ 110

    น้ำตาลในเลือด (mg/dL) — วัดหลังอดอาหาร:
    ──────────────────────────────────────────
    ปกติ        : < 100
    เสี่ยง (Pre): 100-125
    เบาหวาน     : 126-299
    วิกฤต       : ≥ 300
    """

    bp_level = classify_bp(systolic, diastolic)
    glucose_level = classify_glucose(glucose)

    # ใช้ระดับสูงสุดของทั้งสองค่า
    combined = max(bp_level, glucose_level, key=lambda x: x.order)
    return combined.risk


class _Level:
    def __init__(self, risk: RiskLevel, order: int):
        self.risk = risk
        self.order = order


def classify_bp(systolic: int, diastolic: int) -> _Level:
    # วิกฤต
    if systolic >= 180 or diastolic >= 110:
        return _Level(RiskLevel.RED, 3)

    # ป่วย / คุมไม่ได้
    if systolic >= 140 or diastolic >= 90:
        return _Level(RiskLevel.ORANGE, 2)

    # กลุ่มเสี่ยง (Pre-hypertension)
    if systolic >= 130 or diastolic >= 80:
        return _Level(RiskLevel.YELLOW, 1)

    # ปกติ
    return _Level(RiskLevel.GREEN, 0)


def classify_glucose(glucose: int) -> _Level:
    # วิกฤต (Hyperglycemic crisis)
    if glucose >= 300:
        return _Level(RiskLevel.RED, 3)

    # เบาหวาน / คุมไม่ได้
    if glucose >= 126:
        return _Level(RiskLevel.ORANGE, 2)

    # กลุ่มเสี่ยง (Pre-diabetes)
    if glucose >= 100:
        return _Level(RiskLevel.YELLOW, 1)

    # ปกติ
    return _Level(RiskLevel.GREEN, 0)


def get_bp_label(systolic: int, diastolic: int) -> str:
    level = classify_bp(systolic, diastolic)
    labels = {
        RiskLevel.GREEN: "ปกติ ✓",
        RiskLevel.YELLOW: "ค่อนข้างสูง ⚠️",
        RiskLevel.ORANGE: "สูง ต้องดูแล",
        RiskLevel.RED: "สูงวิกฤต 🚨",
    }
    return labels[level.risk]


def get_glucose_label(glucose: int) -> str:
    level = classify_glucose(glucose)
    labels = {
        RiskLevel.GREEN: "ปกติ ✓",
        RiskLevel.YELLOW: "ก่อนเบาหวาน ⚠️",
        RiskLevel.ORANGE: "เบาหวาน ต้องดูแล",
        RiskLevel.RED: "น้ำตาลวิกฤต 🚨",
    }
    return labels[level.risk]
