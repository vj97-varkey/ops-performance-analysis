"""Clean the synthetic orders, split closed (SLA) and open (backlog), load into SQLite, run queries.sql, save charts and an Excel summary."""
import sqlite3
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("data/orders_synthetic.csv")
raw_rows = len(df)

# --- cleaning ---
df = df.drop_duplicates()
df["branch"] = df["branch"].str.strip().str.title()
AS_OF = pd.Timestamp("2026-07-01")
df["order_date"] = pd.to_datetime(df["order_date"])
# open orders have no resolution time yet: they are analysed separately as a backlog, not dropped
open_df = df[df["status"] == "Open"].copy()
open_df["age_days"] = (AS_OF - open_df["order_date"]).dt.days
df = df[df["status"] == "Closed"].copy()
df["order_date"] = df["order_date"].dt.strftime("%Y-%m-%d")
open_df["order_date"] = open_df["order_date"].dt.strftime("%Y-%m-%d")
df["breached"] = (df["resolution_hours"] > df["sla_hours"]).astype(int)
print(f"raw rows {raw_rows} -> {len(df)} closed orders (SLA analysis) + {len(open_df)} open orders (backlog analysis)")

# --- SQL ---
con = sqlite3.connect("output/ops.db")
df.to_sql("orders", con, if_exists="replace", index=False)
open_df.to_sql("open_orders", con, if_exists="replace", index=False)
queries = [q.strip() for q in open("queries.sql").read().split(";") if "SELECT" in q]
names = ["breach_by_branch", "breach_by_category", "delay_reasons", "monthly_trend", "open_backlog"]
results = {}
for name, q in zip(names, queries):
    results[name] = pd.read_sql_query(q, con)
    print("\n" + name + "\n" + results[name].to_string(index=False))
con.close()

# --- charts ---
fig, ax = plt.subplots(2, 3, figsize=(15, 8))
b = results["breach_by_branch"]; ax[0, 0].bar(b.branch, b.breach_pct, color="#4472c4"); ax[0, 0].set_title("SLA breach % by branch")
c = results["breach_by_category"]; ax[0, 1].bar(c.category, c.breach_pct, color="#ed7d31"); ax[0, 1].set_title("SLA breach % by category")
d = results["delay_reasons"]; ax[1, 0].barh(d.delay_reason[::-1], d.breached_orders[::-1], color="#70ad47"); ax[1, 0].set_title("Delay reasons (breached orders)")
m = results["monthly_trend"]; ax[1, 1].plot(m.month, m.breach_pct, marker="o"); ax[1, 1].set_title("Monthly SLA breach %"); ax[1, 1].tick_params(axis="x", rotation=45)
k = results["open_backlog"]; ax[0, 2].bar(k.branch, k.age_0_30d, label="0-30 days"); ax[0, 2].bar(k.branch, k.age_31_90d, bottom=k.age_0_30d, label="31-90 days"); ax[0, 2].bar(k.branch, k.age_over_90d, bottom=k.age_0_30d + k.age_31_90d, label="over 90 days"); ax[0, 2].set_title("Open-order backlog by age (as of 2026-07-01)"); ax[0, 2].legend()
ax[1, 2].axis("off")
for a in ax.flat: a.grid(alpha=0.3)
fig.suptitle("Operations Performance (synthetic data)")
fig.tight_layout(); fig.savefig("output/dashboard.png", dpi=110)

# --- Excel summary ---
with pd.ExcelWriter("output/summary.xlsx", engine="openpyxl") as w:
    for name, r in results.items():
        r.to_excel(w, sheet_name=name, index=False)
    for ws in w.book.worksheets:
        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = max(len(str(c.value)) for c in col) + 3
print("\nSaved output/dashboard.png, output/summary.xlsx, output/ops.db")
