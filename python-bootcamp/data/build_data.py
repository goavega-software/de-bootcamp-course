"""
Build the sample raw datasets used throughout the Python Bootcamp.

Run this once before starting the notebooks:

    uv run python data/build_data.py

It is deterministic (fixed random seed) so everyone gets identical data. It
creates, under ``data/``:

    raw/customers.csv        -> messy customer master (nulls, mixed casing)
    raw/events.jsonl         -> one JSON object per line (clickstream events)
    raw/orders.csv           -> orders fact table
    raw/products.csv         -> product catalog
    retail.db                -> the same tables loaded into SQLite
    (Parquet files are written by the notebooks themselves.)

The data is deliberately small so you can eyeball it, but messy enough to
practice real extract / clean / transform / load work.
"""
from __future__ import annotations

import csv
import json
import os
import random
import sqlite3
from datetime import date, datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
DB_PATH = os.path.join(HERE, "retail.db")

random.seed(42)

CATEGORIES = ["Electronics", "Books", "Home", "Toys", "Grocery"]
COUNTRIES = ["US", "GB", "DE", "IN", "BR", "CA"]
FIRST = ["Ava", "Liam", "Noah", "Emma", "Olivia", "Raj", "Mei", "Ivan",
         "Sofia", "Lucas", "Amara", "Chen", "Diego", "Yara", "Kofi"]
LAST = ["Smith", "Patel", "Kim", "Garcia", "Muller", "Silva", "Okafor",
        "Rossi", "Nguyen", "Haddad", "Ivanov", "Cohen"]


def _ensure_dirs() -> None:
    os.makedirs(RAW, exist_ok=True)


def build_products(n: int = 40) -> list[dict]:
    rows = []
    for pid in range(1, n + 1):
        cat = random.choice(CATEGORIES)
        rows.append({
            "product_id": pid,
            "product_name": f"{cat[:3].upper()}-{pid:03d}",
            "category": cat,
            "unit_price": round(random.uniform(3.5, 400.0), 2),
        })
    return rows


def build_customers(n: int = 60) -> list[dict]:
    rows = []
    for cid in range(1, n + 1):
        name = f"{random.choice(FIRST)} {random.choice(LAST)}"
        # Deliberately messy: some blank emails, mixed-case countries.
        email = "" if random.random() < 0.12 else \
            name.lower().replace(" ", ".") + "@example.com"
        country = random.choice(COUNTRIES)
        if random.random() < 0.3:
            country = country.lower()  # inconsistent casing to clean later
        signup = date(2023, 1, 1) + timedelta(days=random.randint(0, 900))
        rows.append({
            "customer_id": cid,
            "name": name,
            "email": email,
            "country": country,
            "signup_date": signup.isoformat(),
        })
    return rows


def build_orders(customers: list[dict], products: list[dict],
                 n: int = 500) -> tuple[list[dict], list[dict]]:
    orders, items = [], []
    start = datetime(2024, 1, 1)
    for oid in range(1, n + 1):
        cust = random.choice(customers)
        ts = start + timedelta(
            days=random.randint(0, 364),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )
        n_lines = random.randint(1, 4)
        order_total = 0.0
        for _ in range(n_lines):
            prod = random.choice(products)
            qty = random.randint(1, 5)
            order_total += qty * prod["unit_price"]
            items.append({
                "order_id": oid,
                "product_id": prod["product_id"],
                "quantity": qty,
                "unit_price": prod["unit_price"],
            })
        orders.append({
            "order_id": oid,
            "customer_id": cust["customer_id"],
            "order_ts": ts.isoformat(sep=" ", timespec="seconds"),
            "status": random.choices(
                ["completed", "returned", "cancelled"],
                weights=[0.8, 0.12, 0.08])[0],
            "amount": round(order_total, 2),
        })
    return orders, items


def build_events(customers: list[dict], n: int = 800) -> list[dict]:
    """Semi-structured clickstream: nested payloads, optional fields."""
    kinds = ["page_view", "add_to_cart", "checkout", "search"]
    start = datetime(2024, 6, 1)
    out = []
    for i in range(n):
        cust = random.choice(customers)
        kind = random.choice(kinds)
        ts = start + timedelta(seconds=random.randint(0, 60 * 60 * 24 * 30))
        payload = {"path": random.choice(["/", "/deals", "/cart", "/item"])}
        if kind == "search":
            payload["query"] = random.choice(["ssd", "novel", "lego", "milk"])
        if kind == "add_to_cart":
            payload["qty"] = random.randint(1, 3)
        out.append({
            "event_id": i + 1,
            "customer_id": cust["customer_id"],
            "event_type": kind,
            "ts": ts.isoformat(),
            "payload": payload,
        })
    return out


def write_csv(path: str, rows: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def load_sqlite(products, customers, orders, items) -> None:
    # Remove any previous database AND its stale sidecar files (a leftover
    # -journal or -wal can otherwise confuse SQLite on the next open).
    for suffix in ("", "-journal", "-wal", "-shm"):
        stale = DB_PATH + suffix
        if os.path.exists(stale):
            os.remove(stale)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.executescript(
        """
        CREATE TABLE products  (product_id INTEGER PRIMARY KEY, product_name TEXT,
                                category TEXT, unit_price REAL);
        CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT,
                                email TEXT, country TEXT, signup_date TEXT);
        CREATE TABLE orders    (order_id INTEGER PRIMARY KEY, customer_id INTEGER,
                                order_ts TEXT, status TEXT, amount REAL);
        CREATE TABLE order_items (order_id INTEGER, product_id INTEGER,
                                quantity INTEGER, unit_price REAL);
        """
    )
    cur.executemany("INSERT INTO products VALUES (?,?,?,?)",
                    [tuple(r.values()) for r in products])
    cur.executemany("INSERT INTO customers VALUES (?,?,?,?,?)",
                    [tuple(r.values()) for r in customers])
    cur.executemany("INSERT INTO orders VALUES (?,?,?,?,?)",
                    [tuple(r.values()) for r in orders])
    cur.executemany("INSERT INTO order_items VALUES (?,?,?,?)",
                    [tuple(r.values()) for r in items])
    con.commit()
    con.close()


def main() -> None:
    _ensure_dirs()
    products = build_products()
    customers = build_customers()
    orders, items = build_orders(customers, products)
    events = build_events(customers)

    write_csv(os.path.join(RAW, "products.csv"), products)
    write_csv(os.path.join(RAW, "customers.csv"), customers)
    write_csv(os.path.join(RAW, "orders.csv"), orders)
    write_csv(os.path.join(RAW, "order_items.csv"), items)

    with open(os.path.join(RAW, "events.jsonl"), "w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")

    load_sqlite(products, customers, orders, items)

    print("Wrote raw files to", RAW)
    print(f"  products.csv      {len(products):>5} rows")
    print(f"  customers.csv     {len(customers):>5} rows")
    print(f"  orders.csv        {len(orders):>5} rows")
    print(f"  order_items.csv   {len(items):>5} rows")
    print(f"  events.jsonl      {len(events):>5} rows")
    print("Built SQLite database at", DB_PATH)


if __name__ == "__main__":
    main()
