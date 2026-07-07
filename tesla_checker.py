import requests
import urllib.parse
import json

POSTAL_CODE = "B3Z 1H4"
NTFY_TOPIC = "tesla-model3-premium-alert-himani"


def notify(message):
    requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=message.encode("utf-8"),
        headers={"Title": "Tesla Model 3 Inventory Alert"},
        timeout=20
    )


def main():
    query = {
        "query": {
            "model": "m3",
            "condition": "new",
            "arrangeby": "Price",
            "order": "asc",
            "market": "CA",
            "language": "en",
            "super_region": "north america",
            "zip": POSTAL_CODE
        },
        "offset": 0,
        "count": 50,
        "outsideOffset": 0,
        "outsideSearch": False
    }

    api_url = "https://www.tesla.com/inventory/api/v1/inventory-results"
    search_url = (
        "https://www.tesla.com/en_CA/inventory/new/m3"
        f"?arrangeby=plh&zip={urllib.parse.quote(POSTAL_CODE)}&PaymentType=cash"
    )

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": search_url
    }

    print(f"Checking NEW Model 3 inventory near {POSTAL_CODE}...")

    try:
        response = requests.get(
            api_url,
            params={"query": json.dumps(query)},
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        results = response.json().get("results", [])
        count = len(results)

        print(f"Found {count} vehicle(s).")

        if count > 0:
            message = (
                f"🚗 Tesla Model 3 inventory found!\n\n"
                f"Postal Code: {POSTAL_CODE}\n"
                f"New vehicles: {count}\n\n"
                f"{search_url}"
            )
            notify(message)
            print("Notification sent.")
        else:
            print("No inventory found.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
