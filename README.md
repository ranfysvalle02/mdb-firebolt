# mdb-firebolt

**The same question, answered faster and on fresher data.** A runnable companion to the post [*Stop Building Bridges Between What Happened and What Happens Next*](./blog.md), about MongoDB's acquisition of [Firebolt](https://www.mongodb.com/company/blog/news/mongodb-acquires-firebolt) and what a columnar engine next to your documents changes for applications and AI agents.

Two scripts, two stories:

| Script | Story | What it shows |
|---|---|---|
| [`demo.py`](./demo.py) | **Freshness** | A merchant asks *"What should I restock before the weekend?"* Last night's data says Austin. Live data says Denver, and shows why: a nested `promo` field that didn't exist yesterday. No `ALTER TABLE`, no mapping file. |
| [`bench.py`](./bench.py) | **Speed** | The same 500,000 nested orders in MongoDB and Firebolt, with identical results verified, and the same aggregation timed 30 times on each engine. |

## Results

`demo.py`:

```text
Last night's answer: [['Austin', None, 3], ['Denver', None, 1]]
Right now:           [['Denver', 'FLASH20', 6], ['Austin', None, 4], ['Denver', None, 1]]
```

`bench.py` on an Apple M4 Max, single node, no secondary indexes:

```text
  MongoDB $group aggregate   p50   102.0 ms   p95   103.6 ms
  Firebolt SQL aggregate     p50     3.1 ms   p95     3.6 ms
```

That's about **33x faster at the median**. This laptop test shows relative speed, not production performance. Adding a compound index on the MongoDB side didn't change the result. The post explains why the usual alternative, rollup collections, doesn't fully solve the problem.

## Run it

Requires Docker and Python 3 (tested on 3.11).

```bash
git clone https://github.com/ranfysvalle02/mdb-firebolt.git && cd mdb-firebolt
docker compose up -d
pip install pymongo firebolt-sdk
python demo.py
python bench.py
```

> [!WARNING]
> Each run drops and recreates the `shop.orders` and `shop.bench_orders` MongoDB collections and the Firebolt `orders` and `bench_orders` tables on `localhost`. Use these containers, not a database containing data you need.

`docker-compose.yml` starts:

- **[MongoDB Atlas Local](https://hub.docker.com/r/mongodb/mongodb-atlas-local)** on port `27017`. It runs as a replica set, which change streams require.
- **[Firebolt Core](https://github.com/firebolt-db/firebolt-core)** on port `3473`, Firebolt's free, self-hosted engine.

## What's real and what's simulated

- **Simulated:** Firebolt's native MongoDB change data capture (CDC) is in private preview, so `demo.py` plays that part by hand with a change stream. It writes documents in relaxed Extended JSON, as native CDC does, and handles inserts only.
- **Not yet available:** MongoDB's integrated, automatically synced experience is announced for *"the coming months."*
- **In preview:** Firebolt's `JSON` type is in public preview.

The post's appendix tracks each claim's status and source.

## Files

```text
blog.md              the post
demo.py              freshness demo (5 orders)
bench.py             speed benchmark (500k orders)
docker-compose.yml   MongoDB Atlas Local + Firebolt Core
```

## License

[MIT](./LICENSE) for this repo. Firebolt Core is distributed under the [Elastic License 2.0](https://github.com/firebolt-db/firebolt-core/blob/main/LICENSE.md).
