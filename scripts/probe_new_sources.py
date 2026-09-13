#!/usr/bin/env python3
"""Throwaway round 2: discover the PortWatch chokepoint service and the
NASS Cattle on Feed filename. Delete once both are resolved.
"""
from __future__ import annotations

import re
import sys

import requests

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "market-squeeze-probe/1.0", "Accept": "*/*"})
ARCGIS_ROOT = "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services?f=json"


def get(url, timeout=25):
    return SESSION.get(url, timeout=timeout)


print("=== PortWatch: find the chokepoint service ===")
try:
    catalogue = get(ARCGIS_ROOT).json().get("services", [])
    print(f"  {len(catalogue)} services in catalogue")
    hits = [
        svc
        for svc in catalogue
        if re.search(r"choke|transit|daily|strait|port", str(svc.get("name", "")), re.I)
    ]
    for svc in hits[:12]:
        print(f"   candidate: {svc.get('name')} ({svc.get('type')})")
    for svc in hits[:4]:
        url = f"{svc['url']}/0/query?where=1%3D1&outFields=*&resultRecordCount=1&f=json"
        try:
            resp = get(url)
            body = " ".join(resp.text.split())
            print(f"   [{resp.status_code}] query {svc['name']}: {body[:300]}")
        except Exception as exc:  # noqa: BLE001
            print(f"   [ERR] query {svc['name']}: {exc}")
except Exception as exc:  # noqa: BLE001
    print(f"  catalogue failed: {exc}")

print("\n=== NASS Cattle on Feed: find the filename ===")
# catl<MMYY>.txt works, so the host is fine and only the stem is wrong.
for stem in ("cofd", "ctonfd", "cattle_on_feed", "cofdall", "cofl", "cofdx"):
    for name in (f"{stem}0826.txt", f"{stem}0926.txt"):
        for host in (
            "https://release.nass.usda.gov/reports/",
            "https://www.nass.usda.gov/Publications/Todays_Reports/reports/",
        ):
            try:
                resp = get(host + name, timeout=15)
                if resp.ok and "Cattle" in resp.text[:400]:
                    print(f"   [200] HIT {host+name}: {' '.join(resp.text.split())[:160]}")
                else:
                    print(f"   [{resp.status_code}] {host.split('/')[2]}/{name}")
            except Exception as exc:  # noqa: BLE001
                print(f"   [ERR] {name}: {type(exc).__name__}")

print("\n=== NASS: list what the reports directory actually exposes ===")
for url in (
    "https://release.nass.usda.gov/reports/",
    "https://www.nass.usda.gov/Publications/Todays_Reports/",
):
    try:
        resp = get(url)
        names = sorted(set(re.findall(r"([a-z_]{3,20}\d{4}\.txt)", resp.text, re.I)))
        print(f"  [{resp.status_code}] {url} -> {len(names)} report files; sample: {names[:25]}")
        feed = [n for n in names if re.search(r"cof|feed", n, re.I)]
        if feed:
            print(f"   *** cattle-on-feed candidates: {feed}")
    except Exception as exc:  # noqa: BLE001
        print(f"  [ERR] {url}: {exc}")

sys.exit(0)
