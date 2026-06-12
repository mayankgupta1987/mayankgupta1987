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

NTFY_TOPIC = "tesla-model3-premium-alert-himani"
SEEN_FILE = "seen_vins.json"


def notify(message):
    requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=message.encode("utf-8"),
        headers={"Title": "Tesla Inventory Alert"},
        timeout=20,
    )


def load_seen_vins():
    if not os.path.exists(SEEN_FILE):
        return set()

    with open(SEEN_FILE, "r") as f:
        return set(json.load(f))


def save_seen_vins(seen_vins):
    with open(SEEN_FILE, "w") as f:
        json.dump(sorted(list(seen_vins)), f, indent=2)


def tesla_inventory_url(postal_code):
    query = {
        "query": {
            "model": "m3",
            "condition": "new",
            "arrangeby": "Price",
            "order": "asc",
            "market": "CA",
            "language": "en",
            "super_region": "north america",
            "zip": postal_code,
            "range": 200,
        },
        "offset": 0,
        "count": 50,
        "outsideOffset": 0,
        "outsideSearch": False,
    }

    encoded_query = urllib.parse.quote(json.dumps(query))
    return f"https://www.tesla.com/inventory/api/v1/inventory-results?query={encoded_query}"


def normal_tesla_link(postal_code):
    return (
        "https://www.tesla.com/en_CA/inventory/new/m3"
        f"?arrangeby=relevance&zip={urllib.parse.quote(postal_code)}&range=200"
    )


def get_inventory(postal_code):
    url = tesla_inventory_url(postal_code)

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    data = response.json()
    return data.get("results", [])


def format_vehicle(vehicle, postal_code):
    vin = vehicle.get("VIN", "N/A")
    price = vehicle.get("Price", "N/A")
    odometer = vehicle.get("Odometer", "N/A")
    trim = vehicle.get("TrimName", vehicle.get("TrimCode", "Model 3"))
    city = vehicle.get("City", "N/A")
    state = vehicle.get("StateProvince", "N/A")
    exterior = vehicle.get("PAINT", vehicle.get("ExteriorColor", "N/A"))

    return f"""
🚗 New Tesla Model 3 inventory found

Search postal code: {postal_code}
Vehicle location: {city}, {state}
Trim: {trim}
Price: ${price}
Odometer: {odometer}
Exterior: {exterior}
VIN: {vin}

Open Tesla inventory:
{normal_tesla_link(postal_code)}
"""


def main():
    seen_vins = load_seen_vins()
    current_vins = set(seen_vins)

    for postal_code in POSTAL_CODES:
        print(f"Checking {postal_code}...")

        try:
            vehicles = get_inventory(postal_code)
        except Exception as e:
            print(f"Error checking {postal_code}: {e}")
            continue

        print(f"Found {len(vehicles)} vehicle(s) near {postal_code}")

        for vehicle in vehicles:
            vin = vehicle.get("VIN")

            if not vin:
                continue

            if vin not in seen_vins:
                message = format_vehicle(vehicle, postal_code)
                notify(message)
                print(f"Alert sent for VIN {vin}")
                current_vins.add(vin)

    save_seen_vins(current_vins)


if __name__ == "__main__":
    main()
