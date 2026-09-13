# Weekly supply squeeze routine

This is the prompt the weekly routine runs. It performs **no data fetching**: a
GitHub Action (`.github/workflows/fetch-data.yml`) collects raw figures on
GitHub's runners and commits them to `data/`. See `README.md` for how the two
stages fit together.

---

Weekly check on five supply squeezes. Report what the numbers say and what
changed. Do not recommend trades.

Work on the repository's default branch. Detect its name; do not assume it is
`main`. Do not create a branch.

## STEP 1 — READ LAST WEEK

List `reports/` and open the most recent `squeeze-report-*.md`, choosing it the
same way as the data file below: highest `YYYY-MM-DD`, then highest `-N` rerun
suffix, parsed from the filename rather than taken from a sorted list. Its
numbers table is the basis for this week's comparison. The file is
the source of truth, not recall. If none exists, say so in the headline and treat
this as the baseline week with an empty comparison column. Never reconstruct last
week's numbers from news or estimates.

## STEP 2 — READ THIS WEEK'S DATA FILE

Do not fetch any figure yourself. Read the newest `data/*.json`.

Pick that file by parsing filenames, not by sorting the list: take the highest
`YYYY-MM-DD`, then among files sharing that date take the highest `-N` rerun
suffix (a plain date with no suffix is run 1). **A plain alphabetical sort picks
the wrong file** — `2026-09-13-2.json` sorts *before* `2026-09-13.json` — so
never just take the last entry of a sorted list.

Check its age first. **If the newest data file's `run_date` is more than eight
days before today, stop assessing:** say in the headline that the fetcher has not
run, mark every area unassessed, note the data file's date and age, and skip the
status, exposure and ending-signal sections. Still write and commit the report.

Otherwise use only the figures in that file. Each field carries `value`, `unit`,
`as_of`, `source_url`, `source_tier`, `status` and `note`.

Translate status to the report as follows:

- `ok` — usable figure. Still check `as_of`: if it is more than a month before
  today, treat it as **no fresh data** and say so.
- `conflict` — sources disagreed by more than 1%. Report as **no fresh data** and
  quote both values from `note`.
- `unavailable` — report as **no fresh data** and carry the reason from `note`
  into Data gaps.

Never carry last week's number forward as this week's. Never estimate a value the
data file does not contain. Never treat a field's `note` as a figure.

Fields by area:

| Area | Fields |
|---|---|
| Copper | `lme_copper_stocks`, `lme_copper_cash`, `lme_copper_3m`, `lme_copper_cash_3m_spread`, `lme_copper_spread_change`, `lme_copper_stocks_change`, `comex_copper_stocks`, `comex_copper_front_price` |
| Beef | `cme_live_cattle_front`, `cme_feeder_cattle_front`, `usda_cattle_report_release_date`, `usda_cattle_inventory_total`, `usda_beef_heifer_retention`, `usda_cattle_on_feed_report_release_date`, `usda_cattle_on_feed_total`, `usda_cattle_placements`, `usda_cattle_marketings` |
| Cocoa | `ice_cocoa_certified_stocks`, `ice_cocoa_front_price`, `ice_cocoa_next_price`, `ice_cocoa_front_next_spread`, `icco_balance` |
| Gulf energy | `brent_spot`, `brent_front_month`, `hormuz_daily_transits`, `freight_tanker_etf`, `freight_drybulk_etf`, `jkm_lng_spot`, `lng_asia_monthly_index` |
| Data center spending | no data source; see below |

Slow-moving series. Report these only when a new release has appeared since the
last report; otherwise write "no new release since [date]" in one line and do not
mark a status for that figure:

- **USDA cattle inventory and heifer retention** — compare
  `usda_cattle_report_release_date.as_of` against the release date cited in last
  week's report. Cattle futures are still assessed weekly.
- **Data center spending** — quarterly capex and forward guidance from the
  largest cloud providers. There is no fetcher field for this. Report the last
  known release date from last week's report and write "no new release since
  [date]" unless a new quarterly release has appeared, which you may confirm by
  web search of company investor-relations pages only.

The data file also carries a top-level `series` block (currently
`series.lme_copper`, ~30 sessions). **Read it.** A single print shows a level; the
series shows whether the premium for immediate delivery is building or draining,
which is the part that leads. Quote the direction of the spread over the window,
not just today's value.

`hormuz_daily_transits` replaces the old news-sourced Hormuz status, but it lags
roughly a week — check `as_of`. Web search still covers shipping *events*.

`lng_asia_monthly_index` is a **monthly IMF index, not JKM spot**. It is not a
substitute for `jkm_lng_spot`. If you cite it, label it as the monthly index and
still mark JKM itself as no fresh data.

## STEP 3 — JUDGE EACH AREA

Compare with last week and with the normal range. Mark each:

- **Tightening** = price rising AND stocks falling AND a premium for immediate
  delivery.
- **Easing** = stocks rebuilding, premium gone, or price falling from a high.
- **Steady** = within normal weekly movement.
- **Unclear** = signals disagree or data missing.

Use unclear freely; it is right more often than it feels. Do not repeat last
week's conclusion if this week's numbers do not support it.

## STEP 4 — WEB SEARCH, ONLY FOR TWO THINGS

Web search is allowed for exactly two purposes:

1. Explaining **why** a number in the data file moved more than usual.
2. The **Strait of Hormuz shipping status**, which has no data source.

Do not use it to fetch or replace any figure the fetcher covers, and do not add
general commentary, forecasts or price predictions. If nothing moved, the news
section is empty.

## STEP 5 — WRITE THE REPORT

Write tight. A reader should get the whole picture from the verdict block alone.
Cut hedging: no "appears to", "may suggest", "it is worth noting", "arguably",
"broadly". State the number, then the call. If a sentence survives without its
qualifier, drop the qualifier.

Sections, in this order:

### 1. Headline

One sentence on what changed across all five areas. If most areas are unclear or
missing data, lead with that rather than with the one area that moved.

### 2. Verdict

One line per area, number first, in this shape:

> **Copper — Easing.** Cash−3M +5.5 vs +535 peak (Aug 17); stocks −6.2% over 30 sessions.

One line each, about 20 words maximum. The call is Tightening, Easing, Steady or
Unclear — or, for a slow-moving series with no new release, "no new release since
[date]" with no call. **This replaces the old status section; do not write both.**

### 3. Numbers table

Columns: area, figure, this week, **as of**, last week, direction, **trend**,
source link, **source tier**. The trend column carries the series direction where
a series exists (for example `series.lme_copper`); otherwise "—".

### 4. What changed

Only areas that moved. Three sentences maximum each. An area that did not move
gets no paragraph.

### 5. Transmission map

Per STEP 5C.

### 6. Exposed companies

Per STEP 5B.

### 7. Ending signals

For anything tightening, note signs it is resolving — stocks rebuilding, new
supply, buyers switching, capex guidance cut.

### 8. Data gaps

Everything unverified this week, stated plainly as unassessed, carrying each
field's `note` reason.

## STEP 5B — EXPOSED COMPANIES

For each area marked **tightening or easing only**, list companies with direct
operational exposure, grouped as producers/beneficiaries and consumers/victims.
Give ticker, exchange, and one line stating the mechanical link to the squeeze.
Include the most recent close and its date.

Skip any area marked steady or unclear. No exposure list for an area you could
not verify this week. If a company's close cannot be sourced, leave the company
out rather than printing an unsourced price.

This is a factual exposure map, not a recommendation. Do not rank, score or
suggest which to buy. Do not comment on valuation, technicals or entry points. Do
not say anything is well positioned, cheap, or a beneficiary of a trend beyond
the direct mechanical link. For each company add what would break the link — it
hedges the exposure, the squeeze is already in guidance, or that input is a small
share of revenue.

## STEP 5C — TRANSMISSION MAP

Only for areas marked **tightening or easing**. Skip steady, unclear, and
anything you could not verify this week. If no area qualifies, write "No area
qualifies this week." and move on.

A squeeze transmits through six layers, fastest to slowest. The instrument
differs by industry; the role does not.

| Layer | Role | Copper | Cocoa | Beef | Energy |
|---|---|---|---|---|---|
| 1 Trigger | discrete event | mine strike, export ban | harvest failure, disease | drought, feed cost | attack, closure |
| 2 Risk price | market pricing the peril | options skew | options skew | options skew, LRP | war-risk premium |
| 3 Bottleneck | the physical constraint | cancelled warrants, stocks | port arrivals | **placements**, heifer retention | transits, ton-miles |
| 4 Access premium | pay to get it now vs later | cash−3M, regional premium | front−next, origin diff | cash−futures basis | freight rate |
| 5 Forward test | sustained or transient | LME curve | ICE curve | deferred futures | FFA curve |
| 6 Equity | last to move | miners | grinders *(victims)* | packers | tankers, E&P |

Two structural facts to apply, not restate:

- **Layer 4 is always "what do you pay to get it now or here, versus later or
  elsewhere."** In equipment-led squeezes that premium is denominated in **time**
  — lead times, queue position — not money.
- **Layer 3 always has a leading sub-component that a level metric hides.**
  Flows lead, levels lag. Prefer the flow.

Report at **sector level, not ticker level**. For each sector give:

- the mechanism, one line — why this sector's margin moves
- **what breaks the link** — it hedges, it passes the cost through, the input is
  a small share of its cost base, or the squeeze is already in guidance

Mark any link whose sign you cannot establish as **ambiguous** and say so, rather
than assigning it a direction.

Two rules that keep this honest:

- **Most squeezes have no listed beneficiary.** Where the gain accrues to
  private, foreign or smallholder producers, say that plainly instead of reaching
  for a listed name. Note when the entire listed universe sits on the victim side.
- **The map says where margin moves. It says nothing about what is already
  priced.** Never present it as an opportunity and never imply timing.

## STEP 6 — COMMIT

Write the report to `reports/squeeze-report-YYYY-MM-DD.md` using **today's real
run date**. If that file already exists, append `-2` (then `-3`, and so on) —
never file a report under a different day's date, and never overwrite an earlier
report. Keep the table format identical each week so next week's run can read it.

Commit and push to the default branch with message
`Weekly squeeze report YYYY-MM-DD` (the run date, without any rerun suffix).
State the filename, branch and commit result at the end.

## RULES

- Never recommend buying or selling, and never name a ticker as an opportunity.
  Exposure may be described as fact only.
- Every figure needs a source link; unlinked figures stay out of the table.
- Report `source_tier` for every figure. Prefer primary where both exist.
- Never smooth over missing data. `unavailable`, `conflict` and stale all read as
  no fresh data.
- If most areas are unclear or missing data, lead with that rather than the one
  area that moved.
- If the data file is missing entirely, say so at the top in one line and commit
  the report anyway with every area marked unassessed.
