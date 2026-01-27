import csv
import sys
import time
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup
from bs4 import Tag

BASE_URL = "https://www.volby.cz/pls/ps2017nss/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120 Safari/537.36"
    )
}

Municipality = Tuple[str, str, str] 


def parse_args(argv: List[str]) -> Tuple[str, str]:
    if len(argv) != 3:
        print("Použití:")
        print("python main.py <URL_uzemniho_celku> <vystupni_soubor.csv>")
        raise SystemExit(1)
    return argv[1], argv[2]


def create_session() -> requests.Session:
    return requests.Session()


def to_int(s: str) -> int:
    return int(s.replace("\xa0", "").replace(" ", ""))


def validate_district_url(selected_url: str) -> None:
    params = parse_qs(urlparse(selected_url).query)
    if "xkraj" not in params or "xnumnuts" not in params:
        raise SystemExit("District URL is missing expected parameters (xkraj/xnumnuts)")


def get_soup(
    session: requests.Session,
    url: str,
    headers: Dict[str, str],
    referer: Optional[str] = None,
) -> BeautifulSoup:
    local_headers = dict(headers)
    if referer:
        local_headers["Referer"] = referer

    resp = session.get(url, headers=local_headers)
    if resp.status_code != 200:
        raise ValueError(f"Page returned {resp.status_code}: {url}")

    return BeautifulSoup(resp.content, "html.parser")  # type: ignore


def find_publikace(soup: BeautifulSoup, context: str) -> Tag:
    publikace = soup.find(id="publikace")
    if publikace is None:
        raise ValueError(f"Could not find #publikace on {context} page")
    return publikace

def extract_municipalities(publikace: Tag, base_url: str) -> List[Municipality]:
    municipalities: List[Municipality] = []

    for row in publikace.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 2:
            continue

        location = cells[1].get_text(strip=True)

        link = row.find("a", href=lambda h: bool(h) and h.startswith("ps311?"))
        if not link:
            continue

        code = link.get_text(strip=True)
        href = link.get("href")
        if not isinstance(href, str):
            continue
        result_url = base_url + href
        municipalities.append((code, location, result_url))

    if not municipalities:
        raise SystemExit("No municipalities found (code+location+url)")

    return municipalities


def parse_summary(publikace: Tag) -> Tuple[int, int, int]:
    tables = publikace.find_all("table")
    if len(tables) < 1:
        raise ValueError("Unexpected number of tables on result page")

    summary_rows = tables[0].find_all("tr")
    last_cells = summary_rows[-1].find_all("td")
    if len(last_cells) < 9:
        raise ValueError("Unexpected summary row structure")

    registered = to_int(last_cells[3].get_text(strip=True))
    envelopes = to_int(last_cells[4].get_text(strip=True))
    valid = to_int(last_cells[7].get_text(strip=True))
    return registered, envelopes, valid


def parse_party_votes(publikace: Tag) -> Dict[str, int]:
    tables = publikace.find_all("table")
    if len(tables) < 3:
        raise ValueError("Unexpected number of tables on result page")

    party_votes: Dict[str, int] = {}
    for row in tables[2].find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 3:
            continue

        party_name = cells[1].get_text(strip=True)
        votes = to_int(cells[2].get_text(strip=True))
        party_votes[party_name] = votes

    return party_votes


def parse_municipality_results(
    session: requests.Session,
    result_url: str,
    headers: Dict[str, str],
    referer: str,
) -> Tuple[int, int, int, Dict[str, int]]:
    result_soup = get_soup(session, result_url, headers, referer=referer)
    publikace = find_publikace(result_soup, "result")

    registered, envelopes, valid = parse_summary(publikace)
    party_votes = parse_party_votes(publikace)

    return registered, envelopes, valid, party_votes


def build_header(party_names: List[str]) -> List[str]:
    return ["code", "location", "registered", "envelopes", "valid"] + party_names


def build_row(
    code: str,
    location: str,
    registered: int,
    envelopes: int,
    valid: int,
    party_names: List[str],
    party_votes: Dict[str, int],
) -> List[object]:
    row: List[object] = [code, location, registered, envelopes, valid]
    row += [party_votes.get(p, 0) for p in party_names]
    return row


def main() -> None:
    selected_url, output_file = parse_args(sys.argv)
    validate_district_url(selected_url)

    session = create_session()

    district_soup = get_soup(session, selected_url, HEADERS)
    publikace2 = find_publikace(district_soup, "district")

    municipalities = extract_municipalities(publikace2, BASE_URL)

    first_code, first_location, first_url = municipalities[0]
    registered, envelopes, valid, party_votes = parse_municipality_results(
        session, first_url, HEADERS, selected_url
    )

    party_names = sorted(party_votes.keys())

    with open(output_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(build_header(party_names))

        writer.writerow(
            build_row(first_code, first_location, registered, envelopes, valid, party_names, party_votes)
        )

        for code, location, url in municipalities[1:]:
            try:
                registered, envelopes, valid, party_votes = parse_municipality_results(
                    session, url, HEADERS, selected_url
                )
            except Exception as e:
                print(f"Skipping {code} {location}: {e}")
                continue

            writer.writerow(
                build_row(code, location, registered, envelopes, valid, party_names, party_votes)
            )
            time.sleep(0.2)

    print("Saved:", output_file)


if __name__ == "__main__":
    main()
    """Parse command-line arguments and return the selected URL and output file name.
    """