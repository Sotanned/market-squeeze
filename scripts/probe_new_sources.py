#!/usr/bin/env python3
"""Throwaway round 3: query the PortWatch chokepoint service and confirm the
Cattle on Feed line wording. Delete once both are settled.
"""
from __future__ import annotations

import re
import sys

import requests

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "market-squeeze-probe/1.0", "Accept": "*/*"})
ARCGIS_ROOT = "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services?f=json"

print("=== PortWatch: chokepoint services ===")
try:
    catalogue = SESSION.get(ARCGIS_ROOT, timeout=25).json().get("services", [])
    targets = [s for s in catalogue if re.search(r"choke", str(s.get("name", "")), re.I)]
    print(f"  chokepoint services: {[s.get('name') for s in targets]}")
    for svc in targets:
        for layer in (0, 1):
            url = (
                f"{svc['url']}/{layer}/query?where=1%3D1&outFields=*"
                "&resultRecordCount=2&orderByFields=date%20DESC&f=json"
            )
            try:
                resp = SESSION.get(url, timeout=25)
                body = " ".join(resp.text.split())
                print(f"\n  [{resp.status_code}] {svc['name']} layer {layer}:\n    {body[:700]}")
            except Exception as exc:  # noqa: BLE001
                print(f"  [ERR] {svc['name']} layer {layer}: {exc}")
except Exception as exc:  # noqa: BLE001
    print(f"  catalogue failed: {exc}")

print("\n=== PortWatch: daily transit series candidates ===")
try:
    catalogue = SESSION.get(ARCGIS_ROOT, timeout=25).json().get("services", [])
    names = [s.get("name") for s in catalogue]
    print("  daily/transit named services:")
    for n in names:
        if re.search(r"daily|transit|traffic", str(n), re.I):
            print(f"    - {n}")
except Exception as exc:  # noqa: BLE001
    print(f"  failed: {exc}")

print("\n=== Cattle on Feed: confirm line wording ===")
try:
    resp = SESSION.get("https://release.nass.usda.gov/reports/cofd0826.txt", timeout=25)
    print(f"  [{resp.status_code}] cofd0826.txt")
    if resp.ok:
        for line in resp.text.splitlines():
            if re.search(r"on feed|placements|marketings", line, re.I):
                cleaned = " ".join(line.split())
                if cleaned:
                    print(f"   | {cleaned[:150]}")
except Exception as exc:  # noqa: BLE001
    print(f"  failed: {exc}")

sys.exit(0)
