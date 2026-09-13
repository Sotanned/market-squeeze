#!/usr/bin/env python3
"""Throwaway: probe candidate leading-indicator sources from a runner.

Delete once the working ones graduate into fetch_data.py.
"""
from __future__ import annotations

import re
import sys

import requests

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "market-squeeze-probe/1.0", "Accept": "*/*"})


def show(label: str, url: str, extract=None) -> None:
    try:
        resp = SESSION.get(url, timeout=25)
        body = " ".join(resp.text.split())
        detail = extract(resp) if (extract and resp.ok) else body[:180]
        print(f"  [{resp.status_code}] {label}: {detail}")
    except Exception as exc:  # noqa: BLE001
        print(f"  [ERR] {label}: {type(exc).__name__}: {str(exc)[:120]}")


def iv_summary(resp):
    try:
        data = resp.json()["optionChain"]["result"][0]
        calls = data["options"][0].get("calls", [])
        ivs = [c.get("impliedVolatility") for c in calls if c.get("impliedVolatility")]
        return f"expiries={len(data.get('expirationDates', []))} calls={len(calls)} iv_sample={ivs[:3]}"
    except Exception as exc:  # noqa: BLE001
        return f"unparseable: {exc}"


def chart_summary(resp):
    try:
        meta = resp.json()["chart"]["result"][0]["meta"]
        return f"{meta.get('symbol')} price={meta.get('regularMarketPrice')} cur={meta.get('currency')}"
    except Exception as exc:  # noqa: BLE001
        return f"unparseable: {exc}"


def westmetall_header(resp):
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", resp.text, re.S | re.I)[:4]
    out = []
    for row in rows:
        cells = [
            " ".join(re.sub(r"<[^>]+>", " ", c).split())
            for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S | re.I)
        ]
        if cells:
            out.append(" | ".join(cells)[:150])
    return " // ".join(out)


print("=== LAYER 3: NASS Cattle on Feed (monthly placements) ===")
for name in ("cofd0926", "cofd0826", "cofd0726"):
    show(name, f"https://release.nass.usda.gov/reports/{name}.txt")

print("\n=== LAYER 3: LME cancelled warrants (Westmetall column check) ===")
show(
    "westmetall Cu table columns",
    "https://www.westmetall.com/en/markdaten.php?action=table&field=LME_Cu_cash",
    westmetall_header,
)
for field in ("LME_Cu_cancelled_warrants", "LME_Cu_stock", "LME_Cu_3m"):
    show(f"westmetall field={field}", f"https://www.westmetall.com/en/markdaten.php?action=table&field={field}")

print("\n=== LAYER 3: IMF PortWatch chokepoint transits ===")
show("portwatch site", "https://portwatch.imf.org/")
show("portwatch datasets", "https://portwatch.imf.org/datasets")
show(
    "portwatch arcgis root",
    "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services?f=json",
)

print("\n=== LAYER 6: freight equities ===")
for sym in ("BWET", "BDRY", "^BDI"):
    show(
        sym,
        f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=5d",
        chart_summary,
    )

print("\n=== LAYER 2: options implied vol / skew ===")
for sym in ("HG=F", "CC=F", "LE=F"):
    show(
        f"options {sym}",
        f"https://query1.finance.yahoo.com/v7/finance/options/{sym}",
        iv_summary,
    )

sys.exit(0)
