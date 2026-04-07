import requests
import os
from datetime import datetime
from dateutil import parser
import time

# ===== CONFIG =====

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

API_URL = "https://www48.muenchen.de/buergeransicht/api/citizen/available-days-by-office/?startDate=2026-04-07&endDate=2026-10-07&officeId=10470&serviceId=1063648&serviceCount=1"

last_earliest = None


# ===== TELEGRAM =====

def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram not configured")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": message
    })



# ===== API FETCH =====

def fetch_dates():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://stadt.muenchen.de/"
    }

    response = requests.get(API_URL, headers=headers, timeout=10)

    if response.status_code != 200:
        print("API error:", response.status_code)
        return []

    data = response.json()

    print("RAW API RESPONSE:", data)

    dates = []

    available_days = data.get("availableDays", [])

    for entry in available_days:
        date_str = entry.get("time")  # ✅ WICHTIG: "time"

        if date_str:
            try:
                dt = parser.parse(date_str)
                dates.append(dt)
            except Exception as e:
                print("Parse error:", e)

    return dates


# ===== LOGIC =====

def check():
    global last_earliest

    dates = fetch_dates()

    if not dates:
        print("Keine Termine gefunden")
        return

    earliest = min(dates)

    print("Frühester Termin:", earliest)

    if last_earliest is None:
        last_earliest = earliest
        send_telegram(f"ℹ️ Aktuell frühester Termin: {earliest}")
        return

    if earliest < last_earliest:
        send_telegram(f"⚡ Früherer Termin verfügbar: {earliest} Link https://stadt.muenchen.de/buergerservice/terminvereinbarung.html#/appointment/eyJpZCI6MTUyNTkxLCJhdXRoS2V5IjoiY2JmMyJ")
        last_earliest = earliest
    else:
        print("Keine Änderung")


# ===== MAIN LOOP =====

if __name__ == "__main__":
    send_telegram("🤖 Termin-Bot gestartet")

    while True:
        print("Checking...")
        check()
        time.sleep(120)  # alle 5 Minuten
