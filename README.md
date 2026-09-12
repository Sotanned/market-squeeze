# market-squeeze

Weekly tracking of five supply squeezes: copper, beef, cocoa, data center
spending and Gulf energy.

## Why there are two stages

The weekly report routine runs in a sandboxed container whose egress policy
blocks LME, CME, ICE, ICCO and most exchange and finance hosts. Two consecutive
runs produced almost no verifiable data for that reason.

So network access and reporting are split:

| Stage | Where it runs | What it does |
|---|---|---|
| 1. Fetcher | GitHub Actions runner (unrestricted internet) | `scripts/fetch_data.py` pulls raw figures and commits `data/YYYY-MM-DD.json` |
| 2. Routine | Sandboxed container (no exchange access) | Reads the newest `data/*.json` and writes `reports/squeeze-report-YYYY-MM-DD.md` |

The routine fetches nothing. Web search stays available to it for two purposes
only: explaining why a number moved, and the Strait of Hormuz shipping status,
which has no machine-readable source. The routine prompt is `ROUTINE.md`.

If the newest data file is more than eight days old, the routine reports that the
fetcher has not run and marks every area unassessed rather than guessing.

## Running the fetcher

Automatically: Saturdays at 06:00 UTC via `.github/workflows/fetch-data.yml`.

Manually, from the Actions tab: **Fetch commodity data → Run workflow**. Tick
`probe_only` to test source reachability without committing a data file.

Locally:

```bash
pip install -r requirements.txt
python scripts/fetch_data.py --probe                  # reachability report only
python scripts/fetch_data.py --out-dir data           # writes data/<today>.json
python scripts/fetch_data.py --date 2026-09-12        # override the run date
```

The fetcher never fails the workflow when a source is unreachable, and never
substitutes a guessed number: every field is written with an explicit status.

## Data file format

`data/YYYY-MM-DD.json` (a same-day rerun gets `-2`; earlier files are never
overwritten). Every field carries:

```json
{
  "value": 9450.5,
  "unit": "USD/tonne",
  "as_of": "2026-09-11",
  "source_url": "https://...",
  "source_tier": "primary",
  "fetched_at": "2026-09-12T06:00:11+00:00",
  "status": "ok",
  "note": null
}
```

- `status` is `ok`, `conflict` or `unavailable`.
- `conflict` means two sources were fetched and disagreed by more than 1%; both
  values are recorded in `note` and `value` is null. The routine treats it as no
  fresh data.
- `source_tier` is `primary` for exchange, government and company sources,
  `secondary` for aggregators.

## Field coverage

Sources were selected for being free and unauthenticated. **None could be
verified from the sandbox** — its egress policy blocks them all — so the
confidence column reflects whether each source is structurally free, not a
confirmed fetch. Run the workflow with `probe_only` to get ground truth from a
runner, and update this table with the result.

### Attempted

| Field | Source | Tier | Confidence |
|---|---|---|---|
| `brent_spot` | FRED `DCOILBRENTEU` (EIA data, no API key) | primary | high |
| `brent_front_month` | Yahoo `BZ=F`, cross-checked against Stooq `cb.f` | secondary | med-high |
| `comex_copper_front_price` | Yahoo `HG=F`, cross-checked against Stooq `hg.f` | secondary | med-high |
| `cme_live_cattle_front` | Yahoo `LE=F` | secondary | med-high |
| `cme_feeder_cattle_front` | Yahoo `GF=F` | secondary | med-high |
| `ice_cocoa_front_price` | Yahoo `CC=F`, cross-checked against Stooq `cc.f` | secondary | med-high |
| `ice_cocoa_next_price` | Yahoo dated ICE symbol (e.g. `CCH27.NYB`) | secondary | medium |
| `ice_cocoa_front_next_spread` | dated front minus dated next contract | secondary | medium |
| `lme_copper_cash` | Westmetall LME table | secondary | medium |
| `lme_copper_3m` | Westmetall LME table | secondary | medium |
| `lme_copper_stocks` | Westmetall LME table | secondary | medium |
| `lme_copper_cash_3m_spread` | computed from the two Westmetall prices | secondary | medium |
| `usda_cattle_report_release_date` | Cornell ESMIS API | primary | medium |
| `usda_cattle_inventory_total` | regex over the NASS text release | primary | low |
| `usda_beef_heifer_retention` | regex over the NASS text release | primary | low |
| `lng_asia_monthly_index` | FRED `PNGASJPUSDM` (IMF) | primary | high |

Caveats worth knowing when reading a report:

- Cattle prices are Yahoo last-traded prices, **not** official CME settlements.
- LME figures are Westmetall's republication; the LME itself has no free feed.
- `brent_spot` is the official EIA series and lags by roughly a week;
  `brent_front_month` is the futures price and is current.
- USDA numeric extraction is regex-based and fails to `unavailable` rather than
  guessing when the release layout changes. Units are as printed in the release.

### Currently unavailable — open gaps

No free, unauthenticated machine-readable source exists for these. They are
written into every data file as `unavailable` with the reason, and the routine
reports them as unassessed. Endpoints were not invented to fill them.

| Field | Why | Where a human can look |
|---|---|---|
| `comex_copper_stocks` | No free machine-readable endpoint; CME depository reports are Akamai-protected | [CME copper](https://www.cmegroup.com/markets/metals/base/copper.html) |
| `ice_cocoa_certified_stocks` | Published through an interactive/licensed ICE report | [ICE report 41](https://www.ice.com/report/41) |
| `icco_balance` | ICCO Quarterly Bulletin is a paid publication | [ICCO statistics](https://www.icco.org/statistics/) |
| `jkm_lng_spot` | JKM is a proprietary S&P Global Platts assessment | [Platts JKM](https://www.spglobal.com/commodityinsights/en/our-methodology/price-assessments/lng/jkm-japan-korea-marker-gas-price-assessments) |
| Data center capex | Quarterly company disclosure, no feed; routine checks IR pages by search | company IR pages |

Closing any of these means adding a licensed feed or an API key, not a better
scrape.

## Repository layout

```
scripts/fetch_data.py            stage 1 fetcher
.github/workflows/fetch-data.yml weekly schedule + manual dispatch
data/YYYY-MM-DD.json             committed raw figures (rolling history)
reports/squeeze-report-*.md      weekly reports
ROUTINE.md                       the routine prompt for stage 2
```

Report filenames use the real run date. A same-day rerun gets a `-2` suffix; a
report is never filed under a different day's date and never overwritten.
