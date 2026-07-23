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
    
    # ===== SERVICES WITH SERIAL + SORTED RANGES =====
    text += "*📋 SERVICES & RANGES*\n\n"
    
    # Active first, then by time
    services_sorted = sorted(services, 
        key=lambda x: (
            -1 if (current_time - x.get('last_at', 0)) < 300000 else 0,
            -x.get('last_at', 0)
        )
    )
    
    serial = 1
    for svc in services_sorted:
        sid = svc.get('sid', 'Unknown')
        ranges = svc.get('ranges', [])
        last_at = svc.get('last_at', 0)
        
        is_active = (current_time - last_at) < 300000
        status = "🟢" if is_active else "🔴"
        
        # ===== SORTED RANGES (আলফাবেটিক্যালি সাজানো) =====
        if ranges:
            # রেঞ্জ গুলো সাজান
            sorted_ranges = sorted(ranges, key=lambda x: (len(x), x))
            range_str = ', '.join(sorted_ranges)
        else:
            range_str = 'None'
        
        # Time
        if last_at > 0:
            bd_time = datetime.utcfromtimestamp(last_at/1000) + timedelta(hours=6)
            time_str = bd_time.strftime('%H:%M:%S')
        else:
            time_str = 'N/A'
        
        # ===== SERIAL + SID + SORTED RANGES + TIME =====
        text += f"*{serial}.* {status} *{sid}*\n"
        text += f"   📞 `{range_str}`\n"
        text += f"   ⏱️ `{time_str}`\n\n"
        serial += 1
    
    text += "─" * 35 + "\n"
    text += "🔥 *Developer: MAHFUJ CHOWDHURY*"
    
    return text

def send_telegram(text):
    """সব Chat ID-তে মেসেজ পাঠান + কপি বাটন"""
    success = True
    
    # কপি বাটন (সঠিক Callback Data সহ)
    reply_markup = json.dumps({
        "inline_keyboard": [
            [
                {"text": "📋 Copy All", "callback_data": "copy_all"}
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

def handle_callback():
    """কপি বাটনের Callback হ্যান্ডেল করুন"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        if data['ok'] and data['result']:
            for update in data['result']:
                if 'callback_query' in update:
                    callback = update['callback_query']
                    callback_id = callback['id']
                    message = callback['message']
                    chat_id = message['chat']['id']
                    
                    # Answer callback
                    answer_url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
                    answer_data = {
                        "callback_query_id": callback_id,
                        "text": "📋 Data copied to clipboard!",
                        "show_alert": False
                    }
                    requests.post(answer_url, json=answer_data)
                    
                    # Copy মেসেজ পাঠান
                    copy_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                    copy_data = {
                        "chat_id": chat_id,
                        "text": f"📋 *Copy this data:*\n\n```\n{message['text']}\n```",
                        "parse_mode": "Markdown"
                    }
                    requests.post(copy_url, json=copy_data)
    except:
        pass

def main():
    global update_count
    print("🤖 Live Bot Started on Railway!")
    print(f"📱 Sending to {len(CHAT_IDS)} chat IDs")
    print("🔄 Auto-update every 30 seconds")
    print("🇧🇩 Timezone: Bangladesh (UTC+6)")
    print("📋 Copy button with callback")
    
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
            
            # Callback handle
            handle_callback()
            
            time.sleep(30)
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()