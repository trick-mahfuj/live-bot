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
    """Bangladesh Time (UTC+6)"""
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
    
    # ===== SERVICES WITH ALL RANGES (NO +N) =====
    text += "*📋 SERVICES & RANGES*\n\n"
    
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
        
        # ===== সব রেঞ্জ দেখাবে (কোনো +N থাকবে না) =====
        if ranges:
            # সব রেঞ্জ যোগ করুন
            range_str = ', '.join(ranges)
        else:
            range_str = 'None'
        
        # Time
        if last_at > 0:
            bd_time = datetime.utcfromtimestamp(last_at/1000) + timedelta(hours=6)
            time_str = bd_time.strftime('%H:%M:%S')
        else:
            time_str = 'N/A'
        
        # ===== SID + ALL RANGES + TIME =====
        text += f"{status} *{sid}*\n"
        text += f"   📞 `{range_str}`\n"
        text += f"   ⏱️ `{time_str}`\n\n"
    
    text += "─" * 35 + "\n"
    text += "🔥 *Developer: MAHFUJ CHOWDHURY*"
    
    return text

def send_telegram(text):
    """সব Chat ID-তে মেসেজ পাঠান + কপি বাটন"""
    success = True
    
    # কপি বাটন তৈরি
    reply_markup = json.dumps({
        "inline_keyboard": [
            [
                {"text": "📋 Copy Data", "callback_data": "copy"}
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
                print(f"❌ Failed to send to {chat_id}")
                success = False
            else:
                print(f"✅ Sent to {chat_id}")
        except Exception as e:
            print(f"❌ Error sending to {chat_id}: {e}")
            success = False
    
    return success

def main():
    global update_count
    print("🤖 Live Bot Started on Railway!")
    print(f"📱 Sending to {len(CHAT_IDS)} chat IDs")
    print("🔄 Auto-update every 30 seconds")
    print("🇧🇩 Timezone: Bangladesh (UTC+6)")
    print("📋 Copy button added")
    
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