import requests

API_URL = "https://www.tesla.com/inventory/api/v1/inventory-results?query=%7B%22query%22:%7B%22model%22:%22m3%22,%22condition%22:%22new%22,%22arrangeby%22:%22Price%22,%22order%22:%22asc%22,%22market%22:%22CA%22,%22language%22:%22en%22,%22super_region%22:%22north%20america%22,%22zip%22:%22B3Z%201H4%22%7D,%22offset%22:0,%22count%22:50,%22outsideOffset%22:0,%22outsideSearch%22:false%7D"

SEARCH_URL = "https://www.tesla.com/en_CA/inventory/new/m3?arrangeby=plh&zip=B3Z%201H4&PaymentType=cash"
NTFY_TOPIC = "tesla-model3-premium-alert-himani"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": SEARCH_URL,
}

try:
    response = requests.get(API_URL, headers=headers, timeout=30)
    response.raise_for_status()

    results = response.json().get("results", [])
    count = len(results)

    print(f"Found {count} vehicle(s).")

    if count > 0:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=f"🚗 {count} NEW Tesla Model 3 found!\n{SEARCH_URL}".encode("utf-8"),
            headers={"Title": "Tesla Model 3 Alert"},
            timeout=20
        )
        print("Notification sent.")
    else:
        print("No inventory. No notification sent.")

except Exception as e:
    print(f"Error: {e}")
