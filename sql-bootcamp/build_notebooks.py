"""
Generator for the SQL Zero-to-Hero Bootcamp notebooks.

Running this (re)creates every notebook under `notebooks/`. It is safe to run
again at any time if you want to reset the notebooks to their original state:

    uv run python build_notebooks.py

You normally do NOT need to run this — the notebooks ship ready to use. It is
included so the course is fully reproducible and so you can reset your practice
files if you overwrite them.
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
NB_DIR = os.path.join(HERE, "notebooks")

# ---------------------------------------------------------------------------
# tiny notebook-builder helpers
# ---------------------------------------------------------------------------

def _src(text: str):
    text = text.strip("\n")
    return text.splitlines(keepends=True)


def md(text: str):
    return {"cell_type": "markdown", "metadata": {}, "source": _src(text)}


def code(text: str):
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": _src(text)}


def sql(query: str):
    return code("%%sql\n" + query.strip("\n"))


SETUP = code(
    "# ▶ Run this cell first. It loads JupySQL and connects to the SQLite database.\n"
    "%load_ext sql\n"
    "from sqlalchemy import create_engine\n"
    "import os\n"
    "\n"
    "# Works whether the notebook's working dir is the repo root or notebooks/\n"
    "db_path = 'data/retail.db' if os.path.exists('data/retail.db') else '../data/retail.db'\n"
    "engine = create_engine(f'sqlite:///{db_path}')\n"
    "\n"
    "%config SqlMagic.autopandas = True      # results come back as pandas DataFrames\n"
    "%config SqlMagic.displaycon = False\n"
    "%config SqlMagic.feedback = 0\n"
    "%config SqlMagic.displaylimit = 100\n"
    "\n"
    "%sql engine\n"
    "print('Connected to', db_path)"
)


class Ex:
    """Emits an exercise: prompt + a practice cell + a worked solution."""
    def __init__(self):
        self.n = 0

    def __call__(self, prompt: str, solution_sql: str):
        self.n += 1
        cells = [
            md(f"**✏️ Exercise {self.n}.** {prompt}\n\n"
               "Try it yourself in the practice cell, then run the solution to check."),
            sql("-- Your turn! Replace the line below with your own query.\n"
                "SELECT 'edit me, then run' AS your_answer;"),
            md("<details><summary>💡 Show solution</summary>\n\n"
               "Run the next cell to see one correct answer.</details>"),
            sql(solution_sql),
        ]
        return cells


def write_nb(filename: str, cells: list) -> None:
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python",
                            "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    path = os.path.join(NB_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print("wrote", filename)


def flat(*items):
    out = []
    for it in items:
        if isinstance(it, list):
            out.extend(it)
        else:
            out.append(it)
    return out


# ===========================================================================
# 00 - Setup & relational basics
# ===========================================================================

def nb_00():
    c = []
    c.append(md("""
# 00 · Setup & SQL Foundations

Welcome to the **SQL Zero-to-Hero Bootcamp**! 🎓

You will learn SQL by *doing*. Every notebook mixes short explanations with
runnable examples and hands-on exercises. You write SQL directly in cells using
the `%%sql` magic and see results instantly as tables.

## How this works
- The whole course runs on a small SQLite database — no server to install.
- We use [JupySQL](https://jupysql.ploomber.io/) so cells that start with
  `%%sql` are pure SQL. A single-line query can use inline `%sql SELECT ...`.
- Results are returned as pandas DataFrames, so they render as nice tables.

## Before you start
1. Make sure you built the database (from a terminal at the project root):
   ```bash
   uv run python data/build_database.py
   ```
2. Then run the setup cell below in every notebook (it's always the first cell).
"""))
    c.append(SETUP)
    c.append(md("""
## The database: a small retail company

Everything you query is this fictional shop. Understanding the tables now will
make every later module easier.

| Table | What it holds | Key columns |
|-------|---------------|-------------|
| `categories`  | product categories | `category_id` |
| `suppliers`   | who supplies products | `supplier_id` |
| `products`    | the catalog | `product_id`, `category_id`, `supplier_id`, `unit_price` |
| `customers`   | people who buy | `customer_id`, `country`, `signup_date` |
| `employees`   | staff; `manager_id` points at another employee | `employee_id`, `manager_id` |
| `orders`      | one row per order | `order_id`, `customer_id`, `employee_id`, `order_date`, `status` |
| `order_items` | products within an order | (`order_id`, `product_id`), `quantity`, `unit_price` |

**How they relate**

```
categories 1───∞ products ∞───1 suppliers
customers  1───∞ orders   ∞───1 employees (employee who took the order)
orders     1───∞ order_items ∞───1 products
employees  1───∞ employees  (manager_id is a self reference)
```

Let's look at the tables SQLite knows about:
"""))
    c.append(sql("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name;"))
    c.append(md("Peek at a few rows of `products`:"))
    c.append(sql("SELECT * FROM products LIMIT 5;"))
    c.append(md("And a few customers:"))
    c.append(sql("SELECT customer_id, first_name, last_name, country FROM customers LIMIT 5;"))
    c.append(md("""
## Your very first query

`SELECT` retrieves data. `*` means "all columns". `LIMIT` caps the row count.
"""))
    c.append(sql("SELECT * FROM categories;"))
    c.append(md("""
## Think in *sets*, not loops

The single biggest mindset shift for engineers coming from imperative code: SQL
is **declarative and set-based**. You don't tell the database *how* to loop over
rows — you *describe the result you want* and the query planner figures out how
to produce it. A `WHERE` clause isn't an `if` inside a `for`; it's a filter
applied to the whole set at once. Writing row-by-row logic (cursors, procedural
loops) is almost always slower and harder to read than one set-based statement.

## How SQL is actually processed (logical order)

You *write* a query starting with `SELECT`, but the database *evaluates* the
clauses in a different **logical order**. Knowing this explains many "why doesn't
this work?" moments (e.g. why you can't use a `SELECT` alias in `WHERE`, but can
in `ORDER BY`):

```
1. FROM / JOIN      pick the tables and combine them
2. WHERE            filter individual rows
3. GROUP BY         collapse rows into groups
4. HAVING           filter the groups
5. SELECT           choose/compute the output columns (aliases created here)
6. DISTINCT         remove duplicate output rows
7. ORDER BY         sort the final result
8. LIMIT / OFFSET   keep a slice
```

Because `WHERE` (step 2) runs *before* `SELECT` (step 5), a column alias defined
in `SELECT` doesn't exist yet in `WHERE`. But `ORDER BY` (step 7) runs *after*
`SELECT`, so ordering by an alias works. Keep this list handy — it's the mental
model behind everything that follows.

### ✅ You're set up!
You connected to the database, listed its tables, ran your first `SELECT`, and
now understand SQL's set-based, declarative model and its logical evaluation
order.

**Next:** `01_select_basics.ipynb` — choosing columns, aliases, `DISTINCT`, and
calculated columns.
"""))
    write_nb("00_setup_and_foundations.ipynb", c)


# ===========================================================================
# 01 - SELECT basics
# ===========================================================================

def nb_01():
    ex = Ex()
    c = [md("""
# 01 · SELECT Basics

`SELECT` is the heart of SQL. In this module:
- choosing specific columns
- renaming columns with `AS` (aliases)
- calculated / derived columns
- `DISTINCT` to remove duplicates
- `LIMIT` to cap results

> Run the setup cell first (always the first cell of every notebook).
"""), SETUP]

    c += [md("""
## Selecting specific columns
Instead of `*`, list the columns you want, separated by commas. This is faster
and clearer.
"""), sql("SELECT product_name, unit_price FROM products;")]

    c += [md("""
## Column aliases with `AS`
Rename a column in the output. `AS` is optional but makes intent clear.
"""), sql("SELECT product_name AS product, unit_price AS price FROM products LIMIT 5;")]

    c += [md("""
## Calculated columns
You can compute values right in the `SELECT` list.
"""), sql("""
SELECT
    product_name,
    unit_price,
    in_stock,
    unit_price * in_stock AS inventory_value
FROM products
LIMIT 8;
""")]

    c += [md("""
## Text concatenation
SQLite uses `||` to join text. Combine first and last names:
"""), sql("SELECT first_name || ' ' || last_name AS full_name, country FROM customers;")]

    c += [md("""
## `DISTINCT` — unique values only
Which countries do our customers come from?
"""), sql("SELECT DISTINCT country FROM customers;")]

    c += [md("""
## `LIMIT`
Return at most N rows — great for previewing large tables.
"""), sql("SELECT * FROM orders LIMIT 3;")]

    c += [md("## Practice")]
    c += ex("Select just the `product_name` and `in_stock` columns for every product.",
            "SELECT product_name, in_stock FROM products;")
    c += ex("List every distinct `status` value found in the `orders` table.",
            "SELECT DISTINCT status FROM orders;")
    c += ex("Show each product's name and its price including a fictional 10% tax, "
            "in a column called `price_with_tax`.",
            "SELECT product_name, unit_price, ROUND(unit_price * 1.10, 2) AS price_with_tax\nFROM products;")
    c += [md("""
### ✅ Recap
You can pick columns, alias them, compute new columns, dedupe with `DISTINCT`,
and cap rows with `LIMIT`.

**Next:** `02_filtering_where.ipynb` — filtering rows with `WHERE`.
""")]
    write_nb("01_select_basics.ipynb", c)


# ===========================================================================
# 02 - Filtering with WHERE
# ===========================================================================

def nb_02():
    ex = Ex()
    c = [md("""
# 02 · Filtering Rows with `WHERE`

`WHERE` keeps only the rows that match a condition. This module covers:
- comparison operators (`=`, `<>`, `<`, `>`, `<=`, `>=`)
- combining conditions with `AND`, `OR`, `NOT`
- `BETWEEN`, `IN`
- pattern matching with `LIKE`
- handling `NULL` with `IS NULL` / `IS NOT NULL`
"""), SETUP]

    c += [md("## Simple comparison\nProducts that cost more than $50:"),
          sql("SELECT product_name, unit_price FROM products WHERE unit_price > 50;")]

    c += [md("## Equality and not-equal\n`<>` (or `!=`) means \"not equal\"."),
          sql("SELECT order_id, status FROM orders WHERE status <> 'completed';")]

    c += [md("## Combining with `AND` / `OR`\nElectronics (category 1) under $100:"),
          sql("SELECT product_name, unit_price\nFROM products\nWHERE category_id = 1 AND unit_price < 100;")]

    c += [md("## `BETWEEN` (inclusive range)"),
          sql("SELECT product_name, unit_price\nFROM products\nWHERE unit_price BETWEEN 30 AND 60;")]

    c += [md("## `IN` (match any of a list)"),
          sql("SELECT first_name, country\nFROM customers\nWHERE country IN ('USA', 'UK', 'Japan');")]

    c += [md("""
## `LIKE` (pattern matching)
- `%` matches any sequence of characters
- `_` matches exactly one character

Products whose name contains the word "Pro":
"""), sql("SELECT product_name FROM products WHERE product_name LIKE '%Pro%';")]

    c += [md("Customers whose first name starts with a letter A–E is hard to do "
             "with LIKE alone, but names starting with 'A':"),
          sql("SELECT first_name, last_name FROM customers WHERE first_name LIKE 'A%';")]

    c += [md("""
## Working with `NULL`
`NULL` means "unknown / missing". You **cannot** use `= NULL`; use `IS NULL`.
Customer 9 has no email:
"""), sql("SELECT customer_id, first_name, email FROM customers WHERE email IS NULL;")]
    c += [sql("SELECT customer_id, first_name FROM customers WHERE email IS NOT NULL LIMIT 5;")]

    c += [md("## Practice")]
    c += ex("Find all products with `in_stock` greater than 100.",
            "SELECT product_name, in_stock FROM products WHERE in_stock > 100;")
    c += ex("Find orders that are NOT completed (status is 'pending' or 'cancelled') "
            "using the `IN` operator.",
            "SELECT order_id, status FROM orders WHERE status IN ('pending', 'cancelled');")
    c += ex("List products whose name ends with the word \"Set\".",
            "SELECT product_name FROM products WHERE product_name LIKE '%Set';")
    c += ex("Find customers based in the USA who signed up in 2023 "
            "(hint: signup_date is text like '2023-...').",
            "SELECT first_name, last_name, signup_date\nFROM customers\nWHERE country = 'USA' AND signup_date LIKE '2023-%';")
    c += [md("""
### ✅ Recap
`WHERE` filters rows; combine conditions with `AND`/`OR`/`NOT`, use ranges with
`BETWEEN`, lists with `IN`, patterns with `LIKE`, and always test missing values
with `IS NULL`.

**Next:** `03_sorting_and_limiting.ipynb`.
""")]
    write_nb("02_filtering_where.ipynb", c)


# ===========================================================================
# 03 - Sorting and limiting
# ===========================================================================

def nb_03():
    ex = Ex()
    c = [md("""
# 03 · Sorting & Limiting

- `ORDER BY` sorts results (`ASC` ascending default, `DESC` descending)
- sort by multiple columns
- `LIMIT` + `OFFSET` for "top N" and pagination
"""), SETUP]

    c += [md("## Sort ascending (default)"),
          sql("SELECT product_name, unit_price FROM products ORDER BY unit_price;")]
    c += [md("## Sort descending — most expensive first"),
          sql("SELECT product_name, unit_price FROM products ORDER BY unit_price DESC;")]
    c += [md("## Sort by multiple columns\nBy category, then by price within each category:"),
          sql("SELECT category_id, product_name, unit_price\nFROM products\nORDER BY category_id ASC, unit_price DESC;")]
    c += [md("## Top-N with `LIMIT`\nThe 3 most expensive products:"),
          sql("SELECT product_name, unit_price\nFROM products\nORDER BY unit_price DESC\nLIMIT 3;")]
    c += [md("## Pagination with `OFFSET`\nSkip the first 3, then take the next 3 (page 2):"),
          sql("SELECT product_name, unit_price\nFROM products\nORDER BY unit_price DESC\nLIMIT 3 OFFSET 3;")]

    c += [md("## Practice")]
    c += ex("List all customers sorted by `signup_date`, newest first.",
            "SELECT first_name, last_name, signup_date\nFROM customers\nORDER BY signup_date DESC;")
    c += ex("Show the 5 products with the lowest stock.",
            "SELECT product_name, in_stock FROM products ORDER BY in_stock ASC LIMIT 5;")
    c += ex("Show the 5 highest-paid employees (name, title, salary).",
            "SELECT first_name, last_name, title, salary\nFROM employees\nORDER BY salary DESC\nLIMIT 5;")
    c += [md("""
### ✅ Recap
`ORDER BY` sorts (multi-column, `ASC`/`DESC`); `LIMIT`/`OFFSET` give you top-N
and paging.

**Next:** `04_aggregations_group_by.ipynb`.
""")]
    write_nb("03_sorting_and_limiting.ipynb", c)


# ===========================================================================
# 04 - Aggregations & GROUP BY
# ===========================================================================

def nb_04():
    ex = Ex()
    c = [md("""
# 04 · Aggregations & `GROUP BY`

Aggregate functions summarize many rows into one value:
- `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`
- `GROUP BY` computes an aggregate *per group*
- `HAVING` filters groups (like `WHERE` but after aggregation)

**Order of evaluation:** `FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY`.
"""), SETUP]

    c += [md("## Aggregate over the whole table"),
          sql("""
SELECT
    COUNT(*)        AS num_products,
    AVG(unit_price) AS avg_price,
    MIN(unit_price) AS cheapest,
    MAX(unit_price) AS priciest
FROM products;
""")]

    c += [md("## `COUNT(*)` vs `COUNT(column)`\n`COUNT(column)` ignores NULLs. "
             "We have 12 customers but not all have an email:"),
          sql("SELECT COUNT(*) AS total, COUNT(email) AS with_email FROM customers;")]

    c += [md("## `GROUP BY` — one row per group\nHow many products per category?"),
          sql("""
SELECT category_id, COUNT(*) AS num_products, ROUND(AVG(unit_price), 2) AS avg_price
FROM products
GROUP BY category_id
ORDER BY category_id;
""")]

    c += [md("## Counting customers per country"),
          sql("SELECT country, COUNT(*) AS customers\nFROM customers\nGROUP BY country\nORDER BY customers DESC;")]

    c += [md("""
## `HAVING` — filter the groups
`WHERE` filters rows *before* grouping; `HAVING` filters *after*. Show only
categories that have more than 3 products:
"""), sql("""
SELECT category_id, COUNT(*) AS num_products
FROM products
GROUP BY category_id
HAVING COUNT(*) > 3;
""")]

    c += [md("## `WHERE` + `GROUP BY` + `HAVING` together\n"
             "Average price of products **in stock** per category, keeping only "
             "categories whose average exceeds $50:"),
          sql("""
SELECT category_id, ROUND(AVG(unit_price), 2) AS avg_price
FROM products
WHERE in_stock > 0
GROUP BY category_id
HAVING AVG(unit_price) > 50
ORDER BY avg_price DESC;
""")]

    c += [md("## Practice")]
    c += ex("How many orders are there for each `status`?",
            "SELECT status, COUNT(*) AS n FROM orders GROUP BY status;")
    c += ex("What is the total quantity sold for each `product_id` in `order_items`? "
            "Show the top 5.",
            "SELECT product_id, SUM(quantity) AS total_qty\nFROM order_items\nGROUP BY product_id\nORDER BY total_qty DESC\nLIMIT 5;")
    c += ex("Find countries that have 2 or more customers.",
            "SELECT country, COUNT(*) AS customers\nFROM customers\nGROUP BY country\nHAVING COUNT(*) >= 2;")
    c += [md("""
### ✅ Recap
Aggregates collapse rows; `GROUP BY` aggregates per group; `HAVING` filters
groups. Remember `WHERE` (rows) vs `HAVING` (groups).

**Next:** `05_joins.ipynb` — combining tables.
""")]
    write_nb("04_aggregations_group_by.ipynb", c)


# ===========================================================================
# 05 - Joins
# ===========================================================================

def nb_05():
    ex = Ex()
    c = [md("""
# 05 · Joins — Combining Tables

Real questions span multiple tables. Joins connect them on matching keys.
- `INNER JOIN` — only matching rows in both tables
- `LEFT JOIN` — all rows from the left, matches from the right (or NULLs)
- multi-table joins
- self joins (a table joined to itself)
- `CROSS JOIN` (every combination)
"""), SETUP]

    c += [md("""
## `INNER JOIN`
Products don't store the category *name*, only `category_id`. Join to
`categories` to get readable names. The `ON` clause says how rows match.
"""), sql("""
SELECT p.product_name, c.category_name, p.unit_price
FROM products AS p
INNER JOIN categories AS c ON p.category_id = c.category_id
ORDER BY c.category_name, p.product_name
LIMIT 10;
""")]

    c += [md("## Table aliases\n`p` and `c` above are short aliases — they keep "
             "queries readable and are required when the same column name exists "
             "in both tables.")]

    c += [md("## Joining three tables\nWhich employee handled each order, and for "
             "which customer?"),
          sql("""
SELECT o.order_id,
       cu.first_name || ' ' || cu.last_name AS customer,
       e.first_name  || ' ' || e.last_name  AS employee,
       o.order_date
FROM orders AS o
JOIN customers AS cu ON o.customer_id = cu.customer_id
JOIN employees AS e  ON o.employee_id = e.employee_id
ORDER BY o.order_id
LIMIT 10;
""")]

    c += [md("""
## `LEFT JOIN` — keep unmatched left rows
Every product, plus its supplier name. Some products may have no supplier match;
`LEFT JOIN` keeps them with `NULL` on the supplier side.
"""), sql("""
SELECT p.product_name, s.supplier_name
FROM products AS p
LEFT JOIN suppliers AS s ON p.supplier_id = s.supplier_id
ORDER BY p.product_name
LIMIT 10;
""")]

    c += [md("""
### Finding rows with NO match
`LEFT JOIN ... WHERE right.key IS NULL` is the classic "anti-join". Which
customers have never placed an order?
"""), sql("""
SELECT cu.customer_id, cu.first_name, cu.last_name
FROM customers AS cu
LEFT JOIN orders AS o ON cu.customer_id = o.customer_id
WHERE o.order_id IS NULL;
""")]

    c += [md("""
## Joins + aggregation
The most powerful combination. Revenue per category (quantity × price, summed):
"""), sql("""
SELECT c.category_name,
       ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
FROM order_items AS oi
JOIN products   AS p ON oi.product_id = p.product_id
JOIN categories AS c ON p.category_id = c.category_id
GROUP BY c.category_name
ORDER BY revenue DESC;
""")]

    c += [md("""
## Self join
`employees.manager_id` points back into `employees`. Join the table to itself to
show each employee alongside their manager.
"""), sql("""
SELECT e.first_name || ' ' || e.last_name AS employee,
       e.title,
       m.first_name || ' ' || m.last_name AS manager
FROM employees AS e
LEFT JOIN employees AS m ON e.manager_id = m.employee_id
ORDER BY e.employee_id;
""")]

    c += [md("## Practice")]
    c += ex("List each product with its supplier's country (product_name, country).",
            "SELECT p.product_name, s.country\nFROM products AS p\nJOIN suppliers AS s ON p.supplier_id = s.supplier_id\nORDER BY p.product_name;")
    c += ex("Show every order with the customer's full name and the order status, "
            "for completed orders only.",
            "SELECT o.order_id, cu.first_name || ' ' || cu.last_name AS customer, o.status\nFROM orders AS o\nJOIN customers AS cu ON o.customer_id = cu.customer_id\nWHERE o.status = 'completed'\nORDER BY o.order_id;")
    c += ex("Compute total revenue per customer (join orders → order_items). "
            "Show the top 5 customers by revenue.",
            "SELECT cu.first_name || ' ' || cu.last_name AS customer,\n       ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue\nFROM customers AS cu\nJOIN orders AS o      ON cu.customer_id = o.customer_id\nJOIN order_items AS oi ON o.order_id = oi.order_id\nGROUP BY cu.customer_id\nORDER BY revenue DESC\nLIMIT 5;")
    c += [md("""
### ✅ Recap
`INNER JOIN` keeps matches; `LEFT JOIN` keeps all left rows; anti-joins find
missing matches; self-joins relate a table to itself. Joins + `GROUP BY` answer
most business questions.

**Next:** `06_subqueries.ipynb`.
""")]
    write_nb("05_joins.ipynb", c)


# ===========================================================================
# 06 - Subqueries
# ===========================================================================

def nb_06():
    ex = Ex()
    c = [md("""
# 06 · Subqueries

A subquery is a query nested inside another. Flavors:
- **scalar** subquery → returns one value
- subquery with `IN`
- **correlated** subquery → references the outer query
- `EXISTS`
- subquery in `FROM` (a *derived table*)
"""), SETUP]

    c += [md("## Scalar subquery\nProducts priced above the overall average price. "
             "The inner query returns a single number."),
          sql("""
SELECT product_name, unit_price
FROM products
WHERE unit_price > (SELECT AVG(unit_price) FROM products)
ORDER BY unit_price DESC;
""")]

    c += [md("## Subquery with `IN`\nCustomers who have placed at least one order "
             "(their id appears in `orders`)."),
          sql("""
SELECT first_name, last_name
FROM customers
WHERE customer_id IN (SELECT customer_id FROM orders);
""")]

    c += [md("## `NOT IN` — the opposite\nCustomers who have never ordered:"),
          sql("""
SELECT first_name, last_name
FROM customers
WHERE customer_id NOT IN (SELECT customer_id FROM orders);
""")]

    c += [md("""
## Correlated subquery
The inner query runs *per outer row* and references it. Count each customer's
orders inline:
"""), sql("""
SELECT cu.first_name, cu.last_name,
       (SELECT COUNT(*) FROM orders o WHERE o.customer_id = cu.customer_id) AS order_count
FROM customers AS cu
ORDER BY order_count DESC;
""")]

    c += [md("""
## `EXISTS`
Often clearer/faster than `IN` for "does a related row exist?". Products that
have actually been sold:
"""), sql("""
SELECT p.product_name
FROM products AS p
WHERE EXISTS (SELECT 1 FROM order_items oi WHERE oi.product_id = p.product_id)
ORDER BY p.product_name;
""")]

    c += [md("""
## Subquery in `FROM` (derived table)
Compute per-order totals first, then filter on them. You must alias the derived
table.
"""), sql("""
SELECT order_id, order_total
FROM (
    SELECT order_id, SUM(quantity * unit_price) AS order_total
    FROM order_items
    GROUP BY order_id
) AS totals
WHERE order_total > 200
ORDER BY order_total DESC;
""")]

    c += [md("## Practice")]
    c += ex("Find products that are cheaper than the average price of their own... "
            "keep it simple: products cheaper than the overall average price.",
            "SELECT product_name, unit_price\nFROM products\nWHERE unit_price < (SELECT AVG(unit_price) FROM products)\nORDER BY unit_price;")
    c += ex("List employees who have handled at least one order (use IN or EXISTS "
            "against the orders table).",
            "SELECT first_name, last_name\nFROM employees e\nWHERE EXISTS (SELECT 1 FROM orders o WHERE o.employee_id = e.employee_id);")
    c += ex("Using a derived table, find the average order total across all orders.",
            "SELECT ROUND(AVG(order_total), 2) AS avg_order_value\nFROM (\n    SELECT order_id, SUM(quantity * unit_price) AS order_total\n    FROM order_items\n    GROUP BY order_id\n) AS t;")
    c += [md("""
### ✅ Recap
Subqueries let one query feed another: scalars for comparisons, `IN`/`EXISTS`
for membership, correlated subqueries for per-row logic, and derived tables to
query an intermediate result.

**Next:** `07_set_operations.ipynb`.
""")]
    write_nb("06_subqueries.ipynb", c)


# ===========================================================================
# 07 - Set operations
# ===========================================================================

def nb_07():
    ex = Ex()
    c = [md("""
# 07 · Set Operations

Stack the results of two queries vertically. Both queries must return the same
number of columns with compatible types.
- `UNION` — combine and remove duplicates
- `UNION ALL` — combine and keep duplicates (faster)
- `INTERSECT` — rows in both
- `EXCEPT` — rows in the first but not the second
"""), SETUP]

    c += [md("## `UNION ALL`\nA combined contact list of customer and employee "
             "names, tagged by source:"),
          sql("""
SELECT first_name, last_name, 'customer' AS kind FROM customers
UNION ALL
SELECT first_name, last_name, 'employee' AS kind FROM employees
ORDER BY kind, last_name;
""")]

    c += [md("## `UNION` (dedupes)\nAll distinct countries where we have either a "
             "customer or a supplier:"),
          sql("""
SELECT country FROM customers
UNION
SELECT country FROM suppliers
ORDER BY country;
""")]

    c += [md("## `INTERSECT`\nCountries that have **both** a customer and a supplier:"),
          sql("""
SELECT country FROM customers
INTERSECT
SELECT country FROM suppliers;
""")]

    c += [md("## `EXCEPT`\nCountries with a customer but **no** supplier:"),
          sql("""
SELECT country FROM customers
EXCEPT
SELECT country FROM suppliers;
""")]

    c += [md("## Practice")]
    c += ex("Produce one column `city_or_country` listing every distinct customer "
            "city UNION every distinct supplier country.",
            "SELECT city AS city_or_country FROM customers\nUNION\nSELECT country FROM suppliers\nORDER BY 1;")
    c += ex("Which countries appear in the suppliers table but NOT among customers?",
            "SELECT country FROM suppliers\nEXCEPT\nSELECT country FROM customers;")
    c += [md("""
### ✅ Recap
`UNION`/`UNION ALL` stack rows, `INTERSECT` keeps common rows, `EXCEPT`
subtracts. Column count and order must match.

**Next:** `08_string_and_date_functions.ipynb`.
""")]
    write_nb("07_set_operations.ipynb", c)


# ===========================================================================
# 08 - String & date functions
# ===========================================================================

def nb_08():
    ex = Ex()
    c = [md("""
# 08 · String & Date Functions

SQLite ships handy built-in functions.
- **String:** `UPPER`, `LOWER`, `LENGTH`, `SUBSTR`, `REPLACE`, `TRIM`, `||`, `INSTR`
- **Number:** `ROUND`, `ABS`, `CAST`
- **Date/time:** `DATE`, `STRFTIME`, `JULIANDAY` (SQLite stores dates as text)
"""), SETUP]

    c += [md("## String functions"),
          sql("""
SELECT
    product_name,
    UPPER(product_name)              AS upper,
    LENGTH(product_name)             AS len,
    SUBSTR(product_name, 1, 4)       AS first4,
    REPLACE(product_name, ' ', '_')  AS snake
FROM products
LIMIT 6;
""")]

    c += [md("## Building an email-style handle\nLowercase first name + last name:"),
          sql("""
SELECT first_name, last_name,
       LOWER(first_name || '.' || last_name) AS handle
FROM customers
LIMIT 6;
""")]

    c += [md("""
## Date functions
Our dates are ISO text (`'YYYY-MM-DD'`), which SQLite's date functions
understand directly.
"""), sql("""
SELECT
    order_id,
    order_date,
    STRFTIME('%Y', order_date)  AS year,
    STRFTIME('%m', order_date)  AS month,
    STRFTIME('%Y-%m', order_date) AS year_month
FROM orders
LIMIT 8;
""")]

    c += [md("## Grouping by month\nOrders per calendar month:"),
          sql("""
SELECT STRFTIME('%Y-%m', order_date) AS month, COUNT(*) AS orders
FROM orders
GROUP BY month
ORDER BY month;
""")]

    c += [md("## Date arithmetic\nCustomer tenure in days as of 2024-07-01 using "
             "`JULIANDAY`:"),
          sql("""
SELECT first_name, signup_date,
       CAST(JULIANDAY('2024-07-01') - JULIANDAY(signup_date) AS INTEGER) AS days_since_signup
FROM customers
ORDER BY days_since_signup DESC
LIMIT 6;
""")]

    c += [md("## Practice")]
    c += ex("Show each supplier name in UPPERCASE alongside its country.",
            "SELECT UPPER(supplier_name) AS supplier, country FROM suppliers;")
    c += ex("Count how many orders happened in each year.",
            "SELECT STRFTIME('%Y', order_date) AS year, COUNT(*) AS orders\nFROM orders\nGROUP BY year\nORDER BY year;")
    c += ex("For each customer show the month name-number they signed up "
            "(format 'YYYY-MM').",
            "SELECT first_name, STRFTIME('%Y-%m', signup_date) AS signup_month\nFROM customers\nORDER BY signup_month;")
    c += [md("""
### ✅ Recap
String functions clean and reshape text; `STRFTIME`/`JULIANDAY` extract parts of
dates and do date math. Remember SQLite keeps dates as text.

**Next:** `09_case_and_conditional.ipynb`.
""")]
    write_nb("08_string_and_date_functions.ipynb", c)


# ===========================================================================
# 09 - CASE & conditional logic
# ===========================================================================

def nb_09():
    ex = Ex()
    c = [md("""
# 09 · Conditional Logic

- `CASE WHEN ... THEN ... ELSE ... END` — SQL's if/else
- `COALESCE` — first non-NULL value
- `NULLIF` — turn a value into NULL
- the "conditional aggregation" trick (pivoting with `CASE` inside `SUM`)
"""), SETUP]

    c += [md("## `CASE` — bucketing values\nLabel products by a price tier:"),
          sql("""
SELECT product_name, unit_price,
       CASE
           WHEN unit_price < 30  THEN 'budget'
           WHEN unit_price < 100 THEN 'mid'
           ELSE 'premium'
       END AS price_tier
FROM products
ORDER BY unit_price;
""")]

    c += [md("## `COALESCE` — handle NULLs\nShow email, or '(none)' when missing:"),
          sql("SELECT first_name, COALESCE(email, '(none)') AS email FROM customers;")]

    c += [md("## `NULLIF`\nReturns NULL if the two args are equal — handy to avoid "
             "divide-by-zero. Here, treat 0 stock as NULL:"),
          sql("SELECT product_name, NULLIF(in_stock, 0) AS stock_or_null FROM products LIMIT 5;")]

    c += [md("""
## Conditional aggregation (a simple pivot)
Count orders by status **as columns** in a single row using `CASE` inside `SUM`:
"""), sql("""
SELECT
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed,
    SUM(CASE WHEN status = 'pending'   THEN 1 ELSE 0 END) AS pending,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled
FROM orders;
""")]

    c += [md("## Practice")]
    c += ex("Label each employee as 'leadership' if salary >= 150000, "
            "'senior' if >= 90000, else 'staff'.",
            "SELECT first_name, salary,\n       CASE WHEN salary >= 150000 THEN 'leadership'\n            WHEN salary >= 90000  THEN 'senior'\n            ELSE 'staff' END AS band\nFROM employees\nORDER BY salary DESC;")
    c += ex("Show each product with a column 'availability' that says "
            "'in stock' when in_stock > 0 else 'out of stock'.",
            "SELECT product_name, in_stock,\n       CASE WHEN in_stock > 0 THEN 'in stock' ELSE 'out of stock' END AS availability\nFROM products;")
    c += [md("""
### ✅ Recap
`CASE` adds branching logic; `COALESCE`/`NULLIF` tame NULLs; `CASE` inside
aggregates pivots rows into columns.

**Next:** `10_window_functions.ipynb`.
""")]
    write_nb("09_case_and_conditional.ipynb", c)


# ===========================================================================
# 10 - Window functions
# ===========================================================================

def nb_10():
    ex = Ex()
    c = [md("""
# 10 · Window Functions

Window functions compute across a set of rows **related to the current row**
without collapsing them (unlike `GROUP BY`). The magic word is `OVER`.
- `ROW_NUMBER`, `RANK`, `DENSE_RANK`
- `PARTITION BY` (windows per group) and `ORDER BY` inside `OVER`
- running totals with `SUM() OVER (...)`
- `LAG` / `LEAD` (previous / next row)

> Requires SQLite 3.25+ (the version bundled with modern Python — you're fine).
"""), SETUP]

    c += [md("## `ROW_NUMBER` — number rows\nRank products by price, most expensive = 1:"),
          sql("""
SELECT product_name, unit_price,
       ROW_NUMBER() OVER (ORDER BY unit_price DESC) AS price_rank
FROM products
LIMIT 10;
""")]

    c += [md("""
## `PARTITION BY` — restart per group
Rank products **within each category** by price. The partition restarts the
numbering for every category.
"""), sql("""
SELECT category_id, product_name, unit_price,
       RANK() OVER (PARTITION BY category_id ORDER BY unit_price DESC) AS rank_in_cat
FROM products
ORDER BY category_id, rank_in_cat;
""")]

    c += [md("""
## RANK vs DENSE_RANK vs ROW_NUMBER
These three only differ **when there are ties** — rows with the same `ORDER BY`
value. Our product prices are all distinct, so to see the difference clearly we
use a small scoreboard with deliberate ties (Ana & Ben both 95, Cyd & Dan both
88):
"""), sql("""
WITH scores(player, score) AS (
    VALUES ('Ana', 95), ('Ben', 95), ('Cyd', 88), ('Dan', 88), ('Eve', 70)
)
SELECT player, score,
       ROW_NUMBER() OVER (ORDER BY score DESC) AS row_number,
       RANK()       OVER (ORDER BY score DESC) AS rank,
       DENSE_RANK() OVER (ORDER BY score DESC) AS dense_rank
FROM scores;
""")]
    c += [md("""
Read the tied rows to see exactly how they differ:

| player | score | row_number | rank | dense_rank |
|--------|------:|:----------:|:----:|:----------:|
| Ana | 95 | 1 | 1 | 1 |
| Ben | 95 | 2 | 1 | 1 |
| Cyd | 88 | 3 | 3 | 2 |
| Dan | 88 | 4 | 3 | 2 |
| Eve | 70 | 5 | 5 | 3 |

- **`ROW_NUMBER`** — always unique, ties broken arbitrarily: `1, 2, 3, 4, 5`.
- **`RANK`** — ties share a number, then it **skips** (leaves a gap): `1, 1, 3, 3, 5`.
- **`DENSE_RANK`** — ties share a number, **no gaps**: `1, 1, 2, 2, 3`.

Rule of thumb: use `ROW_NUMBER` to pick exactly one row per group, `RANK` for
"standard competition" ranking (two golds → no silver), and `DENSE_RANK` when you
don't want gaps in the numbering.
""")]

    c += [md("""
## Running total
Order revenue over time, plus a cumulative total. The frame defaults to all rows
from the start up to the current row when you add `ORDER BY`.
"""), sql("""
WITH order_totals AS (
    SELECT o.order_id, o.order_date,
           SUM(oi.quantity * oi.unit_price) AS order_total
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.order_id, o.order_date
)
SELECT order_date, order_id, order_total,
       SUM(order_total) OVER (ORDER BY order_date, order_id) AS running_total
FROM order_totals
ORDER BY order_date, order_id;
""")]

    c += [md("""
## `LAG` / `LEAD`
Compare each order's total to the previous order's total.
"""), sql("""
WITH order_totals AS (
    SELECT o.order_id, o.order_date,
           SUM(oi.quantity * oi.unit_price) AS order_total
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.order_id, o.order_date
)
SELECT order_date, order_total,
       LAG(order_total)  OVER (ORDER BY order_date, order_id) AS prev_total,
       order_total - LAG(order_total) OVER (ORDER BY order_date, order_id) AS change
FROM order_totals
ORDER BY order_date, order_id;
""")]

    c += [md("## Average per group alongside each row\n"
             "`AVG() OVER (PARTITION BY ...)` shows the category average next to "
             "each product without collapsing rows:"),
          sql("""
SELECT category_id, product_name, unit_price,
       ROUND(AVG(unit_price) OVER (PARTITION BY category_id), 2) AS cat_avg
FROM products
ORDER BY category_id, unit_price DESC
LIMIT 12;
""")]

    c += [md("## Practice")]
    c += ex("Number the customers by signup order (1 = earliest) using ROW_NUMBER.",
            "SELECT first_name, signup_date,\n       ROW_NUMBER() OVER (ORDER BY signup_date) AS signup_order\nFROM customers;")
    c += ex("Within each category, find the single most expensive product "
            "(use ROW_NUMBER in a CTE and keep rank = 1).",
            "WITH ranked AS (\n  SELECT category_id, product_name, unit_price,\n         ROW_NUMBER() OVER (PARTITION BY category_id ORDER BY unit_price DESC) AS rn\n  FROM products\n)\nSELECT category_id, product_name, unit_price\nFROM ranked WHERE rn = 1\nORDER BY category_id;")
    c += [md("""
### ✅ Recap
Window functions rank, number, and accumulate across related rows while keeping
every row. `PARTITION BY` groups the window; `ORDER BY` inside `OVER` orders it;
`LAG`/`LEAD` look at neighbors.

**Next:** `11_ctes.ipynb`.
""")]
    write_nb("10_window_functions.ipynb", c)


# ===========================================================================
# 11 - CTEs
# ===========================================================================

def nb_11():
    ex = Ex()
    c = [md("""
# 11 · Common Table Expressions (CTEs)

A CTE is a named temporary result defined with `WITH`. CTEs make complex queries
readable by naming each step.
- a single CTE
- chaining multiple CTEs
- **recursive** CTEs (e.g. walking an org hierarchy)
"""), SETUP]

    c += [md("""
## Basic CTE
Same idea as a derived table, but named and readable. Orders above the average
order value:
"""), sql("""
WITH order_totals AS (
    SELECT order_id, SUM(quantity * unit_price) AS total
    FROM order_items
    GROUP BY order_id
)
SELECT order_id, total
FROM order_totals
WHERE total > (SELECT AVG(total) FROM order_totals)
ORDER BY total DESC;
""")]

    c += [md("""
## Multiple CTEs
Chain steps with commas. Compute revenue per customer, then keep the top spenders.
"""), sql("""
WITH per_order AS (
    SELECT order_id, SUM(quantity * unit_price) AS order_total
    FROM order_items
    GROUP BY order_id
),
per_customer AS (
    SELECT o.customer_id, SUM(po.order_total) AS revenue
    FROM orders o
    JOIN per_order po ON o.order_id = po.order_id
    GROUP BY o.customer_id
)
SELECT cu.first_name, cu.last_name, ROUND(pc.revenue, 2) AS revenue
FROM per_customer pc
JOIN customers cu ON pc.customer_id = cu.customer_id
ORDER BY revenue DESC
LIMIT 5;
""")]

    c += [md("""
## Recursive CTE — the employee hierarchy
A recursive CTE has an **anchor** (starting rows) and a **recursive** part that
references the CTE. Here we walk from the CEO down, tracking each person's level.
"""), sql("""
WITH RECURSIVE org AS (
    -- anchor: the top of the tree (no manager)
    SELECT employee_id, first_name, last_name, manager_id, 1 AS level
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- recursive step: everyone who reports to someone already in `org`
    SELECT e.employee_id, e.first_name, e.last_name, e.manager_id, org.level + 1
    FROM employees e
    JOIN org ON e.manager_id = org.employee_id
)
SELECT level,
       PRINTF('%.*c', (level - 1) * 2, ' ') || first_name || ' ' || last_name AS chart
FROM org
ORDER BY level, employee_id;
""")]

    c += [md("""
## Recursive CTE — generate a number series
Recursive CTEs aren't only for hierarchies. Generate numbers 1..10:
"""), sql("""
WITH RECURSIVE nums(n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1 FROM nums WHERE n < 10
)
SELECT n, n * n AS squared FROM nums;
""")]

    c += [md("## Practice")]
    c += ex("Using a CTE, list categories whose total revenue exceeds $300 "
            "(join order_items→products, sum quantity*unit_price per category).",
            "WITH cat_rev AS (\n  SELECT p.category_id, SUM(oi.quantity * oi.unit_price) AS revenue\n  FROM order_items oi\n  JOIN products p ON oi.product_id = p.product_id\n  GROUP BY p.category_id\n)\nSELECT c.category_name, ROUND(cr.revenue, 2) AS revenue\nFROM cat_rev cr\nJOIN categories c ON cr.category_id = c.category_id\nWHERE cr.revenue > 300\nORDER BY revenue DESC;")
    c += ex("Use a recursive CTE to list the first 12 even numbers.",
            "WITH RECURSIVE evens(n) AS (\n  SELECT 2\n  UNION ALL\n  SELECT n + 2 FROM evens WHERE n < 24\n)\nSELECT n FROM evens;")
    c += [md("""
### ✅ Recap
CTEs (`WITH`) name intermediate results so big queries read top-to-bottom. Chain
several with commas. Recursive CTEs walk hierarchies and generate sequences.

**Next:** `12_ddl_create_tables.ipynb`.
""")]
    write_nb("11_ctes.ipynb", c)


# ===========================================================================
# 12 - DDL
# ===========================================================================

def nb_12():
    ex = Ex()
    c = [md("""
# 12 · Data Definition Language (DDL)

DDL creates and changes the **structure** of the database.
- `CREATE TABLE`, data types, `PRIMARY KEY`
- constraints: `NOT NULL`, `UNIQUE`, `CHECK`, `DEFAULT`, `FOREIGN KEY`
- `ALTER TABLE`
- `DROP TABLE`

> These cells create their own throwaway tables (named `demo_*`) so they never
> touch the course data. Each is dropped first, so you can re-run safely.
"""), SETUP]

    c += [md("""
## SQLite data types
SQLite is flexible; the core storage classes are `INTEGER`, `REAL`, `TEXT`,
`BLOB`, and `NULL`. You'll also see `NUMERIC`. Dates are stored as `TEXT`
(ISO strings) or numbers.
""")]

    c += [md("## `CREATE TABLE` with constraints"),
          sql("""
DROP TABLE IF EXISTS demo_students;
CREATE TABLE demo_students (
    student_id INTEGER PRIMARY KEY,          -- auto-increments in SQLite
    full_name  TEXT NOT NULL,                -- required
    email      TEXT UNIQUE,                  -- no duplicates
    age        INTEGER CHECK (age >= 0),     -- validated
    status     TEXT NOT NULL DEFAULT 'active'-- default value
);
""")]
    c += [md("Insert a couple of rows and read them back:"),
          sql("""
INSERT INTO demo_students (full_name, email, age) VALUES
    ('Ada Lovelace', 'ada@school.edu', 28),
    ('Alan Turing',  'alan@school.edu', 30);
SELECT * FROM demo_students;
""")]

    c += [md("Notice `status` defaulted to 'active' and `student_id` auto-filled. "
             "A `CHECK` violation is rejected — this next cell **should error** "
             "(that's the point):"),
          sql("INSERT INTO demo_students (full_name, age) VALUES ('Bad Age', -5);")]

    c += [md("## `ALTER TABLE` — add a column"),
          sql("""
ALTER TABLE demo_students ADD COLUMN gpa REAL;
SELECT student_id, full_name, gpa FROM demo_students;
""")]

    c += [md("## `FOREIGN KEY`\nLink an enrollments table to students:"),
          sql("""
DROP TABLE IF EXISTS demo_enrollments;
CREATE TABLE demo_enrollments (
    enrollment_id INTEGER PRIMARY KEY,
    student_id    INTEGER NOT NULL,
    course        TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES demo_students(student_id)
);
INSERT INTO demo_enrollments (student_id, course) VALUES (1, 'Databases'), (2, 'Logic');
SELECT * FROM demo_enrollments;
""")]

    c += [md("## `DROP TABLE` — clean up our demo tables"),
          sql("""
DROP TABLE IF EXISTS demo_enrollments;
DROP TABLE IF EXISTS demo_students;
SELECT 'cleaned up' AS status;
""")]

    c += [md("## Practice")]
    c += ex("Create a table `demo_books` with book_id (primary key), title "
            "(required text), and price (real, must be >= 0). Then insert one row "
            "and select it.",
            "DROP TABLE IF EXISTS demo_books;\nCREATE TABLE demo_books (\n    book_id INTEGER PRIMARY KEY,\n    title   TEXT NOT NULL,\n    price   REAL CHECK (price >= 0)\n);\nINSERT INTO demo_books (title, price) VALUES ('SQL for All', 24.99);\nSELECT * FROM demo_books;")
    c += [md("""
### ✅ Recap
DDL shapes the schema: `CREATE TABLE` with typed columns and constraints
(`NOT NULL`, `UNIQUE`, `CHECK`, `DEFAULT`, `FOREIGN KEY`), `ALTER TABLE` to
change it, `DROP TABLE` to remove it.

**Next:** `13_dml_insert_update_delete.ipynb`.
""")]
    write_nb("12_ddl_create_tables.ipynb", c)


# ===========================================================================
# 13 - DML
# ===========================================================================

def nb_13():
    ex = Ex()
    c = [md("""
# 13 · Data Manipulation (INSERT / UPDATE / DELETE)

DML changes the **data** inside tables.
- `INSERT` (single & multiple rows, insert-from-select)
- `UPDATE` (always mind the `WHERE`!)
- `DELETE`
- `UPSERT` (`INSERT ... ON CONFLICT`)

> Again we work on a throwaway `demo_inventory` table, rebuilt at the top so you
> can re-run freely and never disturb the course data.
"""), SETUP]

    c += [md("## Set up a sandbox table"),
          sql("""
DROP TABLE IF EXISTS demo_inventory;
CREATE TABLE demo_inventory (
    sku       TEXT PRIMARY KEY,
    name      TEXT NOT NULL,
    quantity  INTEGER NOT NULL DEFAULT 0,
    price     REAL NOT NULL
);
SELECT 'ready' AS status;
""")]

    c += [md("## `INSERT` multiple rows"),
          sql("""
INSERT INTO demo_inventory (sku, name, quantity, price) VALUES
    ('A1', 'Widget',  100, 2.50),
    ('A2', 'Gadget',   40, 9.99),
    ('A3', 'Gizmo',     0, 14.00);
SELECT * FROM demo_inventory;
""")]

    c += [md("## `UPDATE`\nRaise all prices by 10%. The `WHERE` here targets one row; "
             "**omit `WHERE` and every row changes** — a common, costly mistake."),
          sql("""
UPDATE demo_inventory SET price = ROUND(price * 1.10, 2) WHERE sku = 'A2';
SELECT * FROM demo_inventory;
""")]

    c += [md("## `UPDATE` many rows\nRestock everything that's out of stock:"),
          sql("""
UPDATE demo_inventory SET quantity = 25 WHERE quantity = 0;
SELECT * FROM demo_inventory;
""")]

    c += [md("## `DELETE`\nRemove cheap items. Again, mind the `WHERE`."),
          sql("""
DELETE FROM demo_inventory WHERE price < 3;
SELECT * FROM demo_inventory;
""")]

    c += [md("""
## `UPSERT` — insert or update on conflict
Insert a row; if the primary key already exists, update it instead. Run this
cell twice and watch the quantity change rather than erroring.
"""), sql("""
INSERT INTO demo_inventory (sku, name, quantity, price)
VALUES ('A2', 'Gadget', 5, 9.99)
ON CONFLICT(sku) DO UPDATE SET quantity = quantity + excluded.quantity;
SELECT * FROM demo_inventory WHERE sku = 'A2';
""")]

    c += [md("## `INSERT ... SELECT`\nCopy selected course products into our sandbox:"),
          sql("""
INSERT INTO demo_inventory (sku, name, quantity, price)
SELECT 'P' || product_id, product_name, in_stock, unit_price
FROM products
WHERE category_id = 2;               -- Books
SELECT * FROM demo_inventory ORDER BY sku;
""")]

    c += [md("## Clean up"),
          sql("DROP TABLE IF EXISTS demo_inventory;\nSELECT 'cleaned up' AS status;")]

    c += [md("## Practice")]
    c += ex("Create a table demo_tasks(id integer pk, title text, done integer default 0). "
            "Insert two tasks, then mark the first as done (done = 1). Select all.",
            "DROP TABLE IF EXISTS demo_tasks;\nCREATE TABLE demo_tasks (id INTEGER PRIMARY KEY, title TEXT, done INTEGER DEFAULT 0);\nINSERT INTO demo_tasks (title) VALUES ('Learn INSERT'), ('Learn UPDATE');\nUPDATE demo_tasks SET done = 1 WHERE id = 1;\nSELECT * FROM demo_tasks;")
    c += [md("""
### ✅ Recap
`INSERT` adds rows (including from a `SELECT`), `UPDATE` changes them, `DELETE`
removes them — and `WHERE` is what keeps those last two from hitting every row.
`UPSERT` merges inserts with updates.

**Next:** `14_views_and_indexes.ipynb`.
""")]
    write_nb("13_dml_insert_update_delete.ipynb", c)


# ===========================================================================
# 14 - Views & indexes
# ===========================================================================

def nb_14():
    ex = Ex()
    c = [md("""
# 14 · Views & Indexes

- **Views** are saved queries you can treat like a table — great for reuse.
- **Indexes** speed up lookups and joins on large tables.

> Views/indexes here are prefixed `demo_` and dropped at the end.
"""), SETUP]

    c += [md("## Creating a view\nA view named `demo_order_values` that computes each "
             "order's total. Query it like a table afterwards."),
          sql("""
DROP VIEW IF EXISTS demo_order_values;
CREATE VIEW demo_order_values AS
SELECT o.order_id, o.customer_id, o.order_date,
       SUM(oi.quantity * oi.unit_price) AS order_total
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_id, o.customer_id, o.order_date;

SELECT * FROM demo_order_values ORDER BY order_total DESC LIMIT 5;
""")]

    c += [md("## Views compose\nBuild on the view like any table — e.g. total "
             "revenue per customer via the view:"),
          sql("""
SELECT cu.first_name, cu.last_name, ROUND(SUM(v.order_total), 2) AS revenue
FROM demo_order_values v
JOIN customers cu ON v.customer_id = cu.customer_id
GROUP BY v.customer_id
ORDER BY revenue DESC
LIMIT 5;
""")]

    c += [md("""
## Indexes
An index is a lookup structure the database uses to find rows fast. On big
tables, an index on frequently-filtered/joined columns can turn a full scan into
an instant lookup. Create one on `orders.customer_id`:
"""), sql("""
DROP INDEX IF EXISTS demo_idx_orders_customer;
CREATE INDEX demo_idx_orders_customer ON orders(customer_id);
SELECT 'index created' AS status;
""")]

    c += [md("## Did the planner use it?\n`EXPLAIN QUERY PLAN` shows how SQLite will "
             "run a query. After creating the index, a lookup by customer_id can "
             "use it (`SEARCH ... USING INDEX`)."),
          sql("EXPLAIN QUERY PLAN\nSELECT * FROM orders WHERE customer_id = 1;")]

    c += [md("""
### When to index
Index columns you frequently filter or join on. Indexes cost storage and slow
down writes slightly, so don't index everything — index what your queries
actually use.
""")]

    c += [md("## Clean up"),
          sql("DROP VIEW IF EXISTS demo_order_values;\nDROP INDEX IF EXISTS demo_idx_orders_customer;\nSELECT 'cleaned up' AS status;")]

    c += [md("## Practice")]
    c += ex("Create a view demo_expensive_products listing products with unit_price "
            "> 75 (name, price). Then select from it ordered by price desc.",
            "DROP VIEW IF EXISTS demo_expensive_products;\nCREATE VIEW demo_expensive_products AS\nSELECT product_name, unit_price FROM products WHERE unit_price > 75;\nSELECT * FROM demo_expensive_products ORDER BY unit_price DESC;")
    c += [md("""
### ✅ Recap
Views save and reuse queries as virtual tables; indexes accelerate reads on the
columns you filter and join by. Inspect plans with `EXPLAIN QUERY PLAN`.

**Next:** `15_transactions.ipynb`.
""")]
    write_nb("14_views_and_indexes.ipynb", c)


# ===========================================================================
# 15 - Transactions
# ===========================================================================

def nb_15():
    c = [md("""
# 15 · Transactions & ACID

A **transaction** groups several statements into one all-or-nothing unit.
- `BEGIN` starts it, `COMMIT` saves it, `ROLLBACK` undoes it.
- **ACID:** Atomicity, Consistency, Isolation, Durability.

The classic example is a money transfer: subtract from one account and add to
another. If the second step fails, the first must be undone — otherwise money
vanishes.

Because notebook SQL magic auto-commits each cell, this module uses a plain
Python `sqlite3` connection so we can control the transaction explicitly and
show `COMMIT` vs `ROLLBACK` clearly.
"""), SETUP]

    c += [code("""
import sqlite3, os

# Use a separate throwaway database so we never touch the course data.
path = 'data' if os.path.isdir('data') else '.'
demo_db = os.path.join(path, 'demo_bank.db')
conn = sqlite3.connect(demo_db)
conn.execute("DROP TABLE IF EXISTS accounts")
conn.execute(\"\"\"CREATE TABLE accounts (
    name    TEXT PRIMARY KEY,
    balance REAL NOT NULL CHECK (balance >= 0)
)\"\"\")
conn.executemany("INSERT INTO accounts VALUES (?, ?)",
                 [('Alice', 100.0), ('Bob', 50.0)])
conn.commit()
print(conn.execute("SELECT * FROM accounts").fetchall())
""")]

    c += [md("## A successful transfer (COMMIT)\nMove $30 from Alice to Bob atomically."),
          code("""
try:
    conn.execute("BEGIN")
    conn.execute("UPDATE accounts SET balance = balance - 30 WHERE name = 'Alice'")
    conn.execute("UPDATE accounts SET balance = balance + 30 WHERE name = 'Bob'")
    conn.commit()
    print("Committed.")
except Exception as e:
    conn.rollback()
    print("Rolled back:", e)

print(conn.execute("SELECT * FROM accounts").fetchall())
""")]

    c += [md("""
## A failed transfer (ROLLBACK)
Now try to move $1000 from Bob (who only has $80). The `CHECK (balance >= 0)`
constraint rejects the debit, the exception triggers `ROLLBACK`, and **no
partial change** remains — that's Atomicity.
"""), code("""
try:
    conn.execute("BEGIN")
    conn.execute("UPDATE accounts SET balance = balance - 1000 WHERE name = 'Bob'")
    conn.execute("UPDATE accounts SET balance = balance + 1000 WHERE name = 'Alice'")
    conn.commit()
    print("Committed.")
except Exception as e:
    conn.rollback()
    print("Rolled back:", type(e).__name__, "-", e)

# Balances are unchanged from the previous cell:
print(conn.execute("SELECT * FROM accounts").fetchall())
""")]

    c += [md("## Manual ROLLBACK\nYou can also undo deliberately, e.g. after "
             "inspecting the result."),
          code("""
conn.execute("BEGIN")
conn.execute("UPDATE accounts SET balance = 0 WHERE name = 'Alice'")
print("Inside txn:", conn.execute("SELECT * FROM accounts").fetchall())
conn.rollback()
print("After rollback:", conn.execute("SELECT * FROM accounts").fetchall())
""")]

    c += [md("## Clean up"),
          code("""
conn.close()
if os.path.exists(demo_db):
    os.remove(demo_db)
print("cleaned up")
""")]

    c += [md("""
### ✅ Recap
Transactions make multi-step changes atomic: `COMMIT` to save, `ROLLBACK` to
undo. ACID guarantees that your data stays correct even when things fail
midway.

**Next:** `16_capstone_project.ipynb` — put it all together.
""")]
    write_nb("15_transactions.ipynb", c)


# ===========================================================================
# 16 - Capstone
# ===========================================================================

def nb_16():
    ex = Ex()
    c = [md("""
# 16 · Capstone Project — Retail Analytics

Time to be the hero. 🦸 You're the new data analyst at our retail company. The
leadership team has questions; answer them with SQL. Each task lists the skills
it exercises. Try each yourself, then reveal the solution.

Run the setup cell, then work through the challenges.
"""), SETUP]

    c += [md("### Challenge 1 — Monthly revenue trend\n*Skills: joins, aggregation, dates.*\n\n"
             "Report total revenue per month (only `completed` orders), ordered by month.")]
    c += ex("Compute completed-order revenue for each `YYYY-MM`.",
            "SELECT STRFTIME('%Y-%m', o.order_date) AS month,\n       ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue\nFROM orders o\nJOIN order_items oi ON o.order_id = oi.order_id\nWHERE o.status = 'completed'\nGROUP BY month\nORDER BY month;")

    c += [md("### Challenge 2 — Top customers\n*Skills: joins, aggregation, ranking.*\n\n"
             "Rank customers by lifetime revenue (completed orders). Show name, "
             "revenue, and rank; return the top 5.")]
    c += ex("Rank customers by total revenue and show the top 5.",
            "WITH rev AS (\n  SELECT o.customer_id, SUM(oi.quantity * oi.unit_price) AS revenue\n  FROM orders o\n  JOIN order_items oi ON o.order_id = oi.order_id\n  WHERE o.status = 'completed'\n  GROUP BY o.customer_id\n)\nSELECT cu.first_name || ' ' || cu.last_name AS customer,\n       ROUND(rev.revenue, 2) AS revenue,\n       RANK() OVER (ORDER BY rev.revenue DESC) AS rnk\nFROM rev JOIN customers cu ON rev.customer_id = cu.customer_id\nORDER BY rnk\nLIMIT 5;")

    c += [md("### Challenge 3 — Best-selling product per category\n"
             "*Skills: joins, window functions, CTE.*\n\n"
             "For each category, find the product with the highest total units sold.")]
    c += ex("Top product (by units sold) within each category.",
            "WITH sales AS (\n  SELECT p.category_id, p.product_name, SUM(oi.quantity) AS units\n  FROM order_items oi\n  JOIN products p ON oi.product_id = p.product_id\n  GROUP BY p.category_id, p.product_name\n),\nranked AS (\n  SELECT category_id, product_name, units,\n         ROW_NUMBER() OVER (PARTITION BY category_id ORDER BY units DESC) AS rn\n  FROM sales\n)\nSELECT c.category_name, r.product_name, r.units\nFROM ranked r\nJOIN categories c ON r.category_id = c.category_id\nWHERE r.rn = 1\nORDER BY c.category_name;")

    c += [md("### Challenge 4 — Customer segmentation\n*Skills: CASE, aggregation, joins.*\n\n"
             "Label each customer 'VIP' (revenue >= 300), 'Regular' (>= 100), "
             "'New/Low' (> 0), or 'No orders' (0).")]
    c += ex("Segment every customer by lifetime completed revenue.",
            "WITH rev AS (\n  SELECT cu.customer_id,\n         COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS revenue\n  FROM customers cu\n  LEFT JOIN orders o      ON cu.customer_id = o.customer_id AND o.status = 'completed'\n  LEFT JOIN order_items oi ON o.order_id = oi.order_id\n  GROUP BY cu.customer_id\n)\nSELECT cu.first_name || ' ' || cu.last_name AS customer,\n       ROUND(rev.revenue, 2) AS revenue,\n       CASE WHEN rev.revenue >= 300 THEN 'VIP'\n            WHEN rev.revenue >= 100 THEN 'Regular'\n            WHEN rev.revenue > 0    THEN 'New/Low'\n            ELSE 'No orders' END AS segment\nFROM rev JOIN customers cu ON rev.customer_id = cu.customer_id\nORDER BY revenue DESC;")

    c += [md("### Challenge 5 — Sales rep leaderboard\n*Skills: joins, aggregation, self-join.*\n\n"
             "For each sales rep, show their manager and the total revenue they "
             "generated from completed orders.")]
    c += ex("Revenue per employee, with their manager's name.",
            "SELECT e.first_name || ' ' || e.last_name AS employee,\n       m.first_name || ' ' || m.last_name AS manager,\n       ROUND(COALESCE(SUM(oi.quantity * oi.unit_price), 0), 2) AS revenue\nFROM employees e\nLEFT JOIN employees m   ON e.manager_id = m.employee_id\nLEFT JOIN orders o      ON o.employee_id = e.employee_id AND o.status = 'completed'\nLEFT JOIN order_items oi ON o.order_id = oi.order_id\nGROUP BY e.employee_id\nORDER BY revenue DESC;")

    c += [md("""
## 🎉 Congratulations — you finished the SQL Zero-to-Hero Bootcamp!

You can now:
- query, filter, sort, and shape data
- aggregate and group
- join many tables and reason about relationships
- write subqueries, CTEs, and window functions
- define schema (DDL), modify data (DML), and use transactions safely
- build views and indexes

**Where to go next:** try these queries against your own data, learn your
target database's dialect (PostgreSQL, MySQL, SQL Server), and practice on
real datasets. Keep this project around as a reference — re-run
`build_notebooks.py` any time to reset the exercises.
""")]
    write_nb("16_capstone_project.ipynb", c)


# ===========================================================================
# ADVANCED TRACK
# ===========================================================================

# ---- 17 Advanced joins ----------------------------------------------------

def nb_17():
    ex = Ex()
    c = [md("""
# 17 · Advanced Joins

You know `INNER`/`LEFT`/self joins. Engineers also need the full toolbox:
- `CROSS JOIN` (Cartesian product) and when it's useful
- `RIGHT JOIN` and `FULL OUTER JOIN` (SQLite 3.39+)
- `USING` vs `ON`, and the danger of `NATURAL JOIN`
- **non-equi joins** (join on `<`, `>`, `BETWEEN`, not just `=`)
- **semi-joins** (`EXISTS`/`IN`) vs **anti-joins** (`NOT EXISTS`)
- the crucial difference between filtering in `ON` vs `WHERE` for outer joins
"""), SETUP]

    c += [md("""
## `CROSS JOIN` — every combination
Produces every pairing of left × right rows. Great for building grids/matrices,
e.g. every category across every quarter (even ones with no data):
"""), sql("""
WITH quarters(quarter) AS (VALUES ('Q1'), ('Q2'), ('Q3'), ('Q4'))
SELECT c.category_name, quarters.quarter
FROM categories c
CROSS JOIN quarters
ORDER BY c.category_name, quarters.quarter
LIMIT 12;
""")]

    c += [md("""
## `USING` vs `ON`
When the join columns have the **same name** in both tables, `USING (col)` is
shorthand for `ON a.col = b.col` and it collapses the duplicate column into one.
"""), sql("""
SELECT product_name, category_name
FROM products
JOIN categories USING (category_id)
LIMIT 5;
""")]

    c += [md("""
## `NATURAL JOIN` — convenient but risky
`NATURAL JOIN` auto-joins on **all** identically-named columns. It works here
because `products` and `categories` share only `category_id` — but it silently
breaks the day someone adds another same-named column (like `created_at`). Prefer
explicit `ON`/`USING` in real code.
"""), sql("SELECT product_name, category_name FROM products NATURAL JOIN categories LIMIT 5;")]

    c += [md("""
## Non-equi join
The `ON` condition doesn't have to be `=`. Here we join each product to every
*more expensive* product to count how many products outrank it on price — a
non-equi self-join.
"""), sql("""
SELECT p1.product_name, p1.unit_price,
       COUNT(p2.product_id) AS pricier_products
FROM products p1
LEFT JOIN products p2 ON p2.unit_price > p1.unit_price
GROUP BY p1.product_id, p1.product_name, p1.unit_price
ORDER BY pricier_products
LIMIT 8;
""")]

    c += [md("""
## `RIGHT JOIN` and `FULL OUTER JOIN`
`RIGHT JOIN` keeps all rows of the *right* table; `FULL OUTER JOIN` keeps
unmatched rows from **both** sides (NULLs where there's no match). Compare a
target list of countries against the countries we actually have customers in:
"""), sql("""
WITH target(country) AS (VALUES ('USA'), ('UK'), ('Mars')),
     have AS (SELECT DISTINCT country FROM customers)
SELECT target.country AS target_country,
       have.country   AS customer_country
FROM target
FULL OUTER JOIN have ON target.country = have.country
ORDER BY target_country;
""")]
    c += [md("`Mars` appears with a NULL match (a target with no customers); the "
             "real customer countries not in the target list appear with a NULL "
             "target. That two-sided view is what `FULL OUTER JOIN` is for.")]

    c += [md("""
## Semi-join vs anti-join
A **semi-join** returns left rows that *have* a match (without duplicating them) —
express it with `EXISTS` or `IN`. An **anti-join** returns left rows with *no*
match — `NOT EXISTS`.
"""),
          sql("-- SEMI-JOIN: products that have been ordered\n"
              "SELECT product_name FROM products p\n"
              "WHERE EXISTS (SELECT 1 FROM order_items oi WHERE oi.product_id = p.product_id)\n"
              "ORDER BY product_name;"),
          sql("-- ANTI-JOIN: products never ordered\n"
              "SELECT product_name FROM products p\n"
              "WHERE NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.product_id = p.product_id)\n"
              "ORDER BY product_name;")]

    c += [md("""
## ⚠️ `ON` vs `WHERE` in outer joins — a classic trap
With a `LEFT JOIN`, a condition on the **right** table placed in `WHERE` filters
out the NULL-extended rows, silently turning your `LEFT JOIN` back into an
`INNER JOIN`. Put such conditions in `ON` to keep unmatched left rows.

Condition in `ON` (keeps every customer, only counts *completed* orders):
"""), sql("""
SELECT cu.first_name, COUNT(o.order_id) AS completed_orders
FROM customers cu
LEFT JOIN orders o ON o.customer_id = cu.customer_id AND o.status = 'completed'
GROUP BY cu.customer_id, cu.first_name
ORDER BY completed_orders;
""")]
    c += [md("Same filter in `WHERE` instead — customers with **zero** completed "
             "orders vanish, because their single NULL row fails `status = 'completed'`:"),
          sql("""
SELECT cu.first_name, COUNT(o.order_id) AS completed_orders
FROM customers cu
LEFT JOIN orders o ON o.customer_id = cu.customer_id
WHERE o.status = 'completed'
GROUP BY cu.customer_id, cu.first_name
ORDER BY completed_orders;
""")]

    c += [md("## Practice")]
    c += ex("Use a FULL OUTER JOIN to list every country that appears as either a "
            "customer country or a supplier country, showing which side(s) it came "
            "from.",
            "WITH cust AS (SELECT DISTINCT country FROM customers),\n     sup  AS (SELECT DISTINCT country FROM suppliers)\nSELECT cust.country AS customer_country, sup.country AS supplier_country\nFROM cust FULL OUTER JOIN sup ON cust.country = sup.country\nORDER BY COALESCE(cust.country, sup.country);")
    c += ex("Using an anti-join, list employees who have never been assigned to an "
            "order.",
            "SELECT first_name, last_name FROM employees e\nWHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.employee_id = e.employee_id);")
    c += [md("""
### ✅ Recap
`CROSS JOIN` builds combinations; `RIGHT`/`FULL OUTER` keep unmatched rows;
`USING` is tidy same-name joining while `NATURAL JOIN` is fragile; non-equi joins
match on ranges; `EXISTS`/`NOT EXISTS` are semi/anti-joins; and outer-join
filters belong in `ON`, not `WHERE`.

**Next:** `18_advanced_aggregation.ipynb`.
""")]
    write_nb("17_advanced_joins.ipynb", c)


# ---- 18 Advanced aggregation ---------------------------------------------

def nb_18():
    ex = Ex()
    c = [md("""
# 18 · Advanced Aggregation

Beyond `COUNT`/`SUM`/`AVG`:
- `COUNT(DISTINCT ...)`
- `GROUP_CONCAT` (string aggregation)
- the `FILTER (WHERE ...)` clause — per-aggregate conditions
- conditional aggregation (pivoting rows into columns)
- subtotals & grand totals (emulating `ROLLUP`, which SQLite lacks)
"""), SETUP]

    c += [md("## `COUNT(DISTINCT ...)` and `GROUP_CONCAT`\n"
             "How many *distinct* products each category contains, plus a "
             "comma-joined list of their names:"),
          sql("""
SELECT c.category_name,
       COUNT(DISTINCT p.product_id) AS num_products,
       GROUP_CONCAT(p.product_name, ', ') AS product_list
FROM categories c
JOIN products p ON p.category_id = c.category_id
GROUP BY c.category_name
ORDER BY c.category_name;
""")]

    c += [md("""
## The `FILTER` clause
`FILTER (WHERE ...)` restricts which rows feed a *single* aggregate — cleaner
than stuffing `CASE` inside every function. Per employee: total orders vs how
many were completed vs cancelled, in one pass:
"""), sql("""
SELECT e.first_name,
       COUNT(o.order_id)                                   AS total_orders,
       COUNT(*) FILTER (WHERE o.status = 'completed')      AS completed,
       COUNT(*) FILTER (WHERE o.status = 'cancelled')      AS cancelled,
       COUNT(DISTINCT o.customer_id)                       AS unique_customers
FROM employees e
LEFT JOIN orders o ON o.employee_id = e.employee_id
GROUP BY e.employee_id, e.first_name
ORDER BY total_orders DESC;
""")]

    c += [md("""
## Conditional aggregation (pivot)
The portable equivalent of `FILTER`, and the standard way to *pivot* rows into
columns: put `CASE` inside `SUM`. Revenue per category, split by order status:
"""), sql("""
SELECT c.category_name,
       ROUND(SUM(CASE WHEN o.status = 'completed' THEN oi.quantity * oi.unit_price ELSE 0 END), 2) AS completed_rev,
       ROUND(SUM(CASE WHEN o.status = 'pending'   THEN oi.quantity * oi.unit_price ELSE 0 END), 2) AS pending_rev
FROM order_items oi
JOIN products p  ON oi.product_id = p.product_id
JOIN categories c ON p.category_id = c.category_id
JOIN orders o    ON oi.order_id = o.order_id
GROUP BY c.category_name
ORDER BY completed_rev DESC;
""")]

    c += [md("""
## Subtotals + grand total (emulating `ROLLUP`)
Postgres/MySQL have `GROUP BY ... WITH ROLLUP` / `GROUPING SETS`. SQLite doesn't,
so you `UNION ALL` a grand-total row. (Knowing the pattern matters when you move
between databases.)
"""), sql("""
WITH per_cat AS (
    SELECT c.category_name AS category,
           ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
    FROM order_items oi
    JOIN products p   ON oi.product_id = p.product_id
    JOIN categories c ON p.category_id = c.category_id
    GROUP BY c.category_name
),
with_total AS (
    SELECT category, revenue, 0 AS sort_key FROM per_cat
    UNION ALL
    SELECT 'ALL CATEGORIES', ROUND(SUM(revenue), 2), 1 FROM per_cat
)
SELECT category, revenue
FROM with_total
ORDER BY sort_key, revenue DESC;
""")]

    c += [md("## Practice")]
    c += ex("For each country, show the number of customers and a GROUP_CONCAT of "
            "their first names.",
            "SELECT country, COUNT(*) AS customers, GROUP_CONCAT(first_name, ', ') AS names\nFROM customers\nGROUP BY country\nORDER BY customers DESC;")
    c += ex("Using FILTER, for each customer show total orders and how many are "
            "still pending.",
            "SELECT cu.first_name,\n       COUNT(o.order_id) AS orders,\n       COUNT(*) FILTER (WHERE o.status = 'pending') AS pending\nFROM customers cu\nLEFT JOIN orders o ON o.customer_id = cu.customer_id\nGROUP BY cu.customer_id, cu.first_name\nORDER BY orders DESC;")
    c += [md("""
### ✅ Recap
`COUNT(DISTINCT)`, `GROUP_CONCAT`, and `FILTER` sharpen aggregation; `CASE`
inside aggregates pivots data; and `UNION ALL` gives you subtotals/grand totals
where `ROLLUP` isn't available.

**Next:** `19_advanced_window_functions.ipynb`.
""")]
    write_nb("18_advanced_aggregation.ipynb", c)


# ---- 19 Advanced window functions ----------------------------------------

def nb_19():
    ex = Ex()
    c = [md("""
# 19 · Advanced Window Functions

Module 10 introduced windows. Now the powerful parts engineers rely on:
- **frame clauses**: `ROWS`/`RANGE BETWEEN ... AND ...`
- **moving averages** and windowed aggregates
- `NTILE` (quantile buckets)
- `FIRST_VALUE`, `LAST_VALUE`, `NTH_VALUE`
- distribution: `PERCENT_RANK`, `CUME_DIST`
"""), SETUP]

    c += [md("""
## Frames: `ROWS BETWEEN ... AND ...`
A window can be narrowed to a **frame** relative to the current row. This is what
powers moving averages. Here: a 3-order moving average of order totals
(current row + the 2 before it).
"""), sql("""
WITH t AS (
    SELECT o.order_id, o.order_date, SUM(oi.quantity * oi.unit_price) AS total
    FROM orders o JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.order_id, o.order_date
)
SELECT order_date, ROUND(total, 2) AS total,
       ROUND(AVG(total) OVER (ORDER BY order_date, order_id
                              ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS moving_avg_3
FROM t
ORDER BY order_date, order_id;
""")]

    c += [md("""
### `ROWS` vs `RANGE`
`ROWS` counts a fixed number of physical rows; `RANGE` groups rows with the same
`ORDER BY` value into the frame together. For running totals with unique dates
they behave the same, but with ties they differ — reach for `ROWS` when you want
exactly *N* rows.
""")]

    c += [md("""
## `NTILE` — split into buckets
Divide products into 4 price quartiles (1 = cheapest quartile):
"""), sql("""
SELECT product_name, unit_price,
       NTILE(4) OVER (ORDER BY unit_price) AS price_quartile
FROM products
ORDER BY unit_price;
""")]

    c += [md("""
## `FIRST_VALUE` / `LAST_VALUE`
Show, next to each product, the most and least expensive product in its category.
Note the explicit full frame on `LAST_VALUE` — without it the frame ends at the
current row and you'd get the wrong answer (a very common bug).
"""), sql("""
SELECT category_id, product_name, unit_price,
       FIRST_VALUE(product_name) OVER w AS priciest_in_cat,
       LAST_VALUE(product_name)  OVER w AS cheapest_in_cat
FROM products
WINDOW w AS (PARTITION BY category_id ORDER BY unit_price DESC
             ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
ORDER BY category_id, unit_price DESC;
""")]
    c += [md("*(The `WINDOW w AS (...)` clause names a window so multiple functions "
             "can reuse it — handy when several columns share the same frame.)*")]

    c += [md("""
## Distribution: `PERCENT_RANK` & `CUME_DIST`
Where does each product's price sit in the overall distribution?
- `PERCENT_RANK` → relative rank from 0 to 1
- `CUME_DIST` → fraction of rows at or below this value
"""), sql("""
SELECT product_name, unit_price,
       ROUND(PERCENT_RANK() OVER (ORDER BY unit_price), 2) AS pct_rank,
       ROUND(CUME_DIST()   OVER (ORDER BY unit_price), 2) AS cume_dist
FROM products
ORDER BY unit_price DESC
LIMIT 10;
""")]

    c += [md("## Practice")]
    c += ex("Compute a running (cumulative) count of customers over signup_date "
            "order.",
            "SELECT first_name, signup_date,\n       COUNT(*) OVER (ORDER BY signup_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS customers_so_far\nFROM customers\nORDER BY signup_date;")
    c += ex("Split employees into 3 salary bands using NTILE(3) (1 = lowest band).",
            "SELECT first_name, salary, NTILE(3) OVER (ORDER BY salary) AS salary_band\nFROM employees\nORDER BY salary;")
    c += [md("""
### ✅ Recap
Frames (`ROWS`/`RANGE BETWEEN`) turn windows into moving calculations; `NTILE`
buckets rows; `FIRST_VALUE`/`LAST_VALUE` grab boundary values (mind the frame!);
`PERCENT_RANK`/`CUME_DIST` describe distributions.

**Next:** `20_nulls_and_three_valued_logic.ipynb`.
""")]
    write_nb("19_advanced_window_functions.ipynb", c)


# ---- 20 NULLs & three-valued logic ---------------------------------------

def nb_20():
    ex = Ex()
    c = [md("""
# 20 · NULLs & Three-Valued Logic

`NULL` means **unknown**, and it makes SQL logic *three-valued*: expressions can
be `TRUE`, `FALSE`, or `UNKNOWN`. Mishandling NULLs is one of the most common
sources of subtle SQL bugs. This module makes you bulletproof.
"""), SETUP]

    c += [md("""
## `NULL` is not equal to anything — not even `NULL`
`= NULL` is never true; it evaluates to `UNKNOWN`, and `WHERE` only keeps `TRUE`
rows. Always test with `IS NULL` / `IS NOT NULL`.
"""), sql("""
SELECT
    (NULL = NULL)     AS null_eq_null,     -- NULL (unknown), not 1
    (NULL <> 1)       AS null_ne_one,      -- NULL
    (NULL IS NULL)    AS null_is_null;     -- 1 (true)
""")]

    c += [md("Rows with a missing email — only `IS NULL` finds them:"),
          sql("SELECT customer_id, first_name, email FROM customers WHERE email IS NULL;")]

    c += [md("""
## ⚠️ The `NOT IN` + NULL trap
If the list/subquery behind `NOT IN` contains **even one NULL**, the whole
predicate becomes `UNKNOWN` and you get **zero rows** — a notorious bug. Watch:
"""), sql("""
WITH ids(id) AS (VALUES (1), (2), (NULL))
SELECT customer_id, first_name
FROM customers
WHERE customer_id NOT IN (SELECT id FROM ids);   -- returns NOTHING!
""")]
    c += [md("The robust fix is `NOT EXISTS`, which is NULL-safe:"),
          sql("""
WITH ids(id) AS (VALUES (1), (2), (NULL))
SELECT customer_id, first_name
FROM customers cu
WHERE NOT EXISTS (SELECT 1 FROM ids WHERE ids.id = cu.customer_id)
ORDER BY customer_id;
""")]

    c += [md("""
## NULLs in aggregates, `DISTINCT`, and `GROUP BY`
- Aggregates **ignore** NULLs: `AVG`/`SUM`/`COUNT(col)` skip them (so `AVG` can
  differ from `SUM/COUNT(*)`).
- `GROUP BY` treats all NULLs as **one** group.
- `DISTINCT` treats NULLs as **equal** (collapses to one).
"""), sql("""
SELECT COUNT(*)      AS total_rows,
       COUNT(email)  AS non_null_emails,   -- ignores the NULL
       COUNT(DISTINCT country) AS distinct_countries
FROM customers;
""")]

    c += [md("""
## Taming NULLs: `COALESCE`, `IFNULL`, `NULLIF`
- `COALESCE(a, b, c)` → first non-NULL
- `IFNULL(a, b)` → two-argument shortcut
- `NULLIF(a, b)` → NULL when `a = b` (great to avoid divide-by-zero)
"""), sql("""
SELECT first_name,
       COALESCE(email, 'no-email@unknown') AS email,
       IFNULL(email, 'none')               AS email_short
FROM customers
LIMIT 6;
""")]
    c += [md("`NULLIF` guarding a division (returns NULL instead of erroring when "
             "the denominator is 0):"),
          sql("SELECT 100.0 / NULLIF(0, 0) AS safe_divide;")]

    c += [md("""
## Sorting NULLs
By default SQLite sorts NULLs **first** in ascending order. Use
`NULLS LAST` / `NULLS FIRST` to control it explicitly:
"""), sql("SELECT first_name, email FROM customers ORDER BY email NULLS LAST LIMIT 6;")]

    c += [md("## Practice")]
    c += ex("Count how many customers are missing an email, using a NULL-aware "
            "condition.",
            "SELECT COUNT(*) AS missing_email FROM customers WHERE email IS NULL;")
    c += ex("Show each customer's email, substituting the text 'N/A' when it is "
            "missing.",
            "SELECT first_name, COALESCE(email, 'N/A') AS email FROM customers;")
    c += [md("""
### ✅ Recap
`NULL` = unknown → three-valued logic. Compare with `IS [NOT] NULL`, avoid the
`NOT IN`+NULL trap (use `NOT EXISTS`), remember aggregates skip NULLs while
`GROUP BY`/`DISTINCT` fold them together, and reach for
`COALESCE`/`IFNULL`/`NULLIF` to handle them.

**Next:** `21_data_modeling_and_normalization.ipynb`.
""")]
    write_nb("20_nulls_and_three_valued_logic.ipynb", c)


# ---- 21 Data modeling & normalization ------------------------------------

def nb_21():
    ex = Ex()
    c = [md("""
# 21 · Data Modeling & Normalization

Good SQL starts with a good schema. This module covers the design theory every
engineer should know:
- entities, attributes, primary & foreign keys
- surrogate vs natural keys, composite keys
- relationship types: one-to-one, one-to-many, many-to-many
- **normalization** (1NF → 2NF → 3NF) and the anomalies it prevents
- referential integrity with `ON DELETE CASCADE`
"""), SETUP]

    c += [md("""
## Keys
- **Primary key (PK):** uniquely identifies a row (e.g. `customer_id`).
- **Foreign key (FK):** a column referencing another table's PK (e.g.
  `orders.customer_id → customers.customer_id`) — this enforces *referential
  integrity*.
- **Surrogate key:** a meaningless auto-generated id (our integer ids).
- **Natural key:** a real-world unique value (e.g. an email). Surrogate keys are
  usually preferred because natural values can change.
- **Composite key:** a PK spanning multiple columns — like
  `order_items(order_id, product_id)`.
""")]

    c += [md("""
## Relationship types
- **One-to-many (1:N):** one customer → many orders. The "many" side holds the FK.
- **Many-to-many (M:N):** orders ↔ products. You resolve it with a **junction
  table** — that's exactly what `order_items` is.
- **One-to-one (1:1):** rarer; often a table split for optional/large columns.

Our whole schema in one line: `customers 1─∞ orders 1─∞ order_items ∞─1 products`.
""")]

    c += [md("""
## Why normalize? The anomalies of a "wide" table
Imagine cramming everything into one denormalized table:
"""), sql("""
DROP TABLE IF EXISTS demo_orders_flat;
CREATE TABLE demo_orders_flat (
    order_id      INTEGER,
    customer_name TEXT,
    customer_city TEXT,     -- repeated for every order by that customer
    product_name  TEXT,
    product_price REAL,     -- repeated for every order of that product
    quantity      INTEGER
);
INSERT INTO demo_orders_flat VALUES
    (1, 'Alice', 'Seattle', 'Wireless Mouse', 25.00, 2),
    (1, 'Alice', 'Seattle', 'SQL Fundamentals', 39.99, 1),
    (2, 'Alice', 'Seattle', 'USB-C Hub', 34.50, 1);
SELECT * FROM demo_orders_flat;
""")]
    c += [md("""
This design causes three classic anomalies:
- **Update anomaly:** Alice moves city → you must update many rows or data goes
  inconsistent.
- **Insertion anomaly:** you can't record a new product until someone orders it.
- **Deletion anomaly:** delete the last order of a product and you lose the
  product's existence entirely.

Normalization removes this redundancy.
""")]

    c += [md("""
## The normal forms (informally)
- **1NF:** atomic values, no repeating groups, a key on each row. (No
  comma-separated "products" column.)
- **2NF:** 1NF **and** every non-key column depends on the *whole* composite key,
  not just part of it. (In `order_items`, `quantity` depends on both
  `order_id` **and** `product_id`; a product's `price` does **not**, so it lives
  in `products`.)
- **3NF:** 2NF **and** no *transitive* dependencies — non-key columns don't
  depend on other non-key columns. (`customer_city` depends on the customer, not
  the order, so it belongs in `customers`.)

Our course schema is already in 3NF: customer facts live in `customers`, product
facts in `products`, and `order_items` holds only what's true of a specific line
item. That's why there's no redundancy to keep in sync.
""")]

    c += [md("""
## Referential integrity: `ON DELETE CASCADE`
A foreign key can define what happens to children when a parent is deleted.
`ON DELETE CASCADE` deletes the children automatically. Foreign keys must be
enabled per connection with `PRAGMA foreign_keys = ON` (done at the top of this
one cell so the demo is self-contained):
"""), sql("""
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS demo_line_items;
DROP TABLE IF EXISTS demo_orders;

CREATE TABLE demo_orders (
    id INTEGER PRIMARY KEY,
    customer TEXT
);
CREATE TABLE demo_line_items (
    id       INTEGER PRIMARY KEY,
    order_id INTEGER REFERENCES demo_orders(id) ON DELETE CASCADE,
    item     TEXT
);

INSERT INTO demo_orders VALUES (1, 'Alice'), (2, 'Bob');
INSERT INTO demo_line_items (order_id, item) VALUES (1, 'Mouse'), (1, 'Book'), (2, 'Pan');

-- delete order 1: its line items vanish automatically
DELETE FROM demo_orders WHERE id = 1;

SELECT * FROM demo_line_items;
""")]
    c += [md("Only Bob's line item remains — the cascade removed order 1's children."),
          sql("DROP TABLE IF EXISTS demo_line_items;\nDROP TABLE IF EXISTS demo_orders;\nDROP TABLE IF EXISTS demo_orders_flat;\nSELECT 'cleaned up' AS status;")]

    c += [md("## Practice")]
    c += ex("In our schema, which table resolves the many-to-many relationship "
            "between orders and products, and what is its composite primary key? "
            "(Write a query listing that table's columns to confirm.)",
            "PRAGMA table_info(order_items);")
    c += [md("""
### ✅ Recap
Model entities with PKs, connect them with FKs, resolve M:N with junction tables,
and normalize to 3NF to eliminate update/insert/delete anomalies. Use
`ON DELETE CASCADE` (with `PRAGMA foreign_keys = ON`) to keep children consistent
with parents.

**Next:** `22_indexing_and_performance.ipynb`.
""")]
    write_nb("21_data_modeling_and_normalization.ipynb", c)


# ---- 22 Indexing & performance -------------------------------------------

def nb_22():
    ex = Ex()
    c = [md("""
# 22 · Indexing & Query Performance

Correct SQL that's slow still fails in production. This module teaches how the
engine finds rows and how to make it fast:
- reading `EXPLAIN QUERY PLAN` (`SCAN` vs `SEARCH`)
- single-column, **composite**, **covering**, and **unique** indexes
- when an index *won't* be used
- `ANALYZE` and the write-time cost of indexes

> Demo indexes are prefixed `demo_` and dropped at the end.
"""), SETUP]

    c += [md("""
## `EXPLAIN QUERY PLAN`
It shows *how* SQLite will run a query. Two words to watch for:
- **`SCAN`** — read every row (a full table scan; fine for tiny tables, deadly
  for large ones).
- **`SEARCH ... USING INDEX`** — jump straight to matching rows via an index.

With no useful index, filtering `orders` by `customer_id` is a full scan:
"""), sql("EXPLAIN QUERY PLAN\nSELECT * FROM orders WHERE customer_id = 1;")]

    c += [md("## Add an index, watch the plan change"),
          sql("""
DROP INDEX IF EXISTS demo_idx_orders_customer;
CREATE INDEX demo_idx_orders_customer ON orders(customer_id);
EXPLAIN QUERY PLAN
SELECT * FROM orders WHERE customer_id = 1;
""")]
    c += [md("The plan now reads `SEARCH ... USING INDEX demo_idx_orders_customer` — "
             "an indexed lookup instead of a scan.")]

    c += [md("""
## Composite indexes & the leftmost-prefix rule
An index on `(a, b)` can serve queries filtering on `a`, or `a AND b`, but **not
`b` alone** — like a phone book sorted by (last, first). Order the columns by how
you query them.
"""), sql("""
DROP INDEX IF EXISTS demo_idx_prod_cat_price;
CREATE INDEX demo_idx_prod_cat_price ON products(category_id, unit_price);
EXPLAIN QUERY PLAN
SELECT product_name FROM products WHERE category_id = 1 AND unit_price > 50;
""")]

    c += [md("""
## Covering index
If an index contains **every column a query needs**, SQLite answers from the
index alone and never touches the table — shown as `USING COVERING INDEX`.
"""), sql("""
DROP INDEX IF EXISTS demo_idx_cover;
CREATE INDEX demo_idx_cover ON products(category_id, unit_price, product_name);
EXPLAIN QUERY PLAN
SELECT category_id, unit_price, product_name
FROM products WHERE category_id = 2;
""")]

    c += [md("""
## Unique index
Enforces uniqueness *and* speeds lookups. (A `UNIQUE` constraint creates one
automatically — e.g. `customers.email`.)
"""), sql("""
DROP INDEX IF EXISTS demo_idx_unique_sku;
CREATE UNIQUE INDEX demo_idx_unique_sku ON products(product_name);
SELECT 'unique index created' AS status;
""")]

    c += [md("""
## ⚠️ When an index is *not* used
- **A function/expression on the column:** `WHERE LOWER(product_name) = 'x'`
  can't use a plain index on `product_name` (you'd need an *expression index*).
- **A leading wildcard:** `LIKE '%mouse'` can't seek; `LIKE 'mouse%'` can.
- **Low selectivity:** if a value matches most rows, a scan is actually cheaper.

Example the planner will still scan:
"""), sql("EXPLAIN QUERY PLAN\nSELECT * FROM products WHERE LOWER(product_name) = 'usb-c hub';")]

    c += [md("""
## `ANALYZE` and the cost of indexes
`ANALYZE` gathers statistics so the planner makes better choices. Remember every
index **speeds reads but slows writes** (each `INSERT`/`UPDATE`/`DELETE` must
maintain it) and uses disk — index the columns your queries actually filter and
join on, not every column.
"""), sql("ANALYZE;\nSELECT 'stats gathered' AS status;")]

    c += [md("## Clean up"),
          sql("DROP INDEX IF EXISTS demo_idx_orders_customer;\n"
              "DROP INDEX IF EXISTS demo_idx_prod_cat_price;\n"
              "DROP INDEX IF EXISTS demo_idx_cover;\n"
              "DROP INDEX IF EXISTS demo_idx_unique_sku;\n"
              "SELECT 'cleaned up' AS status;")]

    c += [md("## Practice")]
    c += ex("Create an index on order_items(product_id), then use EXPLAIN QUERY "
            "PLAN to confirm a lookup by product_id uses it. Drop it afterwards.",
            "DROP INDEX IF EXISTS demo_idx_oi_product;\nCREATE INDEX demo_idx_oi_product ON order_items(product_id);\nEXPLAIN QUERY PLAN SELECT * FROM order_items WHERE product_id = 6;")
    c += [md("""
### ✅ Recap
Read plans (`SCAN` = bad on big tables, `SEARCH USING INDEX` = good). Composite
indexes follow the leftmost-prefix rule; covering indexes avoid table lookups;
functions/leading-wildcards defeat indexes. Index deliberately — reads get
faster, writes get slower.

**Next:** `23_json_in_sqlite.ipynb`.
""")]
    write_nb("22_indexing_and_performance.ipynb", c)


# ---- 23 JSON --------------------------------------------------------------

def nb_23():
    ex = Ex()
    c = [md("""
# 23 · Working with JSON

Modern apps store semi-structured JSON in a column. SQLite's JSON functions let
you query and build it with SQL.
- extract values: `json_extract`, the `->` and `->>` operators
- build JSON: `json_object`, `json_array`, `json_group_array`
- expand JSON into rows: `json_each` (a table-valued function)
- modify JSON: `json_set`
- indexing JSON with an expression index

> Requires SQLite 3.38+ for the `->>` operator (your Python 3.12 build is newer).
> Uses a throwaway `demo_events` table.
"""), SETUP]

    c += [md("## Store some JSON"),
          sql("""
DROP TABLE IF EXISTS demo_events;
CREATE TABLE demo_events (
    id      INTEGER PRIMARY KEY,
    payload TEXT   -- JSON stored as text
);
INSERT INTO demo_events (payload) VALUES
    ('{"user":"alice","action":"login","amount":0,"tags":["web","mobile"]}'),
    ('{"user":"bob","action":"purchase","amount":42.5,"tags":["web"]}'),
    ('{"user":"carla","action":"purchase","amount":19.0,"tags":["mobile","promo"]}');
SELECT * FROM demo_events;
""")]

    c += [md("""
## Extracting values
- `json_extract(payload, '$.user')` — path-based extraction
- `payload -> '$.user'` — returns JSON
- `payload ->> '$.user'` — returns a plain SQL text/number value (usually what you want)
"""), sql("""
SELECT id,
       json_extract(payload, '$.user')   AS user,
       payload ->> 'action'              AS action,
       CAST(payload ->> 'amount' AS REAL) AS amount
FROM demo_events;
""")]

    c += [md("## Filter and aggregate on JSON fields\nTotal purchase amount per action:"),
          sql("""
SELECT payload ->> 'action' AS action,
       ROUND(SUM(payload ->> 'amount'), 2) AS total_amount,
       COUNT(*) AS events
FROM demo_events
GROUP BY action;
""")]

    c += [md("""
## Expand a JSON array into rows with `json_each`
`json_each` is a table-valued function — join it to a table to unnest arrays.
Here we explode each event's `tags` array into one row per tag, then count tags:
"""), sql("""
SELECT j.value AS tag, COUNT(*) AS uses
FROM demo_events e, json_each(e.payload, '$.tags') AS j
GROUP BY j.value
ORDER BY uses DESC, tag;
""")]

    c += [md("## Build JSON from rows\n`json_object` builds an object; "
             "`json_group_array` aggregates rows into a JSON array:"),
          sql("""
SELECT json_object(
           'category', c.category_name,
           'products', json_group_array(p.product_name)
       ) AS category_json
FROM categories c
JOIN products p ON p.category_id = c.category_id
WHERE c.category_name = 'Books'
GROUP BY c.category_name;
""")]

    c += [md("## Modify JSON with `json_set`\nAdd/replace a field, returning new JSON:"),
          sql("""
SELECT id,
       json_set(payload, '$.processed', json('true')) AS updated
FROM demo_events
WHERE id = 1;
""")]

    c += [md("## Index a JSON field (expression index)\nSpeeds up filters on a "
             "specific JSON path by indexing the extracted value:"),
          sql("""
DROP INDEX IF EXISTS demo_idx_event_user;
CREATE INDEX demo_idx_event_user ON demo_events(json_extract(payload, '$.user'));
EXPLAIN QUERY PLAN
SELECT * FROM demo_events WHERE json_extract(payload, '$.user') = 'bob';
""")]

    c += [md("## Practice")]
    c += ex("From `demo_events` (still populated above), list only the events whose "
            "action is 'purchase', showing user and amount from the JSON.",
            "SELECT payload ->> 'user' AS user, payload ->> 'amount' AS amount\nFROM demo_events\nWHERE payload ->> 'action' = 'purchase';")

    c += [md("## Clean up"),
          sql("DROP INDEX IF EXISTS demo_idx_event_user;\nDROP TABLE IF EXISTS demo_events;\nSELECT 'cleaned up' AS status;")]

    c += [md("""
### ✅ Recap
`json_extract`/`->>` read fields, `json_each` unnests arrays into rows,
`json_object`/`json_group_array` build JSON, `json_set` edits it, and expression
indexes speed up JSON-path filters.

**Next:** `24_triggers_and_advanced_views.ipynb`.
""")]
    write_nb("23_json_in_sqlite.ipynb", c)


# ---- 24 Triggers & advanced views ----------------------------------------

def nb_24():
    ex = Ex()
    c = [md("""
# 24 · Triggers & Advanced Views

- **Triggers** run SQL automatically in response to `INSERT`/`UPDATE`/`DELETE`.
  Uses: audit logs, derived columns, validation, enforcing rules.
- **`INSTEAD OF` triggers** make a view **updatable**.

Triggers reference the special rows `NEW` (the incoming row) and `OLD` (the prior
row). Everything here uses throwaway `demo_` objects.
"""), SETUP]

    c += [md("## Set up an accounts table and an audit log"),
          sql("""
DROP TRIGGER IF EXISTS demo_bal_audit;
DROP TABLE IF EXISTS demo_accounts;
DROP TABLE IF EXISTS demo_audit;

CREATE TABLE demo_accounts (id INTEGER PRIMARY KEY, name TEXT, balance REAL);
CREATE TABLE demo_audit    (entry_id INTEGER PRIMARY KEY, note TEXT);
INSERT INTO demo_accounts VALUES (1, 'Alice', 100.0), (2, 'Bob', 50.0);
SELECT 'setup done' AS status;
""")]

    c += [md("""
## `AFTER UPDATE` trigger → audit log
Whenever a balance changes, automatically record the change. `AFTER UPDATE OF
balance` fires only when that column is updated.
"""), sql("""
CREATE TRIGGER demo_bal_audit
AFTER UPDATE OF balance ON demo_accounts
BEGIN
    INSERT INTO demo_audit (note)
    VALUES (NEW.name || ': ' || OLD.balance || ' -> ' || NEW.balance);
END;
""")]
    c += [md("Now update a balance and watch the audit row appear by itself:"),
          sql("""
UPDATE demo_accounts SET balance = balance + 25 WHERE id = 1;
UPDATE demo_accounts SET balance = balance - 10 WHERE id = 2;
SELECT * FROM demo_audit;
""")]

    c += [md("""
## `BEFORE` trigger for validation with `RAISE`
Reject invalid changes before they happen. This trigger aborts any update that
would make a balance negative.
"""), sql("""
DROP TRIGGER IF EXISTS demo_no_negative;
CREATE TRIGGER demo_no_negative
BEFORE UPDATE OF balance ON demo_accounts
WHEN NEW.balance < 0
BEGIN
    SELECT RAISE(ABORT, 'balance cannot go negative');
END;
SELECT 'validation trigger created' AS status;
""")]
    c += [md("This next update **should fail** on purpose (Bob can't go to -1000), "
             "and the audit table stays clean because the update never commits:"),
          sql("UPDATE demo_accounts SET balance = balance - 1000 WHERE id = 2;")]

    c += [md("""
## Updatable view via `INSTEAD OF`
Views are read-only by default. An `INSTEAD OF` trigger intercepts writes to the
view and applies them to the underlying table.
"""), sql("""
DROP VIEW IF EXISTS demo_account_v;
CREATE VIEW demo_account_v AS SELECT id, name, balance FROM demo_accounts;

CREATE TRIGGER demo_account_v_update
INSTEAD OF UPDATE ON demo_account_v
BEGIN
    UPDATE demo_accounts
    SET name = NEW.name, balance = NEW.balance
    WHERE id = NEW.id;
END;

-- write through the view:
UPDATE demo_account_v SET balance = 500 WHERE id = 1;
SELECT * FROM demo_accounts;
""")]

    c += [md("## Clean up"),
          sql("DROP TRIGGER IF EXISTS demo_account_v_update;\n"
              "DROP VIEW IF EXISTS demo_account_v;\n"
              "DROP TRIGGER IF EXISTS demo_no_negative;\n"
              "DROP TRIGGER IF EXISTS demo_bal_audit;\n"
              "DROP TABLE IF EXISTS demo_accounts;\n"
              "DROP TABLE IF EXISTS demo_audit;\n"
              "SELECT 'cleaned up' AS status;")]

    c += [md("## Practice")]
    c += ex("Describe (in a comment) one real use for an AFTER INSERT trigger, then "
            "write a trigger skeleton that logs every new row inserted into a table "
            "`demo_t(id, val)` into `demo_log(msg)`.",
            "DROP TABLE IF EXISTS demo_t; DROP TABLE IF EXISTS demo_log;\nCREATE TABLE demo_t (id INTEGER PRIMARY KEY, val TEXT);\nCREATE TABLE demo_log (msg TEXT);\nCREATE TRIGGER demo_t_ins AFTER INSERT ON demo_t\nBEGIN\n    INSERT INTO demo_log (msg) VALUES ('inserted id=' || NEW.id);\nEND;\nINSERT INTO demo_t (val) VALUES ('hello');\nSELECT * FROM demo_log;")
    c += [md("""
### ✅ Recap
Triggers automate reactions to data changes (audit, validation with `RAISE`,
derived data) using `NEW`/`OLD`; `INSTEAD OF` triggers make views writable. Use
them judiciously — hidden logic can surprise future readers.

**Next:** `25_query_patterns_and_recipes.ipynb`.
""")]
    write_nb("24_triggers_and_advanced_views.ipynb", c)


# ---- 25 Query patterns & recipes -----------------------------------------

def nb_25():
    ex = Ex()
    c = [md("""
# 25 · Query Patterns & Recipes

A toolkit of real-world patterns that combine what you've learned. These come up
constantly in analytics and application code:
- **Top-N per group**
- **Deduplication** (keep one row per key)
- **Gaps & islands** (find consecutive runs)
- **Pivot / unpivot**
- **Running % of total** (Pareto/cumulative share)
- **Date spine** to fill missing dates
"""), SETUP]

    c += [md("""
## Top-N per group
"Top 2 most expensive products in each category." Rank within each partition,
then keep the top ranks. This is the go-to pattern.
"""), sql("""
WITH ranked AS (
    SELECT category_id, product_name, unit_price,
           ROW_NUMBER() OVER (PARTITION BY category_id ORDER BY unit_price DESC) AS rn
    FROM products
)
SELECT category_id, product_name, unit_price
FROM ranked
WHERE rn <= 2
ORDER BY category_id, unit_price DESC;
""")]

    c += [md("""
## Deduplication — keep one row per key
Given duplicates, keep exactly one (e.g. the earliest signup per country). Same
`ROW_NUMBER` idea, keep `rn = 1`.
"""), sql("""
WITH ranked AS (
    SELECT country, first_name, signup_date,
           ROW_NUMBER() OVER (PARTITION BY country ORDER BY signup_date) AS rn
    FROM customers
)
SELECT country, first_name AS first_signup, signup_date
FROM ranked
WHERE rn = 1
ORDER BY country;
""")]

    c += [md("""
## Gaps & islands
Find consecutive runs in a sequence. The trick: `value - ROW_NUMBER()` is
constant within a consecutive run, so group by that difference.
"""), sql("""
WITH nums(n) AS (VALUES (1), (2), (3), (5), (6), (9), (10), (11)),
     grouped AS (
        SELECT n, n - ROW_NUMBER() OVER (ORDER BY n) AS grp
        FROM nums
     )
SELECT MIN(n) AS run_start, MAX(n) AS run_end, COUNT(*) AS length
FROM grouped
GROUP BY grp
ORDER BY run_start;
""")]

    c += [md("""
## Pivot (rows → columns)
Order counts by status, one column each (conditional aggregation):
"""), sql("""
SELECT
    COUNT(*) FILTER (WHERE status = 'completed') AS completed,
    COUNT(*) FILTER (WHERE status = 'pending')   AS pending,
    COUNT(*) FILTER (WHERE status = 'cancelled') AS cancelled
FROM orders;
""")]

    c += [md("""
## Unpivot (columns → rows)
Turn a product's two metrics into a tall (name, metric, value) shape with
`UNION ALL`:
"""), sql("""
SELECT product_name, 'price' AS metric, unit_price AS value FROM products
UNION ALL
SELECT product_name, 'stock', in_stock FROM products
ORDER BY product_name, metric
LIMIT 8;
""")]

    c += [md("""
## Running % of total (Pareto)
Cumulative share of revenue by category — which categories make up the bulk?
"""), sql("""
WITH cat AS (
    SELECT c.category_name, SUM(oi.quantity * oi.unit_price) AS revenue
    FROM order_items oi
    JOIN products p   ON oi.product_id = p.product_id
    JOIN categories c ON p.category_id = c.category_id
    GROUP BY c.category_name
)
SELECT category_name,
       ROUND(revenue, 2) AS revenue,
       ROUND(100.0 * SUM(revenue) OVER (ORDER BY revenue DESC)
             / SUM(revenue) OVER (), 1) AS cumulative_pct
FROM cat
ORDER BY revenue DESC;
""")]

    c += [md("""
## Date spine — fill missing dates
Reports need a row for *every* day, even days with no orders. Generate a date
series with a recursive CTE, then `LEFT JOIN` the data onto it.
"""), sql("""
WITH RECURSIVE days(day) AS (
    SELECT '2024-02-01'
    UNION ALL
    SELECT DATE(day, '+1 day') FROM days WHERE day < '2024-02-05'
)
SELECT days.day,
       COUNT(o.order_id) AS orders
FROM days
LEFT JOIN orders o ON o.order_date = days.day
GROUP BY days.day
ORDER BY days.day;
""")]

    c += [md("## Practice")]
    c += ex("Find the single most recent order per customer (order_id, customer_id, "
            "order_date) using the top-N-per-group pattern with N=1.",
            "WITH ranked AS (\n  SELECT order_id, customer_id, order_date,\n         ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC, order_id DESC) AS rn\n  FROM orders\n)\nSELECT order_id, customer_id, order_date FROM ranked WHERE rn = 1\nORDER BY customer_id;")
    c += ex("Produce a running percentage-of-total of revenue by customer (top "
            "spenders first).",
            "WITH rev AS (\n  SELECT o.customer_id, SUM(oi.quantity * oi.unit_price) AS revenue\n  FROM orders o JOIN order_items oi ON o.order_id = oi.order_id\n  GROUP BY o.customer_id\n)\nSELECT customer_id, ROUND(revenue,2) AS revenue,\n       ROUND(100.0 * SUM(revenue) OVER (ORDER BY revenue DESC) / SUM(revenue) OVER (), 1) AS cume_pct\nFROM rev ORDER BY revenue DESC;")
    c += [md("""
### ✅ Recap
These patterns — top-N per group, dedup, gaps & islands, pivot/unpivot, running
%, and date spines — solve a huge share of real analytical questions by combining
window functions, CTEs, and conditional aggregation.

**Next:** `26_advanced_capstone.ipynb`.
""")]
    write_nb("25_query_patterns_and_recipes.ipynb", c)


# ---- 26 Advanced capstone -------------------------------------------------

def nb_26():
    ex = Ex()
    c = [md("""
# 26 · Advanced Capstone — Analytics Engineering

The final boss. 🐉 These challenges combine window functions, CTEs, JSON,
conditional aggregation, and the recipes from module 25. Attempt each before
revealing the solution.
"""), SETUP]

    c += [md("### Challenge 1 — Month-over-month growth\n*Skills: dates, window "
             "functions, LAG.*\n\nCompute completed-order revenue per month and the "
             "percentage change vs the previous month.")]
    c += ex("Monthly revenue with month-over-month % change.",
            "WITH m AS (\n  SELECT STRFTIME('%Y-%m', o.order_date) AS month,\n         SUM(oi.quantity * oi.unit_price) AS revenue\n  FROM orders o JOIN order_items oi ON o.order_id = oi.order_id\n  WHERE o.status = 'completed'\n  GROUP BY month\n)\nSELECT month, ROUND(revenue,2) AS revenue,\n       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))\n             / LAG(revenue) OVER (ORDER BY month), 1) AS mom_pct\nFROM m ORDER BY month;")

    c += [md("### Challenge 2 — Customer RFM-style summary\n*Skills: joins, "
             "aggregation, dates.*\n\nFor each customer: number of completed orders "
             "(frequency), total spend (monetary), and days since their last order "
             "as of 2024-08-01 (recency).")]
    c += ex("Recency / frequency / monetary summary per customer.",
            "SELECT cu.first_name || ' ' || cu.last_name AS customer,\n       COUNT(DISTINCT o.order_id) AS frequency,\n       ROUND(COALESCE(SUM(oi.quantity * oi.unit_price), 0), 2) AS monetary,\n       CAST(JULIANDAY('2024-08-01') - JULIANDAY(MAX(o.order_date)) AS INTEGER) AS recency_days\nFROM customers cu\nLEFT JOIN orders o      ON o.customer_id = cu.customer_id AND o.status = 'completed'\nLEFT JOIN order_items oi ON oi.order_id = o.order_id\nGROUP BY cu.customer_id\nORDER BY monetary DESC;")

    c += [md("### Challenge 3 — Top product per category with its share\n*Skills: "
             "window functions, partitioned share.*\n\nFor each category, show its "
             "best-selling product (by units) and what % of the category's units "
             "that product represents.")]
    c += ex("Best product per category + its share of category units.",
            "WITH sales AS (\n  SELECT p.category_id, p.product_name, SUM(oi.quantity) AS units\n  FROM order_items oi JOIN products p ON oi.product_id = p.product_id\n  GROUP BY p.category_id, p.product_name\n),\nannotated AS (\n  SELECT category_id, product_name, units,\n         ROW_NUMBER() OVER (PARTITION BY category_id ORDER BY units DESC) AS rn,\n         ROUND(100.0 * units / SUM(units) OVER (PARTITION BY category_id), 1) AS pct_of_cat\n  FROM sales\n)\nSELECT c.category_name, a.product_name, a.units, a.pct_of_cat\nFROM annotated a JOIN categories c ON a.category_id = c.category_id\nWHERE a.rn = 1 ORDER BY c.category_name;")

    c += [md("### Challenge 4 — Build a JSON API payload\n*Skills: JSON building, "
             "joins, aggregation.*\n\nProduce one JSON object per category containing "
             "the category name, product count, and an array of "
             "`{name, price}` objects for its products.")]
    c += ex("One JSON document per category with nested products.",
            "SELECT json_object(\n         'category', c.category_name,\n         'product_count', COUNT(*),\n         'products', json_group_array(json_object('name', p.product_name, 'price', p.unit_price))\n       ) AS category_payload\nFROM categories c\nJOIN products p ON p.category_id = c.category_id\nGROUP BY c.category_name\nORDER BY c.category_name;")

    c += [md("### Challenge 5 — Employee performance ranking\n*Skills: joins, "
             "aggregation, self-join, window ranking.*\n\nRank sales reps by "
             "completed revenue, showing their manager and dense rank.")]
    c += ex("Rep leaderboard with manager and dense rank.",
            "WITH perf AS (\n  SELECT e.employee_id, e.first_name || ' ' || e.last_name AS employee, e.manager_id,\n         COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS revenue\n  FROM employees e\n  LEFT JOIN orders o      ON o.employee_id = e.employee_id AND o.status = 'completed'\n  LEFT JOIN order_items oi ON oi.order_id = o.order_id\n  GROUP BY e.employee_id\n)\nSELECT perf.employee,\n       m.first_name || ' ' || m.last_name AS manager,\n       ROUND(perf.revenue, 2) AS revenue,\n       DENSE_RANK() OVER (ORDER BY perf.revenue DESC) AS rank\nFROM perf\nLEFT JOIN employees m ON perf.manager_id = m.employee_id\nORDER BY rank;")

    c += [md("""
## 🏆 You've completed the full SQL Zero-to-Hero Bootcamp — Advanced Track included!

You now command the entire toolkit: set-based thinking, every join type, advanced
aggregation and window functions, NULL-safe logic, schema design and
normalization, indexing and performance tuning, JSON, triggers, and the query
patterns that solve real problems.

**Keep growing:** apply these to your own datasets, learn your production
database's dialect (PostgreSQL / MySQL / SQL Server differ mainly at the edges),
and practice reading `EXPLAIN` plans on real tables. You're now a strong SQL
engineer. 🚀
""")]
    write_nb("26_advanced_capstone.ipynb", c)


# ===========================================================================
# THEORY TRACK
# ===========================================================================

# ---- 27 Relational model & relational algebra ----------------------------

def nb_27():
    ex = Ex()
    c = [md("""
# 27 · Theory — The Relational Model & Relational Algebra

Everything you've done so far rests on a small, elegant body of theory from
E. F. Codd (1970). Understanding it makes SQL *click* — you stop memorizing
syntax and start reasoning about operations on sets. This is the theory engineers
are expected to know in design reviews and interviews.
"""), SETUP]

    c += [md("""
## The relational model in five words

| Formal term | What it is | SQL name |
|-------------|-----------|----------|
| **Relation** | a set of tuples | table |
| **Tuple** | one member of the set | row |
| **Attribute** | a named component of a tuple | column |
| **Domain** | the set of allowed values | data type |
| **Degree / cardinality** | number of attributes / tuples | columns / rows |

A **relation is a set**, and a set has two consequences that pure theory demands:
1. **No duplicate tuples** — every row is unique.
2. **No inherent order** — rows have no position; you only get order via
   `ORDER BY`.

SQL is a *practical* relaxation of this: by default it works on **bags**
(multisets) that *do* allow duplicates, which is why `SELECT` can return repeated
rows and you add `DISTINCT` to recover true set semantics.
""")]

    c += [md("""
## Keys — the formal hierarchy
- **Superkey:** any set of attributes that uniquely identifies a tuple.
- **Candidate key:** a *minimal* superkey (remove any column and it stops being
  unique). A table can have several.
- **Primary key:** the candidate key you choose as *the* identifier.
- **Alternate key:** the candidate keys you didn't pick (often given `UNIQUE`).
- **Foreign key:** an attribute referencing a candidate key of another (or the
  same) relation — this is what enforces **referential integrity**.

Example: in `customers`, both `customer_id` and `email` are candidate keys;
`customer_id` is the primary key and `email` is an alternate key (`UNIQUE`).
""")]

    c += [md("""
## Relational algebra → SQL

Relational algebra is the *formal set of operations* on relations. Every operator
below has a direct SQL translation. Crucially, each operator **takes relations
and returns a relation** — the **closure property** — which is exactly why you
can nest subqueries and chain CTEs.

| Algebra | Symbol | Meaning | SQL |
|---------|--------|---------|-----|
| Selection | σ (sigma) | keep rows matching a predicate | `WHERE` |
| Projection | π (pi) | keep certain columns (as a set) | `SELECT DISTINCT cols` |
| Rename | ρ (rho) | rename a relation/attribute | `AS` |
| Union | ∪ | rows in either relation | `UNION` |
| Intersection | ∩ | rows in both | `INTERSECT` |
| Difference | − | rows in first, not second | `EXCEPT` |
| Cartesian product | × | every pairing | `CROSS JOIN` |
| Join | ⋈ | product then selection | `JOIN ... ON` |
| Division | ÷ | "for all" matching | double `NOT EXISTS` |
""")]

    c += [md("**Selection σ** — `WHERE`:"),
          sql("SELECT * FROM products WHERE unit_price > 50;")]
    c += [md("**Projection π** — note `DISTINCT` for a true *set* projection:"),
          sql("SELECT DISTINCT category_id FROM products ORDER BY category_id;")]
    c += [md("**Cartesian product ×** — every pairing (20 products × 5 categories = 100):"),
          sql("SELECT COUNT(*) AS pairings FROM products CROSS JOIN categories;")]
    c += [md("**Join ⋈** — a product followed by a selection on matching keys:"),
          sql("SELECT p.product_name, c.category_name\nFROM products p JOIN categories c USING (category_id)\nLIMIT 5;")]
    c += [md("**Union / Intersection / Difference** — set operations on two relations:"),
          sql("SELECT country FROM customers\nINTERSECT\nSELECT country FROM suppliers;")]

    c += [md("""
## Relational division — the "for all" operator
Division answers *"find X related to **every** Y"*. There's no keyword for it;
the idiom is **double `NOT EXISTS`** ("there is no Y that X is *not* related to").

Here: employees who have handled an order of **every** status that exists.
"""), sql("""
SELECT e.employee_id, e.first_name
FROM employees e
WHERE NOT EXISTS (
    SELECT s.status
    FROM (SELECT DISTINCT status FROM orders) AS s          -- all statuses (the divisor)
    WHERE NOT EXISTS (
        SELECT 1 FROM orders o
        WHERE o.employee_id = e.employee_id
          AND o.status = s.status
    )
)
ORDER BY e.employee_id;
""")]
    c += [md("Read it inside-out: *keep an employee when there is no status that "
             "they have not handled.* That double-negative is the signature of "
             "relational division.")]

    c += [md("""
## Why this matters
Because every operation returns a relation, SQL is **compositional**: the output
of one query is valid input to another. That single property is what makes
subqueries, derived tables, CTEs, and views possible — and it's why "think in
sets, not loops" is the whole game.
""")]

    c += [md("## Practice")]
    c += ex("Express in SQL the relational-algebra expression: the projection of "
            "distinct customer countries, selected to those in Europe is hard to "
            "define here — instead, give the set difference of customer countries "
            "minus supplier countries (customers-only countries).",
            "SELECT country FROM customers\nEXCEPT\nSELECT country FROM suppliers;")
    c += [md("""
### ✅ Recap
Relations are sets of tuples; keys form a hierarchy (super → candidate → primary
/ alternate / foreign); relational algebra's operators map one-to-one onto SQL;
and the closure property (relation in, relation out) is what makes SQL
composable.

**Next:** `28_theory_transactions_and_isolation.ipynb`.
""")]
    write_nb("27_theory_relational_model.ipynb", c)


# ---- 28 Transactions, concurrency & isolation ----------------------------

def nb_28():
    ex = Ex()
    c = [md("""
# 28 · Theory — Transactions, Concurrency & Isolation

Module 15 showed `COMMIT`/`ROLLBACK`. This module is the *theory* every backend
engineer needs: what ACID really guarantees, what goes wrong when transactions
run **concurrently**, the standard **isolation levels**, and how SQLite
specifically behaves.
"""), SETUP]

    c += [md("""
## ACID, precisely
- **Atomicity** — all statements in a transaction succeed or none do. Enforced by
  the rollback journal / WAL: on failure, changes are undone.
- **Consistency** — a transaction moves the database from one valid state to
  another, respecting all constraints (PK, FK, `CHECK`, `NOT NULL`).
- **Isolation** — concurrent transactions don't step on each other; the result is
  *as if* they ran in some serial order.
- **Durability** — once committed, data survives a crash (fsync to disk / WAL
  checkpoint).
""")]

    c += [md("""
## The concurrency anomalies
Isolation exists to prevent these phenomena, which occur when transactions
interleave:

| Anomaly | What happens |
|---------|--------------|
| **Dirty read** | T2 reads data T1 wrote but hasn't committed (and may roll back). |
| **Non-repeatable read** | T1 reads a row twice and gets different values because T2 updated & committed in between. |
| **Phantom read** | T1 re-runs a range query and new rows *appear* because T2 inserted matching rows. |
| **Lost update** | T1 and T2 both read a value, both write; one write silently overwrites the other. |
| **Write skew** | Two transactions read overlapping data and make disjoint writes that together violate an invariant. |
""")]

    c += [md("""
## The ANSI isolation levels
Higher levels prevent more anomalies but reduce concurrency. Databases let you
trade correctness for throughput per transaction.

| Level | Dirty read | Non-repeatable | Phantom |
|-------|-----------|----------------|---------|
| READ UNCOMMITTED | possible | possible | possible |
| READ COMMITTED | prevented | possible | possible |
| REPEATABLE READ | prevented | prevented | possible |
| SERIALIZABLE | prevented | prevented | prevented |

Two implementation strategies:
- **Pessimistic (locking):** take locks so conflicting access blocks. Simple, but
  contention and deadlocks.
- **Optimistic (MVCC — multi-version concurrency control):** readers see a
  consistent *snapshot* and never block writers; conflicts are detected at commit.
  PostgreSQL and MySQL/InnoDB use MVCC.
""")]

    c += [md("""
## How SQLite does it
SQLite is deliberately simple and always effectively **SERIALIZABLE**:
- **Database-level locking** (not row-level). In the classic *rollback journal*
  mode, a writer takes an exclusive lock — readers and the writer can't overlap.
- **WAL mode** (`PRAGMA journal_mode=WAL`) is the big upgrade: a **single writer
  and many readers run concurrently**, because readers see a consistent snapshot
  while the writer appends to a write-ahead log.
- Transaction start modes: `BEGIN DEFERRED` (default; lock acquired lazily on
  first write), `BEGIN IMMEDIATE` (take the write lock now), `BEGIN EXCLUSIVE`.
- When a lock can't be obtained you get **`SQLITE_BUSY` ("database is locked")**;
  `PRAGMA busy_timeout = ms` makes it wait instead of failing immediately.

Let's *prove* SQLite gives no dirty reads, using two live connections.
"""), code("""
import os, tempfile, sqlite3

path = tempfile.mktemp(suffix='.db')
A = sqlite3.connect(path, isolation_level=None)   # manual transaction control
A.execute("PRAGMA journal_mode=WAL")              # readers + 1 writer concurrently
A.execute("CREATE TABLE acct(id INTEGER PRIMARY KEY, balance INTEGER)")
A.execute("INSERT INTO acct VALUES (1, 100)")

B = sqlite3.connect(path, isolation_level=None)   # a second, independent connection

A.execute("BEGIN")                                # A starts a transaction...
A.execute("UPDATE acct SET balance = 999 WHERE id = 1")   # ...and writes (uncommitted)

# B reads WHILE A's change is uncommitted -> must still see the OLD value (no dirty read)
print("B sees during A's open txn :", B.execute("SELECT balance FROM acct WHERE id=1").fetchone()[0])
A.commit()
print("B sees after A committed   :", B.execute("SELECT balance FROM acct WHERE id=1").fetchone()[0])

A.close(); B.close(); os.remove(path.replace('.db','.db'))
for ext in ('-wal','-shm'):
    if os.path.exists(path+ext): os.remove(path+ext)
""")]
    c += [md("You should see `100` during A's open transaction and `999` after "
             "commit — SQLite never exposed the dirty, uncommitted value.")]

    c += [md("""
## Demonstrating `SQLITE_BUSY`
Two write transactions can't overlap — the second gets "database is locked".
"""), code("""
import os, tempfile, sqlite3

path = tempfile.mktemp(suffix='.db')
A = sqlite3.connect(path, isolation_level=None)
A.execute("PRAGMA journal_mode=WAL")
A.execute("CREATE TABLE t(id INTEGER PRIMARY KEY, v INTEGER)")
A.execute("INSERT INTO t VALUES (1, 0)")
B = sqlite3.connect(path, isolation_level=None)

A.execute("BEGIN IMMEDIATE")            # A grabs the write lock
A.execute("UPDATE t SET v = 1 WHERE id = 1")
try:
    B.execute("BEGIN IMMEDIATE")        # B wants to write too -> blocked
    print("B acquired the write lock (unexpected)")
except sqlite3.OperationalError as e:
    print("B blocked with:", e)         # 'database is locked'
A.commit()                              # releasing the lock lets B proceed

A.close(); B.close()
if os.path.exists(path): os.remove(path)
for ext in ('-wal','-shm'):
    if os.path.exists(path+ext): os.remove(path+ext)
""")]

    c += [md("""
## Practical guidance
- Turn on **WAL** for apps with concurrent readers and a writer.
- Set a **`busy_timeout`** so transient locks retry instead of erroring.
- Keep transactions **short** — hold locks for as little time as possible.
- Use `BEGIN IMMEDIATE` when you know you'll write, to fail fast on contention
  rather than mid-transaction.
- On other databases, pick the **isolation level** deliberately: `READ COMMITTED`
  (Postgres default) is usually fine; step up to `SERIALIZABLE` when correctness
  under concurrency is critical.
""")]

    c += [md("## Practice")]
    c += ex("Which journal mode lets one writer and many readers work at the same "
            "time? Confirm the *current* journal mode of this database.",
            "PRAGMA journal_mode;")
    c += [md("""
### ✅ Recap
ACID defines the guarantees; dirty / non-repeatable / phantom reads, lost updates
and write skew are what isolation prevents; the ANSI levels trade concurrency for
safety via locking or MVCC; and SQLite is serializable with database-level
locking, made concurrent-friendly by WAL.

**Next:** `29_theory_storage_indexes_and_optimizer.ipynb`.
""")]
    write_nb("28_theory_transactions_and_isolation.ipynb", c)


# ---- 29 Storage, indexes & the optimizer ---------------------------------

def nb_29():
    ex = Ex()
    c = [md("""
# 29 · Theory — Storage, Indexes & the Query Optimizer

The final theory piece: how the data physically lives on disk, what an index
*really* is, how the planner decides, and SQLite's unusual **type system**. This
is the mental model behind every performance decision.
"""), SETUP]

    c += [md("""
## How the database is stored
- A SQLite database is a **single file** divided into fixed-size **pages** (often
  4096 bytes).
- Each **table** and each **index** is stored as a **B-tree** of pages.
- Default tables are **rowid tables**: every row has a hidden 64-bit `rowid`, and
  the table B-tree is keyed by it. A `WITHOUT ROWID` table is keyed by its primary
  key instead (good for large text PKs).

See the physical layout of *this* database:
"""), sql("PRAGMA page_size;"),
          sql("PRAGMA page_count;")]

    c += [md("""
## What a B-tree buys you
A B-tree is **balanced** and keeps keys **sorted**, giving:
- **O(log n)** lookups by key (vs O(n) scanning every row),
- efficient **range scans** (`BETWEEN`, `>`, `ORDER BY`) because leaf pages are
  sorted,
- ordered traversal without a separate sort.

## What an index really is
An index is just **another B-tree** holding a *sorted copy* of the chosen
column(s) plus a pointer (the rowid) back to the full row. That's why:
- lookups/`ORDER BY` on indexed columns are fast,
- the **leftmost-prefix rule** exists (a `(a,b)` index is sorted by `a` then `b`,
  so it can't help a query filtering on `b` alone),
- a **covering index** (one that contains every column the query needs) avoids
  touching the table at all.
""")]

    c += [md("""
## The optimizer is cost-based
SQLite's planner estimates the cost of alternative plans and picks the cheapest.
It relies on **statistics** gathered by `ANALYZE` (stored in `sqlite_stat1`):
roughly, how many rows an index lookup will return (**selectivity**). A highly
*selective* filter (few matching rows) favors an index; a low-selectivity one
(matches most rows) favors a full scan.

Create an index, gather stats, and inspect them:
"""), sql("""
DROP INDEX IF EXISTS demo_idx_orders_cust;
CREATE INDEX demo_idx_orders_cust ON orders(customer_id);
ANALYZE;
SELECT * FROM sqlite_stat1 WHERE tbl = 'orders';
""")]
    c += [md("Each `sqlite_stat1` row reads roughly *\"for this index, an average "
             "key matches N rows\"* — the numbers the planner uses to choose.")]

    c += [md("""
## Two flavors of `EXPLAIN`
- **`EXPLAIN QUERY PLAN`** — the high-level strategy (`SCAN` vs `SEARCH ... USING
  INDEX`). This is what you read 99% of the time.
- **`EXPLAIN`** (no "QUERY PLAN") — the low-level **VM bytecode** SQLite compiles
  your query into. Rarely needed, but it shows SQL is *compiled*, not interpreted
  row-by-row.
"""), sql("EXPLAIN QUERY PLAN\nSELECT * FROM orders WHERE customer_id = 1;")]

    c += [md("""
## Join algorithm
SQLite joins with a **nested-loop**: for each row of the outer table, it looks up
matching rows in the inner table. Without an index that's O(n × m); **with an
index on the inner join column** it becomes O(n × log m). The planner also
chooses the **join order** (which table is outer) based on cost. This is the
single biggest reason to index foreign-key columns you join on.
"""), sql("EXPLAIN QUERY PLAN\nSELECT c.first_name, o.order_id\nFROM customers c JOIN orders o ON o.customer_id = c.customer_id;")]

    c += [md("## Clean up the demo index"),
          sql("DROP INDEX IF EXISTS demo_idx_orders_cust;\nSELECT 'cleaned up' AS status;")]

    c += [md("""
## SQLite's type system — storage classes & affinity
Unlike most databases, SQLite uses **dynamic typing**. A *value's* type is one of
five **storage classes**:
"""), sql("SELECT typeof(42) AS int_, typeof(3.14) AS real_, typeof('hi') AS text_, typeof(NULL) AS null_, typeof(x'01') AS blob_;")]

    c += [md("""
A *column's* declared type only sets a **type affinity** — a *preference* SQLite
uses to convert incoming values when it reasonably can. The five affinities are
`TEXT`, `NUMERIC`, `INTEGER`, `REAL`, `BLOB`, determined from the declared type
name. Watch what actually gets stored:
"""), sql("""
DROP TABLE IF EXISTS demo_affinity;
CREATE TABLE demo_affinity (
    i INTEGER,   -- INTEGER affinity
    t TEXT,      -- TEXT affinity
    r REAL,      -- REAL affinity
    b BLOB,      -- BLOB affinity (no conversion)
    n NUMERIC    -- NUMERIC affinity
);
INSERT INTO demo_affinity VALUES ('123', 123, '1.5', 9, '42');
SELECT typeof(i) AS i, typeof(t) AS t, typeof(r) AS r, typeof(b) AS b, typeof(n) AS n
FROM demo_affinity;
""")]
    c += [md("""
Notice: the text `'123'` inserted into the `INTEGER`-affinity column was
**converted to an integer**; the integer `123` inserted into the `TEXT` column
became **text**; and the `BLOB` column left `9` untouched. This flexible typing
is powerful but surprising — declare columns carefully and don't rely on the
database to reject a wrong-typed value the way a strict system would.
"""), sql("DROP TABLE IF EXISTS demo_affinity;\nSELECT 'cleaned up' AS status;")]

    c += [md("## Practice")]
    c += ex("Show the storage class SQLite assigns to the literals 100, 2.5, and "
            "'sql' using typeof().",
            "SELECT typeof(100) AS a, typeof(2.5) AS b, typeof('sql') AS c;")
    c += ex("Create an index on products(unit_price), run EXPLAIN QUERY PLAN for a "
            "price range query to confirm it's used, then drop the index.",
            "DROP INDEX IF EXISTS demo_idx_price;\nCREATE INDEX demo_idx_price ON products(unit_price);\nEXPLAIN QUERY PLAN SELECT * FROM products WHERE unit_price BETWEEN 30 AND 60;")
    c += [md("""
### ✅ Recap
Data lives in fixed-size pages as B-trees; an index is a sorted B-tree copy of
columns (hence leftmost-prefix and covering indexes); the planner is cost-based
and driven by `ANALYZE` statistics; joins are nested loops that love indexes on
the inner key; and SQLite's dynamic typing means columns have *affinity*, not
strict types.

## 🎓 That's the whole bootcamp — practice, advanced, and theory.
You now understand SQL from the syntax down to the storage engine. Go build.
""")]
    write_nb("29_theory_storage_indexes_and_optimizer.ipynb", c)


def main():
    os.makedirs(NB_DIR, exist_ok=True)
    nb_00(); nb_01(); nb_02(); nb_03(); nb_04(); nb_05(); nb_06(); nb_07()
    nb_08(); nb_09(); nb_10(); nb_11(); nb_12(); nb_13(); nb_14(); nb_15(); nb_16()
    # advanced track
    nb_17(); nb_18(); nb_19(); nb_20(); nb_21(); nb_22(); nb_23(); nb_24()
    nb_25(); nb_26()
    # theory track
    nb_27(); nb_28(); nb_29()
    print("\nAll notebooks generated in", NB_DIR)


if __name__ == "__main__":
    main()
