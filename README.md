# Operations Performance Analysis: Order Fulfilment, SLA and Backlog

A small end-to-end analysis of order fulfilment: generate data, clean it, query it with SQL, test the results, chart them and export a summary for Excel. The scope is orders only (SLA performance and open-order backlog). It does not cover support tickets.

**The data is synthetic.** `generate_data.py` creates 5,000 random orders with a fixed seed. It is not data from any real company. The branch differences below were built into the generator, so the results show the method, not real business findings.

**Built with AI assistance.** The code and documentation were written with an AI assistant.

## What it does
1. `generate_data.py` creates `data/orders_synthetic.csv` (order, branch, category, SLA hours, status, resolution time, delay reason). It adds duplicates and inconsistent branch spelling on purpose.
2. `analysis.py` cleans the data (removes duplicates, fixes branch names), then splits it:
   - closed orders: SLA breach = resolution hours greater than SLA hours
   - open orders: backlog analysis by branch and age as of 2026-07-01
3. It loads both into SQLite, runs `queries.sql` (5 queries), and saves `output/dashboard.png` and `output/summary.xlsx` (one sheet per query).
4. `test_project.py` checks the results: no duplicate orders, row counts add up, breach flag matches the rule, and the SQL results match independent pandas calculations.

## Run it
```
./run.sh
```
This installs requirements, generates the data, runs the analysis and runs the tests (needs Python 3).

## Sample output (synthetic data)
- 5,025 raw rows -> 5,000 unique orders: 4,791 closed (SLA analysis) and 209 open (backlog).
- SLA breach rate by branch: Kozhikode 41.3%, Trivandrum 34.8%, Kochi 26.8%, Thrissur 17.2%.
- Breach reasons are spread fairly evenly (about 19-21% each).
- Open backlog: Kochi 68, Thrissur 61, Kozhikode 42, Trivandrum 38 orders; most are older than 30 days.

## Skills shown
SQL (aggregation, CASE, subqueries, date grouping), Python (pandas, matplotlib, SQLite), data cleaning, SLA and backlog KPIs, automated tests, Excel export.

## Limits
Synthetic data, one random seed, no statistical testing, no ticket data. A real version would use actual operational data and investigate why branches differ.
