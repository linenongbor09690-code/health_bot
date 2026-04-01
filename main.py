"""
ระบบติดตามความดัน/น้ำตาลในเลือด ผ่าน Line OA
Health Monitoring Webhook - FastAPI + Line Messaging API
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import re
import os
from datetime import datetime

from database import save_record, get_history, save_location, get_location, db
from classifier import classify_risk, RiskLevel
from line_messages import (
    build_green_message,
    build_yellow_message,
    build_orange_message,
    build_red_message,
)

app = FastAPI(title="NCDs Health Monitor", version="1.0.0")

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
LINE_REPLY_URL = "https://api.line.me/v2/bot/message/reply"
LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"

VOLUNTEER_GROUP_ID = os.getenv("VOLUNTEER_GROUP_ID", "")
STAFF_GROUP_ID = os.getenv("STAFF_GROUP_ID", "")


@app.get("/")
async def root():
    return {"status": "ok", "service": "NCDs Health Monitor"}


@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    for event in body.get("events", []):
        if event["type"] == "message":
            await handle_message(event)
    return JSONResponse(content={"status": "ok"})


async def handle_message(event: dict):
    msg_type = event["message"]["type"]
    reply_token = event["replyToken"]
    user_id = event["source"]["userId"]

    if msg_type == "text":
        text = event["message"]["text"].strip()
        await process_health_text(text, reply_token, user_id)

    elif msg_type == "image":
        await reply_message(reply_token, [{
            "type": "text",
            "text": "📷 ได้รับรูปภาพแล้วค่ะ\nกรุณาพิมพ์ค่าในรูปแบบ:\n\nความดัน/น้ำตาล\nตัวอย่าง: 125/82, 108"
        }])

    elif msg_type == "location":
        lat = event["message"]["latitude"]
        lng = event["message"]["longitude"]
        await save_location(user_id, lat, lng)
        await reply_message(reply_token, [{
            "type": "text",
            "text": f"📍 บันทึกพิกัดบ้านของท่านเรียบร้อยแล้วค่ะ\n({lat:.4f}, {lng:.4f})\nระบบจะใช้พิกัดนี้หากเกิดเหตุฉุกเฉิน"
        }])


async def process_health_text(text: str, reply_token: str, user_id: str):
    parsed = parse_health_values(text)

    if not parsed:
        await reply_message(reply_token, [{
            "type": "text",
            "text": (
                "สวัสดีค่ะ 😊 กรุณาส่งค่าในรูปแบบ:\n\n"
                "📌 ความดัน/น้ำตาล\n"
                "ตัวอย่าง: 125/82, 108\n\n"
                "หรือส่งพิกัดบ้านเพื่อบันทึกข้อมูลที่อยู่ค่ะ"
            )
        }])
        return

    systolic, diastolic, glucose = parsed
    risk = classify_risk(systolic, diastolic, glucose)

    record = {
        "user_id": user_id,
        "systolic": systolic,
        "diastolic": diastolic,
        "glucose": glucose,
        "risk_level": risk.value,
        "timestamp": datetime.now().isoformat(),
    }
    await save_record(record)

    if risk == RiskLevel.GREEN:
        messages = build_green_message(systolic, diastolic, glucose)
    elif risk == RiskLevel.YELLOW:
        messages = build_yellow_message(systolic, diastolic, glucose)
    elif risk == RiskLevel.ORANGE:
        messages = build_orange_message(systolic, diastolic, glucose)
        await notify_volunteer(user_id, systolic, diastolic, glucose, risk)
    elif risk == RiskLevel.RED:
        messages = build_red_message(systolic, diastolic, glucose)
        await notify_emergency(user_id, systolic, diastolic, glucose)

    await reply_message(reply_token, messages)


def parse_health_values(text: str):
    text = text.replace("，", ",").replace("／", "/")

    pattern1 = r"(\d{2,3})\s*/\s*(\d{2,3})\s*[,\s]\s*(\d{2,3})"
    m = re.search(pattern1, text)
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))

    pattern2 = r"(\d{2,3})\s+(\d{2,3})\s+(\d{2,3})"
    m = re.search(pattern2, text)
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))

    return None


async def reply_message(reply_token: str, messages: list):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
    }
    payload = {"replyToken": reply_token, "messages": messages}
    async with httpx.AsyncClient() as client:
        await client.post(LINE_REPLY_URL, headers=headers, json=payload)


async def push_message(to: str, messages: list):
    if not to:
        return
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
    }
    payload = {"to": to, "messages": messages}
    async with httpx.AsyncClient() as client:
        await client.post(LINE_PUSH_URL, headers=headers, json=payload)


async def notify_volunteer(user_id: str, sys: int, dia: int, glucose: int, risk):
    name = await get_user_name(user_id)
    text = (
        f"🟠 แจ้งเตือนจากระบบ NCDs\n"
        f"ผู้รับบริการ: {name}\n"
        f"ความดัน: {sys}/{dia} mmHg\n"
        f"น้ำตาล: {glucose} mg/dL\n"
        f"ระดับ: {risk.value}\n\n"
        f"กรุณาติดตามและนัดพบเจ้าหน้าที่ รพ.สต."
    )
    await push_message(VOLUNTEER_GROUP_ID, [{"type": "text", "text": text}])


async def notify_emergency(user_id: str, sys: int, dia: int, glucose: int):
    name = await get_user_name(user_id)
    location = await get_location(user_id)

    alert_text = (
        f"🚨 เหตุฉุกเฉิน! ระดับวิกฤต\n"
        f"ผู้รับบริการ: {name}\n"
        f"ความดัน: {sys}/{dia} mmHg\n"
        f"น้ำตาล: {glucose} mg/dL\n\n"
        f"กรุณาออกเยี่ยมทันที!"
    )

    messages = [{"type": "text", "text": alert_text}]

    if location:
        messages.append({
            "type": "location",
            "title": f"พิกัดบ้าน {name}",
            "address": "ที่อยู่ผู้รับบริการ",
            "latitude": location["lat"],
            "longitude": location["lng"],
        })

    await push_message(VOLUNTEER_GROUP_ID, messages)
    await push_message(STAFF_GROUP_ID, messages)


async def get_user_name(user_id: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://api.line.me/v2/bot/profile/{user_id}",
                headers={"Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"},
            )
            return resp.json().get("displayName", "ผู้ใช้งาน")
    except Exception:
        return "ผู้ใช้งาน"
