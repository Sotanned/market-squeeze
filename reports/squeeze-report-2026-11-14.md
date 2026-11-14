# Weekly Supply Squeeze Report — 2026-11-14

Data file: `data/2026-11-14.json` (run_date 2026-11-14, 0 days old). Comparison basis: `reports/squeeze-report-2026-11-07.md` (figures as of 2026-11-06). **That report is not on the default branch** — it sits on `claude/nice-gates-nait3e`, as do the Oct 3 – Oct 31 reports on their own side branches. The newest report on the default branch is 2026-09-26. Last week's figures were read from the committed file on the side branch, not reconstructed.

## 1. Headline

Two areas ease: copper stocks rose another 3.9% to 329,100 t while the cash premium fell from +175 to +65, and Brent spot dropped 13.9% to 92.14; cocoa is steady, beef is unclear on a contract roll, and six of 29 fields are unavailable or stale, including Hormuz transits for the first time.

## 2. Verdict

> **Copper — Easing.** Cash−3M +65 (Nov 13) vs +175 last week, +210 peak (Oct 29); stocks 329,100 t, +3.9% w/w, +34.4% over 30 sessions.

> **Beef — Unclear.** Feeder 335.35¢ (+5.3% w/w); live 224.8¢ is a rolled contract, not comparable; placements 1.78M unchanged since Oct 23 release.

> **Cocoa — Steady.** Front 5,123 USD/t (+0.1% w/w); front−next −144 (contango, 24 wider); certified stocks and ICCO balance unavailable.

> **Data center spending — no new release since 2026-10-29.**

> **Gulf energy — Easing.** Brent spot 92.14 (Nov 11), −13.9% vs Nov 3; front 95.84 (−2.5% w/w); tanker ETF −8.5%; Hormuz transits unavailable.

## 3. Numbers table

"Last week" = 2026-11-07 report (as of 2026-11-06) unless marked. Trend = `series.lme_copper` over 30 sessions (Oct 5 → Nov 13).

| Area | Figure | This week | As of | Last week | Direction | Trend | Source | Tier |
|---|---|---|---|---|---|---|---|---|
| Copper | LME cash | 13,610 USD/t | 2026-11-13 | 13,955 | −2.5% | 14,430 → 13,610 (−5.7%); high 14,822 Oct 12 | [Westmetall](https://www.westmetall.com/en/markdaten.php?action=table&field=LME_Cu_cash) | secondary |
| Copper | LME 3-month | 13,545 USD/t | 2026-11-13 | 13,780 | −1.7% | 14,366 → 13,545 (−5.7%) | [Westmetall](https://www.westmetall.com/en/markdaten.php?action=table&field=LME_Cu_cash) | secondary |
| Copper | LME cash−3M spread | +65 USD/t | 2026-11-13 | +175 | −110 | +64 → +65 (+1); built to +210 Oct 29, drained since; +175 Nov 9, +162 Nov 10, +80.5 Nov 11, +57 Nov 12 | [Westmetall](https://www.westmetall.com/en/markdaten.php?action=table&field=LME_Cu_cash) | secondary |
| Copper | LME stocks | 329,100 t | 2026-11-13 | 316,675 | +3.9% | 244,900 → 329,100 (+84,200, +34.4%); low 225,425 Oct 16 | [Westmetall](https://www.westmetall.com/en/markdaten.php?action=table&field=LME_Cu_cash) | secondary |
| Copper | COMEX front price | 6.09 USd/lb | 2026-11-13 | 6.238 | −2.4% | — | [Yahoo Finance](https://finance.yahoo.com/quote/HG=F/) | secondary |
| Copper | COMEX stocks | no fresh data | — | unavailable | n/a | — | [CME](https://www.cmegroup.com/markets/metals/base/copper.html) | primary (unavailable) |
| Beef | CME live cattle front | 224.8 ¢/lb | 2026-11-13 | 214.05 | +5.0% (contract roll; see §4) | — | [Yahoo Finance](https://finance.yahoo.com/quote/LE=F/) | secondary |
| Beef | CME feeder cattle front | 335.35 ¢/lb | 2026-11-13 | 318.375 | +5.3% | — | [Yahoo Finance](https://finance.yahoo.com/quote/GF=F/) | secondary |
| Beef | USDA cattle inventory | 94.2M head | 2026-07-24 | 94.2M | no new release since 2026-07-24 | — | [USDA NASS](https://release.nass.usda.gov/reports/catl0726.txt) | primary |
| Beef | USDA heifer retention | 3.8M head | 2026-07-24 | 3.8M | no new release since 2026-07-24 | — | [USDA NASS](https://release.nass.usda.gov/reports/catl0726.txt) | primary |
| Beef | USDA cattle on feed total | 11.4M head | 2026-10-23 | 11.4M | no new release since 2026-10-23 | — | [USDA NASS](https://release.nass.usda.gov/reports/cofd1026.txt) | primary |
| Beef | USDA placements | 1.78M head | 2026-10-23 | 1.78M | no new release since 2026-10-23 | — | [USDA NASS](https://release.nass.usda.gov/reports/cofd1026.txt) | primary |
| Beef | USDA marketings | 1.52M head | 2026-10-23 | 1.52M | no new release since 2026-10-23 | — | [USDA NASS](https://release.nass.usda.gov/reports/cofd1026.txt) | primary |
| Cocoa | ICE front price (CCZ26) | 5,123 USD/t | 2026-11-13 | 5,119 | +0.1% | — | [Yahoo Finance](https://query1.finance.yahoo.com/v8/finance/chart/CCZ26.NYB?interval=1d&range=10d) | secondary |
| Cocoa | ICE next price (CCH27) | 5,267 USD/t | 2026-11-13 | 5,239 | +0.5% | — | [Yahoo Finance](https://query1.finance.yahoo.com/v8/finance/chart/CCH27.NYB?interval=1d&range=10d) | secondary |
| Cocoa | ICE front−next spread | −144 USD/t (contango) | 2026-11-13 | −120 | wider by 24 | — | [Yahoo Finance](https://query1.finance.yahoo.com/v8/finance/chart/CCZ26.NYB?interval=1d&range=10d) | secondary |
| Cocoa | ICE certified stocks | no fresh data | — | unavailable | n/a | — | [ICE report 41](https://www.ice.com/report/41) | primary (unavailable) |
| Cocoa | ICCO balance | no fresh data | — | unavailable | n/a | — | [ICCO](https://www.icco.org/statistics/) | primary (unavailable) |
| Data center | Hyperscaler capex guidance | no new release since 2026-10-29 | 2026-10 | new releases Oct 21–29 | no new release | — | secondary aggregators (not IR pages) | secondary |
| Gulf energy | Brent spot | 92.14 USD/bbl | 2026-11-11 | 107.03 (Nov 3) | −13.9% | — | [FRED DCOILBRENTEU](https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILBRENTEU) | primary |
| Gulf energy | Brent front-month | 95.84 USD/bbl | 2026-11-13 | 98.32 | −2.5% | — | [Yahoo Finance](https://finance.yahoo.com/quote/BZ=F/) | secondary |
| Gulf energy | Hormuz daily transits | no fresh data | — | 2 (Oct 25) | n/a | — | [IMF PortWatch](https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Daily_Chokepoints_Data/FeatureServer/0/query) | primary (unavailable) |
| Gulf energy | Tanker freight ETF | 618.68 USD | 2026-11-13 | 676.5 | −8.5% | — | [Yahoo Finance](https://finance.yahoo.com/quote/BWET/) | secondary |
| Gulf energy | Drybulk freight ETF | 12.93 USD | 2026-11-13 | 13.24 | −2.3% | — | [Yahoo Finance](https://finance.yahoo.com/quote/BDRY/) | secondary |
| Gulf energy | JKM LNG spot | no fresh data | — | unavailable | n/a | — | [S&P Global Platts](https://www.spglobal.com/commodityinsights/en/our-methodology/price-assessments/lng/jkm-japan-korea-marker-gas-price-assessments) | primary (unavailable) |
| Gulf energy | Asia LNG monthly index (not JKM) | 26.637 USD/MMBtu | 2026-09-01 (74 days old: no fresh data) | 26.637 (Sep 1) | same observation | — | [FRED PNGASJPUSDM](https://fred.stlouisfed.org/graph/fredgraph.csv?id=PNGASJPUSDM) | primary |

## 4. What changed

**Copper — premium drains, stocks keep building.** Cash−3M fell from +175 (Nov 9) to +57 (Nov 12) and closed the week at +65, back to where the 30-session window opened (+64, Oct 5) after peaking at +210 on Oct 29. Stocks rose 12,425 t on the week to 329,100 t, with 8,925 t arriving on Nov 12 alone; cash fell 2.5%. Trade press attributes the inflow to the COMEX–LME arbitrage reversing: the COMEX premium moved from about +$89/t to about −$85/t by Nov 4, and more than 70% of LME stock sat in US warehouses on Nov 5 ([S&P Global](https://www.spglobal.com/energy/en/news-research/latest-news/metals/110626-china-copper-premium-hits-record-as-market-weighs-us-stock-shift), [SMM](https://news.metal.com/newscontent/104202729-high-premiums-and-weak-demand-continue-to-suppress-end-use-demand-copper-futures-prices-pull-back-sharply-smm-copper-morning-meeting-summary); search summaries, pages not opened).

**Beef — feeders up 5.3%; the live cattle print is a roll.** Feeder cattle rose from 318.375 to 335.35, matching the January contract's +$16.975 weekly gain reported by [Brownfield](https://brownfieldagnews.com/news/closing-grain-and-livestock-futures-november-13-2026/). The live cattle field moved from 214.05 to 224.8, but 224.8 is the February settlement and 214.05 was December; December closed at 220.65, +$6.60 (+3.1%) on the week ([WLJ](https://www.wlj.net/market-wrap-up-friday-nov-13/)). Futures rose against lower cash trade ([Pro Farmer](https://www.profarmer.com/news/after-bell/after-bell-cattle-futures-firm-despite-weak-cash-trade)), and no bottleneck figure updated, so the area stays Unclear.

**Gulf energy — Brent falls on US–Iran talk hopes.** Brent spot fell from 107.03 (Nov 3) to 92.14 (Nov 11); futures settled at 91.49 on Nov 10, the lowest since August, after President Trump said the Iran war could end "fairly soon" ([CNBC](https://www.cnbc.com/2026/11/10/oil-prices-trump-iran.html), [Gulf News](https://gulfnews.com/business/energy/oil-hits-lowest-since-august-as-trump-holds-off-on-iran-strikes-1.500743137)). Front-month recovered to 95.84 by Nov 13 after reported explosions on four tankers in Hormuz on Nov 12, for a second weekly loss ([The National](https://thenationalnews.com/business/energy/2026/11/13/oil-on-track-to-post-second-weekly-decline-as-trump-eases-fears-of-renewed-war-with-iran)). Spot traded 8.7 above front last week and 3.7 below it this week, on dates two days apart.

**Hormuz shipping status (web, no data source this week).** Traffic is below normal but moving: UKMTO's weekly report as of Nov 10 counted 170 outbound and 155 inbound transits ([Gulf News](https://gulfnews.com/world/mena/hormuz-shipping-below-normal-but-not-stalled-1.500741839)); Lloyd's List counted 95 tanker and gas-carrier transits for Oct 19–25 ([Lloyd's List](https://www.lloydslistintelligence.com/resources/blog/strait-of-hormuz-brief-5-november-2026)). Attacks continue: a tanker strike on Nov 8 caused a fire and crew evacuation ([UANI](https://www.unitedagainstnucleariran.com/node/46596)). These counts use different definitions and are not comparable with the PortWatch series.

## 5. Transmission map

**Copper (Easing)**

| Layer | Sector | Mechanism | What breaks the link |
|---|---|---|---|
| 3 Bottleneck | Miners | LME stocks +84,200 t in 30 sessions; the flow is inbound on every week of November | Reported cause is relocation of US metal onto LME warrant, not new supply — sign for miner margins is **ambiguous** |
| 4 Access premium | Miners | Cash−3M +210 → +65 removes most of the prompt-delivery premium | Mine output sells on annual contracts at LME average plus a fixed premium; the daily spread barely enters realized price |
| 4–5 Access / forward test | Fabricators (wire, tube, cable) | Cash −2.5% w/w and a thinner backwardation lower the cost of prompt metal | Metal-surcharge clauses pass copper cost through; inventory bought at higher prices produces a holding loss |
| 6 Equity | Miners / fabricators | Last to move | Says nothing about what is priced |

**Gulf energy (Easing)**

| Layer | Sector | Mechanism | What breaks the link |
|---|---|---|---|
| 2 Risk price | Integrated oil, E&P | Brent spot −13.9% removes part of the war-risk premium from realized prices | Driver is talk of a deal, not a signed one; front-month rebounded 4.35 from the Nov 10 settle |
| 3 Bottleneck | Tanker owners | More transits shorten voyages and cut ton-miles; no transit figure this week | PortWatch unavailable — the flow is unmeasured, so this link is **ambiguous** |
| 4 Access premium | Tanker owners | Tanker freight ETF −8.5% w/w points to lower charter rates | ETF is a proxy with roll and fee drag, not a Baltic index; time-chartered fleets reprice slowly |
| 4–5 | Airlines, refiners, chemicals | Lower crude lowers fuel and feedstock cost | Fuel hedges delay the benefit; refiners' margin depends on the crack spread, not the crude level — **ambiguous** for refiners |
| 6 Equity | Tankers, E&P | Last to move | Most Gulf production gain accrues to state producers with no listing |

## 6. Exposed companies

Factual exposure only. Closes are 2026-11-13.

**Copper (Easing)**

Producers (revenue falls with the copper price):

- **Freeport-McMoRan — FCX, NYSE — $59.24** ([FCX investor page](https://investors.fcx.com/investors/stock-and-dividend-information/stock-quote/default.aspx)). Sells copper cathode and concentrate at LME/COMEX-linked prices. Breaks the link: gold and molybdenum by-product revenue; US sales price off COMEX, not LME.
- **Southern Copper — SCCO, NYSE — $164.08** ([Stock Analysis](https://stockanalysis.com/stocks/scco/)). Mined copper is the majority of revenue, unhedged. Breaks the link: low unit cost keeps margin positive across this price range; by-product credits.

Consumers (input cost falls with the copper price):

- **Mueller Industries — MLI, NYSE — $54.89** ([Morningstar](https://www.morningstar.com/stocks/xnys/mli/quote)). Buys copper cathode and scrap to make tube and fittings. Breaks the link: selling prices track COMEX copper, so the cost passes through; falling prices cut the value of metal in inventory.

**Gulf energy (Easing)**

Producers / carriers (revenue falls as the premium drains):

- **ExxonMobil — XOM, NYSE — $170.59** ([Yahoo Finance](https://finance.yahoo.com/quote/XOM/history/)). Upstream realizations follow Brent. Breaks the link: refining and chemicals margins move the other way on lower feedstock cost.
- **Frontline — FRO, NYSE — $46.97** ([Yahoo Finance](https://finance.yahoo.com/quote/FRO/history/)). VLCC and Suezmax fleet earns spot charter rates, which rise with rerouting and war-risk. Breaks the link: reopened Gulf flows add cargo volume even as voyage length falls.

Consumers (input cost falls):

- **Delta Air Lines — DAL, NYSE — $86.25** ([Yahoo Finance](https://finance.yahoo.com/quote/DAL/history/)). Jet fuel is its second-largest cost and it does not hedge. Breaks the link: jet crack spreads can stay wide while crude falls; fares adjust to fuel.

## 7. Ending signals

Nothing is marked Tightening this week.

Signs the easing reverses — copper: LME stocks falling back below 316,675 t (Nov 6) or cash−3M back above +175. Neither occurred as of Nov 13. Gulf energy: Brent front-month back above 98.32 (Nov 6), or a drop in transits once PortWatch reports again; attacks on tankers on Nov 8 and Nov 12 did not reverse the weekly loss.

## 8. Data gaps

- **Reports are not reaching the default branch.** Every report from Oct 3 to Nov 7 was committed to a separate `claude/nice-gates-*` branch; the default branch `claude/weekly-supply-squeeze-geecke` holds none after 2026-09-26. Last week's run could not see the Oct reports for the same reason.
- **Fetcher: `source_url` is wrong on nine Yahoo fields.** `brent_front_month`, `comex_copper_front_price`, `cme_live_cattle_front`, `cme_feeder_cattle_front`, `ice_cocoa_front_price`, `ice_cocoa_next_price`, `freight_tanker_etf` and `freight_drybulk_etf` carry a currency code (`USD`/`USX`) in place of a URL, and `ice_cocoa_front_next_spread` has ` | USD` appended. Table links for these fields are the Yahoo quote pages named in `README.md`, not the data file's value.
- **Fetcher: `cme_live_cattle_front` rolls contracts without marking it.** This week's value is February, last week's December; the field's week-on-week change is not like-for-like.
- **Copper:** COMEX warehouse stocks — unavailable (no free machine-readable endpoint; CME depository reports are Akamai-protected). Cause of the LME inflow rests on search summaries; spglobal.com and cruxinvestor.com are outside this session's allowed network domains.
- **Beef:** cattle prices single-source, last traded, not CME settlement. USDA inventory and heifer retention — no new release since 2026-07-24. Cattle on Feed — no new release since 2026-10-23.
- **Cocoa:** ICE certified stocks — unavailable (interactive/licensed report, no free endpoint). ICCO balance — unavailable (paid bulletin). The Steady call rests on price and spread alone.
- **Data center spending:** no fetcher field; the Oct 21–29 releases were never confirmed against IR pages.
- **Gulf energy:** Hormuz daily transits — unavailable ("PortWatch lookup failed: no features returned (keys: ['error'])"); first failure of this field. JKM spot — unavailable (proprietary Platts assessment). Asia LNG monthly index — as_of 2026-09-01, 74 days old, no fresh data, and not JKM. Brent spot (Nov 11) and front-month (Nov 13) are two days apart. The Easing call rests on prices and a freight proxy; the transit flow is unmeasured.
- **Exposed companies:** closes come from search summaries of quote pages, single date, not cross-checked beyond the sources linked. MLI sources differed by cents (54.86–54.89).
