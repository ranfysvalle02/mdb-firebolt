"""Friday, 4:52 PM: "What should I restock before the weekend?"

The same question, asked of last night's data and then of live data.
Native MongoDB CDC in Firebolt is in private preview, so sync() plays that part by hand.
Change streams need a replica set: MongoDB Atlas Local is one, a standalone mongod is not.
Each run resets the demo's `orders` table and collection.
"""
import json
from pymongo import MongoClient
from firebolt.db import connect
from firebolt.client.auth import FireboltCore

YESTERDAY = [
    {"order_id": "ord_097", "sku": "sneaker-red", "qty": 3, "city": "Austin"},
    {"order_id": "ord_098", "sku": "sneaker-red", "qty": 1, "city": "Denver"},
]
# This morning's flash sale: engineering starts tagging orders with a nested `promo` field.
THIS_MORNING = [
    {"order_id": "ord_101", "sku": "sneaker-red", "qty": 2, "city": "Denver", "promo": {"code": "FLASH20"}},
    {"order_id": "ord_102", "sku": "sneaker-red", "qty": 4, "city": "Denver", "promo": {"code": "FLASH20"}},
    {"order_id": "ord_103", "sku": "sneaker-red", "qty": 1, "city": "Austin"},
]
QUESTION = """
    SELECT JSON_VALUE(doc.city) AS city, JSON_VALUE(doc.promo.code) AS promo,
           SUM(JSON_VALUE(doc.qty)::INT) AS units
    FROM orders GROUP BY ALL ORDER BY units DESC;
"""

col = MongoClient("mongodb://localhost:27017/?directConnection=true")["shop"]["orders"]
col.drop()

with connect(auth=FireboltCore(), url="http://localhost:3473", database="firebolt") as conn:
    fb = conn.cursor()
    fb.execute("DROP TABLE IF EXISTS orders;")
    fb.execute("CREATE TABLE orders (doc JSON);")  # the only DDL in this story

    def sync(stream, count):
        """Move `count` change events from MongoDB into Firebolt."""
        for _ in range(count):
            doc = next(stream)["fullDocument"]
            doc.pop("_id", None)  # a BSON ObjectId isn't JSON-serializable
            fb.execute("INSERT INTO orders VALUES (?::JSON);", [json.dumps(doc)])

    def ask():
        fb.execute(QUESTION)
        return fb.fetchall()

    with col.watch() as stream:
        col.insert_many(YESTERDAY)
        sync(stream, len(YESTERDAY))
        print("Last night's answer:", ask())

        col.insert_many(THIS_MORNING)  # the first orders with a nested `promo` field
        sync(stream, len(THIS_MORNING))
        print("Right now:          ", ask())
