"""
Line Flex Message Templates — 4 ระดับความเสี่ยง
ใช้ Bubble Container ของ Line Messaging API
"""

from classifier import get_bp_label, get_glucose_label

# ───────────────────────────────────────────────
# 🟢 ปกติ — ชื่นชม + คลิปออกกำลังกาย
# ───────────────────────────────────────────────
def build_green_message(sys: int, dia: int, glucose: int) -> list:
    bp_label = get_bp_label(sys, dia)
    gl_label = get_glucose_label(glucose)

    return [
        {
            "type": "flex",
            "altText": f"🟢 ผลวัดความดัน/น้ำตาล — ปกติ",
            "contents": {
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#E8F5E9",
                    "paddingAll": "16px",
                    "contents": [
                        {
                            "type": "text",
                            "text": "🟢 ผลการวัด — ปกติ",
                            "weight": "bold",
                            "size": "lg",
                            "color": "#1B5E20",
                        }
                    ],
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        _value_row("💓 ความดัน", f"{sys}/{dia} mmHg", bp_label, "#4CAF50"),
                        _value_row("🩸 น้ำตาล", f"{glucose} mg/dL", gl_label, "#4CAF50"),
                        {"type": "separator", "margin": "md"},
                        {
                            "type": "text",
                            "text": "ขอบคุณที่ดูแลสุขภาพอย่างสม่ำเสมอนะคะ 💪\nรักษาระดับนี้ต่อไปเลยค่ะ!",
                            "wrap": True,
                            "size": "sm",
                            "color": "#388E3C",
                            "margin": "md",
                        },
                    ],
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        _button("🎬 คลิปออกกำลังกาย 10 นาที", "https://youtube.com/shorts/", "#4CAF50"),
                        _button("📋 ดูประวัติของฉัน", "https://your-dashboard.com/history", "#81C784"),
                    ],
                },
            },
        }
    ]


# ───────────────────────────────────────────────
# 🟡 กลุ่มเสี่ยง — เมนู 2:1:1 + นัดคัดกรองซ้ำ
# ───────────────────────────────────────────────
def build_yellow_message(sys: int, dia: int, glucose: int) -> list:
    bp_label = get_bp_label(sys, dia)
    gl_label = get_glucose_label(glucose)

    return [
        {
            "type": "flex",
            "altText": f"🟡 ผลวัดความดัน/น้ำตาล — กลุ่มเสี่ยง",
            "contents": {
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#FFFDE7",
                    "paddingAll": "16px",
                    "contents": [
                        {
                            "type": "text",
                            "text": "🟡 กลุ่มเสี่ยง — ควรระวัง",
                            "weight": "bold",
                            "size": "lg",
                            "color": "#E65100",
                        }
                    ],
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        _value_row("💓 ความดัน", f"{sys}/{dia} mmHg", bp_label, "#FFA000"),
                        _value_row("🩸 น้ำตาล", f"{glucose} mg/dL", gl_label, "#FFA000"),
                        {"type": "separator", "margin": "md"},
                        {
                            "type": "text",
                            "text": "🍽️ สูตรจานอาหาร 2:1:1",
                            "weight": "bold",
                            "size": "sm",
                            "margin": "md",
                        },
                        {
                            "type": "text",
                            "text": "• 2 ส่วน: ผักใบเขียว\n• 1 ส่วน: โปรตีน (ปลา ไข่ เต้าหู้)\n• 1 ส่วน: ข้าว/แป้ง (ลดลง)",
                            "wrap": True,
                            "size": "sm",
                            "color": "#5D4037",
                        },
                        {
                            "type": "text",
                            "text": "⚠️ แนะนำให้คัดกรองซ้ำภายใน 1 เดือน",
                            "wrap": True,
                            "size": "sm",
                            "color": "#E65100",
                            "margin": "sm",
                        },
                    ],
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        _button("📅 นัดคัดกรองซ้ำ", "https://your-app.com/appointment", "#FFA000"),
                        _button("🥗 ดูเมนูอาหารสุขภาพ", "https://your-app.com/menu", "#FFCC02"),
                    ],
                },
            },
        }
    ]


# ───────────────────────────────────────────────
# 🟠 ป่วย/คุมไม่ได้ — เตือนพบหมอ + แจ้ง อสม.
# ───────────────────────────────────────────────
def build_orange_message(sys: int, dia: int, glucose: int) -> list:
    bp_label = get_bp_label(sys, dia)
    gl_label = get_glucose_label(glucose)

    return [
        {
            "type": "flex",
            "altText": f"🟠 ผลวัดความดัน/น้ำตาล — ต้องพบแพทย์",
            "contents": {
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#FFF3E0",
                    "paddingAll": "16px",
                    "contents": [
                        {
                            "type": "text",
                            "text": "🟠 ค่าสูงเกินเกณฑ์ — กรุณาพบแพทย์",
                            "weight": "bold",
                            "size": "md",
                            "color": "#BF360C",
                            "wrap": True,
                        }
                    ],
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        _value_row("💓 ความดัน", f"{sys}/{dia} mmHg", bp_label, "#E64A19"),
                        _value_row("🩸 น้ำตาล", f"{glucose} mg/dL", gl_label, "#E64A19"),
                        {"type": "separator", "margin": "md"},
                        {
                            "type": "text",
                            "text": "⚠️ ค่าของท่านอยู่ในระดับที่ต้องได้รับการดูแลจากแพทย์ค่ะ\n\nอสม. ในพื้นที่จะติดต่อท่านเพื่อนำส่ง รพ.สต.",
                            "wrap": True,
                            "size": "sm",
                            "color": "#BF360C",
                        },
                    ],
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        _button("🏥 ติดต่อ รพ.สต.", "tel:0XXXXXXXXX", "#E64A19"),
                        _button("📋 บันทึกอาการ", "https://your-app.com/symptoms", "#FF8A65"),
                    ],
                },
            },
        }
    ]


# ───────────────────────────────────────────────
# 🔴 วิกฤต — ส่งพิกัด + แจ้งด่วน
# ───────────────────────────────────────────────
def build_red_message(sys: int, dia: int, glucose: int) -> list:
    return [
        {
            "type": "flex",
            "altText": f"🚨 ฉุกเฉิน! ความดัน {sys}/{dia} น้ำตาล {glucose} — ต้องการความช่วยเหลือทันที",
            "contents": {
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#FFEBEE",
                    "paddingAll": "16px",
                    "contents": [
                        {
                            "type": "text",
                            "text": "🚨 ระดับวิกฤต — ต้องการความช่วยเหลือทันที!",
                            "weight": "bold",
                            "size": "md",
                            "color": "#B71C1C",
                            "wrap": True,
                        }
                    ],
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        _value_row("💓 ความดัน", f"{sys}/{dia} mmHg", "วิกฤต 🚨", "#D32F2F"),
                        _value_row("🩸 น้ำตาล", f"{glucose} mg/dL", "อันตราย 🚨", "#D32F2F"),
                        {"type": "separator", "margin": "md"},
                        {
                            "type": "text",
                            "text": "ระบบได้แจ้งเตือนไปยัง อสม. และเจ้าหน้าที่ รพ.สต. แล้วค่ะ\n\n📍 พิกัดบ้านของท่านถูกส่งไปให้ทีมช่วยเหลือแล้ว",
                            "wrap": True,
                            "size": "sm",
                            "color": "#B71C1C",
                        },
                    ],
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        _button("📞 โทร 1669 (ฉุกเฉิน)", "tel:1669", "#D32F2F"),
                        _button("📍 ส่งพิกัดปัจจุบัน", "https://line.me/R/nv/location/", "#EF5350"),
                    ],
                },
            },
        }
    ]


# ───────────────────────────────────────────────
# Helper functions
# ───────────────────────────────────────────────
def _value_row(label: str, value: str, status: str, color: str) -> dict:
    return {
        "type": "box",
        "layout": "horizontal",
        "contents": [
            {"type": "text", "text": label, "size": "sm", "color": "#666666", "flex": 3},
            {"type": "text", "text": value, "size": "sm", "weight": "bold", "flex": 3},
            {"type": "text", "text": status, "size": "xs", "color": color, "flex": 4, "align": "end"},
        ],
    }


def _button(label: str, url: str, color: str) -> dict:
    return {
        "type": "button",
        "action": {"type": "uri", "label": label, "uri": url},
        "style": "primary",
        "color": color,
        "height": "sm",
    }
