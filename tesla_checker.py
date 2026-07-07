import requests
import webbrowser

URL = "https://www.tesla.com/en_CA/inventory/new/m3?arrangeby=plh&zip=B3Z%201H4&PaymentType=cash"
NTFY_TOPIC = "tesla-model3-premium-alert-himani"

webbrowser.open(URL)

requests.post(
    f"https://ntfy.sh/{NTFY_TOPIC}",
    data=f"Check Tesla Model 3 inventory:\n{URL}".encode("utf-8"),
    headers={"Title": "Tesla Model 3 Check"},
    timeout=20
)

print("Tesla page opened and notification sent.")
