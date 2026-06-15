import json
import urllib.parse
import requests

POSTAL_CODES = [
    "E7L 2T3",
    "E7L 1B2", "E1A 2K3", "E3B 1B5", "E2L 1E8",
    "B3M 1G5", "B2N 5A9", "B1P 6J7",
    "C1A 4P3", "C1N 1B4",
    "G1R 5M1", "H3B 1A7", "J8X 2W3", "J1H 5H3", "G8Y 1T6",
    "K1P 1J1", "K7L 1A1", "M5V 2T6", "L8P 1A1", "N6A 1A1", "P3E 3E6",
]

NTFY_TOPIC = "tesla-model3-premium-alert-himani"


def notify(message):
    requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=message.encode("utf-8"),
        headers={"Title": "Tesla Model 3 Inventory Alert"},
        timeout=20
    )


def build_web_url(postal_code, condition):
    zip_encoded = urllib.parse.quote(postal_code)

    if condition == "new":
        return (
            f"https://www.tesla.com/en_CA/inventory/new/m3"
            f"?arrangeby=plh&zip={zip_encoded}&PaymentType=cash"
        )

    return (
        f"https://www.tesla.com/en_CA/inventory/used/m3"
        f"?arrangeby=plh&zip={zip_encoded}"
    )


def build_api_url(postal_code, condition):
    query = {
        "query": {
            "model": "m3",
            "condition": condition,
            "arrangeby": "Price",
            "order": "asc",
            "market": "CA",
            "language": "en",
            "super_region": "north america",
            "zip": postal_code
        },
        "offset": 0,
        "count": 50,
        "outsideOffset": 0,
        "outsideSearch": False
    }

    encoded = urllib.parse.quote(json.dumps(query))
    return f"https://www.tesla.com/inventory/api/v1/inventory-results?query={encoded}"


def check_inventory(postal_code, condition):
    api_url = build_api_url(postal_code, condition)
    web_url = build_web_url(postal_code, condition)

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": web_url,
    }

    print(f"Checking {condition.upper()} near {postal_code}")

    try:
        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error checking {postal_code} {condition}: {e}")
        return 0, web_url

    cars = data.get("results", [])
    return len(cars), web_url


def main():
    found_lines = []

    for postal_code in POSTAL_CODES:
        new_count, new_url = check_inventory(postal_code, "new")
        used_count, used_url = check_inventory(postal_code, "used")

        if new_count > 0 or used_count > 0:
            line = f"""
{postal_code}
NEW: {new_count}
USED: {used_count}
New Search: {new_url}
Used Search: {used_url}
"""
            print(line)
            found_lines.append(line)

    if not found_lines:
        print("\nNo Model 3 inventory found.")
        return

    message = "🚗 Tesla Model 3 inventory found\n" + "\n".join(found_lines)
    notify(message)


if __name__ == "__main__":
    main()
