"""Generate a SYNTHETIC operations dataset (orders with SLA tracking).
All data is randomly generated with a fixed seed. It is not real company data."""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 5000
branches = ["Thrissur", "Kochi", "Kozhikode", "Trivandrum"]
categories = ["Standard", "Express", "Bulk", "Return"]
sla_hours = {"Standard": 48, "Express": 24, "Bulk": 72, "Return": 60}
base_delay = {"Thrissur": 0.9, "Kochi": 1.0, "Kozhikode": 1.15, "Trivandrum": 1.05}
reasons = ["None", "Stock shortage", "Staff shortage", "Data entry error", "Customer unavailable", "Transport delay"]

dates = pd.to_datetime("2026-01-01") + pd.to_timedelta(rng.integers(0, 180, N), unit="D")
branch = rng.choice(branches, N, p=[0.25, 0.35, 0.2, 0.2])
category = rng.choice(categories, N, p=[0.5, 0.2, 0.15, 0.15])
sla = np.array([sla_hours[c] for c in category])
factor = np.array([base_delay[b] for b in branch])
# resolution time: lognormal around 80% of SLA, scaled by branch factor
resolution = rng.lognormal(mean=np.log(sla * 0.8), sigma=0.35) * factor
resolution = resolution.round(1)
breached = resolution > sla
reason = np.where(breached, rng.choice(reasons[1:], N), "None")
status = np.where(rng.random(N) < 0.04, "Open", "Closed")
resolution = np.where(status == "Open", np.nan, resolution)
# introduce a few data quality issues to clean later
branch = branch.astype(object)
idx = rng.choice(N, 40, replace=False)
branch[idx] = [b.upper() for b in branch[idx]]
df = pd.DataFrame({
    "order_id": [f"ORD{100000+i}" for i in range(N)],
    "order_date": dates.strftime("%Y-%m-%d"),
    "branch": branch,
    "category": category,
    "sla_hours": sla,
    "status": status,
    "resolution_hours": resolution,
    "delay_reason": reason,
})
dup = df.sample(25, random_state=1)
df = pd.concat([df, dup]).sample(frac=1, random_state=2).reset_index(drop=True)
df.to_csv("data/orders_synthetic.csv", index=False)
print("rows written:", len(df))
