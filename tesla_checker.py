import urllib.parse
import requests
from bs4 import BeautifulSoup

POSTAL_CODES = [
    "E7L 1B2",
    "E1A 2K3",
    "E3B 1B5",
    "E2L 1E8",
    "B3M 1G5",
    "B2N 5A9",
    "B1P 6J7",
]

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0 Safari/537.36"
    )
}


def build_url(postal_code, condition):

    postal = urllib.parse.quote(postal_code)

    if condition == "new":

        return (
            f"https://www.tesla.com/en_CA/inventory/new/m3"
            f"?arrangeby=plh&zip={postal}&PaymentType=cash"
        )

    return (
        f"https://www.tesla.com/en_CA/inventory/used/m3"
        f"?arrangeby=plh&zip={postal}&range=200&PaymentType=cash"
    )


def check_inventory(postal_code, condition):

    url = build_url(postal_code, condition)

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        page = soup.get_text().lower()

        if "no available inventory" in page:
            return 0

        if "model 3" in page:
            return 1

        return 0

    except Exception as e:

        print(
            f"{postal_code} {condition}: {e}"
        )

        return 0


for postal in POSTAL_CODES:

    new_found = check_inventory(
        postal,
        "new"
    )

    used_found = check_inventory(
        postal,
        "used"
    )

    print(
        postal,
        f"NEW:{new_found}",
        f"USED:{used_found}"
    )
