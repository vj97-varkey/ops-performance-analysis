"""Automated checks: data quality, SQL results vs independent pandas calculations."""
import sqlite3
import pandas as pd

raw = pd.read_csv("data/orders_synthetic.csv")
con = sqlite3.connect("output/ops.db")
closed = pd.read_sql_query("SELECT * FROM orders", con)
open_ = pd.read_sql_query("SELECT * FROM open_orders", con)

def test_no_duplicates_and_row_accounting():
    assert closed.order_id.is_unique and open_.order_id.is_unique
    assert not set(closed.order_id) & set(open_.order_id)
    assert len(closed) + len(open_) == raw.order_id.nunique()

def test_branch_names_clean():
    assert set(closed.branch) | set(open_.branch) == {"Thrissur", "Kochi", "Kozhikode", "Trivandrum"}

def test_breach_flag_matches_rule():
    assert ((closed.resolution_hours > closed.sla_hours).astype(int) == closed.breached).all()
    assert closed.resolution_hours.notna().all()

def test_branch_breach_sql_matches_pandas():
    sql = pd.read_sql_query([s for s in open("queries.sql").read().split(";") if "GROUP BY branch ORDER BY breach_pct" in s][0], con).set_index("branch")
    exp = (closed.groupby("branch").breached.mean() * 100).round(1)
    assert (sql.breach_pct - exp).abs().max() < 0.051
    assert sql.orders.sum() == len(closed)

def test_delay_reasons_cover_all_breaches():
    q = [s for s in open("queries.sql").read().split(";") if "delay_reason" in s and "GROUP BY delay_reason" in s][0]
    sql = pd.read_sql_query(q, con)
    assert sql.breached_orders.sum() == closed.breached.sum()
    assert "None" not in set(sql.delay_reason)

def test_backlog_sql_matches_pandas():
    q = [s for s in open("queries.sql").read().split(";") if "open_orders GROUP BY" in s][0]
    sql = pd.read_sql_query(q, con)
    assert sql.open_orders.sum() == len(open_)
    assert (sql.age_0_30d + sql.age_31_90d + sql.age_over_90d == sql.open_orders).all()
    assert (open_.age_days >= 0).all()

def test_monthly_trend_covers_all_closed_orders():
    q = [s for s in open("queries.sql").read().split(";") if "strftime" in s][0]
    assert pd.read_sql_query(q, con).orders.sum() == len(closed)
