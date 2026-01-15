#!/usr/bin/env python3
"""Send campaign rows from a CSV

Usage:
  pip install requests
  python send_campaign.py users.csv --dry-run
"""

import csv
import re
import time
import os
import json
import argparse
import logging
import requests
from requests.adapters import HTTPAdapter, Retry

API_URL = "https://backend.aisensy.com/campaign/t1/api/v2"
API_KEY = os.getenv("AISENSY_API_KEY", "<INSERT_API_KEY>")
MEDIA_URL = "https://www.erickson.co.in/wp-content/uploads/2026/01/TASC1and2.jpeg"
DEFAULT_CC = "91"   # prefix if phone is 10 digits

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def normalize_phone(raw):
    s = re.sub(r'\D', '', (raw or ""))
    if len(s) == 10:
        return DEFAULT_CC + s
    if s.startswith("0") and len(s) > 10:
        return s.lstrip("0")
    return s


def create_session():
    s = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429,500,502,503,504])
    s.mount("https://", HTTPAdapter(max_retries=retries))
    return s


def build_payload(name, phone):
    return {
        "apiKey": API_KEY,
        "campaignName": "TASC1and2",
        "destination": str(phone),
        "userName": "Erickson Coaching (Nov)",
        "templateParams": ["$FirstName"],
        "source": "new-landing-page form",
        "media": {"url": MEDIA_URL, "filename": "TASC1and2.jpeg"},
        "buttons": [],
        "carouselCards": [],
        "location": {},
        "attributes": {},
        "paramsFallbackValue": {"FirstName": "user"},
        "params": {"FirstName": name}
    }


def send_row(session, name, phone, dry_run=False):
    payload = build_payload(name, phone)
    if dry_run:
        logging.info("DRY RUN -> %s : %s", name, json.dumps(payload, ensure_ascii=False))
        return True, {"dry_run": True}
    try:
        r = session.post(API_URL, json=payload, timeout=15)
    except Exception as e:
        logging.error("Exception sending to %s (%s): %s", name, phone, e)
        return False, {"error": str(e)}
    try:
        data = r.json()
    except Exception:
        data = {"text": r.text}
    if r.ok:
        logging.info("Sent to %s (%s): %s", name, phone, r.text.strip()[:200])
        return True, data
    logging.error("Failed for %s (%s): %s %s", name, phone, r.status_code, r.text.strip()[:300])
    return False, data


def main(path, delay, dry_run, limit=None, test_number=None, output='results.csv'):
    session = create_session()
    success = 0
    total = 0
    results = []
    with open(path, newline='', encoding='utf-8') as fh:
        sample = fh.read(2048)
        fh.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",\t;")
        except Exception:
            dialect = None
        reader = csv.DictReader(fh, dialect=dialect) if dialect else csv.DictReader(fh)
        for row in reader:
            if limit is not None and total >= limit:
                break
            total += 1
            name = row.get('Name') or row.get('name') or ''
            phone_raw = row.get('Phone') or row.get('phone') or ''
            phone = normalize_phone(phone_raw)
            if not name or not phone:
                logging.warning("Skipping row %d: missing name or phone -> %s", total, row)
                continue
            if test_number and normalize_phone(test_number) != phone:
                logging.info("Skipping %s (%s) because it does not match test-number", name, phone)
                continue
            ok, data = send_row(session, name.strip(), phone, dry_run=dry_run)
            status = 'ok' if ok else 'failed'
            msgid = None
            if isinstance(data, dict):
                msgid = data.get('submitted_message_id') or data.get('message_id') or data.get('id') or data.get('messageId')
            results.append({
                'Name': name.strip(),
                'Phone': phone,
                'Status': status,
                'Response': json.dumps(data, ensure_ascii=False),
                'MessageID': msgid,
            })
            if ok:
                success += 1
            time.sleep(delay)
    # write results CSV
    try:
        with open(output, 'w', newline='', encoding='utf-8') as outfh:
            writer = csv.DictWriter(outfh, fieldnames=['Name', 'Phone', 'Status', 'Response', 'MessageID'])
            writer.writeheader()
            for r in results:
                writer.writerow(r)
        logging.info("Done. %d/%d succeeded. Results saved to %s", success, total, output)
    except Exception as e:
        logging.error("Error writing results to %s: %s", output, e)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", help="CSV file with Name and Phone headers")
    ap.add_argument("--delay", type=float, default=0.3, help="Seconds to wait between calls")
    ap.add_argument("--dry-run", action='store_true', help="Don't actually send - print payloads")
    ap.add_argument("--limit", type=int, default=None, help="Limit number of rows to process")
    ap.add_argument("--test-number", type=str, default=None, help="Only send to this phone (normalized)")
    ap.add_argument("--output", default='results.csv', help="CSV file to write per-row results")
    args = ap.parse_args()
    main(args.csv, args.delay, args.dry_run, args.limit, args.test_number, args.output)
