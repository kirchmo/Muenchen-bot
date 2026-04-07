import time
import re
from datetime import datetime
from playwright.sync_api import sync_playwright
import requests
import os

URL = "https://stadt.muenchen.de/buergerservice/terminvereinbarung.html#/services/1063648/locations/10470"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

def extract_earliest_date(html):
    matches = re.findall(r"\d{1,2}\.\d{1,2}\.\d{4}", html)
    dates = []
    for m in matches:
        try:
            dates.append(datetime.strptime(m, "%d.%m.%Y"))
        except:
            pass
    return min(dates) if dates else None

def check():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(5000)

        content = page.content()

        if "Keine Termine verfügbar" in content:
            browser.close()
            return None

        earliest = extract_earliest_date(content)
        browser.close()
        return earliest

last_found = None

while True:
    try:
        result = check()

        if result:
            if last_found is None or result < last_found:
                send_telegram(f"🎉 Neuer Termin: {result.strftime('%d.%m.%Y')}")
                last_found = result

        time.sleep(60)

    except Exception as e:
        print("Error:", e)
        time.sleep(120)
