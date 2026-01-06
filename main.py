import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import csv
import sys
import time

if len(sys.argv) != 3:
    print("Použití:")
    print("python main.py <URL_uzemniho_celku> <vystupni_soubor.csv>")
    sys.exit(1)


def to_int(s: str) -> int:
    return int(s.replace("\xa0", "").replace(" ", ""))


def parse_municipality_results(result_url: str, headers: dict, referer: str) -> tuple[int, int, int, dict]:
    local_headers = dict(headers)
    local_headers["Referer"] = referer
    result_response = session.get(result_url, headers=local_headers)
    if result_response.status_code != 200:
        raise ValueError(f"Result page returned {result_response.status_code}")

    result_soup = BeautifulSoup(result_response.content, "html.parser") # type: ignore
    publikace = result_soup.find(id="publikace")
    if publikace is None:
        raise ValueError("Could not find #publikace on result page")

    tables = publikace.find_all("table")
    if len(tables) < 3:
        raise ValueError("Unexpected number of tables on result page")

    summary_rows = tables[0].find_all("tr")
    last_cells = summary_rows[-1].find_all("td")
    if len(last_cells) < 9:
        raise ValueError("Unexpected summary row structure")

    registered = to_int(last_cells[3].get_text(strip=True))
    envelopes = to_int(last_cells[4].get_text(strip=True))
    valid = to_int(last_cells[7].get_text(strip=True))

    party_votes = {}
    for row in tables[2].find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 3:
            continue

        party_name = cells[1].get_text(strip=True)
        votes = to_int(cells[2].get_text(strip=True))
        party_votes[party_name] = votes

    return registered, envelopes, valid, party_votes

SELECTED_URL = sys.argv[1] 
OUTPUT_FILE = sys.argv[2]
MAIN_URL = "https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ"
BASE_URL = "https://www.volby.cz/pls/ps2017nss/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
}
session = requests.Session()

district_response = session.get(SELECTED_URL, headers=HEADERS)
if district_response.status_code != 200:
    raise SystemExit(f"District page returned {district_response.status_code}")

district_soup = BeautifulSoup(district_response.content, "html.parser") # type: ignore
publikace2 = district_soup.find(id="publikace")
if publikace2 is None:
    raise SystemExit("Could not find #publikace on district page")

rows2 = publikace2.find_all("tr")
if not rows2:
    raise SystemExit("No rows found on district page")

params = parse_qs(urlparse(SELECTED_URL).query)
if "xkraj" not in params or "xnumnuts" not in params:
    raise SystemExit("District URL is missing expected parameters (xkraj/xnumnuts)")

municipalities = []
for row in rows2:
    cells = row.find_all("td")
    if len(cells) < 2:
        continue

    location = cells[1].get_text(strip=True)

    link = row.find("a", href=lambda h: h and h.startswith("ps311?"))
    if not link:
        continue

    code = link.get_text(strip=True)
    result_url = BASE_URL + link["href"]
    municipalities.append((code, location, result_url))

if not municipalities:
    raise SystemExit("No municipalities found (code+location+url)")

first_code, first_location, first_url = municipalities[0]
registered, envelopes, valid, party_votes = parse_municipality_results(first_url, HEADERS, SELECTED_URL)

party_names = sorted(party_votes.keys())
header = ["code", "location", "registered", "envelopes", "valid"] + party_names

with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)

    row_out = [first_code, first_location, registered, envelopes, valid]
    for party in party_names:
        row_out.append(party_votes.get(party, 0))
    writer.writerow(row_out)

    for code, location, url in municipalities[1:]:
        try:
            registered, envelopes, valid, party_votes = parse_municipality_results(first_url, HEADERS, SELECTED_URL)
        except Exception as e:
            print(f"Skipping {code} {location}: {e}")
            continue

        row_out = [code, location, registered, envelopes, valid]
        for party in party_names:
            row_out.append(party_votes.get(party, 0))
        writer.writerow(row_out)

        time.sleep(0.2)

print("Saved:", OUTPUT_FILE)
