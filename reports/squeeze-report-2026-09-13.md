# Weekly Supply Squeeze Report — 2026-09-13

**Data file:** `data/2026-09-13-3.json` (run_date 2026-09-13, 25 fields ok / 4 unavailable).
**Comparison basis:** `reports/squeeze-report-2026-09-12-2.md` (last week's report).

**Note on comparability:** Several fields the fetcher now reports cleanly (LME cash/3M/stocks, COMEX front price, cattle futures, cocoa front/next, Brent) were logged as "no fresh data" in last week's report because of blocked primary sources and conflicting web-search snippets. There is therefore no confirmed prior-week print to diff most of these against — this week's number is real, but the week-over-week comparison is not. Cattle-on-Feed (placements/marketings/on-feed total) and the freight ETFs are new fields with no prior report entry at all. This is noted per figure below rather than silently treated as a "no change."

## 1. Headline

Four of five areas are Unclear this week — not because signals disagree, but because most figures lack a confirmed prior-week print to compare against or a corroborating second source. The one clear read is Copper: the record backwardation has drained from +535 (Aug 17 peak) to +5.5 USD/t and LME stocks have rebuilt off their Aug 14 low, an Easing call the underlying 30-session series supports independent of last week's report.

## 2. Verdict

> **Copper — Easing.** Cash−3M +5.5 vs +535 peak (Aug 17); stocks −6.2% over 30 sessions, up off the Aug 14 low.

> **Beef — Unclear.** Live cattle 219.675¢, feeder 332.5¢ (Sep 11) are fresh single-source prints with no confirmed prior week to diff; new Cattle-on-Feed data (placements 1.42M head) has no baseline yet.

> **Cocoa — Unclear.** Front 5,913 / next 6,036 USD/t (contango, −123 spread); no confirmed prior-week print; certified stocks still unavailable.

> **Gulf energy — Unclear.** Hormuz at 6.0 vessels/day (~93% below the 85/day baseline, as_of Sep 6, unchanged read); Brent and JKM lack a confirmed week-ago print.

> **Data center spending — no new release since Jul 22–31, 2026** (Q2 CY2026 earnings); next expected ~late Oct 2026.

## 3. Numbers table

| Area | Figure | This week | As of | Last week | Direction | Trend | Source | Tier |
|---|---|---|---|---|---|---|---|---|
| Copper | LME cash−3M spread | +5.5 USD/t | 2026-09-11 | no fresh data (prior report unconfirmed) | n/a vs. last week | Draining: +535 (Aug 17 peak) → +5.5, 30 sessions | [Westmetall](https://www.westmetall.com/en/markdaten.php?action=table&field=LME_Cu_cash) | Secondary |
| Copper | LME copper stocks | 234,475 t | 2026-09-11 | no fresh data | n/a vs. last week | −6.2% over 30 sessions (249,850→234,475); +14.4% off the Aug 14 low (204,975) | [Westmetall](https://www.westmetall.com/en/markdaten.php?action=table&field=LME_Cu_cash) | Secondary |
| Copper | LME cash price | 14,238.5 USD/t | 2026-09-11 | no fresh data | n/a | — | [Westmetall](https://www.westmetall.com/en/markdaten.php?action=table&field=LME_Cu_cash) | Secondary |
| Copper | LME 3-month price | 14,233.0 USD/t | 2026-09-11 | no fresh data | n/a | — | [Westmetall](https://www.westmetall.com/en/markdaten.php?action=table&field=LME_Cu_cash) | Secondary |
| Copper | COMEX copper stocks | unavailable | — | no fresh data | n/a | — | [CME Group](https://www.cmegroup.com/markets/metals/base/copper.html) | Primary (unreachable) |
| Copper | COMEX front price | 6.548 USd/lb | 2026-09-11 | no fresh data | n/a | — | Yahoo Finance | Secondary |
| Beef | CME live cattle, front month | 219.675 ¢/lb | 2026-09-11 | no fresh data | n/a | — | Yahoo Finance | Secondary |
| Beef | CME feeder cattle, front month | 332.5 ¢/lb | 2026-09-11 | no fresh data | n/a | — | Yahoo Finance | Secondary |
| Beef | USDA cattle inventory / heifer retention | no new release since 2026-07-24 | 2026-07-24 | 94.2M head / 3.80M head (Jul 24, 2026) | — | — | [USDA NASS](https://release.nass.usda.gov/reports/catl0726.txt) | Primary |
| Beef | USDA Cattle on Feed: total / placements / marketings | 11.1M / 1.42M / 1.62M head | 2026-08-21 | new field, no prior entry | n/a (baseline) | — | [USDA NASS](https://release.nass.usda.gov/reports/cofd0826.txt) | Primary |
| Cocoa | ICE cocoa front price | 5,913 USD/t | 2026-09-11 | no fresh data | n/a | — | Yahoo Finance (CCZ26.NYB) | Secondary |
| Cocoa | ICE cocoa next price | 6,036 USD/t | 2026-09-11 | no fresh data | n/a | — | Yahoo Finance (CCH27.NYB) | Secondary |
| Cocoa | ICE front−next spread | −123.0 USD/t (contango) | 2026-09-11 | no fresh data | n/a | — | Yahoo Finance | Secondary |
| Cocoa | ICE certified stocks | unavailable | — | no fresh data | n/a | — | [ICE](https://www.ice.com/report/41) | Primary (unreachable) |
| Cocoa | ICCO global balance | unavailable | — | no new release since Aug 2026 bulletin | — | — | [ICCO](https://www.icco.org/statistics/) | Primary (unreachable) |
| Gulf energy | Brent spot (EIA/FRED) | 109.51 USD/bbl | 2026-09-09 | no prior entry (new field) | n/a (baseline) | — | [FRED DCOILBRENTEU](https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILBRENTEU) | Primary (lags ~1wk) |
| Gulf energy | Brent front-month | 104.61 USD/bbl | 2026-09-11 | no fresh data (prior report conflicting) | n/a | — | Yahoo Finance | Secondary |
| Gulf energy | Hormuz daily transits | 6.0 vessels/day | 2026-09-06 | ~6/day (Sep 6, cited as prior-week reference in last report) | Unchanged | Still ~93% below the ~85/day pre-crisis baseline | [IMF PortWatch](https://portwatch.imf.org/) | Primary |
| Gulf energy | Freight tanker ETF | 726.92 USD | 2026-09-11 | no prior entry (new field) | n/a (baseline) | — | Yahoo Finance | Secondary |
| Gulf energy | Freight drybulk ETF | 16.01 USD | 2026-09-11 | no prior entry (new field) | n/a (baseline) | — | Yahoo Finance | Secondary |
| Gulf energy | JKM LNG spot | unavailable | — | $24.81–24.82/MMBtu (Sep 10–11, via search last week) | n/a | — | S&P Global Platts (no free source) | Primary (unavailable) |
| Gulf energy | Asia LNG monthly index (IMF) | no fresh data (as_of >1 month old) | 2026-07-01 | — | — | — | [FRED PNGASJPUSDM](https://fred.stlouisfed.org/graph/fredgraph.csv?id=PNGASJPUSDM) | Primary |

## 4. What changed

**Copper — backwardation has drained, stocks rebuilt.** The cash−3-month spread peaked at +535 USD/t on Aug 17 (a 5-year-plus high) and has fallen in nearly every session since, closing at +5.5 on Sep 11. Stocks bottomed at 204,975 t on Aug 14 and have rebuilt to 234,475 t. Reporting corroborates this: on-warrant inventory reportedly rose roughly 63,000 t within three days in mid-to-late August as holders delivered metal to capture the backwardation, which is the mechanism behind both moves.

All other areas carry no confirmed week-over-week change: Beef, Cocoa and Gulf-energy price fields are fresh prints without a verifiable prior-week figure to diff against, and data center capex has no new release.

## 5. Transmission map

Only Copper qualifies (Easing this week); all other areas are Unclear or lack a confirmed comparison this week.

**Copper — Easing**

- **Layer 3 (bottleneck, flow over level):** On-warrant stock inflows — reported at roughly +63,000 t over three days in mid/late August — are the leading flow behind the level recovery now visible in the 30-session series (204,975 t → 234,475 t). The flow moved before the level did.
- **Layer 4 (access premium):** Cash−3M spread, +535 (Aug 17 peak) → +5.5 (Sep 11). This is the premium for immediate delivery, now essentially gone.
- **Layer 5 (forward test):** The spread's decline has been sustained across roughly 30 sessions rather than a single-day print, which is what separates a durable unwind from noise.
- **Layer 6 (equity) — Miners sector:** Mechanism — LME-deliverable producers captured elevated near-term realized pricing while the spot premium was open; as it drains toward zero, near-term realized pricing converges back to the futures curve. What breaks the link — most volume moves under long-term offtake contracts insulated from spot LME pricing, so the equity effect from this specific spread move is smaller than the headline number suggests.
- **Layer 6 (equity) — Copper fabricators/consumers (wire, cable):** Mechanism — consumers paying a premium for prompt metal see that input-cost pressure ease as the spread compresses. What breaks the link — many supply contracts carry cost-indexation or pass-through clauses tied to LME reference prices, which dampens the margin effect in either direction.

## 6. Exposed companies

Copper is the only area marked Easing/Tightening this week, so it is the only area with an exposure list.

**Producers (captured the now-fading premium):**
- **Freeport-McMoRan (NYSE: FCX)** — closed $71.21 on 2026-09-11 ([Trefis/Yahoo Finance](https://www.trefis.com/stock/fcx/articles/615048/why-did-freeport-mcmoran-stock-drop-on-doubts-over-a-tariff-it-would-gain-from/2026-09-11)). Large LME/COMEX-deliverable copper producer; benefited from elevated near-term realized pricing while the cash−3M premium was open. Breaks the link: bulk of volume sold under long-term contracts, and the Sep 11 move itself was driven by copper-tariff news, not the LME spread.
- **Southern Copper Corp (NYSE: SCCO)** — closed $193.49 on 2026-09-11 ([Yahoo Finance](https://finance.yahoo.com/quote/SCCO/)). Same mechanical link as FCX. Breaks the link: most output is sold under long-term offtake agreements insulated from spot LME swings.

**Consumers (relieved as the premium drains):**
- **Nexans SA (Euronext Paris: NEX)** — closed EUR 142.30 on 2026-09-10 ([ad-hoc-news.de](https://www.ad-hoc-news.de/boerse/news/corporate-news/nexans-stock-gains-support-from-fresh-share-buyback/70065555)). Major copper wire/cable manufacturer; pays the LME premium for prompt copper input, so the drain from +535 to +5.5 eases near-term input cost. Breaks the link: cable pricing contracts typically pass copper costs through to customers via indexation clauses, limiting the margin effect either way.

## 7. Ending signals

No area is marked Tightening this week, so no ending-signals commentary applies under Step 5's criteria. Copper's own easing (see Verdict and Transmission map) is itself the resolution of the squeeze flagged in prior weeks: stocks rebuilding off the Aug 14 low and the backwardation draining from +535 to +5.5 are the two signs that were being watched for.

## 8. Data gaps

- **Copper:** COMEX warehouse stocks — unavailable (CME depository reports are Akamai-protected, no free machine-readable endpoint).
- **Beef:** No gaps in this week's fetched fields; USDA cattle inventory/heifer retention carries no new release since Jul 24, 2026 (next expected ~Jan 2027). CME futures prints are single-source (Yahoo last-traded, not the official CME settlement) and not cross-checked.
- **Cocoa:** ICE certified stocks — unavailable (interactive/licensed report, no free endpoint). ICCO global balance — unavailable (paid Quarterly Bulletin; no new release since Aug 2026). Front/next prices are single-source and not cross-checked.
- **Gulf energy:** JKM LNG spot — unavailable (proprietary S&P Global Platts assessment, no free spot source). Asia LNG monthly index — stale (as_of 2026-07-01, over a month old), reported as no fresh data despite `ok` status. Hormuz transit figure lags roughly a week (as_of 2026-09-06) per the source's own latency. Brent front-month, both freight ETFs, and Brent spot are each single-source and not cross-checked.
- **Data center spending:** No fetcher field exists; no new release since Q2 CY2026 (Jul 22–31, 2026); next reports expected ~late Oct 2026.

---
*Report generated per `ROUTINE.md`. Data file: `data/2026-09-13-3.json`. No trade recommendations are made or implied.*
