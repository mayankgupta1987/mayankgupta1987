import json
import urllib.parse
import requests

POSTAL_CODES = [
    "E7L 1B2", "E1A 2K3", "E3B 1B5", "E2L 1E8",
    "B3M 1G5", "B2N 5A9", "B1P 6J7",
    "C1A 4P3", "C1N 1B4",
    "G1R 5M1", "H3B 1A7", "J8X 2W3", "J1H 5H3", "G8Y 1T6",
    "K1P 1J1", "K7L 1A1", "M5V 2T6", "L8P 1A1", "N6A 1A1", "P3E 3E6",
]

NTFY_TOPIC = "tesla-model3-premium-alert-himani"
MIN_YEAR = 2025


def notify(message):
    requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=message.encode("utf-8"),
        headers={"Title": "Tesla Model 3 Inventory Alert"},
        timeout=20
    )


def build_api_url(postal_code, condition):
    query = {
        "query": {
            "model": "m3",
            "condition": condition,   # "new" or "used"
            "arrangeby": "Price",
            "order": "asc",
            "market": "CA",
            "language": "en",
            "super_region": "north america",
            "zip": postal_code,
            "range": 200
        },
        "offset": 0,
        "count": 50,
        "outsideOffset": 0,
        "outsideSearch": False
    }

    encoded = urllib.parse.quote(json.dumps(query))
    return f"https://www.tesla.com/inventory/api/v1/inventory-results?query={encoded}"


def get_year(car):
    for key in ["Year", "year", "modelYear", "ModelYear"]:
        if key in car and car[key]:
            try:
                return int(car[key])
            except:
                pass

    vin = car.get("VIN", "")
    if vin:
        # Tesla sometimes includes year separately, but VIN decoding is not always reliable here.
        pass

    return None


def get_car_link(car):
    vin = car.get("VIN") or car.get("vin")
    if vin:
        return f"https://www.tesla.com/en_CA/m3/order/{vin}"
    return "https://www.tesla.com/en_CA/inventory/new/m3"


def check_inventory(postal_code, condition):
    api_url = build_api_url(postal_code, condition)

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.tesla.com/en_CA/inventory/new/m3",
    }

    print(f"\nChecking {condition.upper()} Model 3 near {postal_code}")

    try:
        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error checking {postal_code} {condition}: {e}")
        return []

    cars = data.get("results", [])
    matches = []

    for car in cars:
        year = get_year(car)

        if year is not None and year < MIN_YEAR:
            continue

        title = car.get("Title", "Tesla Model 3")
        price = car.get("PurchasePrice") or car.get("price") or "N/A"
        trim = car.get("TrimName") or car.get("TRIM") or ""
        odometer = car.get("Odometer") or car.get("odometer") or "N/A"
        vin = car.get("VIN", "N/A")
        location = car.get("City") or car.get("Location") or "N/A"
        link = get_car_link(car)

        matches.append({
            "condition": condition,
            "year": year or "Year not shown",
            "title": title,
            "trim": trim,
            "price": price,
            "odometer": odometer,
            "vin": vin,
            "location": location,
            "link": link
        })

    return matches


def main():
    all_matches = []

    for postal_code in POSTAL_CODES:
        for condition in ["new", "used"]:
            matches = check_inventory(postal_code, condition)
            for m in matches:
                m["postal_code"] = postal_code
            all_matches.extend(matches)

    if not all_matches:
        print("\nNo 2025+ new or used Model 3 inventory found.")
        return

    message_lines = ["🚗 Tesla Model 3 inventory found — 2025 or newer\n"]

    for car in all_matches:
        line = f"""
{car['condition'].upper()} | {car['year']} | {car['title']} {car['trim']}
Price: {car['price']}
KM: {car['odometer']}
Location: {car['location']}
Search postal code: {car['postal_code']}
VIN: {car['vin']}
Link: {car['link']}
"""
        print(line)
        message_lines.append(line)

    notify("\n".join(message_lines))


if __name__ == "__main__":
    main()