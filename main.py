import requests
import os
from datetime import datetime
from dateutil import parser
import time

# ===== CONFIG =====

API_URL = "https://www48.muenchen.de/buergeransicht/api/citizen/available-days-by-office/?startDate=2026-04-07&endDate=2026-10-07&officeId=10470&serviceId=1063648&serviceCount=1"

BOOKING_URL = "https://stadt.muenchen.de/buergerservice/terminvereinbarung.html#/services/1063648/locations/10470"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

TARGET_MONTH = 4
TARGET_YEAR = 2026

last_earliest = None


# ===== TELEGRAM =====

def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram not configured")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": message
        })
    except Exception as e:
        print("Telegram error:", e)


# ===== API =====

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

    dates = []

    for entry in data.get("availableDays", []):
        date_str = entry.get("time")

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

    # 🎯 Filter: nur April 2026
    april_dates = [
        d for d in dates
        if d.month == TARGET_MONTH and d.year == TARGET_YEAR
    ]

    if not april_dates:
        print("Keine Termine im April verfügbar")
        return

    earliest = min(april_dates)

    print("Frühester April-Termin:", earliest.date())

    if last_earliest is None:
        last_earliest = earliest
        send_telegram(
            f"ℹ️ Frühester April-Termin: {earliest.date()}\n\n👉 Jetzt buchen:\n{BOOKING_URL}"
        )
        return

    if earliest < last_earliest:
        send_telegram(
            f"⚡ Früherer April-Termin verfügbar: {earliest.date()}\n\n👉 Jetzt buchen:\n{BOOKING_URL}"
        )
        last_earliest = earliest
    else:
        print("Keine Verbesserung im April")


# ===== MAIN LOOP =====

if __name__ == "__main__":
    send_telegram("🤖 Termin-Bot gestartet")

    while True:
        print("Checking...")
        try:
            check()
        except Exception as e:
            print("Error:", e)

        time.sleep(60)  # alle 5 Minuten
