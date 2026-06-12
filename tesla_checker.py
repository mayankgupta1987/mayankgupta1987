import json
import os
import urllib.parse
import requests

POSTAL_CODES = [
    # New Brunswick
    "E7L 1B2",  # Florenceville-Bristol
    "E1A 2K3",  # Moncton
    "E3B 1B5",  # Fredericton
    "E2L 1E8",  # Saint John

    # Nova Scotia
    "B3M 1G5",  # Halifax
    "B2N 5A9",  # Truro
    "B1P 6J7",  # Sydney

    # PEI
    "C1A 4P3",  # Charlottetown
    "C1N 1B4",  # Summerside

    # Quebec
    "G1R 5M1",  # Quebec City
    "H3B 1A7",  # Montreal
    "J8X 2W3",  # Gatineau
    "J1H 5H3",  # Sherbrooke
    "G8Y 1T6",  # Trois-Rivières

    # Ontario
    "K1P 1J1",  # Ottawa
    "K7L 1A1",  # Kingston
    "M5V 2T6",  # Toronto
    "L8P 1A1",  # Hamilton
    "N6A 1A1",  # London
    "P3E 3E6",  # Sudbury
]



NTFY_TOPIC = "tesla-model3-premium-alert-himani"  # you can change this


def notify(message):
    requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=message.encode("utf-8"),
        headers={"Title": "Tesla Inventory Alert"}
    )


def check_postal_code(postal_code):
    tesla_url = (
        "https://www.tesla.com/en_CA/inventory/new/m3"
        f"?arrangeby=relevance&zip={urllib.parse.quote(postal_code)}&range=200"
    )

    print(f"Checking: {postal_code}")
    print(tesla_url)

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(tesla_url, headers=headers, timeout=30)

    page_text = response.text.lower()

    # Simple page-based check
    if "model 3" in page_text and ("premium" in page_text or "inventory" in page_text):
        message = f"""
🚗 Possible New Model 3 Premium inventory found

Search postal code: {postal_code}
Tesla link:
{tesla_url}

Please open the link and verify availability.
"""
        notify(message)
        print("Inventory alert sent.")
    else:
        print("No matching inventory found.")


def main():
    for postal_code in POSTAL_CODES:
        check_postal_code(postal_code)


if __name__ == "__main__":
    main()
