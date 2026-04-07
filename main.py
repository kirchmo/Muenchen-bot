import requests
import os
from datetime import datetime
from dateutil import parser
import time

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ⚠️ Diese API stammt aus dem Netzwerk-Call der Terminseite
API_URL = "https://terminvereinbarung.muenchen.de/api/slots?serviceId=1063648&locationId=10470"

last_earliest = None


def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram not configured")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": message
    })


def fetch_earliest_date():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    response = requests.get(API_URL, headers=headers, timeout=10)

    if response.status_code != 200:
        print("API error:", response.status_code)
        return None

    data = response.json()

    dates = []

    # ⚠️ Struktur kann variieren → typische Felder:
    # data -> slots -> date / start / time etc.
    for slot in data.get("slots", []):
        date_str = slot.get("start") or slot.get("date")

        if date_str:
            try:
                dt = parser.parse(date_str)
                dates.append(dt)
            except:
                pass

    if not dates:
        return None

    return min(dates)


def check():
    global last_earliest

    earliest = fetch_earliest_date()

    if not earliest:
        print("Keine Termine gefunden")
        return

    print("Frühester Termin:", earliest)

    # Vergleich
    if last_earliest is None:
        last_earliest = earliest
        send_telegram(f"ℹ️ Aktuell frühester Termin: {earliest}")
        return

    if earliest < last_earliest:
        send_telegram(f"⚡ Früherer Termin verfügbar: {earliest}")
        last_earliest = earliest
    else:
        print("Keine Verbesserung")


if __name__ == "__main__":
    send_telegram("🤖 Termin-Bot gestartet")

    while True:
        print("Checking...")
        check()
        time.sleep(300)
