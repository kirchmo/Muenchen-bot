import requests
import time
import os

URL = "https://stadt.muenchen.de/buergerservice/terminvereinbarung.html#/services/1063648/locations/10470"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

last_status = None

def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram not configured")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(url, json=payload)


def check_page():
    global last_status

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers, timeout=10)

    if response.status_code != 200:
        print("Fehler:", response.status_code)
        return

    html = response.text

    # Simple Heuristik
    if "Keine Termine" in html:
        status = "no_appointments"
    else:
        status = "appointments_possible"

    print("Status:", status)

    # Nur benachrichtigen wenn sich etwas ändert
    if status != last_status:
        if status == "appointments_possible":
            send_telegram("⚡ Möglicherweise neue Termine verfügbar!")
        else:
            send_telegram("❌ Keine Termine verfügbar")

        last_status = status


if __name__ == "__main__":
    send_telegram("🤖 Bot gestartet")

    while True:
        print("Checking...")
        check_page()
        time.sleep(300)
