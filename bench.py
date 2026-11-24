"""Same question, same data, two engines. Measure query latency side by side.

The dataset is generated once and loaded into both MongoDB and Firebolt. Row
counts and results are verified equal before any timing, so the comparison is
apples to apples. Neither side has a secondary index: this is the wide
aggregation scan that a columnar engine is built for.

Uses its own `shop.bench_orders` collection and `bench_orders` table, so it
never touches the demo's `shop.orders`. Both are dropped and recreated per run.
"""
import copy
import json
import random
import time

from firebolt.client.auth import FireboltCore
from firebolt.db import connect
from pymongo import MongoClient

N = 500_000
BATCH = 5_000
RUNS = 30
CITIES = ["Austin", "Denver", "Seattle", "Miami", "Chicago", "Boston"]
PROMOS = [None, None, None, "FLASH20", "WEEKEND"]
random.seed(7)

DATA = []
for i in range(N):
    doc = {"order_id": f"ord_{i}", "sku": "sneaker-red",
           "qty": random.randint(1, 5), "city": random.choice(CITIES)}
    code = random.choice(PROMOS)
    if code:
        doc["promo"] = {"code": code}  # same nested field the flash sale adds
    DATA.append(doc)
EXPECTED_UNITS = sum(d["qty"] for d in DATA)


def pct(xs, p):
    xs = sorted(xs)
    k = (len(xs) - 1) * p
    lo = int(k)
    return xs[lo] + (xs[min(lo + 1, len(xs) - 1)] - xs[lo]) * (k - lo)


def summarize(label, t):
    print(f"  {label:<26} p50 {pct(t,0.5):7.1f} ms   p95 {pct(t,0.95):7.1f} ms   min {min(t):7.1f} ms")


col = MongoClient("mongodb://localhost:27017/?directConnection=true")["shop"]["bench_orders"]
col.drop()

print(f"Loading {N:,} orders into MongoDB...")
for s in range(0, N, BATCH):
    col.insert_many(copy.deepcopy(DATA[s:s + BATCH]), ordered=True)
assert col.count_documents({}) == N

MONGO_PIPELINE = [
    {"$group": {"_id": {"city": "$city", "promo": "$promo.code"}, "units": {"$sum": "$qty"}}},
    {"$sort": {"units": -1}},
]

FB_QUESTION = """
    SELECT JSON_VALUE(doc.city) AS city, JSON_VALUE(doc.promo.code) AS promo,
           SUM(JSON_VALUE(doc.qty)::INT) AS units
    FROM bench_orders GROUP BY ALL ORDER BY units DESC;
"""

with connect(auth=FireboltCore(), url="http://localhost:3473", database="firebolt") as conn:
    fb = conn.cursor()
    fb.execute("DROP TABLE IF EXISTS bench_orders;")
    fb.execute("CREATE TABLE bench_orders (doc JSON);")

    print(f"Loading {N:,} orders into Firebolt...")
    for s in range(0, N, BATCH):
        chunk = [json.dumps(d) for d in DATA[s:s + BATCH]]
        fb.execute("INSERT INTO bench_orders VALUES " + ",".join(["(?::JSON)"] * len(chunk)) + ";", chunk)
    fb.execute("SELECT COUNT(*) FROM bench_orders;")
    assert fb.fetchone()[0] == N

    def mongo_ask():
        return list(col.aggregate(MONGO_PIPELINE))

    def fb_ask():
        fb.execute(FB_QUESTION)
        return fb.fetchall()

    key = lambda t: (t[0] or "", t[1] or "", t[2])
    mongo_rows = sorted(((r["_id"].get("city"), r["_id"].get("promo"), r["units"]) for r in mongo_ask()), key=key)
    fb_rows = sorted(((c, p, int(u)) for c, p, u in fb_ask()), key=key)
    assert sum(r[2] for r in mongo_rows) == sum(r[2] for r in fb_rows) == EXPECTED_UNITS
    print(f"\nRow counts equal {N:,} and results identical across engines: {mongo_rows == fb_rows}")
    print(f"Distinct (city, promo) groups: {len(fb_rows)}\n")

    for _ in range(3):  # warm up
        mongo_ask()
        fb_ask()

    print(f"Query latency over {RUNS} runs on {N:,} rows (no secondary indexes):")
    mongo_times, fb_times = [], []
    for _ in range(RUNS):
        t = time.perf_counter(); mongo_ask(); mongo_times.append((time.perf_counter() - t) * 1000)
    for _ in range(RUNS):
        t = time.perf_counter(); fb_ask(); fb_times.append((time.perf_counter() - t) * 1000)

    summarize("MongoDB $group aggregate", mongo_times)
    summarize("Firebolt SQL aggregate", fb_times)
    print(f"\n  Firebolt p50 speedup vs MongoDB: {pct(mongo_times,0.5)/pct(fb_times,0.5):.0f}x")

col.drop()
