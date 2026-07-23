import requests
import json
import time
import os
from datetime import datetime, timedelta

API_KEY = "MV0ZO9UE2NE"
BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tnemn/@public/api"
BOT_TOKEN = "8229683960:AAFoJqIMYkGElPNXBro7QrmPnFyd4NCjfpk"
CHAT_IDS = [
    "5579156849",
    "6235519694",
    "5950373551"
]

def get_bd_time():
    return datetime.now() + timedelta(hours=6)

def fetch_services():
    try:
        resp = requests.get(f"{BASE_URL}/liveaccess", headers={"mauthapi": API_KEY}, timeout=10)
        data = resp.json()
        if data.get('meta', {}).get('code') == 200:
            return data.get('data', {}).get('services', [])
        return []
    except:
        return []

def fetch_otps():
    try:
        resp = requests.get(f"{BASE_URL}/success-otp", headers={"mauthapi": API_KEY}, timeout=10)
        data = resp.json()
        if data.get('meta', {}).get('code') == 200:
            return data.get('data', {}).get('otps', [])
        return []
    except:
        return []

def format_message(services, otps):
    if not services:
        return "⚠️ No services found!"

    current_time = time.time() * 1000
    now = get_bd_time().strftime('%H:%M:%S')

    text = "📡 *LIVE SERVICE & OTP MONITOR*\n"
    text += "═" * 35 + "\n\n"
    text += f"⏱️ *Update:* `{now}` (BD Time)\n\n"

    total = len(services)
    active = sum(1 for s in services if (current_time - s.get('last_at', 0)) < 300000)

    text += f"📊 *STATS*\n"
    text += f"   • Services: `{total}`  |  Active: `{active}`\n"
    text += f"   • OTPs: `{len(otps)}`\n\n"
    text += "─" * 35 + "\n\n"

    text += "*📋 SERVICES & RANGES*\n\n"

    services_sorted = sorted(services, key=lambda x: (
        -1 if (current_time - x.get('last_at', 0)) < 300000 else 0,
        -x.get('last_at', 0)
    ))

    for svc in services_sorted[:15]:
        sid = svc.get('sid', 'Unknown')
        ranges = svc.get('ranges', [])
        last_at = svc.get('last_at', 0)

        is_active = (current_time - last_at) < 300000
        status = "🟢" if is_active else "🔴"

        if ranges:
            range_str = ', '.join(ranges)
        else:
            range_str = 'None'

        if last_at > 0:
            bd_time = datetime.utcfromtimestamp(last_at/1000) + timedelta(hours=6)
            time_str = bd_time.strftime('%H:%M:%S')
        else:
            time_str = 'N/A'

        text += f"{status} *{sid}*\n"
        text += f"   📞 `{range_str}`\n"
        text += f"   ⏱️ `{time_str}`\n\n"

    text += "─" * 35 + "\n"
    text += "🔥 *Developer: MAHFUJ CHOWDHURY*"

    return text

def send_telegram(text):
    success = True

    for chat_id in CHAT_IDS:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        try:
            resp = requests.post(url, json=data, timeout=10)
            if resp.status_code != 200:
                success = False
        except:
            success = False

    return success

def handler(request):
    services = fetch_services()
    otps = fetch_otps()

    if services:
        text = format_message(services, otps)
        send_telegram(text)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "services": len(services),
                "otps": len(otps)
            })
        }
    else:
        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": False,
                "message": "No services found"
            })
        }