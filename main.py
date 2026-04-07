import requests
import time

URL = "https://stadt.muenchen.de/buergerservice/terminvereinbarung.html#/services/1063648/locations/10470"

def check_page():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(URL, headers=headers, timeout=10)

    if response.status_code != 200:
        print("Fehler beim Laden:", response.status_code)
        return

    html = response.text

    # Simple Heuristik: suche nach Datumseinträgen im HTML
    # (je nach Seite ggf. anpassen)
    if "Termin" in html:
        print("Seite geladen - Inhalte vorhanden")

    # Beispiel: prüfe ob bestimmte Keywords fehlen
    if "Keine Termine" in html:
        print("Keine Termine verfügbar")
    else:
        print("⚡ Möglicherweise Termine verfügbar!")

if __name__ == "__main__":
    while True:
        print("Checking...")
        check_page()
        time.sleep(300)  # alle 5 Minuten
