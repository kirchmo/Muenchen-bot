import time
import re
from datetime import datetime
import os
import requests
from playwright.sync_api import sync_playwright

# 🔗 Zielseite
URL = "https://stadt.muenchen.de/buergerservice/terminvereinbarung.html#/services/1063648/locations/10470"

# 🔔 Telegram (über Railway Variables setzen)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram not configured")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": message})
    except Exception as e:
        print("Telegram error:", e)


def extract_earliest_date(html):
    matches = re.findall(r"\d{1,2}\.\d{1,2}\.\d{4}", html)

    dates = []
    for m in matches:
        try:
            dates.append(datetime.strptime(m, "%d.%m.%Y"))
        except:
            pass

    return min(dates) if dates else None


def check_site():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        page = browser.new_page()
        page.goto(URL, timeout=60000)

        # warten bis JS geladen ist
        page.wait_for_timeout(5000)

        content = page.content()

        browser.close()

        # keine Termine vorhanden
        if "Keine Termine verfügbar" in content:
            return None

        return extract_earliest_date(content)


last_found = None

while True:
    try:
        print("Checking...")

        result = check_site()

        if result:
            print("Earliest found:", result)

            if last_found is None or result < last_found:
                msg = f"🎉 Neuer früher Termin gefunden: {result.strftime('%d.%m.%Y')}"
                print(msg)
                send_telegram(msg)
                last_found = result
        else:
            print("No appointments")

        time.sleep(60)

    except Exception as e:
        print("Error:", e)
        time.sleep(120)
