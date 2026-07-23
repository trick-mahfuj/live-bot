import requests
import json
import time
import re
import os
from datetime import datetime, timedelta

# ============================================
# 🔥 DEVELOPER: MAHFUJ CHOWDHURY
# ============================================

API_KEY = "MV0ZO9UE2NE"
BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tnemn/@public/api"
BOT_TOKEN = "8229683960:AAFoJqIMYkGElPNXBro7QrmPnFyd4NCjfpk"

# ✅ একাধিক Chat ID
CHAT_IDS = [
    "5579156849",
    "6235519694",
    "5950373551"
]

update_count = 0

# ============================================
# 🇧🇩 BANGLADESH TIME (UTC+6)
# ============================================
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
    
    # ===== MNIT NETWORK SERVICES & RANGES =====
    text += "*📋 MNIT NETWORK SERVICES & RANGES*\n\n"
    
    services_sorted = sorted(services, 
        key=lambda x: (
            -1 if (current_time - x.get('last_at', 0)) < 300000 else 0,
            -x.get('last_at', 0)
        )
    )
    
    for svc in services_sorted[:15]:
        sid = svc.get('sid', 'Unknown')
        ranges = svc.get('ranges', [])
        last_at = svc.get('last_at', 0)
        
        is_active = (current_time - last_at) < 300000
        status = "🟢" if is_active else "🔴"
        
        # Time
        if last_at > 0:
            bd_time = datetime.utcfromtimestamp(last_at/1000) + timedelta(hours=6)
            time_str = bd_time.strftime('%H:%M:%S')
        else:
            time_str = 'N/A'
        
        # ===== SID হেডার =====
        text += f"*{status} {sid}*\n"
        
        # ===== RANGE গুলো (প্রতি লাইনে ৪টি) =====
        if ranges:
            for i in range(0, len(ranges), 4):
                chunk = ranges[i:i+4]
                # প্রতিটি রেঞ্জ আলাদা কপি লিংক হিসেবে
                range_links = []
                for r in chunk:
                    # প্রতিটি রেঞ্জের জন্য আলাদা কপি লিংক
                    range_links.append(f"[`{r}`](https://t.me/share/url?url={r})")
                text += f"   {', '.join(range_links)}\n"
        else:
            text += "   None\n"
        
        # ===== সময় =====
        text += f"   ⏱️ {time_str}\n\n"
    
    text += "─" * 35 + "\n"
    text += "🔥 *Developer: MAHFUJ CHOWDHURY*"
    
    return text

def send_telegram(text):
    success = True
    
    # ===== COPY BUTTON (সব ডাটা কপি) =====
    reply_markup = json.dumps({
        "inline_keyboard": [
            [
                {"text": "📋 Copy All Data", "callback_data": "copy_all"}
            ]
        ]
    })
    
    for chat_id in CHAT_IDS:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
            "reply_markup": reply_markup
        }
        try:
            resp = requests.post(url, json=data, timeout=10)
            if resp.status_code != 200:
                success = False
        except:
            success = False
    
    return success

def main():
    global update_count
    print("🤖 Live Bot Started on Railway!")
    print(f"📱 Sending to {len(CHAT_IDS)} chat IDs")
    print("🔄 Auto-update every 30 seconds")
    print("🇧🇩 Timezone: Bangladesh (UTC+6)")
    
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