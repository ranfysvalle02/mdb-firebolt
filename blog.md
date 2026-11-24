# Stop Building Bridges Between What Happened and What Happens Next

*MongoDB spent years absorbing complexity so developers wouldn't have to. Analytics is the next bridge to shorten.*

*By [Fabian Valle](https://github.com/ranfysvalle02). I've spent more than five years at MongoDB, building with the document model and watching it absorb one category of complexity after another. So yes, I'm biased. The sources and the distinction between what's available and what's planned are at the end.*

---

It's 4:52 on a Friday afternoon. A merchant on your commerce platform types one question into the AI assistant you launched last quarter:

**"What should I restock before the weekend?"**

The agent answers in under a second, with a tidy chart and a confident tone: send the red sneakers to Austin.

It's wrong.

Not hallucination-wrong. *Plumbing*-wrong. That morning, marketing launched a flash sale, and engineering added a nested `promo` field to flash-sale orders to track it. MongoDB took the new field without blinking. But the agent's analytics come from a warehouse that refreshes overnight, through a pipeline whose mapping file doesn't know `promo` exists. So the agent reasoned about today using yesterday.

The merchant moves the inventory. The red sneakers sell out in Denver, where the sale was actually working. On Monday, she opens a support ticket. In March, she doesn't renew.

The database was up. The pipeline was green. The answer was still wrong.

The story is fictional. The uncomfortable part is that you've lived some version of it: the field that shipped on Tuesday and showed up in the dashboard three sprints later, or the Slack thread titled *"why does the agent think we still have stock?"*

To see how we got here, we have to walk back a little.

## Migrations were the first tax

*Chapter I · 2009*

Before there was a pipeline problem, there was a schema problem.

Remember needing the landlord's permission to hang a picture? That could be a relational migration. Product wanted a nested `shipping_preferences` object, so you might write an `ALTER TABLE`, schedule the change, and hold your breath.

MongoDB's founding bet was almost rude in its simplicity: **store data the way your code already thinks about it.** A document, nested where your objects are nested, free to grow a new field on a Tuesday afternoon. By default, collections use a [flexible schema](https://www.mongodb.com/docs/manual/core/schema-validation/); applications can also enforce validation rules.

That meant less object-to-table translation and fewer migrations for changes like adding a field. Applications still need to manage schemas and compatibility. But some of the complexity moved off the developer's plate. **The platform absorbed it.**

Hold on to that phrase. It's the whole story.

## One more database, one more sync script

*Chapter II · The 2010s to now*

Then your app grew, and a common answer to a new need was: *spin up another database and sync it.* Maps, recommendations, search, AI. Each could mean a second copy of the truth, and a 3 AM page when the copies disagreed.

MongoDB kept asking a different question: *why is this a different kind of data?*

A coordinate is a nested array. A relationship is a reference. An embedding is an array of floats. A stream event is a document in motion. So the platform got [geospatial indexes](https://www.mongodb.com/docs/manual/core/indexes/index-types/geospatial/2dsphere/), [`$graphLookup`](https://www.mongodb.com/docs/manual/reference/operator/aggregation/graphLookup/), Vector Search with [Voyage AI](https://www.mongodb.com/company/blog/news/redefining-database-ai-why-mongodb-acquired-voyage-ai) embeddings, and [Atlas Stream Processing](https://www.mongodb.com/docs/atlas/atlas-stream-processing/). Each capability offered a chance to retire another sync script.

Analytics was a harder bridge to shorten.

## Nobody got paged

*Chapter III · Today*

For many teams, analytics still meant building a bridge, and for a sound reason: columnar engines are built for scanning billions of rows. Documents got flattened and passed down a line of connectors, queues, and transformation jobs until they reached a warehouse.

That doesn't mean MongoDB was sitting this out. The [BI Connector](https://www.mongodb.com/docs/bi-connector/current/) helped customers connect their BI tools to MongoDB; [Atlas SQL and the SQL Interface](https://www.mongodb.com/docs/sql-interface/) bring SQL access to live data, including integrations with Tableau and Power BI. MongoDB has been working with customers and partners on analytics for years. The BI Connector has since reached end of life, but that work didn't disappear. (More on that pattern in [Appendix B](#appendix-b-the-pattern-build-ahead-retire-without-sentiment).)

Firebolt is the next step in that story, not the first: the planned addition of a specialized analytics engine for demanding applications and agents.

It's a bucket brigade. Every handoff is another place for data to lag or need attention. Introduce a new kind of bucket, say a `promo` field, and a rigid mapping may need to change before the field reaches the other end.

MongoDB calls this the **data-movement tax**. It isn't paid in bytes. It's paid in lag, on-call rotations, and the quiet death of *"can we just add that field to the dashboard?"*

For years the tax was tolerable, because the readers were humans. A dashboard is starlight: by the time it reaches you, the thing it shows may have moved. That's fine for a Monday review.

Then agents started reading. An agent on overnight data is a GPS routing you around yesterday's traffic jam, perfectly confident, straight into today's. And where a dashboard is a dinner party, agents are the concession stand at halftime: thousands of orders at once, each one expected in under a second.

So go back to Friday and ask what it actually cost:

- **How long had it been wrong?** The pipeline was green, and nobody got paged. What would have told you?
- **Whose number is it?** Whoever owns that merchant's renewal wasn't in the architecture review. Should they have been?
- **How big is the gap, in hours?** Measure from "we shipped the field" to "an agent can reason about it."

That's the last bridge. Here's why it's coming down.

## Getting rid of the last bridge

*Chapter IV · November 2026*

On November 17, 2026, [MongoDB announced](https://www.mongodb.com/company/blog/news/mongodb-acquires-firebolt) that it had acquired Firebolt, a real-time analytics engine built for low-latency, high-concurrency workloads.

If you've followed the story this far, the move reads less like a surprise and more like the next sentence:

> **The flexibility of the document on the write path. The speed of a columnar engine on the read path. And, if the plan delivers, no pipeline for your team to build in between.**

MongoDB's stated plan is to run Firebolt's engine right alongside the database and keep the two in sync automatically, *"so there's no pipeline to build or manage."* The announcement says customers will be able to turn it on *"in the coming months,"* and links to a waitlist.

Instead of hiring more waiters to run plates from a kitchen across town, you move the kitchen next to the dining room.

This also isn't a weekend project with a new logo. Firebolt's CTO, Mosha Pasumansky, was an architect of Microsoft Analysis Services, co-invented the MDX query language, and led the technical development of Google's Dremel and BigQuery. CEO Benjamin Wagner came out of analytical-database research at the Technical University of Munich and built the engineering team behind the engine. That's years of hard engine work, now headed toward the document.

> **The document is the contract. Everything else is the platform's job.**

MongoDB is also plain about what this *isn't*. It doesn't replace your warehouse: warehouses and lakes *"remain the right fit for internal BI, reporting, and data science."* Firebolt is aimed at analytics *inside* live applications and agents. Knowing what not to absorb is part of the discipline. And for existing Firebolt customers, MongoDB's answer is two words: *"Nothing changes."*

If it's this fast and needs no pipeline, why not make it the warehouse too? Because the jobs are different. A warehouse usually brings together data from across the business, such as billing, CRM, and ad spend, for analysts and data scientists. The announced integration starts with your MongoDB data; analyzing other sources alongside it is a roadmap item, described as coming *"over time."* Real-time analytics is tuned for a different target: sub-second answers to many concurrent queries on fresh data, the questions your application or agent asks repeatedly. Some of the techniques behind that speed have costs too. Firebolt's own docs say aggregating indexes add work to every write, aren't suited to frequent row-level updates, and don't help when the grouping changes constantly. Use the right engine for each job.

## Open the hood

*Chapter V · What you can examine today*

> **How to read this chapter.** Firebolt's JSON type is in public preview, and its MongoDB CDC is in private preview. "Automatic column shredding" and the Similarweb numbers come from MongoDB's announcement. The local demo and benchmark later in this post ran on my laptop: they show behavior and relative speed, not production performance. Appendix A separates documented capabilities from the announced roadmap.

### The mailroom with labeled cubbies

Remember the `promo` field the pipeline never heard about? Firebolt's [native JSON type](https://docs.firebolt.io/reference-sql/data-types/json.md) stores a parsed JSON value in one column and lets you query nested paths with SQL. It doesn't preserve the original text's whitespace or key order, and retains only the last value for duplicate keys.

Think of a mailroom that sorts letters into labeled cubbies so you can find `promo` without sorting every letter again. Pasumansky describes the approach as **"smart automatic column shredding"**: columnar storage and vectorized processing, working with flexible schemas.

The [local demo](#build-the-small-version) inserts documents with different shapes, then queries a new nested field without changing the table definition. Documents without the field return `NULL`. No `ALTER TABLE`. No mapping file. No ticket.

Flexible isn't the same as forgiving, though. A malformed `qty` of `"two"` can't be cast to an integer: a plain `CAST` returns an error, while [`TRY_CAST`](https://docs.firebolt.io/reference-sql/functions-reference/conditional-and-miscellaneous/try-cast.md) returns `NULL` for a failed conversion. One fails loudly and the other returns a null, so choose on purpose.

### Real documents aren't flat

Real orders have line items, money, timestamps, and an `_id`, and they get updated and deleted. I tested each of these on Firebolt Core.

**Arrays of nested objects** work, with one rough edge. You can index into an array directly, as in `doc.line_items[0].sku`. Aggregating across *every* element of `line_items[]` requires unnesting, and today that means a round trip through text:

```sql
SELECT JSON_VALUE((li::JSON).sku) AS sku, SUM(JSON_VALUE((li::JSON).qty)::INT) AS units
FROM orders, UNNEST(JSON_POINTER_EXTRACT_ARRAY(doc::TEXT, '/line_items')) AS t(li)
GROUP BY ALL;
```

It returned the correct totals. A direct `JSON`-to-`ARRAY(JSON)` cast is rejected, so it's not as clean as the dot path yet.

**BSON types** arrive as [relaxed Extended JSON](https://docs.firebolt.io/guides/change-data-capture/mongodb.md). Firebolt's CDC docs say an `int` or `double` becomes a JSON number, while types JSON has no equivalent for become objects, such as `{"$numberDecimal": "1.5"}`. Dates and `ObjectId`s follow the same pattern. You extract and cast them yourself: `JSON_VALUE(doc['total']['$numberDecimal'])::NUMERIC(10,2)` and `JSON_VALUE(doc['placed_at']['$date'])::TIMESTAMPTZ` both returned the expected values. The CDC table also stores `_id` as Extended JSON in its own column. The demo below keeps `_id` the same way.

**Updates and deletes** are where hand-rolled sync usually breaks, and where native CDC does the most work. According to the docs, a CDC table holds one live row per `_id`, plus the shard key on sharded collections. It applies inserts, updates, replaces, and deletes in the order MongoDB committed them. The latest change wins, and a delete removes the row. CDC reads MongoDB's pre- and post-images, so an update is never applied out of order or half-applied. The demo below handles inserts only because it plays CDC by hand; it doesn't show this behavior.

### A bookmark that only moves when you've read the page

Anyone can demo data moving when everything goes right. The real question is what happens when something fails halfway through.

Firebolt's [MongoDB CDC](https://docs.firebolt.io/guides/change-data-capture/mongodb.md) reads MongoDB change streams and advances its stored position *in the same transaction* that writes the data. The docs describe exactly-once ingestion, with changes arriving within seconds.

It's a bookmark that only moves once you've actually read the page. After an interruption, ingestion can resume from that position as long as the required history is still retained. If the position has aged out of the MongoDB oplog, Firebolt's docs say the table must be re-bootstrapped.

**Freshness is only worth something if you can trust what arrived, and recover when it didn't.**

### A scoreboard, not a recount

Nobody recounts every basket to know the score; the scoreboard updates with each point. Firebolt's [aggregating indexes](https://docs.firebolt.io/performance-and-observability/storage-and-indexing/aggregating-index.md) work the same way. They update pre-computed aggregates in the same transaction as each write, and the optimizer can use them automatically for matching queries, even with coarser groupings than the index defines.

The docs show `EXPLAIN` using an index for a coarser `GROUP BY`. The scorekeeper does have a job, though: maintaining the index adds work to writes. Whether that trade pays off depends on the workload.

### Separate kitchens, same pantry

[Firebolt separates storage and compute](https://docs.firebolt.io/overview/architecture-overview.md). In a multi-cluster deployment, independent clusters read the same data from object storage, each with its own compute and cache. That lets ingestion and customer-facing queries run on separate compute resources, reducing contention between them.

### "Why not just use Analytics Nodes?"

It's a fair question, and the first one a MongoDB architect will ask. [Atlas analytics nodes](https://www.mongodb.com/docs/atlas/reference/replica-set-tags/) are real workload isolation: read-only replica-set members that keep reporting and ETL off your operational nodes. But they're replicas. They hold the same documents in the same storage engine. You get a quieter room in the same house, not a different engine.

Firebolt changes what happens inside the engine: columnar storage, vectorized execution, sparse indexes that skip data before it's read, aggregates kept current on every write, and compute sized per workload. Analytics nodes are still the right call for plenty of reporting. Firebolt is for when the scans get wide, concurrency climbs, and the answer still has to arrive in under a second.

### Why the read path matters: the same question, timed

The whole argument is that a columnar engine answers this shape of question faster. That's measurable, so I measured it. [`bench.py`](https://github.com/ranfysvalle02/mdb-firebolt/blob/main/bench.py) loads the **same 500,000 nested orders** into both MongoDB and Firebolt, checks that both return byte-for-byte identical results, then times the same "units by city and promo" aggregation 30 times on each. Neither side has a secondary index.

```text
Query latency over 30 runs on 500,000 rows (no secondary indexes):
  MongoDB $group aggregate   p50   102.0 ms   p95   103.6 ms
  Firebolt SQL aggregate     p50     3.1 ms   p95     3.6 ms
```

On my laptop, Firebolt answered about **33x faster at the median** — roughly 3 ms versus 100 ms. This is the honest version of the comparison, so here's what's behind it: both engines scan the full dataset with no index to help. That's not a knock on MongoDB; it's the point. A `$group` over every document is a collection scan, and a wide scan-and-aggregate is exactly the workload columnar storage and vectorized execution are built for. Give MongoDB a narrow filter on an indexed field and it shines; ask it to crunch the whole set, and you feel why the warehouse existed.

This isn't a production benchmark: single-node [Firebolt Core](https://github.com/firebolt-db/firebolt-core) and MongoDB Atlas Local, both on one Apple M4 Max, 500k rows. Run it yourself and the absolute numbers will move. The gap is the part that travels.

An experienced MongoDB architect will push back here: *nobody serves a hot, customer-facing aggregate from a collection scan.* Fair. I tried the first fix, a compound index on `city`, `promo.code`, and `qty`. It didn't help: the median stayed around 100 ms, and forcing the planner to use the index made it 268 ms. The real fix is a rollup, a [materialized view](https://www.mongodb.com/docs/manual/core/materialized-views/) refreshed by `$merge`, and for a question you know in advance it's fast. That's the catch. A rollup answers the question someone anticipated, at the freshness of its last refresh. On Friday morning, nobody had a rollup by `promo`, because `promo` didn't exist. An agent that asks *"units by city, promo, and hour, for orders over $50"* needs a new rollup and a new refresh job. That's the bridge again, rebuilt every time someone asks a new question. The columnar engine's argument is that the raw documents are fast enough to ask directly.

### Proof at two more scales

MongoDB cites **Similarweb**, which uses Firebolt for customer-facing analytics over more than a trillion rows at petabyte scale, with sub-second dynamic queries *"without extensive pre-aggregation."*

At the other end of the scale, the runnable demo below uses five orders to show the *freshness* side of the story: the same question, a different answer, once a new nested field arrives. That's a separate beat from speed, and it's what the next section replays.

## Don't take my word for it

*Chapter VI · Your architecture*

The real competitor here was never another database. It was *"we'll just add one more job to the pipeline."* The status quo always looks free, because its cost is spread thinly across a dozen teams and a hundred tickets. So make that cost visible.

Pick one decision your application or agent makes for a customer. Then run four tests:

1. **Freshness, end to end.** Measure from source write to correct answer, not just query runtime.
2. **Schema drift.** Ship a new nested field, then change an existing field's type. Count the hours, and the humans, before both are queryable.
3. **Crash mid-batch.** Kill ingestion halfway. After resume, check for duplicates and gaps.
4. **Concurrency.** Measure p95 latency under a realistic mix of simultaneous queries, not one hero query.

Score your current pipeline, analytics nodes, and Firebolt the same way.

Then count the cost honestly. Integrated doesn't mean free. You're running a second engine, which means a second, columnar copy of the data, compute to keep it in sync, and more compute to serve queries. Analytics nodes add cost too, but they're replicas of a system you already run. A new engine is a new line item. MongoDB hasn't announced pricing for the integrated experience, so model it before you assume anything.

Then put it next to what you pay today: pipeline infrastructure, warehouse refreshes, the engineers who maintain the bridge, and the cost of answers that were wrong on Friday. If analytics nodes or the SQL Interface already answer your questions quickly and accurately enough, keep using them. The new engine has to earn its line item. Bring the app owner, the data team, security, and whoever owns the renewal to the same readout, because they're the people who have to say yes.

One practical note for whoever has to get this approved: native CDC is in private preview, and the integrated experience is still "in the coming months." Start an evaluation on Firebolt Core, but check availability and production requirements before making deployment commitments.

Somewhere in your organization, someone may have been drawing this bridge on whiteboards for years. They maintain it at 2 AM and explain why the numbers lag. Bring them into the evaluation.

Maybe it's you.

## Build the small version

*Chapter VII · Friday, replayed*

Back to Friday. [`demo.py`](https://github.com/ranfysvalle02/mdb-firebolt/blob/main/demo.py) replays it with five orders: two from yesterday, then three from this morning, when the flash sale started and the nested `promo` field first appeared. It asks the merchant's question twice, once with only yesterday's orders synced and once with everything.

One note first: native MongoDB CDC is in private preview, so `sync()` plays that part by hand. The planned integration is meant to make that the platform's job, so the bridge stops being yours.

```python
QUESTION = """
    SELECT JSON_VALUE(doc.city) AS city, JSON_VALUE(doc.promo.code) AS promo,
           SUM(JSON_VALUE(doc.qty)::INT) AS units
    FROM orders GROUP BY ALL ORDER BY units DESC;
"""

def sync(stream, count):
    """Move `count` change events from MongoDB into Firebolt."""
    for _ in range(count):
        doc = next(stream)["fullDocument"]
        # Relaxed Extended JSON, as native CDC stores it: ObjectId becomes {"$oid": ...}
        fb.execute("INSERT INTO orders VALUES (?::JSON);", [dumps(doc, json_options=RELAXED)])

with col.watch() as stream:
    col.insert_many(YESTERDAY)
    sync(stream, len(YESTERDAY))
    print("Last night's answer:", ask())

    col.insert_many(THIS_MORNING)  # the first orders with a nested `promo` field
    sync(stream, len(THIS_MORNING))
    print("Right now:          ", ask())
```

```text
Last night's answer: [['Austin', None, 3], ['Denver', None, 1]]
Right now:           [['Denver', 'FLASH20', 6], ['Austin', None, 4], ['Denver', None, 1]]
```

Same question, same SQL, different answer. Last night's data says Austin. Live data says Denver, and it says why: the `promo` field that didn't exist yesterday is sitting right there in the result. The table was created once, as `(doc JSON)`, and nobody touched it again.

<details>
<summary><strong>Run it locally</strong> (Docker + Python)</summary>

Everything lives in [ranfysvalle02/mdb-firebolt](https://github.com/ranfysvalle02/mdb-firebolt).

**Each run drops the `shop.orders` and `shop.bench_orders` MongoDB collections and the Firebolt `orders` and `bench_orders` tables on localhost.** Use isolated demo instances, not existing services containing data you need.

```bash
git clone https://github.com/ranfysvalle02/mdb-firebolt.git && cd mdb-firebolt
docker compose up -d
pip install pymongo firebolt-sdk
python demo.py     # the freshness story: same question, new answer
python bench.py    # the speed story: same 500k rows, timed on both engines
```

Change streams need a replica set. MongoDB Atlas Local, which the compose file uses, is one; a standalone `mongod` container is not. `demo.py` handles inserts only; updates, deletes, and crash recovery are the native CDC's job. `bench.py` loads the same data into both engines, verifies the results match, and times the aggregation on each.

</details>

---

A coordinate was just an array. A graph edge was a reference. An embedding was an array of floats. A stream event was a document in motion. And a question about this morning's orders is just a question about documents, one that's finally getting an engine built to answer it as fast as agents ask.

The bet in 2009 was that the data in your code and the data in your database should have the same shape.

The bet in 2026 is that the gap between the data you act on and the data you analyze can get much smaller.

**Stop building bridges between what happened and what happens next.**

---

## Appendix A: What's real today

| Capability | Status | Evidence |
|---|---|---|
| Integrated MongoDB + Firebolt, synced automatically | 🗓️ **Roadmap** ("coming months") | [MongoDB announcement](https://www.mongodb.com/company/blog/news/mongodb-acquires-firebolt) |
| Analyze other sources and formats alongside MongoDB | 🗓️ **Roadmap** ("over time") | [MongoDB announcement](https://www.mongodb.com/company/blog/news/mongodb-acquires-firebolt) |
| Native MongoDB CDC, exactly-once, fresh within seconds | 🧪 **Private preview** | [Firebolt docs](https://docs.firebolt.io/guides/change-data-capture/mongodb.md) |
| Sync latency of the integrated product | ❓ **Not announced** | No latency target or SLA in the announcement |
| `JSON` type; query new nested fields with no DDL | 🧪 **Public preview** | [Firebolt docs](https://docs.firebolt.io/reference-sql/data-types/json.md); [local demo](https://github.com/ranfysvalle02/mdb-firebolt/blob/main/demo.py) |
| Automatic column shredding | 💬 **Vendor-stated** | CTO quote in [MongoDB announcement](https://www.mongodb.com/company/blog/news/mongodb-acquires-firebolt) |
| Transactional aggregating indexes, automatic rewrite | ✅ **Documented** | [Firebolt docs](https://docs.firebolt.io/performance-and-observability/storage-and-indexing/aggregating-index.md) |
| Storage/compute separation, isolated clusters | ✅ **Documented** | [Firebolt docs](https://docs.firebolt.io/overview/architecture-overview.md) |
| Trillion rows, petabyte scale, sub-second | 🏢 **Customer reference** | Similarweb, per [MongoDB announcement](https://www.mongodb.com/company/blog/news/mongodb-acquires-firebolt) |
| ~33x faster aggregate on 500k unindexed rows | 💻 **My laptop test** | [`bench.py`](https://github.com/ranfysvalle02/mdb-firebolt/blob/main/bench.py); identical results verified; single-node, one Apple M4 Max; not a production benchmark |
| Firebolt Core, self-hosted | ✅ **Available** | [GitHub](https://github.com/firebolt-db/firebolt-core); [Elastic License 2.0](https://github.com/firebolt-db/firebolt-core/blob/main/LICENSE.md) |

## Appendix B: The pattern: build ahead, retire without sentiment

Firebolt is MongoDB's third swing at analytics on operational data, not its first:

1. **The [BI Connector](https://www.mongodb.com/docs/bi-connector/current/)** let SQL tools such as Tableau query MongoDB. Customers used it. It reached end of life in September 2026.
2. **The [SQL Interface](https://www.mongodb.com/docs/sql-interface/)** replaced it with live, read-only JDBC and ODBC access, direct cluster connections, and schema updates that don't interrupt queries ([transition guide](https://www.mongodb.com/docs/sql-interface/transition-bic-to-atlas-sql/)).
3. **Firebolt** goes further, with a separate columnar engine for sub-second, high-concurrency analytics served to applications and agents.

The willingness to retire products isn't limited to analytics. [Atlas Device SDKs and Device Sync](https://www.mongodb.com/docs/device-sdks-deprecation/) and the [Atlas Data API](https://www.mongodb.com/docs/atlas/app-services/data-api/) have also reached end of life.

MongoDB builds ahead of demand and retires products when something better comes along. If you're on the retired path, factor that into any evaluation, including this one.

## Appendix C: Sources

**Announcement:** [MongoDB acquires Firebolt](https://www.mongodb.com/company/blog/news/mongodb-acquires-firebolt)

**Reporting:** [Calcalist](https://www.calcalistech.com/ctechnews/article/anq8b3yg3) · [Techzine](https://www.techzine.eu/news/analytics/145917/mongodb-acquires-firebolt-for-real-time-analytics/)

**Docs:** [Firebolt JSON type](https://docs.firebolt.io/reference-sql/data-types/json.md) · [Firebolt MongoDB CDC](https://docs.firebolt.io/guides/change-data-capture/mongodb.md) · [MongoDB change streams](https://www.mongodb.com/docs/manual/changeStreams/) · [Aggregating indexes](https://docs.firebolt.io/performance-and-observability/storage-and-indexing/aggregating-index.md) · [Firebolt architecture](https://docs.firebolt.io/overview/architecture-overview.md) · [Firebolt Core](https://github.com/firebolt-db/firebolt-core) · [MongoDB BI Connector](https://www.mongodb.com/docs/bi-connector/current/) · [MongoDB SQL Interface](https://www.mongodb.com/docs/sql-interface/) · [MongoDB materialized views](https://www.mongodb.com/docs/manual/core/materialized-views/) · [Atlas analytics nodes](https://www.mongodb.com/docs/atlas/reference/replica-set-tags/) · [Why MongoDB acquired Voyage AI](https://www.mongodb.com/company/blog/news/redefining-database-ai-why-mongodb-acquired-voyage-ai)
