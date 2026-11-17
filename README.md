# FP&A Reporting Kit for Claude

Turn a monthly Excel workbook into an interactive FP&A reporting workspace — seven connected views, one set of controls, built-in validation checks and draft variance commentary that follows a strict *difference → evidence → next step → owner* format.

**Try it first:** [open the live demo](https://buddhikaramanayake.github.io/fpa-reporting-kit/demo/) (or open `demo/index.html` locally). An overview deck is in [`docs/FPA_Reporting_Kit_Overview.pptx`](docs/FPA_Reporting_Kit_Overview.pptx). It runs on illustrative data for a fictional company, *Cedar & Pine Home Goods Inc.*

![Views](https://img.shields.io/badge/views-7-2a78d6) ![Data](https://img.shields.io/badge/data-illustrative-eb6834)

## What the workspace does

| View | Answers |
|---|---|
| Dashboard | How did we do this month / quarter / year, and what moved profit? |
| Income Statement | Which lines are over or under plan, and is that good or bad for profit? |
| Balance Sheet | Where do we stand at month-end — cash, inventory, working capital? |
| Margins | Why did gross and EBITDA margin change, in basis points? |
| Budget Variance | EBITDA bridge from Budget to Actual; which variances need an explanation? |
| Forecast | Full-year Latest Estimate vs Budget — and which forecast assumptions look too optimistic? |
| Action Plan | Who owns each issue, by when — editable and exportable to CSV |

Controls: **Year · Month · Period (Month / QTD / YTD / Full year) · Compare (Actual vs Budget, Actual vs Prior Year, Latest Estimate vs Budget, Latest Estimate vs Prior Year)**.

## Finance rules built into every view

- Revenue and expenses belong to a **period**; balance sheet items belong to a **closing date**.
- Margins come from **totals**, never from averaging monthly percentages.
- A positive cost variance is **unfavourable** — every table shows a separate profit-impact column.
- The Latest Estimate replaces **only open months**; closed actuals are never overwritten.
- Missing data shows "—", never zero.
- A balance doesn't explain an operating cause: commentary names the evidence still needed.
- Validation checks run on load (balance sheet balances, retained earnings roll-forward, LE tie-out, subtotal ties), and known gaps stay visible.

## What's inside

```
demo/index.html              Interactive seven-view worked example (open in a browser)
prompts/00_master_prompt.md  Master prompt: discovery → build → validate → commentary
prompts/01–07_*.md           One focused prompt per view
templates/                   Discovery brief, input mapping, reporting definitions,
                             validation checklist, commentary and action-plan templates
data/sample_financials.xlsx  Sample workbook (long-format data + wide P&L sheets)
data/financials_long.csv     Same data as CSV;  data/chart_of_accounts.csv
docs/expected_results.md     Key figures to test a build against
scripts/                     Regenerate sample data / rebuild the demo
```

## Use it with your own numbers

1. Explore the demo to see the expected behaviour.
2. Fill in `templates/discovery_brief.md`.
3. Paste `prompts/00_master_prompt.md` into Claude and attach your workbook. Claude maps your columns, proposes definitions and lists gaps — **confirm before it builds**.
4. Use the section prompts to refine individual views.
5. Run `templates/validation_checklist.md` before circulating anything.

## Rebuild the demo

```bash
pip install openpyxl
python scripts/generate_sample_data.py   # writes /data
python scripts/build_demo.py             # injects data into demo/index.html
```

## Disclaimer

The company, figures and commentary are fictional and illustrative. Demo commentary is produced by transparent rules that mirror the commentary template; in real use, Claude drafts it and the owner confirms the cause. Review all numbers and definitions against your own source data and accounting policies.
