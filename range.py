import requests
import json
import time
import re
import os
from datetime import datetime

# ============================================
# 🔥 DEVELOPER: MAHFUJ CHOWDHURY
# ============================================

API_KEY = "MV0ZO9UE2NE"
BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tnemn/@public/api"
BOT_TOKEN = "8229683960:AAFoJqIMYkGElPNXBro7QrmPnFyd4NCjfpk"
CHAT_ID = "5579156849"

update_count = 0

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
    now = datetime.now().strftime('%H:%M:%S')
    
    text = "📡 *LIVE SERVICE & OTP MONITOR*\n"
    text += "═" * 35 + "\n\n"
    text += f"⏱️ *Update:* `{now}`\n\n"
    
    total = len(services)
    active = sum(1 for s in services if (current_time - s.get('last_at', 0)) < 300000)
    
    text += f"📊 *STATS*\n"
    text += f"   • Services: `{total}`  |  Active: `{active}`\n"
    text += f"   • OTPs: `{len(otps)}`\n\n"
    text += "─" * 35 + "\n\n"
    
    text += "*📋 SERVICES & RANGES*\n\n"
    for svc in services[:10]:
        sid = svc.get('sid', 'Unknown')
        ranges = svc.get('ranges', [])
        is_active = (current_time - svc.get('last_at', 0)) < 300000
        status = "🟢" if is_active else "🔴"
        range_str = ', '.join(ranges[:2]) if ranges else 'None'
        text += f"{status} *{sid}* → `{range_str}`\n"
    
    text += "\n" + "─" * 35 + "\n"
    text += "🔥 *Developer: MAHFUJ CHOWDHURY*"
    
    return text

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        resp = requests.post(url, json=data, timeout=10)
        return resp.status_code == 200
    except:
        return False

def main():
    global update_count
    print("🤖 Live Bot Started on Railway!")
    print("🔄 Auto-update every 30 seconds")
    
    while True:
        try:
            update_count += 1
            services = fetch_services()
            otps = fetch_otps()
            
            if services:
                text = format_message(services, otps)
                send_telegram(text)
                print(f"✅ Update #{update_count} sent")
            else:
                print("⚠️ No services found")
            
            time.sleep(30)
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
