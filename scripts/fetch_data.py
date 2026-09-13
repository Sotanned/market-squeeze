#!/usr/bin/env python3
"""Fetch raw commodity data and write data/YYYY-MM-DD.json.

Runs on GitHub's runners, which have unrestricted internet. The weekly report
routine reads the committed JSON and performs no network access of its own.

Never substitutes a guessed number for a failed fetch: every field is emitted
with an explicit status of ok, conflict or unavailable.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

USER_AGENT = "market-squeeze-fetcher/1.0"
TIMEOUT = 25
RETRIES = 2
CONFLICT_THRESHOLD = 0.01

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT, "Accept": "*/*"})

YAHOO_CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=10d"
FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
WESTMETALL_CU = "https://www.westmetall.com/en/markdaten.php?action=table&field=LME_Cu_cash"
# IMF PortWatch daily chokepoint transits: the only free quantified read on
# Hormuz, replacing a news-scraped status.
PORTWATCH_CHOKEPOINTS = (
    "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/"
    "Daily_Chokepoints_Data/FeatureServer/0/query"
)
# NASS publishes the semi-annual Cattle report as catlMMYY.txt on two hosts.
NASS_REPORT_HOSTS = (
    "https://release.nass.usda.gov/reports/{name}",
    "https://www.nass.usda.gov/Publications/Todays_Reports/reports/{name}",
)

# Data that exists only behind licensing or an interactive viewer. Recorded as
# unavailable with the human-readable location, never as a fabricated endpoint.
NO_FREE_SOURCE = {
    "comex_copper_stocks": (
        "https://www.cmegroup.com/markets/metals/base/copper.html",
        "No free machine-readable endpoint verified; CME depository stock reports are "
        "Akamai-protected. Check manually or add a licensed CME feed.",
    ),
    "ice_cocoa_certified_stocks": (
        "https://www.ice.com/report/41",
        "ICE certified stocks publish through an interactive/licensed report with no free "
        "unauthenticated endpoint. Check manually.",
    ),
    "icco_balance": (
        "https://www.icco.org/statistics/",
        "ICCO Quarterly Bulletin of Cocoa Statistics is a paid publication; headline balance "
        "appears only in irregular press releases. Check manually.",
    ),
    "jkm_lng_spot": (
        "https://www.spglobal.com/commodityinsights/en/our-methodology/price-assessments/lng/jkm-japan-korea-marker-gas-price-assessments",
        "JKM is a proprietary S&P Global Platts assessment with no free spot source. See "
        "lng_asia_monthly_index for a free monthly IMF proxy (a different series, not JKM).",
    ),
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def make_field(
    value=None,
    unit="",
    as_of=None,
    source_url="",
    source_tier="secondary",
    status="unavailable",
    note=None,
) -> dict:
    return {
        "value": value,
        "unit": unit,
        "as_of": as_of,
        "source_url": source_url,
        "source_tier": source_tier,
        "fetched_at": now_iso(),
        "status": status,
        "note": note,
    }


def unavailable(source_url: str, note: str, tier: str = "secondary", unit: str = "") -> dict:
    return make_field(
        unit=unit, source_url=source_url, source_tier=tier, status="unavailable", note=note[:500]
    )


def http_get(url: str) -> requests.Response:
    last = None
    for attempt in range(RETRIES + 1):
        try:
            resp = SESSION.get(url, timeout=TIMEOUT)
            resp.raise_for_status()
            return resp
        except Exception as exc:  # noqa: BLE001 - a failed fetch must never abort the run
            last = exc
            # NASS answers bursts with 403. Without a pause that false negative
            # makes the report walk fall through to an older release and
            # present it as the latest.
            if attempt < RETRIES:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"{type(last).__name__}: {last}")


def parse_number(raw: str) -> float:
    """Parse a price cell written in either US (1,234.56) or European (1.234,56) format."""
    text = re.sub(r"[^\d.,-]", "", raw or "").strip()
    if not text:
        raise ValueError("empty number")
    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        # A single comma is a decimal separator only when it is not grouping digits.
        text = text.replace(",", "." if re.search(r",\d{1,2}$", text) else "")
    return float(text)


# --- sources ---------------------------------------------------------------


def yahoo_last(symbol: str) -> tuple[float, str | None, str, str]:
    url = YAHOO_CHART.format(sym=symbol)
    payload = http_get(url).json()
    results = (payload.get("chart") or {}).get("result") or []
    if not results:
        error = (payload.get("chart") or {}).get("error")
        raise RuntimeError(f"no chart result (error={error})")
    meta = results[0].get("meta") or {}
    value = meta.get("regularMarketPrice")
    if value is None:
        closes = (
            ((results[0].get("indicators") or {}).get("quote") or [{}])[0].get("close") or []
        )
        closes = [c for c in closes if c is not None]
        if not closes:
            raise RuntimeError("no regularMarketPrice and no non-null closes")
        value = closes[-1]
    stamp = meta.get("regularMarketTime")
    as_of = (
        datetime.fromtimestamp(stamp, timezone.utc).date().isoformat()
        if isinstance(stamp, (int, float))
        else None
    )
    return float(value), as_of, (meta.get("currency") or ""), url


def fred_last(series_id: str) -> tuple[float, str, str]:
    url = FRED_CSV.format(sid=series_id)
    rows = list(csv.reader(io.StringIO(http_get(url).text)))
    if len(rows) < 2:
        raise RuntimeError("CSV had no observations")
    observations = [
        (r[0].strip(), r[1].strip())
        for r in rows[1:]
        if len(r) >= 2 and r[1].strip() not in (".", "")
    ]
    if not observations:
        raise RuntimeError("no numeric observations")
    day, value = observations[-1]
    return parse_number(value), day, url


def westmetall_copper_rows(limit: int = 30) -> list[dict]:
    """LME copper cash, 3-month and stocks, newest first.

    The page carries a multi-session table; reading only the top row discards
    the trend, which is the part that leads.
    """
    html = http_get(WESTMETALL_CU).text
    rows: list[dict] = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S | re.I):
        cells = [
            re.sub(r"<[^>]+>", " ", c).replace("&nbsp;", " ").strip()
            for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S | re.I)
        ]
        if len(cells) < 4:
            continue
        as_of = None
        for fmt in ("%d. %B %Y", "%d %B %Y", "%Y-%m-%d", "%d.%m.%Y"):
            try:
                as_of = datetime.strptime(cells[0].strip(), fmt).date().isoformat()
                break
            except ValueError:
                continue
        if not as_of:
            continue
        try:
            cash, three_month, stocks = (
                parse_number(cells[1]),
                parse_number(cells[2]),
                parse_number(cells[3]),
            )
        except ValueError:
            continue
        rows.append(
            {
                "date": as_of,
                "cash": cash,
                "three_month": three_month,
                "spread": round(cash - three_month, 2),
                "stocks": stocks,
            }
        )
        if len(rows) >= limit:
            break
    if not rows:
        raise RuntimeError("no parseable data row found in table (page layout may have changed)")
    return rows


def _arcgis_date(value) -> str | None:
    if isinstance(value, str) and re.match(r"\d{4}-\d{2}-\d{2}", value):
        return value[:10]
    if isinstance(value, (int, float)) and value > 1e9:
        return datetime.fromtimestamp(value / 1000, timezone.utc).date().isoformat()
    return None


def portwatch_chokepoint(name: str = "hormuz") -> tuple[float, str | None, str]:
    """Latest daily transit count for a chokepoint.

    Field names are discovered from the response rather than assumed, so a
    schema change degrades to unavailable instead of a wrong number.
    """
    url = (
        f"{PORTWATCH_CHOKEPOINTS}?where=1%3D1&outFields=*&resultRecordCount=400"
        "&orderByFields=date%20DESC&f=json"
    )
    payload = http_get(url).json()
    features = payload.get("features") or []
    if not features:
        raise RuntimeError(f"no features returned (keys: {list(payload)[:6]})")
    for feature in features:
        attrs = feature.get("attributes") or {}
        if not any(isinstance(v, str) and name in v.lower() for v in attrs.values()):
            continue
        as_of = next(
            (_arcgis_date(v) for k, v in attrs.items() if re.search(r"date", str(k), re.I)
             and _arcgis_date(v)),
            None,
        )
        for key, val in attrs.items():
            if isinstance(val, (int, float)) and re.search(
                r"n_transit|transit_calls|^n_total|vessel", str(key), re.I
            ):
                return float(val), as_of, url
        raise RuntimeError(
            f"found {name} row but no transit field; keys were {sorted(attrs)[:15]}"
        )
    raise RuntimeError(f"no {name} row in the 400 most recent records")


def nass_cattle_report(today: datetime | None = None) -> tuple[str, str, str]:
    """Most recent semi-annual NASS Cattle report: (release date, body text, url)."""
    today = today or datetime.now(timezone.utc)
    for year in (today.year, today.year - 1):
        for month in (7, 1):
            if (year, month) > (today.year, today.month):
                continue
            name = f"catl{month:02d}{str(year)[-2:]}.txt"
            for host in NASS_REPORT_HOSTS:
                url = host.format(name=name)
                try:
                    text = http_get(url).text
                except Exception:  # noqa: BLE001 - try the next host or older cycle
                    continue
                match = re.search(r"Released\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})", text)
                if not match:
                    continue
                released = datetime.strptime(match.group(1), "%B %d, %Y").date().isoformat()
                return released, text, url
    raise RuntimeError("no NASS Cattle report found for the last two release cycles")


def nass_cattle_on_feed(today: datetime | None = None) -> tuple[str, str, str]:
    """Most recent monthly NASS Cattle on Feed report: (release date, body, url)."""
    today = today or datetime.now(timezone.utc)
    for back in range(5):
        month, year = today.month - back, today.year
        while month <= 0:
            month += 12
            year -= 1
        name = f"cofd{month:02d}{str(year)[-2:]}.txt"
        for host in NASS_REPORT_HOSTS:
            url = host.format(name=name)
            try:
                text = http_get(url).text
            except Exception:  # noqa: BLE001 - try the next host or an older month
                continue
            match = re.search(r"Released\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})", text)
            if not match:
                continue
            released = datetime.strptime(match.group(1), "%B %d, %Y").date().isoformat()
            return released, text, url
    raise RuntimeError("no Cattle on Feed report found in the last five months")


def parse_cof_numbers(text: str) -> dict[str, tuple[float, str]]:
    """On-feed level plus the placements and marketings flows."""
    flat = " ".join(text.split())
    patterns = {
        "on_feed": r"[Cc]attle and calves on feed[^.]{0,220}?totaled\s+([\d.,]+)\s*(million|thousand)?",
        "placements": r"Placements[^.]{0,220}?totaled\s+([\d.,]+)\s*(million|thousand)?",
        "marketings": r"Marketings[^.]{0,220}?totaled\s+([\d.,]+)\s*(million|thousand)?",
    }
    scales = {"million": "million head", "thousand": "thousand head"}
    found: dict[str, tuple[float, str]] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, flat)
        if match:
            found[key] = (
                parse_number(match.group(1)),
                scales.get((match.group(2) or "").lower(), "head (unit as printed, verify)"),
            )
    if not found:
        raise RuntimeError("on-feed/placements/marketings lines not found")
    return found


def parse_cattle_numbers(text: str) -> dict[str, tuple[float, str]]:
    """Pull headline inventory figures out of the NASS Cattle text release."""
    # The release hard-wraps mid-phrase ("Beef replacement\nheifers, at 3.80
    # million head"), so match against whitespace-collapsed text.
    flat = " ".join(text.split())
    patterns = {
        "total": r"All cattle and calves in the United States[^.]{0,120}?"
        r"totaled\s+([\d.,]+)\s*(million|thousand)?",
        "heifers": r"Beef replacement heifers,?\s*at\s+([\d.,]+)\s*(million|thousand)?",
    }
    scales = {"million": "million head", "thousand": "thousand head"}
    found: dict[str, tuple[float, str]] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, flat, re.I)
        if match:
            scale = (match.group(2) or "").lower()
            found[key] = (
                parse_number(match.group(1)),
                scales.get(scale, "head (unit as printed in release, verify)"),
            )
    if not found:
        raise RuntimeError("headline inventory lines not found in text release")
    return found


# --- reconciliation --------------------------------------------------------


def cross_checked(
    label: str,
    unit_hint: str,
    primary_getter,
    secondary_getter,
    tier: str = "secondary",
) -> dict:
    """Fetch a figure from two sources; flag >1% disagreement as a conflict."""
    values, notes, url, as_of, unit = {}, [], "", None, unit_hint
    for name, getter in (("a", primary_getter), ("b", secondary_getter)):
        if getter is None:
            continue
        try:
            result = getter()
            values[name] = result
            url = url or result[2]
            as_of = as_of or result[1]
            # An explicit unit hint carries the denominator (USd/lb); the feed's
            # currency field alone would flatten it to "USD".
            if not unit_hint and len(result) > 3 and result[3]:
                unit = result[3]
        except Exception as exc:  # noqa: BLE001
            notes.append(f"{label}[{name}] failed: {exc}")

    if not values:
        return unavailable(url or label, "; ".join(notes) or "all sources failed", tier, unit)

    if len(values) == 2:
        first, second = values["a"][0], values["b"][0]
        mean = (abs(first) + abs(second)) / 2
        drift = abs(first - second) / mean if mean else 0.0
        if drift > CONFLICT_THRESHOLD:
            return make_field(
                value=None,
                unit=unit,
                as_of=as_of,
                source_url=f"{values['a'][2]} | {values['b'][2]}",
                source_tier=tier,
                status="conflict",
                note=(
                    f"sources disagree by {drift * 100:.2f}% (>1%): "
                    f"{first} ({values['a'][2]}) vs {second} ({values['b'][2]})"
                ),
            )
        chosen = values["a"]
        return make_field(
            value=chosen[0],
            unit=unit,
            as_of=chosen[1],
            source_url=chosen[2],
            source_tier=tier,
            status="ok",
            note=f"cross-checked within 1% against {values['b'][2]} ({values['b'][0]})",
        )

    only = values.get("a") or values.get("b")
    return make_field(
        value=only[0],
        unit=unit,
        as_of=only[1],
        source_url=only[2],
        source_tier=tier,
        status="ok",
        note="; ".join(notes + ["single source only, not cross-checked"]) or None,
    )


def cocoa_contract_symbols(today: datetime) -> tuple[str, str]:
    """Yahoo symbols for the front and next ICE cocoa delivery months (Mar/May/Jul/Sep/Dec)."""
    months = [(3, "H"), (5, "K"), (7, "N"), (9, "U"), (12, "Z")]
    schedule = []
    for year in (today.year, today.year + 1, today.year + 2):
        for month, code in months:
            schedule.append((year, month, code))
    upcoming = [s for s in schedule if (s[0], s[1]) > (today.year, today.month)]
    return tuple(f"CC{code}{str(year)[-2:]}.NYB" for year, _, code in upcoming[:2])


# --- assembly --------------------------------------------------------------


def collect() -> tuple[dict[str, dict], dict[str, list]]:
    fields: dict[str, dict] = {}
    series: dict[str, list] = {}
    today = datetime.now(timezone.utc)

    # Copper
    try:
        rows = westmetall_copper_rows()
        latest = rows[0]
        series["lme_copper"] = rows
        for key, name, unit, note in (
            ("cash", "lme_copper_cash", "USD/tonne", "Westmetall republication of LME settlements"),
            ("three_month", "lme_copper_3m", "USD/tonne", "Westmetall republication of LME settlements"),
            ("stocks", "lme_copper_stocks", "tonnes", "Westmetall republication of LME stocks"),
            (
                "spread",
                "lme_copper_cash_3m_spread",
                "USD/tonne",
                "positive = cash above 3-month (backwardation, premium for immediate delivery)",
            ),
        ):
            fields[name] = make_field(
                value=latest[key],
                unit=unit,
                as_of=latest["date"],
                source_url=WESTMETALL_CU,
                source_tier="secondary",
                status="ok",
                note=note,
            )
        if len(rows) >= 2:
            oldest = rows[-1]
            fields["lme_copper_spread_change"] = make_field(
                value=round(latest["spread"] - oldest["spread"], 2),
                unit="USD/tonne",
                as_of=latest["date"],
                source_url=WESTMETALL_CU,
                source_tier="secondary",
                status="ok",
                note=f"cash-3M spread moved {oldest['spread']} ({oldest['date']}) -> "
                f"{latest['spread']} ({latest['date']}) across {len(rows)} sessions; "
                "negative = premium for immediate metal draining",
            )
            fields["lme_copper_stocks_change"] = make_field(
                value=round(latest["stocks"] - oldest["stocks"], 1),
                unit="tonnes",
                as_of=latest["date"],
                source_url=WESTMETALL_CU,
                source_tier="secondary",
                status="ok",
                note=f"stocks moved {oldest['stocks']:,.0f} ({oldest['date']}) -> "
                f"{latest['stocks']:,.0f} ({latest['date']}) across {len(rows)} sessions",
            )
    except Exception as exc:  # noqa: BLE001
        detail = f"Westmetall scrape failed: {exc}"
        for name, unit in (
            ("lme_copper_cash", "USD/tonne"),
            ("lme_copper_3m", "USD/tonne"),
            ("lme_copper_stocks", "tonnes"),
            ("lme_copper_cash_3m_spread", "USD/tonne"),
            ("lme_copper_spread_change", "USD/tonne"),
            ("lme_copper_stocks_change", "tonnes"),
        ):
            fields[name] = unavailable(WESTMETALL_CU, detail, "secondary", unit)

    fields["comex_copper_front_price"] = cross_checked(
        "comex_copper_front_price",
        "USd/lb",
        lambda: yahoo_last("HG=F"),
        None,
    )

    # Beef
    fields["cme_live_cattle_front"] = cross_checked(
        "cme_live_cattle_front", "USd/lb", lambda: yahoo_last("LE=F"), None
    )
    fields["cme_feeder_cattle_front"] = cross_checked(
        "cme_feeder_cattle_front", "USd/lb", lambda: yahoo_last("GF=F"), None
    )
    for name in ("cme_live_cattle_front", "cme_feeder_cattle_front"):
        if fields[name]["status"] == "ok":
            existing = fields[name]["note"] or ""
            fields[name]["note"] = (
                existing + "; last traded price from Yahoo, not the official CME settlement"
            ).lstrip("; ")

    try:
        release_date, body, report_url = nass_cattle_report(today)
        fields["usda_cattle_report_release_date"] = make_field(
            value=None,
            unit="date",
            as_of=release_date,
            source_url=report_url,
            source_tier="primary",
            status="ok",
            note=f"latest USDA NASS Cattle report released {release_date}; compare against the "
            "release date cited in the previous report to decide whether it is new",
        )
        try:
            numbers = parse_cattle_numbers(body)
            for key, name in (
                ("total", "usda_cattle_inventory_total"),
                ("heifers", "usda_beef_heifer_retention"),
            ):
                if key in numbers:
                    value, unit = numbers[key]
                    fields[name] = make_field(
                        value=value,
                        unit=unit,
                        as_of=release_date,
                        source_url=report_url,
                        source_tier="primary",
                        status="ok",
                        note="regex extraction from the NASS text release",
                    )
        except Exception as exc:  # noqa: BLE001
            for name in ("usda_cattle_inventory_total", "usda_beef_heifer_retention"):
                fields.setdefault(
                    name, unavailable(report_url, f"text-release parse failed: {exc}", "primary")
                )
    except Exception as exc:  # noqa: BLE001
        detail = f"NASS Cattle report lookup failed: {exc}"
        for name in (
            "usda_cattle_report_release_date",
            "usda_cattle_inventory_total",
            "usda_beef_heifer_retention",
        ):
            fields[name] = unavailable(NASS_REPORT_HOSTS[0], detail, "primary")

    for name in (
        "usda_cattle_inventory_total",
        "usda_beef_heifer_retention",
        "usda_cattle_report_release_date",
    ):
        fields.setdefault(name, unavailable(NASS_REPORT_HOSTS[0], "not attempted", "primary"))

    try:
        cof_date, cof_body, cof_url = nass_cattle_on_feed(today)
        fields["usda_cattle_on_feed_report_release_date"] = make_field(
            value=None, unit="date", as_of=cof_date, source_url=cof_url,
            source_tier="primary", status="ok",
            note=f"monthly Cattle on Feed released {cof_date}; placements is the leading "
            "flow behind the semi-annual inventory level",
        )
        try:
            cof_numbers = parse_cof_numbers(cof_body)
            for key, name in (
                ("on_feed", "usda_cattle_on_feed_total"),
                ("placements", "usda_cattle_placements"),
                ("marketings", "usda_cattle_marketings"),
            ):
                if key in cof_numbers:
                    value, unit = cof_numbers[key]
                    fields[name] = make_field(
                        value=value, unit=unit, as_of=cof_date, source_url=cof_url,
                        source_tier="primary", status="ok",
                        note="regex extraction from the NASS Cattle on Feed text release",
                    )
        except Exception as exc:  # noqa: BLE001
            for name in ("usda_cattle_on_feed_total", "usda_cattle_placements",
                         "usda_cattle_marketings"):
                fields.setdefault(name, unavailable(cof_url, f"parse failed: {exc}", "primary"))
    except Exception as exc:  # noqa: BLE001
        for name in ("usda_cattle_on_feed_report_release_date", "usda_cattle_on_feed_total",
                     "usda_cattle_placements", "usda_cattle_marketings"):
            fields[name] = unavailable(NASS_REPORT_HOSTS[0], f"Cattle on Feed lookup failed: {exc}", "primary")

    # Cocoa
    fields["ice_cocoa_front_price"] = cross_checked(
        "ice_cocoa_front_price",
        "USD/tonne",
        lambda: yahoo_last("CC=F"),
        None,
    )
    front_symbol, next_symbol = cocoa_contract_symbols(today)
    fields["ice_cocoa_next_price"] = cross_checked(
        "ice_cocoa_next_price", "USD/tonne", lambda: yahoo_last(next_symbol), None
    )
    if fields["ice_cocoa_next_price"]["status"] == "ok":
        fields["ice_cocoa_next_price"]["note"] = f"dated contract symbol {next_symbol}"

    # The spread compares two dated contracts; pairing a continuous front against a
    # dated next would price the roll, not the curve.
    try:
        dated_front, front_as_of, _, front_url = yahoo_last(front_symbol)
        dated_next = fields["ice_cocoa_next_price"]
        if dated_next["status"] != "ok":
            raise RuntimeError(f"next contract {next_symbol} unavailable")
        fields["ice_cocoa_front_next_spread"] = make_field(
            value=round(dated_front - dated_next["value"], 2),
            unit="USD/tonne",
            as_of=front_as_of,
            source_url=f"{front_url} | {dated_next['source_url']}",
            source_tier="secondary",
            status="ok",
            note=f"{front_symbol} minus {next_symbol}; positive = front above next (backwardation)",
        )
    except Exception as exc:  # noqa: BLE001
        fields["ice_cocoa_front_next_spread"] = unavailable(
            "", f"needs both dated contracts ({front_symbol}, {next_symbol}): {exc}",
            "secondary", "USD/tonne",
        )

    # Energy
    fields["brent_spot"] = cross_checked(
        "brent_spot", "USD/bbl", lambda: fred_last("DCOILBRENTEU"), None, tier="primary"
    )
    if fields["brent_spot"]["status"] == "ok":
        fields["brent_spot"]["note"] = (
            "EIA Brent spot via FRED series DCOILBRENTEU; official series lags by roughly a week"
        )
    fields["brent_front_month"] = cross_checked(
        "brent_front_month",
        "USD/bbl",
        lambda: yahoo_last("BZ=F"),
        None,
    )
    fields["lng_asia_monthly_index"] = cross_checked(
        "lng_asia_monthly_index",
        "USD/MMBtu",
        lambda: fred_last("PNGASJPUSDM"),
        None,
        tier="primary",
    )
    if fields["lng_asia_monthly_index"]["status"] == "ok":
        fields["lng_asia_monthly_index"]["note"] = (
            "IMF global price of LNG (Asia) via FRED PNGASJPUSDM; MONTHLY index, not JKM spot, "
            "and not a substitute for it"
        )

    try:
        transits, transit_date, transit_url = portwatch_chokepoint("hormuz")
        fields["hormuz_daily_transits"] = make_field(
            value=transits, unit="vessels/day", as_of=transit_date,
            source_url=transit_url, source_tier="primary", status="ok",
            note="IMF PortWatch daily transit count; quantified replacement for the "
            "news-sourced Hormuz status",
        )
    except Exception as exc:  # noqa: BLE001
        fields["hormuz_daily_transits"] = unavailable(
            PORTWATCH_CHOKEPOINTS, f"PortWatch lookup failed: {exc}", "primary", "vessels/day"
        )

    # Freight equities stand in for charter rates: the Baltic indices themselves
    # are licensed, so these ETFs are the only free read on the rate layer.
    for name, symbol, label in (
        ("freight_tanker_etf", "BWET", "tanker"),
        ("freight_drybulk_etf", "BDRY", "dry bulk"),
    ):
        fields[name] = cross_checked(name, "USD", (lambda sym=symbol: yahoo_last(sym)), None)
        if fields[name]["status"] == "ok":
            fields[name]["note"] = (
                f"{label} freight ETF as a proxy for charter rates; NOT a Baltic index, "
                "and an equity wrapper carries roll and fee drag"
            )

    for name, (url, note) in NO_FREE_SOURCE.items():
        fields[name] = unavailable(url, note, "primary")

    return fields, series


def next_free_path(directory: Path, stem: str, suffix: str = ".json") -> Path:
    candidate = directory / f"{stem}{suffix}"
    if not candidate.exists():
        return candidate
    index = 2
    while (directory / f"{stem}-{index}{suffix}").exists():
        index += 1
    return directory / f"{stem}-{index}{suffix}"


def probe() -> int:
    today = datetime.now(timezone.utc)
    _, next_cocoa = cocoa_contract_symbols(today)
    checks = [
        ("FRED Brent spot (DCOILBRENTEU)", lambda: fred_last("DCOILBRENTEU")),
        ("FRED Asia LNG monthly (PNGASJPUSDM)", lambda: fred_last("PNGASJPUSDM")),
        ("Yahoo HG=F copper", lambda: yahoo_last("HG=F")),
        ("Yahoo LE=F live cattle", lambda: yahoo_last("LE=F")),
        ("Yahoo GF=F feeder cattle", lambda: yahoo_last("GF=F")),
        ("Yahoo CC=F cocoa front", lambda: yahoo_last("CC=F")),
        ("Yahoo BZ=F Brent front", lambda: yahoo_last("BZ=F")),
        (f"Yahoo {next_cocoa} cocoa next", lambda: yahoo_last(next_cocoa)),
        ("Westmetall LME copper table", lambda: westmetall_copper_rows()[:3]),
        ("Yahoo BWET tanker ETF", lambda: yahoo_last("BWET")),
        ("Yahoo BDRY dry bulk ETF", lambda: yahoo_last("BDRY")),
        ("NASS Cattle report", lambda: nass_cattle_report()[::2]),
        ("NASS Cattle on Feed", lambda: nass_cattle_on_feed()[::2]),
        ("NASS COF numbers", lambda: parse_cof_numbers(nass_cattle_on_feed()[1])),
        ("PortWatch Hormuz transits", lambda: portwatch_chokepoint("hormuz")),
        ("NASS cattle numbers", lambda: parse_cattle_numbers(nass_cattle_report()[1])),
    ]
    print(f"Source probe {now_iso()}\n")
    working = 0
    for label, getter in checks:
        try:
            result = getter()
            working += 1
            print(f"  OK        {label}: {str(result)[:120]}")
        except Exception as exc:  # noqa: BLE001
            print(f"  FAILED    {label}: {type(exc).__name__}: {str(exc)[:160]}")
    print(f"\n{working}/{len(checks)} probes reachable.")
    print("Declared gaps (no free source, not probed): " + ", ".join(sorted(NO_FREE_SOURCE)))

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", default="data")
    parser.add_argument("--date", help="override run date (YYYY-MM-DD)")
    parser.add_argument(
        "--probe",
        action="store_true",
        help="report source reachability without writing a data file",
    )
    args = parser.parse_args()

    if args.probe:
        return probe()

    run_date = args.date or datetime.now(timezone.utc).date().isoformat()
    fields, series = collect()

    counts: dict[str, int] = {}
    for spec in fields.values():
        counts[spec["status"]] = counts.get(spec["status"], 0) + 1

    document = {
        "schema_version": 1,
        "run_date": run_date,
        "fetched_at": now_iso(),
        "field_count": len(fields),
        "status_counts": counts,
        "fields": fields,
        "series": series,
    }

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = next_free_path(out_dir, run_date)
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"wrote {path}")
    for status in sorted(counts):
        print(f"  {status}: {counts[status]}")
    for name, spec in sorted(fields.items()):
        if spec["status"] != "ok":
            print(f"  [{spec['status']}] {name}: {spec['note']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())


