"""Generate illustrative sample data for the FP&A Reporting Kit (fictional company)."""
import csv, json, random
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

random.seed(42)
import pathlib
OUT = str(pathlib.Path(__file__).resolve().parent.parent)
SEAS = [0.85, 0.80, 0.90, 0.95, 1.00, 0.95, 0.90, 0.95, 1.00, 1.05, 1.25, 1.40]
LAST_CLOSED = 10  # Oct-2026 is the last closed month

PL = ["Revenue - Direct-to-Consumer", "Revenue - Wholesale", "Cost of Goods Sold",
      "Fulfillment & Freight", "Salaries & Benefits", "Marketing & Advertising",
      "Rent & Occupancy", "Technology & Software", "Professional Fees", "Other G&A",
      "Depreciation & Amortization", "Interest Expense", "Income Tax"]
BS = ["Cash", "Accounts Receivable", "Inventory", "Prepaid Expenses", "PP&E (net)",
      "Accounts Payable", "Accrued Liabilities", "Deferred Revenue", "Long-term Debt",
      "Share Capital", "Retained Earnings"]
SECTION = {a: "Revenue" for a in PL[:2]}
SECTION.update({a: "Cost of Sales" for a in PL[2:4]})
SECTION.update({a: "Operating Expenses" for a in PL[4:10]})
SECTION.update({PL[10]: "D&A", PL[11]: "Financing", PL[12]: "Tax"})
SECTION.update({a: "Assets" for a in BS[:5]})
SECTION.update({a: "Liabilities" for a in BS[5:9]})
SECTION.update({a: "Equity" for a in BS[9:]})

def n(x, pct=0.02):
    return round(x * (1 + random.uniform(-pct, pct)), 0)

def pl_month(dtc, wh, cogs_pct, frt_pct, sal, mkt_pct, tech, prof, debt):
    rev = dtc + wh
    r = {PL[0]: dtc, PL[1]: wh, PL[2]: rev * cogs_pct, PL[3]: rev * frt_pct,
         PL[4]: sal, PL[5]: dtc * mkt_pct, PL[6]: 45000, PL[7]: tech,
         PL[8]: prof, PL[9]: n(20000, 0.08), PL[10]: 30000, PL[11]: debt * 0.07 / 12}
    r = {k: round(v, 0) for k, v in r.items()}
    pbt = r[PL[0]] + r[PL[1]] - sum(r[k] for k in PL[2:12])
    r[PL[12]] = round(max(pbt, 0) * 0.25, 0)
    return r

rows = []  # year, month, scenario, account, amount
def add(year, m, scen, d):
    for k, v in d.items():
        rows.append((year, m, scen, k, v))

# ---------- P&L ----------
pl = {}  # (year, scen) -> {m: dict}
debt_open_2025 = 1_440_000
def debt_at(year, m):  # closing debt, amortising 20k/month from 1.44M at Dec-2024
    k = (year - 2025) * 12 + m
    return debt_open_2025 - 20000 * k

pl[(2025, "Actual")] = {}
for m in range(1, 13):
    s = SEAS[m - 1]
    pl[(2025, "Actual")][m] = pl_month(n(650000 * s), n(350000 * s), 0.42, 0.060,
                                       n(195000, 0.01), 0.11, 27000, n(15000, 0.1), debt_at(2025, m - 1))
pl[(2026, "Budget")] = {}
for m in range(1, 13):
    s = SEAS[m - 1]
    pl[(2026, "Budget")][m] = pl_month(round(650000 * s * 1.12, -2), round(350000 * s * 1.08, -2), 0.42, 0.060,
                                       210000 if m < 4 else 222000, 0.11, 28000, 15000, debt_at(2026, m - 1))
pl[(2026, "Actual")] = {}
for m in range(1, LAST_CLOSED + 1):
    b = pl[(2026, "Budget")][m]
    dtc_f = 1.01 if m <= 4 else [0.96, 0.94, 0.93, 0.92, 0.93, 0.94][m - 5]
    wh_f = 1.00 if m <= 5 else [1.07, 1.09, 1.10, 1.10, 1.11][m - 6]
    frt = 0.061 if m <= 6 else {7: 0.078, 8: 0.080, 9: 0.077, 10: 0.070}[m]
    mkt = 0.112 if m <= 4 else 0.13
    sal = round(b[PL[4]] * 0.97, 0)
    tech = 27500 if m < 3 else 31500
    prof = 45000 if m == 8 else n(15000, 0.1)
    pl[(2026, "Actual")][m] = pl_month(n(b[PL[0]] * dtc_f, 0.01), n(b[PL[1]] * wh_f, 0.01), 0.428, frt,
                                       sal, mkt, tech, prof, debt_at(2026, m - 1))
pl[(2026, "Forecast")] = {}
for m in range(LAST_CLOSED + 1, 13):
    b = pl[(2026, "Budget")][m]
    pl[(2026, "Forecast")][m] = pl_month(round(b[PL[0]] * 0.95, -2), round(b[PL[1]] * 1.08, -2), 0.428, 0.068,
                                         round(b[PL[4]] * 0.98, 0), 0.125, 31500, 16000, debt_at(2026, m - 1))

def ni(d):
    return d[PL[0]] + d[PL[1]] - sum(d[k] for k in PL[2:])

# ---------- Balance sheet (closing balances; cash is the balancing figure) ----------
RE_OPEN_2025 = 1_100_000
def bs_from(d, m_debt_year, m, re, scen):
    rev_wh, rev_dtc = d[PL[1]], d[PL[0]]
    cogs = d[PL[2]]
    inv_mult = 2.0 if scen == "Budget" else (2.6 if (m_debt_year == 2026 and m >= 7) else 2.2)
    capex_months = (m_debt_year - 2025) * 12 + m
    ppe = 1_500_000 + capex_months * (35000 - 30000)
    b = {"Accounts Receivable": round(rev_wh * 1.5 + rev_dtc * 0.05, 0),
         "Inventory": round(cogs * inv_mult, 0), "Prepaid Expenses": 60000, "PP&E (net)": ppe,
         "Accounts Payable": round((cogs + d[PL[3]]) * 0.9, 0),
         "Accrued Liabilities": round(sum(d[k] for k in PL[4:10]) * 0.35, 0),
         "Deferred Revenue": round(rev_dtc * 0.04, 0), "Long-term Debt": debt_at(m_debt_year, m),
         "Share Capital": 2_000_000, "Retained Earnings": round(re, 0)}
    le = sum(b[k] for k in BS[5:])
    b["Cash"] = le - sum(b[k] for k in BS[1:5])
    return {k: b[k] for k in BS}

bs = {}
re = RE_OPEN_2025
bs[(2025, "Actual")] = {}
for m in range(1, 13):
    re += ni(pl[(2025, "Actual")][m]); bs[(2025, "Actual")][m] = bs_from(pl[(2025, "Actual")][m], 2025, m, re, "Actual")
re_close_2025 = re
re = re_close_2025; bs[(2026, "Budget")] = {}
for m in range(1, 13):
    re += ni(pl[(2026, "Budget")][m]); bs[(2026, "Budget")][m] = bs_from(pl[(2026, "Budget")][m], 2026, m, re, "Budget")
re = re_close_2025; bs[(2026, "Actual")] = {}
for m in range(1, LAST_CLOSED + 1):
    re += ni(pl[(2026, "Actual")][m]); bs[(2026, "Actual")][m] = bs_from(pl[(2026, "Actual")][m], 2026, m, re, "Actual")
bs[(2026, "Forecast")] = {}
for m in range(LAST_CLOSED + 1, 13):
    re += ni(pl[(2026, "Forecast")][m]); bs[(2026, "Forecast")][m] = bs_from(pl[(2026, "Forecast")][m], 2026, m, re, "Forecast")

for (y, s), md in list(pl.items()) + list(bs.items()):
    for m, d in md.items():
        add(y, m, s, d)

# ---------- outputs ----------
MON = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
with open(f"{OUT}/data/financials_long.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["year", "month", "period", "scenario", "statement", "section", "account", "amount_usd"])
    for y, m, s, a, v in rows:
        w.writerow([y, m, f"{MON[m-1]}-{y}", s, "IS" if a in PL else "BS", SECTION[a], a, int(v)])

accounts = [{"account": a, "statement": "IS" if a in PL else "BS", "section": SECTION[a],
             "sign": "credit" if a in PL[:2] or a in BS[5:] else "debit"} for a in PL + BS]
with open(f"{OUT}/data/chart_of_accounts.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["account", "statement", "section", "sign"]); w.writeheader(); w.writerows(accounts)

wb = Workbook()
ws = wb.active; ws.title = "README"
for r in [["Cedar & Pine Home Goods Inc. - illustrative FP&A sample data (fictional company)"],
          ["All figures USD, illustrative only."], ["Actuals: Jan-2025 to Oct-2026 (Oct-2026 = last closed month)"],
          ["Budget: FY2026 (12 months)"], ["Forecast: Nov-Dec 2026 (latest estimate = Actual YTD + Forecast)"],
          ["Balance sheet values are month-end closing balances; Cash is the balancing figure in this sample."],
          ["Sheets: Data (long format), Accounts, IS_Wide_<scenario>_<year>"]]:
    ws.append(r)
ws["A1"].font = Font(bold=True, size=13)
wd = wb.create_sheet("Data"); wd.append(["year", "month", "period", "scenario", "statement", "section", "account", "amount_usd"])
for y, m, s, a, v in rows:
    wd.append([y, m, f"{MON[m-1]}-{y}", s, "IS" if a in PL else "BS", SECTION[a], a, int(v)])
wa = wb.create_sheet("Accounts"); wa.append(["account", "statement", "section", "sign"])
for a in accounts: wa.append(list(a.values()))
hdr = PatternFill("solid", fgColor="DDE8F7")
for (y, s), md in pl.items():
    w2 = wb.create_sheet(f"IS_{s}_{y}"); w2.append(["account"] + [f"{MON[m-1]}-{y}" for m in md])
    for a in PL: w2.append([a] + [int(md[m][a]) for m in md])
    for c in w2[1]: c.font = Font(bold=True); c.fill = hdr
    w2.column_dimensions["A"].width = 32
for sh in wb.worksheets:
    for c in sh[1]: c.font = Font(bold=True)
wb["Data"].column_dimensions["G"].width = 30
wb.save(f"{OUT}/data/sample_financials.xlsx")

data = {"company": "Cedar & Pine Home Goods Inc.", "currency": "USD", "lastClosed": {"year": 2026, "month": LAST_CLOSED},
        "plAccounts": PL, "bsAccounts": BS, "section": SECTION,
        "rows": [[y, m, s, a, int(v)] for y, m, s, a, v in rows]}
json.dump(data, open(f"{OUT}/data/financials.json", "w"))

# ---------- expected results (for testing the build) ----------
def tot(y, s, ms, f):
    return sum(f(pl[(y, s)][m]) for m in ms)
rev = lambda d: d[PL[0]] + d[PL[1]]
gp = lambda d: rev(d) - d[PL[2]] - d[PL[3]]
ebitda = lambda d: gp(d) - sum(d[k] for k in PL[4:10])
ytd = range(1, 11)
le = lambda f: tot(2026, "Actual", ytd, f) + tot(2026, "Forecast", [11, 12], f)
exp = {
    "YTD Oct-2026 Revenue Actual": tot(2026, "Actual", ytd, rev),
    "YTD Oct-2026 Revenue Budget": tot(2026, "Budget", ytd, rev),
    "YTD Oct-2026 Gross Profit Actual": tot(2026, "Actual", ytd, gp),
    "YTD Oct-2026 EBITDA Actual": tot(2026, "Actual", ytd, ebitda),
    "YTD Oct-2026 EBITDA Budget": tot(2026, "Budget", ytd, ebitda),
    "YTD Oct-2026 Net Income Actual": tot(2026, "Actual", ytd, ni),
    "YTD Oct-2026 Net Income Budget": tot(2026, "Budget", ytd, ni),
    "Oct-2026 Revenue Actual": rev(pl[(2026, "Actual")][10]),
    "Oct-2026 EBITDA Actual": ebitda(pl[(2026, "Actual")][10]),
    "FY2026 Revenue Latest Estimate": le(rev), "FY2026 Revenue Budget": tot(2026, "Budget", range(1, 13), rev),
    "FY2026 EBITDA Latest Estimate": le(ebitda), "FY2026 EBITDA Budget": tot(2026, "Budget", range(1, 13), ebitda),
    "FY2025 Revenue Actual": tot(2025, "Actual", range(1, 13), rev),
    "Cash 31-Oct-2026 Actual": bs[(2026, "Actual")][10]["Cash"],
    "Cash 31-Oct-2026 Budget": bs[(2026, "Budget")][10]["Cash"],
    "Inventory 31-Oct-2026 Actual": bs[(2026, "Actual")][10]["Inventory"],
}
json.dump({k: int(v) for k, v in exp.items()}, open(f"{OUT}/data/expected_results.json", "w"), indent=1)
for k, v in exp.items(): print(f"{k:40s} {v:>14,.0f}")
print("min cash", min(b["Cash"] for md in bs.values() for b in md.values()))
