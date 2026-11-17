# Input mapping

Map every source column and account to the standard model. Unmapped items stay visible in the build note.

## Columns
| Source sheet | Source column | Standard field | Notes |
|---|---|---|---|
| Data | year | year | |
| Data | month | month | 1–12 |
| Data | scenario | scenario | Actual / Budget / Forecast |
| Data | account | account | see account map |
| Data | amount_usd | amount | costs stored as positive numbers |

## Accounts
| Source account | Standard line | Section | Statement | Sign |
|---|---|---|---|---|
| Revenue - Direct-to-Consumer | Revenue - Direct-to-Consumer | Revenue | IS | credit |
| … | … | … | … | … |

Unmapped accounts: _list here_
