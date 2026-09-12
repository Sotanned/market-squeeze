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

List `reports/` and open the most recent `squeeze-report-*.md` by date in the
filename. Its numbers table is the basis for this week's comparison. The file is
the source of truth, not recall. If none exists, say so in the headline and treat
this as the baseline week with an empty comparison column. Never reconstruct last
week's numbers from news or estimates.

## STEP 2 — READ THIS WEEK'S DATA FILE

Do not fetch any figure yourself. Read the newest `data/*.json` (highest date in
the filename; a `-2` suffix is a same-day rerun and sorts after the plain date).

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
| Copper | `lme_copper_stocks`, `lme_copper_cash`, `lme_copper_3m`, `lme_copper_cash_3m_spread`, `comex_copper_stocks`, `comex_copper_front_price` |
| Beef | `cme_live_cattle_front`, `cme_feeder_cattle_front`, `usda_cattle_report_release_date`, `usda_cattle_inventory_total`, `usda_beef_heifer_retention` |
| Cocoa | `ice_cocoa_certified_stocks`, `ice_cocoa_front_price`, `ice_cocoa_next_price`, `ice_cocoa_front_next_spread`, `icco_balance` |
| Gulf energy | `brent_spot`, `brent_front_month`, `jkm_lng_spot`, `lng_asia_monthly_index` |
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

- **Headline**: one sentence on what changed across all five areas.
- **Numbers table**: area, figure, this week, **as of**, last week, direction,
  source link, **source tier** (primary or secondary, from `source_tier`).
- **Status**: each area marked, with one sentence of evidence naming the figure.
- **What changed**: only areas that moved, one short paragraph each.
- **Ending signals**: for anything tightening, note signs it is resolving —
  stocks rebuilding, new supply, buyers switching, capex guidance cut.
- **Data gaps**: everything unverified this week, stated plainly as unassessed,
  carrying each field's `note` reason.

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
