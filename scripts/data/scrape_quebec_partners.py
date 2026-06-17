#!/usr/bin/env python3
"""Download Quebec immigration partner organizations to local CSV and JSON."""

from __future__ import annotations

import argparse
import csv
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag


DATA_ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = DATA_ROOT / "Datasets"

BASE_URL = "https://www.quebec.ca"
LIST_URL = f"{BASE_URL}/en/immigration/partners"
DEFAULT_PAGES = 17
LIST_FIELDS = (
    "name",
    "detail_url",
    "listing_address",
    "listing_languages",
    "map_url",
    "listing_website",
)
DETAIL_FIELDS = (
    "services",
    "regular_staff_languages",
    "casual_volunteer_languages",
    "reduced_mobility_access",
    "daycare",
    "contact_hours",
    "phone",
    "email",
    "website",
    "address",
    "holiday_period",
    "territory_covered",
    "administrative_region",
    "municipality",
    "source_last_updated",
)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def get_soup(session: requests.Session, url: str, attempts: int = 3) -> BeautifulSoup:
    for attempt in range(attempts):
        try:
            response = session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException:
            if attempt == attempts - 1:
                raise
            time.sleep(2**attempt)
    raise RuntimeError("unreachable")


def parse_listing_card(card: Tag) -> dict[str, str]:
    name_link = card.select_one(".partner-name a")
    paragraphs = card.find_all("p", recursive=False)
    address = clean_text(paragraphs[1].get_text(" ", strip=True)) if len(paragraphs) > 1 else ""

    links = card.find_all("a", href=True)
    map_link = next((link for link in links if "map" in clean_text(link.get_text()).lower()), None)
    website_link = next(
        (link for link in links if clean_text(link.get_text()).lower() == "website"), None
    )
    languages = card.select_one(".langs")

    return {
        "name": clean_text(name_link.get_text()) if name_link else "",
        "detail_url": urljoin(BASE_URL, name_link["href"]) if name_link else "",
        "listing_address": address,
        "listing_languages": clean_text(languages.get_text()) if languages else "",
        "map_url": map_link["href"] if map_link else "",
        "listing_website": website_link["href"] if website_link else "",
    }


def collect_listing_records(session: requests.Session, pages: int) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for page in range(1, pages + 1):
        soup = get_soup(session, f"{LIST_URL}?tx_solr%5Bpage%5D={page}")
        cards = soup.select(".partner-element")
        if not cards:
            break
        records.extend(parse_listing_card(card) for card in cards)
    return records


def heading_list(soup: BeautifulSoup, heading_text: str) -> list[str]:
    heading = next(
        (h for h in soup.find_all(["h2", "h3"]) if clean_text(h.get_text()) == heading_text),
        None,
    )
    if not heading:
        return []
    container = heading.parent
    return [clean_text(item.get_text()) for item in container.find_all("li")]


def property_values(soup: BeautifulSoup) -> dict[str, str]:
    values: dict[str, str] = {}
    for label in soup.select(".prop-title"):
        parent = label.parent
        full_text = clean_text(parent.get_text(" ", strip=True))
        label_text = clean_text(label.get_text())
        values[label_text] = clean_text(full_text.removeprefix(label_text))
    return values


def parse_detail(session: requests.Session, record: dict[str, str]) -> dict[str, str]:
    soup = get_soup(session, record["detail_url"])
    props = property_values(soup)
    contact = soup.select_one(".coordonnees-section")

    phone_link = contact.select_one('a[href^="tel:"]') if contact else None
    email_link = contact.select_one('a[href^="mailto:"]') if contact else None
    website_link = contact.select_one(".coordonnee-item a[href^='http']") if contact else None
    address = contact.select_one(".address") if contact else None
    hours = contact.select_one(".date-section") if contact else None

    # The first HTTP link in the contact block may be the map link; choose a non-map URL.
    if contact:
        website_link = next(
            (
                link
                for link in contact.select('a[href^="http"]')
                if "map" not in link["href"].lower()
            ),
            None,
        )

    updated = soup.select_one(".dateMiseAJour")
    detail = {
        "services": " | ".join(heading_list(soup, "Offered service(s)")),
        "regular_staff_languages": props.get("By regular personal", ""),
        "casual_volunteer_languages": props.get("By casual and voluntary personal", ""),
        "reduced_mobility_access": props.get("Access for people with reduced mobility", ""),
        "daycare": props.get("Daycare center", ""),
        "contact_hours": clean_text(hours.get_text(" ", strip=True)) if hours else "",
        "phone": clean_text(phone_link.get_text()) if phone_link else "",
        "email": email_link["href"].removeprefix("mailto:") if email_link else "",
        "website": website_link["href"] if website_link else record["listing_website"],
        "address": clean_text(address.get_text(" ", strip=True)) if address else record["listing_address"],
        "holiday_period": props.get("Holiday period", ""),
        "territory_covered": props.get("Territory covered by the organization", ""),
        "administrative_region": props.get("Administrative region", ""),
        "municipality": props.get("Municipality", ""),
        "source_last_updated": clean_text(updated.get_text()).removeprefix("Last update:").strip()
        if updated
        else "",
    }
    return {**record, **detail}


def write_outputs(records: list[dict[str, str]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "quebec_immigration_partners.json"
    csv_path = output_dir / "quebec_immigration_partners.csv"

    json_path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=LIST_FIELDS + DETAIL_FIELDS)
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=DEFAULT_PAGES)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--output-dir", type=Path, default=DATASETS_DIR)
    args = parser.parse_args()

    session = requests.Session()
    session.headers["User-Agent"] = "BUSA-649 community project research downloader/1.0"
    listing_records = collect_listing_records(session, args.pages)

    records: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(parse_detail, session, record) for record in listing_records]
        for future in as_completed(futures):
            records.append(future.result())

    records.sort(key=lambda item: (item["name"].casefold(), item["address"].casefold()))
    write_outputs(records, args.output_dir)
    print(f"Wrote {len(records)} records to {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
