# Master prompt — FP&A Reporting Workspace

Copy everything below the line into Claude, attach your workbook (or the sample in `/data`), and fill in the `{{placeholders}}`.

---

You are an FP&A analyst building an interactive monthly reporting workspace from the attached workbook for **{{Company name}}** (currency **{{USD}}**, fiscal year starts **{{January}}**).

## Step 1 — Discovery (do this before building anything)
1. List every sheet and column you find. Map each column to the standard fields: `year, month, scenario, statement, section, account, amount`. Use `templates/input_mapping.md` as the format.
2. Identify the scenarios present (Actual, Budget, Forecast, Prior Year) and the **last closed month**. Ask me to confirm it.
3. Show me the reporting definitions you intend to use (`templates/reporting_definitions.md`) and ask me to confirm or change them. In particular confirm:
   - sign convention (are costs stored as positive numbers?)
   - how the Latest Estimate is formed (closed actuals + forecast for open months only)
   - the materiality threshold for variance commentary
4. List any gaps (missing months, unmapped accounts, scenarios without a balance sheet). **Do not fill gaps with invented numbers.**

Stop and wait for my confirmation after Step 1.

## Step 2 — Build
Build a single self-contained HTML file with seven views that share one set of controls (Year, Month, Period = Month / QTD / YTD / Full year, Compare = Actual vs Budget / Actual vs Prior Year / Latest Estimate vs Budget / Latest Estimate vs Prior Year):

1. Dashboard — KPI tiles, revenue trend, EBITDA by month, top three profit drivers
2. Income Statement — selected vs comparison, Var $, Var %, % of revenue, profit impact
3. Balance Sheet — closing balances at the last month of the selection, balance check, working-capital metrics
4. Margins — margins from totals, monthly margin trend
5. Budget Variance — EBITDA bridge and variance table sorted by profit impact, materiality flag
6. Forecast — Actual YTD + Forecast = Latest Estimate vs Budget and Prior Year, assumption flags
7. Action Plan — items from material unfavourable variances and forecast flags, each with owner, due date, status

Use the section prompts in `/prompts` for the detailed rules of each view.

## Calculation rules (non-negotiable)
- Revenue and expenses **belong to a period**: sum the months in the selection.
- Balance sheet items **belong to a closing date**: never sum them; take the last month of the selection.
- Margins are **profit total ÷ revenue total** for the selection — never an average of monthly percentages.
- Variance = Selected − Comparison. For cost lines a positive variance is **unfavourable**. Always show a separate "profit impact" column so the sign is never ambiguous.
- The Latest Estimate replaces only months that are not closed. Closed actuals are never overwritten.
- If a selection includes months with no actuals, show "—" and say why. Never display zero for missing data.

## Validation (show in the file)
Add a "Checks" panel that runs on load: balance sheet balances for every month, retained earnings rolls forward by net income, Latest Estimate = actual + forecast, subtotals tie. List known gaps and untested items explicitly.

## Commentary
Draft commentary using `templates/commentary_template.md`: **difference → evidence → next step → owner**. An account balance does not explain an operational cause; when evidence is missing, say what evidence is needed instead of guessing.

## Output
1. The HTML file.
2. A short build note: definitions used, mappings, checks passed/failed, open questions.
3. Compare your key figures with `docs/expected_results.md` (sample data) or with my reported totals (my data) and show the differences.
