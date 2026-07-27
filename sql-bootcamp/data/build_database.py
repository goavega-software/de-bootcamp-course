"""
Build the sample SQLite database used throughout the SQL Bootcamp.

Run this once before starting the notebooks:

    uv run python data/build_database.py

It creates `data/retail.db`, a small fictional retail company with:
    categories  -> product categories
    suppliers   -> who supplies products
    products    -> catalog of products
    customers   -> people who place orders
    employees   -> staff (self-referencing manager_id -> great for self-joins
                   and recursive CTEs)
    orders      -> one row per order
    order_items -> line items within an order (many-to-many products<->orders)

The data is deliberately small so you can eyeball results, but rich enough to
practice joins, aggregations, window functions, subqueries and more.
"""
from __future__ import annotations

import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "retail.db")

SCHEMA = """
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS suppliers;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS employees;

CREATE TABLE categories (
    category_id   INTEGER PRIMARY KEY,
    category_name TEXT NOT NULL UNIQUE
);

CREATE TABLE suppliers (
    supplier_id   INTEGER PRIMARY KEY,
    supplier_name TEXT NOT NULL,
    country       TEXT NOT NULL
);

CREATE TABLE products (
    product_id   INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category_id  INTEGER NOT NULL,
    supplier_id  INTEGER,
    unit_price   REAL NOT NULL CHECK (unit_price >= 0),
    in_stock     INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    first_name  TEXT NOT NULL,
    last_name   TEXT NOT NULL,
    email       TEXT UNIQUE,
    city        TEXT,
    country     TEXT,
    signup_date TEXT NOT NULL          -- ISO date string 'YYYY-MM-DD'
);

CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY,
    first_name  TEXT NOT NULL,
    last_name   TEXT NOT NULL,
    title       TEXT,
    hire_date   TEXT NOT NULL,
    salary      REAL,
    manager_id  INTEGER,               -- self reference
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
);

CREATE TABLE orders (
    order_id    INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    employee_id INTEGER,
    order_date  TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'completed',
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE order_items (
    order_id   INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity   INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL,          -- price captured at time of sale
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
"""

CATEGORIES = [
    (1, "Electronics"),
    (2, "Books"),
    (3, "Home & Kitchen"),
    (4, "Toys"),
    (5, "Clothing"),
]

SUPPLIERS = [
    (1, "Globex Corp", "USA"),
    (2, "Initech", "USA"),
    (3, "Umbrella Ltd", "UK"),
    (4, "Hooli", "USA"),
    (5, "Nakatomi Trading", "Japan"),
    (6, "Wonka Industries", "Germany"),
]

# product_id, name, category_id, supplier_id, unit_price, in_stock
PRODUCTS = [
    (1,  "Wireless Mouse",        1, 1,  25.00, 120),
    (2,  "Mechanical Keyboard",   1, 1,  79.99,  60),
    (3,  "27in Monitor",          1, 4, 199.99,  25),
    (4,  "USB-C Hub",             1, 5,  34.50,  90),
    (5,  "Noise Cancel Headset",  1, 5, 149.00,  40),
    (6,  "SQL Fundamentals",      2, 3,  39.99, 200),
    (7,  "Python Crash Course",   2, 3,  44.95, 150),
    (8,  "Data Modeling Guide",   2, 2,  52.00,  80),
    (9,  "The Pragmatic Coder",   2, 2,  41.50, 110),
    (10, "Chef Knife Set",        3, 6,  89.00,  35),
    (11, "Nonstick Pan",          3, 6,  29.99,  70),
    (12, "Coffee Maker",          3, 4,  59.99,  45),
    (13, "Blender Pro",           3, 1,  74.00,  30),
    (14, "Building Blocks 500pc", 4, 5,  32.00, 140),
    (15, "RC Car",                4, 5,  48.00,  55),
    (16, "Puzzle 1000pc",         4, 3,  18.99, 210),
    (17, "Cotton T-Shirt",        5, 3,  15.00, 300),
    (18, "Rain Jacket",           5, 2,  69.99,  65),
    (19, "Running Shoes",         5, 4,  95.00,  50),
    (20, "Wool Socks 3pk",        5, 6,  12.50, 400),
]

# customer_id, first, last, email, city, country, signup_date
CUSTOMERS = [
    (1,  "Alice",   "Nguyen",    "alice@example.com",   "Seattle",   "USA",     "2023-01-15"),
    (2,  "Bob",     "Smith",     "bob@example.com",     "Austin",    "USA",     "2023-02-03"),
    (3,  "Carla",   "Diaz",      "carla@example.com",   "Madrid",    "Spain",   "2023-02-20"),
    (4,  "Dmitri",  "Petrov",    "dmitri@example.com",  "London",    "UK",      "2023-03-11"),
    (5,  "Emma",    "Johnson",   "emma@example.com",    "Toronto",   "Canada",  "2023-03-28"),
    (6,  "Farid",   "Hassan",    "farid@example.com",   "Dubai",     "UAE",     "2023-04-05"),
    (7,  "Grace",   "Lee",       "grace@example.com",   "Seoul",     "Korea",   "2023-05-19"),
    (8,  "Hiro",    "Tanaka",    "hiro@example.com",    "Tokyo",     "Japan",   "2023-06-02"),
    (9,  "Ivana",   "Kovac",     None,                  "Zagreb",    "Croatia", "2023-07-14"),
    (10, "Jamal",   "Brown",     "jamal@example.com",   "Chicago",   "USA",     "2023-08-09"),
    (11, "Kira",    "Volkova",   "kira@example.com",    "Berlin",    "Germany", "2024-01-22"),
    (12, "Liam",    "OConnor",   "liam@example.com",    "Dublin",    "Ireland", "2024-02-17"),
]

# employee_id, first, last, title, hire_date, salary, manager_id
EMPLOYEES = [
    (1, "Nora",   "Adams",   "CEO",              "2019-01-10", 220000, None),
    (2, "Owen",   "Clark",   "VP Sales",         "2019-06-01", 160000, 1),
    (3, "Priya",  "Rao",     "VP Operations",    "2019-08-15", 158000, 1),
    (4, "Quinn",  "Meyer",   "Sales Manager",    "2020-03-05", 120000, 2),
    (5, "Rosa",   "Ibarra",  "Sales Rep",        "2021-02-20",  78000, 4),
    (6, "Sam",    "Turner",  "Sales Rep",        "2021-09-13",  75000, 4),
    (7, "Tara",   "Boyd",    "Sales Rep",        "2022-05-30",  72000, 4),
    (8, "Umar",   "Farooq",  "Ops Analyst",      "2022-07-11",  84000, 3),
]

# order_id, customer_id, employee_id, order_date, status
ORDERS = [
    (1001, 1,  5, "2024-01-05", "completed"),
    (1002, 2,  6, "2024-01-07", "completed"),
    (1003, 1,  5, "2024-01-20", "completed"),
    (1004, 3,  7, "2024-02-02", "completed"),
    (1005, 4,  6, "2024-02-14", "completed"),
    (1006, 5,  5, "2024-02-28", "cancelled"),
    (1007, 6,  7, "2024-03-03", "completed"),
    (1008, 2,  6, "2024-03-15", "completed"),
    (1009, 7,  5, "2024-03-22", "completed"),
    (1010, 8,  7, "2024-04-01", "completed"),
    (1011, 10, 6, "2024-04-18", "completed"),
    (1012, 11, 5, "2024-05-06", "pending"),
    (1013, 1,  7, "2024-05-19", "completed"),
    (1014, 12, 6, "2024-06-01", "completed"),
    (1015, 3,  5, "2024-06-11", "completed"),
    (1016, 5,  7, "2024-06-25", "completed"),
    (1017, 8,  6, "2024-07-04", "completed"),
    (1018, 4,  5, "2024-07-15", "pending"),
]

# order_id, product_id, quantity, unit_price
ORDER_ITEMS = [
    (1001, 1,  2, 25.00), (1001, 6, 1, 39.99),
    (1002, 3,  1, 199.99), (1002, 4, 2, 34.50),
    (1003, 7,  3, 44.95),
    (1004, 10, 1, 89.00), (1004, 11, 2, 29.99), (1004, 20, 4, 12.50),
    (1005, 2,  1, 79.99), (1005, 5, 1, 149.00),
    (1006, 16, 5, 18.99),
    (1007, 17, 6, 15.00), (1007, 20, 2, 12.50),
    (1008, 12, 1, 59.99), (1008, 13, 1, 74.00),
    (1009, 6,  2, 39.99), (1009, 8, 1, 52.00), (1009, 9, 1, 41.50),
    (1010, 14, 2, 32.00), (1010, 15, 1, 48.00),
    (1011, 19, 1, 95.00), (1011, 18, 1, 69.99),
    (1012, 3,  2, 199.99),
    (1013, 1,  1, 25.00), (1013, 4, 1, 34.50), (1013, 5, 1, 149.00),
    (1014, 7,  1, 44.95), (1014, 6, 1, 39.99),
    (1015, 11, 3, 29.99), (1015, 12, 1, 59.99),
    (1016, 20, 10, 12.50), (1016, 17, 5, 15.00),
    (1017, 2,  2, 79.99), (1017, 3, 1, 199.99),
    (1018, 10, 1, 89.00), (1018, 13, 1, 74.00),
]


def build() -> None:
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    cur.executescript(SCHEMA)
    cur.executemany("INSERT INTO categories VALUES (?, ?)", CATEGORIES)
    cur.executemany("INSERT INTO suppliers VALUES (?, ?, ?)", SUPPLIERS)
    cur.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)", PRODUCTS)
    cur.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?)", CUSTOMERS)
    cur.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?)", EMPLOYEES)
    cur.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", ORDERS)
    cur.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?)", ORDER_ITEMS)

    conn.commit()

    counts = {
        t: cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        for t in ["categories", "suppliers", "products", "customers",
                  "employees", "orders", "order_items"]
    }
    conn.close()

    print(f"Created database at: {DB_PATH}")
    for table, n in counts.items():
        print(f"  {table:<12} {n:>4} rows")


if __name__ == "__main__":
    build()
