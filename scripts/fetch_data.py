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


def westmetall_copper() -> dict[str, tuple[float, str]]:
    """Scrape LME copper cash, 3-month and warehouse stocks from Westmetall's table."""
    html = http_get(WESTMETALL_CU).text
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
        return {
            "cash": (cash, as_of),
            "three_month": (three_month, as_of),
            "stocks": (stocks, as_of),
        }
    raise RuntimeError("no parseable data row found in table (page layout may have changed)")


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


def parse_cattle_numbers(text: str) -> dict[str, tuple[float, str]]:
    """Pull headline inventory figures out of the NASS Cattle text release."""
    patterns = {
        "total": (
            r"All cattle and calves[^.]{0,160}?totaled\s+([\d.,]+)\s*(million|thousand)?",
            r"All cattle and calves[^\n\d]{0,40}([\d,]{3,})()",
        ),
        "heifers": (
            r"Beef (?:cow )?replacement heifers[^.]{0,160}?(?:totaled|at|were)\s+"
            r"([\d.,]+)\s*(million|thousand)?",
            r"Beef (?:cow )?replacement heifers[^\n\d]{0,40}([\d,]{3,})()",
        ),
    }
    scales = {"million": "million head", "thousand": "thousand head"}
    found: dict[str, tuple[float, str]] = {}
    for key, candidates in patterns.items():
        for pattern in candidates:
            match = re.search(pattern, text, re.I)
            if match:
                scale = (match.group(2) or "").lower()
                found[key] = (
                    parse_number(match.group(1)),
                    scales.get(scale, "head (unit as printed in release, verify)"),
                )
                break
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


def collect() -> dict[str, dict]:
    fields: dict[str, dict] = {}
    today = datetime.now(timezone.utc)

    # Copper
    try:
        lme = westmetall_copper()
        for key, name in (
            ("cash", "lme_copper_cash"),
            ("three_month", "lme_copper_3m"),
        ):
            value, as_of = lme[key]
            fields[name] = make_field(
                value=value,
                unit="USD/tonne",
                as_of=as_of,
                source_url=WESTMETALL_CU,
                source_tier="secondary",
                status="ok",
                note="Westmetall republication of LME settlement data; LME itself has no free feed",
            )
        stocks_value, stocks_as_of = lme["stocks"]
        fields["lme_copper_stocks"] = make_field(
            value=stocks_value,
            unit="tonnes",
            as_of=stocks_as_of,
            source_url=WESTMETALL_CU,
            source_tier="secondary",
            status="ok",
            note="Westmetall republication of LME warehouse stocks",
        )
        cash_value = lme["cash"][0]
        fields["lme_copper_cash_3m_spread"] = make_field(
            value=round(cash_value - lme["three_month"][0], 2),
            unit="USD/tonne",
            as_of=lme["cash"][1],
            source_url=WESTMETALL_CU,
            source_tier="secondary",
            status="ok",
            note="positive = cash above 3-month (backwardation, premium for immediate delivery)",
        )
    except Exception as exc:  # noqa: BLE001
        detail = f"Westmetall scrape failed: {exc}"
        for name, unit in (
            ("lme_copper_cash", "USD/tonne"),
            ("lme_copper_3m", "USD/tonne"),
            ("lme_copper_stocks", "tonnes"),
            ("lme_copper_cash_3m_spread", "USD/tonne"),
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

    for name, (url, note) in NO_FREE_SOURCE.items():
        fields[name] = unavailable(url, note, "primary")

    return fields


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
        ("Westmetall LME copper table", westmetall_copper),
        ("NASS Cattle report", lambda: nass_cattle_report()[::2]),
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

    print("\nNASS heifer lines:")
    try:
        _, body, _ = nass_cattle_report()
        for line in body.splitlines():
            if re.search(r"heifer|All cattle and calves", line, re.I):
                print(f"  | {' '.join(line.split())[:150]}")
    except Exception as exc:  # noqa: BLE001
        print(f"  failed: {exc}")
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
    fields = collect()

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


