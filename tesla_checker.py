import requests
import urllib.parse

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


def get_api_url(postal_code, condition):
    zip_encoded = urllib.parse.quote(postal_code)

    return (
        "https://www.tesla.com/inventory/api/v1/inventory-results"
        "?query=%7B%22query%22%3A%20%7B"
        "%22model%22%3A%20%22m3%22%2C%20"
        f"%22condition%22%3A%20%22{condition}%22%2C%20"
        "%22arrangeby%22%3A%20%22Price%22%2C%20"
        "%22order%22%3A%20%22asc%22%2C%20"
        "%22market%22%3A%20%22CA%22%2C%20"
        "%22language%22%3A%20%22en%22%2C%20"
        "%22super_region%22%3A%20%22north%20america%22%2C%20"
        f"%22zip%22%3A%20%22{zip_encoded}%22"
        "%7D%2C%20%22offset%22%3A%200%2C%20"
        "%22count%22%3A%2050%2C%20"
        "%22outsideOffset%22%3A%200%2C%20"
        "%22outsideSearch%22%3A%20false%7D"
    )


def get_search_url(postal_code, condition):
    zip_encoded = urllib.parse.quote(postal_code)

    if condition == "new":
        return f"https://www.tesla.com/en_CA/inventory/new/m3?arrangeby=plh&zip={zip_encoded}&PaymentType=cash"

    return f"https://www.tesla.com/en_CA/inventory/used/m3?arrangeby=plh&zip={zip_encoded}&range=200&PaymentType=cash"


def check_inventory(session, postal_code, condition):
    api_url = get_api_url(postal_code, condition)
    search_url = get_search_url(postal_code, condition)

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": search_url,
    }

    print(f"Checking {condition.upper()} near {postal_code}")

    try:
        response = session.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return len(data.get("results", [])), search_url

    except Exception as e:
        print(f"Error checking {postal_code} {condition}: {e}")
        return 0, search_url


def main():
    found_lines = []

    with requests.Session() as session:
        for postal_code in POSTAL_CODES:
            new_count, new_url = check_inventory(session, postal_code, "new")
            used_count, used_url = check_inventory(session, postal_code, "used")

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
