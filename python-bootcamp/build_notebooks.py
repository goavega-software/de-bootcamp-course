"""
Generator for the Python Zero-to-Hero Bootcamp notebooks.

Running this (re)creates every notebook under ``notebooks/``. It is safe to run
again at any time to reset the notebooks to their original state:

    uv run python build_notebooks.py

You normally do NOT need to run this — the notebooks ship ready to use. It is
included so the course is fully reproducible.

Design: every notebook is *explanation-first*. Markdown cell explains a concept,
a code cell demonstrates it with a runnable example that prints output. No
hidden exercises.
"""
from __future__ import annotations

import json
import os
import re

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


# A path bootstrap for the data-engineering notebooks. Works whether the
# notebook's working directory is the repo root or the notebooks/ folder.
DATA_BOOT = code(
    "# \u25b6 Run this first. Locates the sample data no matter where the kernel starts.\n"
    "from pathlib import Path\n"
    "\n"
    "def find_data() -> Path:\n"
    "    here = Path.cwd()\n"
    "    for base in (here, *here.parents):\n"
    "        if (base / 'data' / 'raw').exists():\n"
    "            return base / 'data'\n"
    "    raise FileNotFoundError('Run: uv run python data/build_data.py')\n"
    "\n"
    "DATA = find_data()\n"
    "RAW = DATA / 'raw'\n"
    "print('Data directory:', DATA)\n"
    "print('Raw files:', sorted(p.name for p in RAW.glob('*')))"
)


def _sync_title_number(filename: str, cells: list) -> None:
    """Force the H1 '# NN · Title' to match the filename's number, so the
    registry order is the single source of truth for numbering."""
    m = re.match(r"(\d+)_", filename)
    if not m or not cells:
        return
    num = m.group(1)
    src = cells[0].get("source", [])
    for i, line in enumerate(src):
        if line.lstrip().startswith("# ") and "·" in line:
            src[i] = re.sub(r"# \d+ ·", f"# {num} ·", line, count=1)
            break


def write_nb(filename: str, cells: list) -> None:
    _sync_title_number(filename, cells)
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


def nb_00():
    c = []
    c.append(md("""
# 00 · Setup & How to Run

Welcome to the **Python Zero-to-Hero Bootcamp** (data-engineering focus) 🐍

You will learn Python by *reading and running*. Every notebook follows the same
rhythm: a short explanation, then a runnable code cell that demonstrates it and
prints a result. **Run every cell** (`Shift+Enter`), then change things and
re-run — that is how it sticks.

This first notebook checks your environment and shows the sample data. There is
nothing to memorize here.
"""))

    c.append(md("""
## How Python runs your code

Python is an **interpreted** language: you write plain-text `.py` files (or
notebook cells) and the Python interpreter executes them line by line. There is
no separate compile step you manage. A notebook cell is just a chunk of Python
the kernel runs, keeping all variables in memory between cells.

The cell below is real Python. Run it.
"""))
    c.append(code(
        "print('Hello, data engineering!')\n"
        "\n"
        "import sys\n"
        "print('Python version:', sys.version.split()[0])\n"
        "print('Running from:', sys.executable)"
    ))

    c.append(md("""
## Everything is an *object*

In Python, every value — a number, some text, a list, even a function — is an
**object** with a *type*. `type(x)` tells you what something is. You will lean
on this constantly when data arrives in an unknown shape.
"""))
    c.append(code(
        "print(type(42))\n"
        "print(type(3.14))\n"
        "print(type('etl'))\n"
        "print(type([1, 2, 3]))\n"
        "print(type(print))   # even a function is an object"
    ))

    c.append(md("""
## The sample dataset

Throughout the course you work with a fictional retail company delivered as
**raw files**, the way real ingestion sees them:

- `data/raw/customers.csv` — customer master (deliberately messy)
- `data/raw/products.csv` — product catalog
- `data/raw/orders.csv` + `data/raw/order_items.csv` — orders fact + line items
- `data/raw/events.jsonl` — clickstream, one JSON object per line
- `data/retail.db` — the same tables in SQLite

If the next cell errors, run `uv run python data/build_data.py` in a terminal
first.
"""))
    c.append(DATA_BOOT)

    c.append(md("""
Let's peek at the first few lines of one raw file. Don't worry about the code —
`pathlib` and file reading get their own notebooks. This is just proof the data
is there.
"""))
    c.append(code(
        "text = (RAW / 'customers.csv').read_text(encoding='utf-8')\n"
        "for line in text.splitlines()[:5]:\n"
        "    print(line)"
    ))

    c.append(md("""
## How to work through the course

Go in numbered order. **Track 1 (00–11)** makes you fluent in the language.
**Track 2 (12–18)** works with data using only the standard library.
**Track 3 (19–24)** is the engineering craft that makes code production-grade.

> pandas, NumPy, Parquet and a full ETL capstone live in the companion
> **pandas-numpy-bootcamp** — take it after finishing Track 2 here.

Onward to `01_variables_and_types`. 🚀
"""))
    return c


def nb_01():
    c = []
    c.append(md("""
# 01 · Variables & Types

A **variable** is a name that refers to an object. Assignment (`=`) binds a name
to a value. Python is **dynamically typed**: a name can refer to any type, and
you never declare the type up front — but every *object* still has a definite
type.
"""))
    c.append(code(
        "rows_loaded = 1500        # int\n"
        "success_rate = 0.98       # float\n"
        "pipeline = 'daily_etl'    # str\n"
        "is_healthy = True         # bool\n"
        "\n"
        "print(rows_loaded, success_rate, pipeline, is_healthy)\n"
        "print(type(rows_loaded), type(success_rate), type(pipeline), type(is_healthy))"
    ))

    c.append(md("""
## Names are references, not boxes

A variable does not *contain* a value — it *points at* one. Assigning one
variable to another makes both names point at the **same object**. For
**immutable** values (numbers, strings, tuples) this never surprises you. For
**mutable** values (lists, dicts, sets) it matters a lot: mutating through one
name is visible through the other.
"""))
    c.append(code(
        "a = [1, 2, 3]\n"
        "b = a            # b points at the SAME list\n"
        "b.append(4)\n"
        "print('a:', a)   # changed too!\n"
        "print('a is b:', a is b)   # same object\n"
        "\n"
        "c = a.copy()     # a new, independent list\n"
        "c.append(99)\n"
        "print('a:', a, '| c:', c, '| a is c:', a is c)"
    ))

    c.append(md("""
## `==` vs `is`

- `==` asks *are these values equal?*
- `is` asks *are these the exact same object in memory?*

You almost always want `==`. Use `is` only for singletons like `None`.
"""))
    c.append(code(
        "x = [1, 2, 3]\n"
        "y = [1, 2, 3]\n"
        "print('x == y:', x == y)   # equal values\n"
        "print('x is y:', x is y)   # different objects\n"
        "\n"
        "value = None\n"
        "print('value is None:', value is None)   # the idiomatic None check"
    ))

    c.append(md("""
## Converting between types (casting)

Data arrives as text far more often than as numbers. Converting cleanly — and
knowing when a conversion fails — is a core data-engineering skill.
"""))
    c.append(code(
        "raw = '42'\n"
        "print(int(raw) + 8)          # '42' -> 42\n"
        "print(float('3.14') * 2)     # '3.14' -> 3.14\n"
        "print(str(100) + ' rows')    # 100 -> '100'\n"
        "print(bool(0), bool(''), bool('x'), bool([]))   # truthiness of values\n"
        "\n"
        "# A conversion that fails raises ValueError (more on errors in the errors notebook):\n"
        "try:\n"
        "    int('not-a-number')\n"
        "except ValueError as e:\n"
        "    print('conversion failed:', e)"
    ))

    c.append(md("""
## `None` — the absence of a value

`None` is Python's null. It is its own type (`NoneType`) and shows up constantly
in data work to mean *missing / unknown*. Always test it with `is None`.
"""))
    c.append(code(
        "middle_name = None\n"
        "print(middle_name is None)\n"
        "print(type(None))\n"
        "\n"
        "# A common pattern: default a possibly-missing value\n"
        "country = None\n"
        "clean = country if country is not None else 'UNKNOWN'\n"
        "print(clean)"
    ))

    c.append(md("""
### Recap

Variables are names bound to objects; objects have types; mutable values are
shared by reference; use `==` for value equality and `is None` for null checks;
cast text to numbers deliberately and handle failures. Next: working with
numbers and strings.
"""))
    return c


def nb_02():
    c = []
    c.append(md("""
# 02 · Numbers & Strings

Two of the most common data types you will manipulate. This notebook covers
arithmetic, the difference between `int` and `float`, and the string toolkit you
will use to parse and clean text every single day.
"""))

    c.append(md("""
## Numeric types and arithmetic

`int` is an arbitrary-precision integer (no overflow). `float` is a 64-bit
IEEE-754 double. Note the two division operators: `/` always gives a float,
`//` does floor division, and `%` is the remainder.
"""))
    c.append(code(
        "print(7 / 2)      # 3.5   true division -> float\n"
        "print(7 // 2)     # 3     floor division\n"
        "print(7 % 2)      # 1     remainder (modulo)\n"
        "print(2 ** 10)    # 1024  exponent\n"
        "print(10_000_000 * 3)   # underscores are legal digit separators\n"
        "\n"
        "big = 2 ** 100    # ints never overflow\n"
        "print(big)"
    ))

    c.append(md("""
## Floats are approximate

Floating-point numbers cannot represent every decimal exactly. This bites
everyone eventually — never test float equality with `==`, and use `round()` or
the `decimal` module for money.
"""))
    c.append(code(
        "print(0.1 + 0.2)                 # 0.30000000000000004\n"
        "print(0.1 + 0.2 == 0.3)          # False!\n"
        "print(round(0.1 + 0.2, 2) == 0.3)   # True\n"
        "\n"
        "from decimal import Decimal\n"
        "print(Decimal('0.1') + Decimal('0.2'))   # exact: 0.3"
    ))

    c.append(md("""
## Strings and f-strings

A string is an immutable sequence of characters. **f-strings** (prefix `f`) let
you embed expressions in `{}` — this is the modern way to build text, log lines
and file names. The `:` inside braces adds formatting (width, decimals, etc.).
"""))
    c.append(code(
        "table = 'orders'\n"
        "rows = 1523\n"
        "rate = 0.9834\n"
        "\n"
        "print(f'Loaded {rows} rows into {table}')\n"
        "print(f'Success rate: {rate:.1%}')        # percent with 1 decimal\n"
        "print(f'Padded: |{table:>10}|')            # right-align in width 10\n"
        "print(f'{rows:,} rows')                    # thousands separator\n"
        "print(f'{255:#x} and {255:08b}')           # hex and zero-padded binary"
    ))

    c.append(md("""
## The string-cleaning toolkit

These methods return **new** strings (strings are immutable). You will use them
constantly to normalize dirty input: trim whitespace, fix casing, split fields,
and test contents.
"""))
    c.append(code(
        "raw = '  Ava.Smith@Example.COM  '\n"
        "print(repr(raw.strip()))            # remove surrounding whitespace\n"
        "print(raw.strip().lower())          # normalize case\n"
        "print('  US '.strip().upper())\n"
        "print('a,b,c'.split(','))           # -> ['a', 'b', 'c']\n"
        "print('-'.join(['2024', '01', '15']))   # -> '2024-01-15'\n"
        "print('report.csv'.endswith('.csv'))\n"
        "print('customer_id'.replace('_', ' '))\n"
        "print('Ava Smith'.startswith('Ava'))"
    ))

    c.append(md("""
## Slicing and indexing

Strings (and lists) support `[start:stop:step]` slicing. Indexing is 0-based;
negative indices count from the end. `stop` is exclusive.
"""))
    c.append(code(
        "s = 'ORD-2024-0042'\n"
        "print(s[0])        # 'O'  first char\n"
        "print(s[-1])       # '2'  last char\n"
        "print(s[:3])       # 'ORD' first three\n"
        "print(s[4:8])      # '2024'\n"
        "print(s[-4:])      # '0042' last four\n"
        "print(s[::-1])     # reversed"
    ))

    c.append(md("""
## A tiny real example: parse an order id

Combine the tools to pull structured pieces out of a raw code.
"""))
    c.append(code(
        "code = 'ORD-2024-0042'\n"
        "prefix, year, seq = code.split('-')\n"
        "print(f'type={prefix} year={int(year)} number={int(seq)}')"
    ))

    c.append(md("""
### Recap

`/` vs `//` vs `%`; floats are approximate so round money; f-strings build text
with `{expr:format}`; string methods return new strings for cleaning; slicing is
`[start:stop:step]`. Next: the collection types that hold many values.
"""))
    return c


def nb_03():
    c = []
    c.append(md("""
# 03 · Collections: list, tuple, set, dict

Real data is *collections* of values. Python's four core containers each have a
job:

- **`list`** — ordered, mutable sequence (the workhorse)
- **`tuple`** — ordered, **immutable** sequence (fixed records, dict keys)
- **`set`** — unordered collection of **unique** values (dedup, membership)
- **`dict`** — key → value mapping (lookups, JSON-shaped data)
"""))

    c.append(md("""
## Lists

Ordered and mutable. Grow with `append`/`extend`, index and slice like strings,
sort in place or with `sorted()`.
"""))
    c.append(code(
        "prices = [19.99, 5.0, 120.0, 5.0]\n"
        "prices.append(42.0)\n"
        "print(prices)\n"
        "print('length:', len(prices))\n"
        "print('first two:', prices[:2])\n"
        "print('sorted:', sorted(prices))\n"
        "print('max:', max(prices), '| sum:', round(sum(prices), 2))\n"
        "\n"
        "prices.sort(reverse=True)   # in-place\n"
        "print('sorted desc in place:', prices)"
    ))

    c.append(md("""
## Tuples

Like lists but **immutable** — you cannot change them after creation. Use them
for fixed-shape records (a row, a coordinate) and anywhere you need a hashable
sequence. **Unpacking** a tuple into names is idiomatic Python.
"""))
    c.append(code(
        "row = (1042, 'completed', 89.90)      # order_id, status, amount\n"
        "order_id, status, amount = row         # unpacking\n"
        "print(order_id, status, amount)\n"
        "\n"
        "try:\n"
        "    row[0] = 999      # tuples can't be modified\n"
        "except TypeError as e:\n"
        "    print('immutable:', e)"
    ))

    c.append(md("""
## Sets

Unordered, no duplicates. Perfect for **deduplication** and fast **membership**
tests, plus mathematical set operations (union, intersection, difference).
"""))
    c.append(code(
        "countries = ['US', 'GB', 'US', 'DE', 'US', 'GB']\n"
        "unique = set(countries)\n"
        "print('unique:', unique)\n"
        "print('count:', len(unique))\n"
        "print(\"'US' in set:\", 'US' in unique)     # O(1) membership\n"
        "\n"
        "a = {'US', 'GB', 'DE'}\n"
        "b = {'DE', 'IN'}\n"
        "print('intersection:', a & b)\n"
        "print('union:', a | b)\n"
        "print('only in a:', a - b)"
    ))

    c.append(md("""
## Dictionaries

The most important container in data work: a mapping from **keys** to
**values**. JSON objects, config, lookup tables and row records are all dicts.
Access with `[]` (errors if missing) or `.get()` (returns a default).
"""))
    c.append(code(
        "customer = {\n"
        "    'customer_id': 7,\n"
        "    'name': 'Ava Smith',\n"
        "    'country': 'US',\n"
        "}\n"
        "print(customer['name'])\n"
        "print(customer.get('email', 'MISSING'))   # safe access with default\n"
        "\n"
        "customer['email'] = 'ava@example.com'      # add / update\n"
        "print(customer.keys())\n"
        "print(customer.values())\n"
        "\n"
        "for key, value in customer.items():        # iterate key/value pairs\n"
        "    print(f'  {key} = {value}')"
    ))

    c.append(md("""
## Counting with a dict (a classic pattern)

Tallying occurrences is everywhere in data engineering. The idiom below, and the
purpose-built `collections.Counter`, both do it.
"""))
    c.append(code(
        "statuses = ['completed', 'returned', 'completed', 'cancelled', 'completed']\n"
        "\n"
        "counts = {}\n"
        "for s in statuses:\n"
        "    counts[s] = counts.get(s, 0) + 1\n"
        "print('manual:', counts)\n"
        "\n"
        "from collections import Counter\n"
        "print('Counter:', Counter(statuses))\n"
        "print('most common:', Counter(statuses).most_common(1))"
    ))

    c.append(md("""
## Nesting: the shape of real data

Combine containers to model records. A list of dicts is exactly what a CSV or a
JSON array becomes in memory.
"""))
    c.append(code(
        "orders = [\n"
        "    {'id': 1, 'amount': 89.9, 'items': ['ELE-001', 'BOO-014']},\n"
        "    {'id': 2, 'amount': 12.5, 'items': ['GRO-003']},\n"
        "]\n"
        "print('order 1 first item:', orders[0]['items'][0])\n"
        "total = sum(o['amount'] for o in orders)\n"
        "print('total amount:', total)"
    ))

    c.append(md("""
## `namedtuple` and `deque` (from `collections`)

Two specialized containers worth knowing. A **`namedtuple`** is a tuple whose
fields have names — a lightweight, immutable record that reads clearly without
the weight of a class. A **`deque`** ("deck") is a list-like queue with fast
appends and pops at **both** ends — ideal for buffers and sliding windows where
a plain list would be slow at the front.
"""))
    c.append(code(
        "from collections import namedtuple, deque\n"
        "\n"
        "Order = namedtuple('Order', ['order_id', 'amount', 'status'])\n"
        "o = Order(1042, 89.9, 'completed')\n"
        "print(o.order_id, o.amount)         # access by name, not position\n"
        "print(o)                            # readable repr\n"
        "\n"
        "recent = deque(maxlen=3)            # keeps only the last 3 items\n"
        "for i in range(6):\n"
        "    recent.append(i)\n"
        "print('sliding window:', list(recent))\n"
        "recent.appendleft(-1)               # fast insert at the front\n"
        "print('after appendleft:', list(recent))"
    ))

    c.append(md("""
### Recap

`list` (ordered/mutable), `tuple` (ordered/immutable, unpackable), `set`
(unique/fast membership), `dict` (key→value, the shape of JSON and rows);
`namedtuple` for readable records and `deque` for fast double-ended queues.
Next: control flow — making decisions and looping.
"""))
    return c


def nb_04():
    c = []
    c.append(md("""
# 04 · Control Flow

Programs make **decisions** (`if`) and **repeat** work (`for`, `while`). This is
how you route records, validate rows, and process every item in a file.
"""))

    c.append(md("""
## `if` / `elif` / `else`

Branches run based on a boolean condition. Python uses **indentation** (4
spaces) to define blocks — there are no braces. Comparison operators:
`==  !=  <  <=  >  >=`, combined with `and`, `or`, `not`.
"""))
    c.append(code(
        "amount = 250.0\n"
        "\n"
        "if amount >= 1000:\n"
        "    tier = 'enterprise'\n"
        "elif amount >= 100:\n"
        "    tier = 'standard'\n"
        "else:\n"
        "    tier = 'small'\n"
        "\n"
        "print(tier)\n"
        "\n"
        "status = 'completed'\n"
        "if status == 'completed' and amount > 0:\n"
        "    print('count toward revenue')"
    ))

    c.append(md("""
## Truthiness

`if` evaluates the *truthiness* of a value, not just `True`/`False`. Empty
containers, `0`, `''` and `None` are **falsy**; everything else is **truthy**.
This makes for clean guards against missing/empty data.
"""))
    c.append(code(
        "for value in [0, 1, '', 'x', [], [1], None, {}]:\n"
        "    print(f'{value!r:>6} -> {bool(value)}')\n"
        "\n"
        "email = ''\n"
        "if not email:                 # falsy check for missing data\n"
        "    print('email is missing')"
    ))

    c.append(md("""
## `for` loops

Iterate over any *iterable* — a list, string, dict, file, range, etc. `range()`
generates numbers on demand. `break` stops the loop; `continue` skips to the
next item.
"""))
    c.append(code(
        "for i in range(3):\n"
        "    print('attempt', i)\n"
        "\n"
        "total = 0\n"
        "for price in [10, -5, 20, 0, 8]:\n"
        "    if price <= 0:\n"
        "        continue          # skip invalid rows\n"
        "    total += price\n"
        "print('total of valid:', total)"
    ))

    c.append(md("""
## `enumerate` and `zip`

Two loop helpers you will use daily. `enumerate` gives you the index alongside
the value (great for row numbers). `zip` walks several sequences in lockstep
(great for pairing columns).
"""))
    c.append(code(
        "products = ['SSD', 'Book', 'Lego']\n"
        "for idx, name in enumerate(products, start=1):\n"
        "    print(idx, name)\n"
        "\n"
        "names = ['Ava', 'Liam', 'Mei']\n"
        "amounts = [89.9, 12.5, 240.0]\n"
        "for name, amount in zip(names, amounts):\n"
        "    print(f'{name}: {amount}')"
    ))

    c.append(md("""
## `while` loops

Repeat *until* a condition changes. Ideal when you don't know the count up front
— e.g. paginating an API until there are no more pages (you'll do the real
version in the APIs notebook).
"""))
    c.append(code(
        "page = 1\n"
        "remaining = 7      # pretend the API says how many records are left\n"
        "while remaining > 0:\n"
        "    take = min(3, remaining)\n"
        "    print(f'fetch page {page}: {take} records')\n"
        "    remaining -= take\n"
        "    page += 1\n"
        "print('done')"
    ))

    c.append(md("""
## `match` (structural pattern matching, Python 3.10+)

A clean way to branch on the *shape* or value of data — handy for routing events
by type.
"""))
    c.append(code(
        "def route(event):\n"
        "    match event['type']:\n"
        "        case 'page_view':\n"
        "            return 'analytics'\n"
        "        case 'checkout' | 'add_to_cart':\n"
        "            return 'revenue'\n"
        "        case _:\n"
        "            return 'other'\n"
        "\n"
        "for t in ['page_view', 'checkout', 'search']:\n"
        "    print(t, '->', route({'type': t}))"
    ))

    c.append(md("""
## The walrus operator `:=`

The **walrus operator** assigns *and* returns a value in one expression. It
shines when you'd otherwise compute something twice or need the value inside a
loop/`if` condition — e.g. reading batches until one comes back empty.
"""))
    c.append(code(
        "data = [4, 9, 16, 25]\n"
        "\n"
        "# compute once, test and reuse in one line\n"
        "if (n := len(data)) > 3:\n"
        "    print(f'{n} items — plenty')\n"
        "\n"
        "# a classic: loop until a sentinel, without duplicating the read\n"
        "queue = iter([5, 8, 0, 3])          # pretend this is a data source\n"
        "while (value := next(queue, None)) is not None and value != 0:\n"
        "    print('processing', value)\n"
        "print('stopped')"
    ))

    c.append(md("""
### Recap

`if/elif/else` with truthiness for missing-data guards; `for` over any iterable
with `break`/`continue`; `enumerate` and `zip` for indexed and parallel loops;
`while` for open-ended repetition; `match` for shape-based routing; the walrus
`:=` assigns-and-returns inline. Next: comprehensions — loops as expressions.
"""))
    return c


def nb_05():
    c = []
    c.append(md("""
# 05 · Comprehensions

A **comprehension** builds a collection from an iterable in one readable
expression. They replace the common "make an empty list, loop, append" pattern
and are the idiomatic way to transform and filter data in Python.
"""))

    c.append(md("""
## List comprehensions

Read it as: *expression* **for** *item* **in** *iterable* (**if** *condition*).
"""))
    c.append(code(
        "prices = [10, 25, 5, 100, 3]\n"
        "\n"
        "# the long way\n"
        "with_tax = []\n"
        "for p in prices:\n"
        "    with_tax.append(round(p * 1.2, 2))\n"
        "print('loop:', with_tax)\n"
        "\n"
        "# the comprehension way\n"
        "with_tax = [round(p * 1.2, 2) for p in prices]\n"
        "print('comp:', with_tax)"
    ))

    c.append(md("""
## Filtering with `if`

Add a trailing `if` to keep only items that match — cleaning and selecting rows
in one line.
"""))
    c.append(code(
        "amounts = [120, -5, 89, 0, 240, -12]\n"
        "valid = [a for a in amounts if a > 0]\n"
        "print('valid:', valid)\n"
        "\n"
        "# conditional expression INSIDE (transform every item, two ways)\n"
        "labels = ['big' if a >= 100 else 'small' for a in valid]\n"
        "print('labels:', labels)"
    ))

    c.append(md("""
## Dict and set comprehensions

Same syntax, different braces. Build lookup tables and unique sets directly.
"""))
    c.append(code(
        "products = [('ELE-001', 19.99), ('BOO-014', 8.5), ('GRO-003', 3.2)]\n"
        "\n"
        "price_by_sku = {sku: price for sku, price in products}\n"
        "print(price_by_sku)\n"
        "print('lookup BOO-014:', price_by_sku['BOO-014'])\n"
        "\n"
        "categories = {'Electronics', 'Books', 'Books', 'Home'}\n"
        "initials = {c[0] for c in categories}     # set comprehension\n"
        "print('initials:', initials)"
    ))

    c.append(md("""
## Generator expressions

Swap `[]` for `()` and you get a **generator**: it produces items lazily, one at
a time, without building the whole list in memory. Perfect for aggregating over
huge inputs (you'll go deeper in the generators notebook).
"""))
    c.append(code(
        "amounts = [120, 89, 240, 15, 60]\n"
        "\n"
        "total = sum(a for a in amounts if a >= 50)   # no intermediate list\n"
        "print('total >= 50:', total)\n"
        "\n"
        "gen = (a * 2 for a in amounts)\n"
        "print(type(gen))\n"
        "print('first value:', next(gen))            # pulled on demand"
    ))

    c.append(md("""
## Nested comprehensions (flatten)

Two `for` clauses flatten nested structure. Keep it to one or two levels — past
that, a normal loop reads better.
"""))
    c.append(code(
        "orders = [['ELE-001', 'BOO-014'], ['GRO-003'], ['TOY-009', 'HOM-002']]\n"
        "all_skus = [sku for order in orders for sku in order]\n"
        "print(all_skus)"
    ))

    c.append(md("""
### Recap

Comprehensions turn "init, loop, append" into one expression; add `if` to
filter; `{}` builds dicts/sets; `()` builds a lazy generator for big data.
Next: functions — packaging logic for reuse.
"""))
    return c


def nb_06():
    c = []
    c.append(md("""
# 06 · Functions

A **function** packages logic behind a name so you can reuse it and test it.
Functions are the primary unit of a data pipeline: `extract()`, `clean()`,
`transform()`, `load()`.
"""))

    c.append(md("""
## Defining and calling

`def` creates a function; `return` sends a value back. Parameters are inputs;
arguments are the values you pass. A **docstring** (the first string) documents
it.
"""))
    c.append(code(
        "def net_amount(gross, tax_rate=0.2):\n"
        "    '''Return gross plus tax, rounded to cents.'''\n"
        "    return round(gross * (1 + tax_rate), 2)\n"
        "\n"
        "print(net_amount(100))          # uses default tax_rate\n"
        "print(net_amount(100, 0.05))    # positional\n"
        "print(net_amount(gross=100, tax_rate=0.1))   # keyword args\n"
        "print(net_amount.__doc__)"
    ))

    c.append(md("""
## Default arguments — one sharp edge

Default values are evaluated **once**, when the function is defined. Never use a
**mutable** default (like `[]` or `{}`) — it is shared across calls. Use `None`
and create the object inside.
"""))
    c.append(code(
        "# WRONG: the list persists between calls\n"
        "def bad(item, bucket=[]):\n"
        "    bucket.append(item)\n"
        "    return bucket\n"
        "print(bad('a'), bad('b'))   # ['a'] then ['a', 'b'] — surprise!\n"
        "\n"
        "# RIGHT: sentinel default\n"
        "def good(item, bucket=None):\n"
        "    if bucket is None:\n"
        "        bucket = []\n"
        "    bucket.append(item)\n"
        "    return bucket\n"
        "print(good('a'), good('b'))   # ['a'] then ['b']"
    ))

    c.append(md("""
## `*args` and `**kwargs`

`*args` collects extra positional arguments into a tuple; `**kwargs` collects
extra keyword arguments into a dict. This lets a function accept a variable
number of inputs — common in wrappers and config-driven code.
"""))
    c.append(code(
        "def summarize(*values, **options):\n"
        "    label = options.get('label', 'total')\n"
        "    return f'{label}: {sum(values)}'\n"
        "\n"
        "print(summarize(10, 20, 30))\n"
        "print(summarize(10, 20, 30, label='revenue'))\n"
        "\n"
        "# The reverse: unpack a list/dict INTO a call\n"
        "nums = [1, 2, 3, 4]\n"
        "print(summarize(*nums, label='unpacked'))"
    ))

    c.append(md("""
## Type hints

Annotations document the expected types. Python does **not** enforce them at
runtime, but they make code self-describing and power editors, linters and
tools like `mypy` and `pydantic` (the typing notebook).
"""))
    c.append(code(
        "def clean_country(value: str) -> str:\n"
        "    return value.strip().upper()\n"
        "\n"
        "print(clean_country('  us '))\n"
        "print(clean_country.__annotations__)"
    ))

    c.append(md("""
## Scope and closures

Names created inside a function are **local** to it. A function defined inside
another can *capture* variables from the enclosing scope — a **closure**. This
is the basis for decorators and configurable functions.
"""))
    c.append(code(
        "def make_multiplier(factor):\n"
        "    def multiply(x):\n"
        "        return x * factor      # 'factor' captured from the outer scope\n"
        "    return multiply\n"
        "\n"
        "double = make_multiplier(2)\n"
        "triple = make_multiplier(3)\n"
        "print(double(10), triple(10))"
    ))

    c.append(md("""
## `lambda` — small anonymous functions

A one-expression function without a name. Handy as a `key=` for sorting or as a
quick callback. For anything non-trivial, use a real `def`.
"""))
    c.append(code(
        "orders = [\n"
        "    {'id': 1, 'amount': 89.9},\n"
        "    {'id': 2, 'amount': 240.0},\n"
        "    {'id': 3, 'amount': 12.5},\n"
        "]\n"
        "by_amount = sorted(orders, key=lambda o: o['amount'], reverse=True)\n"
        "print([o['id'] for o in by_amount])"
    ))

    c.append(md("""
### Recap

`def`/`return`, positional vs keyword args, safe (`None`) defaults, `*args`/`**kwargs`
for variadic inputs, type hints for clarity, closures for captured state, and
`lambda` for tiny callbacks. Next: iterators and generators for lazy data.
"""))
    return c


def nb_07():
    c = []
    c.append(md("""
# 07 · Iterators & Generators

Data engineering means processing data that may not fit in memory. **Iterators**
and **generators** let you stream items one at a time instead of materializing
everything at once — the foundation of scalable pipelines.
"""))

    c.append(md("""
## The iterator protocol

Anything you can loop over is **iterable**: calling `iter()` on it returns an
**iterator**, and `next()` pulls the next item until `StopIteration`. `for`
does all of this for you under the hood.
"""))
    c.append(code(
        "nums = [10, 20, 30]\n"
        "it = iter(nums)\n"
        "print(next(it))\n"
        "print(next(it))\n"
        "print(next(it))\n"
        "try:\n"
        "    next(it)\n"
        "except StopIteration:\n"
        "    print('exhausted')"
    ))

    c.append(md("""
## Generators with `yield`

A function that uses `yield` becomes a **generator**: each `yield` produces a
value and *pauses*, resuming where it left off on the next request. State is
kept automatically. This reads like normal code but runs lazily.
"""))
    c.append(code(
        "def countdown(n):\n"
        "    while n > 0:\n"
        "        yield n\n"
        "        n -= 1\n"
        "\n"
        "for x in countdown(3):\n"
        "    print(x)\n"
        "\n"
        "print('as list:', list(countdown(5)))"
    ))

    c.append(md("""
## Why lazy matters: process a big source with constant memory

The generator below yields one 'record' at a time. A pipeline built from
generators holds only the current item in memory, no matter how large the
source — the key to processing files bigger than RAM.
"""))
    c.append(code(
        "def read_records(n):\n"
        "    for i in range(n):\n"
        "        yield {'id': i, 'amount': (i * 7) % 100}\n"
        "\n"
        "# Chain lazy steps: filter -> transform -> aggregate, no big lists\n"
        "records = read_records(1_000_000)\n"
        "big = (r for r in records if r['amount'] >= 50)\n"
        "taxed = (r['amount'] * 1.2 for r in big)\n"
        "total = sum(taxed)          # everything streams; memory stays tiny\n"
        "print('total:', round(total, 2))"
    ))

    c.append(md("""
## `itertools` — batteries for iterators

The standard library `itertools` module has fast, memory-efficient building
blocks. A few you'll reach for in data work:
"""))
    c.append(code(
        "import itertools\n"
        "\n"
        "# islice: take the first N from any (even infinite) iterator\n"
        "first5 = list(itertools.islice(range(1_000_000), 5))\n"
        "print('islice:', first5)\n"
        "\n"
        "# chain: concatenate iterables lazily\n"
        "print('chain:', list(itertools.chain([1, 2], [3, 4])))\n"
        "\n"
        "# groupby: group CONSECUTIVE items by a key (sort first!)\n"
        "rows = [('US', 1), ('US', 2), ('GB', 3), ('GB', 4), ('DE', 5)]\n"
        "for country, group in itertools.groupby(rows, key=lambda r: r[0]):\n"
        "    print(country, [g[1] for g in group])"
    ))

    c.append(md("""
## Batching a stream (a real DE pattern)

Loaders often write in batches (e.g. 1000 rows per INSERT). Here's a reusable
generator that chunks any iterable — you'll use this idea in the capstone.
"""))
    c.append(code(
        "import itertools\n"
        "\n"
        "def batched(iterable, size):\n"
        "    it = iter(iterable)\n"
        "    while True:\n"
        "        chunk = list(itertools.islice(it, size))\n"
        "        if not chunk:\n"
        "            return\n"
        "        yield chunk\n"
        "\n"
        "for batch in batched(range(10), 4):\n"
        "    print('batch of', len(batch), '->', batch)"
    ))

    c.append(md("""
### Recap

Iterables give iterators via `iter()`; `next()` advances them; `yield` makes
lazy generators that stream with constant memory; `itertools` supplies
`islice`, `chain`, `groupby`; batching is a core loader pattern. Next: modules
and the standard library.
"""))
    return c


def nb_08():
    c = []
    c.append(md("""
# 08 · Modules & the Standard Library

Code lives in **modules** (`.py` files) and **packages** (folders of modules).
`import` brings them in. Python ships with a huge **standard library** — batteries
included — so much of what a pipeline needs is already there.
"""))

    c.append(md("""
## Importing

Several forms, each with a use. Prefer importing the module (`import json`) or
specific names (`from pathlib import Path`); avoid `from x import *`.
"""))
    c.append(code(
        "import math\n"
        "from math import sqrt, pi\n"
        "import statistics as stats      # alias\n"
        "\n"
        "print(math.ceil(4.2), sqrt(144), round(pi, 4))\n"
        "print('mean:', stats.mean([10, 20, 30]))\n"
        "print('median:', stats.median([1, 2, 3, 100]))"
    ))

    c.append(md("""
## A quick tour of high-value stdlib modules

You will meet several of these in depth later. Here's a taste of how much you
get for free.
"""))
    c.append(code(
        "from collections import Counter, defaultdict\n"
        "\n"
        "words = 'etl etl load extract etl load'.split()\n"
        "print('Counter:', Counter(words))\n"
        "\n"
        "# defaultdict: never worry about missing keys\n"
        "groups = defaultdict(list)\n"
        "for country, cid in [('US', 1), ('GB', 2), ('US', 3)]:\n"
        "    groups[country].append(cid)\n"
        "print('grouped:', dict(groups))"
    ))
    c.append(code(
        "from pathlib import Path\n"
        "import os, sys, random, uuid\n"
        "\n"
        "print('cwd:', Path.cwd().name)\n"
        "print('an env var (PATH exists):', 'PATH' in os.environ)\n"
        "random.seed(0)\n"
        "print('random pick:', random.choice(['a', 'b', 'c']))\n"
        "print('a unique id:', uuid.uuid4())"
    ))

    c.append(md("""
## `dataclasses` and `typing` sneak peek

Two modules so useful they get their own treatment later (the OOP and typing notebooks),
but here's why they matter: structured records with almost no boilerplate.
"""))
    c.append(code(
        "from dataclasses import dataclass\n"
        "\n"
        "@dataclass\n"
        "class Order:\n"
        "    order_id: int\n"
        "    amount: float\n"
        "    status: str = 'completed'\n"
        "\n"
        "o = Order(1042, 89.9)\n"
        "print(o)                       # readable repr for free\n"
        "print('amount:', o.amount)"
    ))

    c.append(md("""
## How `import` finds code, and `__main__`

When you run a file directly, Python sets its `__name__` to `'__main__'`. The
`if __name__ == '__main__':` guard lets a file be both an importable module and
a runnable script — you saw it in `data/build_data.py`.
"""))
    c.append(code(
        "def main():\n"
        "    print('this runs only when executed as a script')\n"
        "\n"
        "print('__name__ in a notebook is:', __name__)\n"
        "\n"
        "if __name__ == '__main__':\n"
        "    main()"
    ))

    c.append(md("""
### Recap

`import` modules/packages; the standard library covers `math`, `statistics`,
`collections` (`Counter`, `defaultdict`), `pathlib`, `os`, `random`, `uuid`,
`dataclasses` and much more; the `__main__` guard makes a file both importable
and runnable. Next: object-oriented programming.
"""))
    return c


def nb_09():
    c = []
    c.append(md("""
# 09 · Object-Oriented Programming

A **class** is a blueprint for objects that bundle **data** (attributes) with
**behavior** (methods). In data engineering you'll use classes for connectors,
config, and typed records — and you'll read a lot of library code built this
way.
"""))

    c.append(md("""
## Defining a class

`__init__` is the constructor: it runs when you create an instance and sets up
attributes on `self` (the instance). Methods are functions defined in the class
that take `self` first.
"""))
    c.append(code(
        "class Accumulator:\n"
        "    '''Running total and count of amounts.'''\n"
        "    def __init__(self):\n"
        "        self.total = 0.0\n"
        "        self.count = 0\n"
        "\n"
        "    def add(self, amount):\n"
        "        self.total += amount\n"
        "        self.count += 1\n"
        "\n"
        "    def average(self):\n"
        "        return self.total / self.count if self.count else 0.0\n"
        "\n"
        "acc = Accumulator()\n"
        "for a in [10, 20, 30]:\n"
        "    acc.add(a)\n"
        "print('total:', acc.total, '| avg:', acc.average())"
    ))

    c.append(md("""
## Dunder methods

Special `__method__` names hook into Python syntax. `__repr__` controls how an
object prints; `__eq__` defines equality; `__len__` powers `len()`. Implementing
them makes your objects feel native.
"""))
    c.append(code(
        "class Money:\n"
        "    def __init__(self, cents):\n"
        "        self.cents = cents\n"
        "    def __repr__(self):\n"
        "        return f'Money(${self.cents / 100:.2f})'\n"
        "    def __eq__(self, other):\n"
        "        return self.cents == other.cents\n"
        "    def __add__(self, other):\n"
        "        return Money(self.cents + other.cents)\n"
        "\n"
        "a = Money(1099)\n"
        "b = Money(500)\n"
        "print(a)                 # uses __repr__\n"
        "print(a + b)             # uses __add__\n"
        "print(a == Money(1099))  # uses __eq__"
    ))

    c.append(md("""
## `@dataclass` — records without boilerplate

For plain data-holding classes, `@dataclass` generates `__init__`, `__repr__`
and `__eq__` for you. This is the go-to for typed records in a pipeline.
"""))
    c.append(code(
        "from dataclasses import dataclass, field\n"
        "\n"
        "@dataclass\n"
        "class Customer:\n"
        "    customer_id: int\n"
        "    name: str\n"
        "    country: str = 'US'\n"
        "    tags: list = field(default_factory=list)   # safe mutable default\n"
        "\n"
        "c1 = Customer(1, 'Ava Smith')\n"
        "c2 = Customer(1, 'Ava Smith')\n"
        "print(c1)\n"
        "print('equal:', c1 == c2)   # value equality for free\n"
        "c1.tags.append('vip')\n"
        "print(c1.tags, c2.tags)     # independent lists"
    ))

    c.append(md("""
## Inheritance

A subclass *extends* or *specializes* a base class, reusing its code. Use it for
"is-a" relationships — e.g. specific loaders that share a common interface.
Prefer composition for "has-a".
"""))
    c.append(code(
        "class Loader:\n"
        "    def load(self, rows):\n"
        "        raise NotImplementedError('subclasses must implement load()')\n"
        "\n"
        "class ConsoleLoader(Loader):\n"
        "    def load(self, rows):\n"
        "        for r in rows:\n"
        "            print('LOAD', r)\n"
        "\n"
        "loader = ConsoleLoader()\n"
        "loader.load([{'id': 1}, {'id': 2}])\n"
        "print('is a Loader:', isinstance(loader, Loader))"
    ))

    c.append(md("""
## Properties

`@property` exposes a computed value as if it were an attribute — good for
derived, always-consistent fields.
"""))
    c.append(code(
        "class Order:\n"
        "    def __init__(self, quantity, unit_price):\n"
        "        self.quantity = quantity\n"
        "        self.unit_price = unit_price\n"
        "    @property\n"
        "    def total(self):\n"
        "        return round(self.quantity * self.unit_price, 2)\n"
        "\n"
        "o = Order(3, 19.99)\n"
        "print('total:', o.total)     # no parentheses — looks like an attribute"
    ))

    c.append(md("""
### Recap

Classes bundle state + behavior via `__init__` and methods on `self`; dunder
methods integrate with Python syntax; `@dataclass` removes boilerplate for
records; inheritance shares an interface; `@property` exposes computed fields.
Next: errors and context managers.
"""))
    return c


def nb_10():
    c = []
    c.append(md("""
# 10 · Errors & Context Managers

Real data is dirty and systems fail. Robust pipelines *expect* errors and handle
them deliberately. This notebook covers exceptions and the `with` statement that
guarantees cleanup.
"""))

    c.append(md("""
## Exceptions and `try` / `except`

When something goes wrong Python **raises** an exception. Unhandled, it stops the
program. `try/except` lets you catch specific error types and respond. Catch the
*narrowest* exception you can — never a bare `except:`.
"""))
    c.append(code(
        "def to_int(value):\n"
        "    try:\n"
        "        return int(value)\n"
        "    except ValueError:\n"
        "        return None          # couldn't parse -> treat as missing\n"
        "\n"
        "for v in ['42', '3.5', '', 'abc', '  7 ']:\n"
        "    print(repr(v), '->', to_int(v))"
    ))

    c.append(md("""
## `else` and `finally`

`else` runs only if no exception was raised; `finally` runs **no matter what**
— the place for cleanup (closing files, connections).
"""))
    c.append(code(
        "def divide(a, b):\n"
        "    try:\n"
        "        result = a / b\n"
        "    except ZeroDivisionError:\n"
        "        print('cannot divide by zero')\n"
        "        return None\n"
        "    else:\n"
        "        print('division ok')\n"
        "        return result\n"
        "    finally:\n"
        "        print('...cleanup always runs')\n"
        "\n"
        "print(divide(10, 2))\n"
        "print(divide(10, 0))"
    ))

    c.append(md("""
## Common exception types

Knowing the built-in exceptions helps you catch precisely and read tracebacks.
"""))
    c.append(code(
        "examples = [\n"
        "    ('int(\"x\")', lambda: int('x')),          # ValueError\n"
        "    ('[1,2][5]', lambda: [1, 2][5]),            # IndexError\n"
        "    ('{}[\"k\"]', lambda: {}['k']),             # KeyError\n"
        "    ('1 + \"a\"', lambda: 1 + 'a'),             # TypeError\n"
        "    ('open(\"nope\")', lambda: open('nope')),   # FileNotFoundError\n"
        "]\n"
        "for label, fn in examples:\n"
        "    try:\n"
        "        fn()\n"
        "    except Exception as e:\n"
        "        print(f'{label:>14} -> {type(e).__name__}: {e}')"
    ))

    c.append(md("""
## Raising and custom exceptions

Raise your own errors to signal problems clearly. A custom exception class makes
pipeline failures self-documenting and easy to catch selectively.
"""))
    c.append(code(
        "class DataQualityError(Exception):\n"
        "    '''Raised when a record fails validation.'''\n"
        "\n"
        "def validate(order):\n"
        "    if order['amount'] < 0:\n"
        "        raise DataQualityError(f\"negative amount in order {order['id']}\")\n"
        "    return order\n"
        "\n"
        "try:\n"
        "    validate({'id': 5, 'amount': -10})\n"
        "except DataQualityError as e:\n"
        "    print('rejected:', e)"
    ))

    c.append(md("""
## Context managers: the `with` statement

A **context manager** guarantees setup and teardown around a block, even if an
error occurs. Opening files is the classic case — `with` closes the file
automatically, so you never leak handles.
"""))
    c.append(code(
        "from pathlib import Path\n"
        "import tempfile\n"
        "\n"
        "tmp = Path(tempfile.gettempdir()) / 'demo.txt'\n"
        "with open(tmp, 'w', encoding='utf-8') as f:\n"
        "    f.write('line 1\\nline 2\\n')\n"
        "# file is guaranteed closed here, even if write() had raised\n"
        "\n"
        "with open(tmp, encoding='utf-8') as f:\n"
        "    print(f.read().strip())"
    ))

    c.append(md("""
## Writing your own context manager

`contextlib.contextmanager` turns a generator into a context manager — the code
before `yield` is setup, after `yield` is teardown. Great for timing, temporary
state, or transactions.
"""))
    c.append(code(
        "import time\n"
        "from contextlib import contextmanager\n"
        "\n"
        "@contextmanager\n"
        "def timer(label):\n"
        "    start = time.perf_counter()\n"
        "    try:\n"
        "        yield\n"
        "    finally:\n"
        "        elapsed = time.perf_counter() - start\n"
        "        print(f'{label} took {elapsed*1000:.1f} ms')\n"
        "\n"
        "with timer('sum 1M'):\n"
        "    total = sum(range(1_000_000))\n"
        "print('result:', total)"
    ))

    c.append(md("""
### Recap

`try/except` catches specific exceptions; `else`/`finally` structure success and
cleanup; raise custom exceptions for clear pipeline failures; `with` guarantees
teardown; `@contextmanager` builds your own. That completes **Track 1** — you're
fluent in the language. Next: Track 2 opens with files and `pathlib`.
"""))
    return c


def nb_11():
    c = []
    c.append(md("""
# 11 · Files & `pathlib`

**Track 2 begins.** Data engineering is, first of all, moving bytes in and out
of files. This notebook covers reading and writing files, handling paths
portably with `pathlib`, encodings, and streaming files too big for memory.
"""))
    c.append(DATA_BOOT)

    c.append(md("""
## `pathlib.Path` — portable paths

Never build paths by gluing strings with `/` or `\\`. `Path` joins with the `/`
operator and works identically on Windows, macOS and Linux. It also answers
questions about files.
"""))
    c.append(code(
        "customers = RAW / 'customers.csv'      # join with /\n"
        "print('path:', customers)\n"
        "print('name:', customers.name)\n"
        "print('stem:', customers.stem)\n"
        "print('suffix:', customers.suffix)\n"
        "print('parent:', customers.parent.name)\n"
        "print('exists:', customers.exists())\n"
        "print('size (bytes):', customers.stat().st_size)"
    ))

    c.append(md("""
## Reading text

For small files, `read_text()` returns the whole content as one string;
`.splitlines()` breaks it into lines. **Always specify `encoding='utf-8'`** — the
default varies by platform and causes subtle bugs.
"""))
    c.append(code(
        "text = customers.read_text(encoding='utf-8')\n"
        "lines = text.splitlines()\n"
        "print('total lines:', len(lines))\n"
        "print('header:', lines[0])\n"
        "print('first row:', lines[1])"
    ))

    c.append(md("""
## Streaming line by line (memory-safe)

Opening a file gives an iterator of lines — you can process a multi-gigabyte
file while holding one line at a time. This is the default way to read big data
files in plain Python.
"""))
    c.append(code(
        "count = 0\n"
        "sample = []\n"
        "with open(customers, encoding='utf-8') as f:\n"
        "    header = next(f)                 # consume header line\n"
        "    for line in f:                   # streams; constant memory\n"
        "        count += 1\n"
        "        if count <= 3:\n"
        "            sample.append(line.strip())\n"
        "print('data rows:', count)\n"
        "print('sample:', sample)"
    ))

    c.append(md("""
## Writing files

Open with mode `'w'` (overwrite) or `'a'` (append). Writing through a `with`
block guarantees the file is flushed and closed. Here we write a small report
into a scratch folder next to the data.
"""))
    c.append(code(
        "out_dir = DATA / 'staging'\n"
        "out_dir.mkdir(parents=True, exist_ok=True)   # create if missing\n"
        "report = out_dir / 'row_counts.txt'\n"
        "\n"
        "with open(report, 'w', encoding='utf-8') as f:\n"
        "    f.write('file,rows\\n')\n"
        "    f.write(f'customers,{count}\\n')\n"
        "\n"
        "print(report.read_text(encoding='utf-8'))"
    ))

    c.append(md("""
## Text vs bytes, and encodings

Text mode decodes bytes to `str` using an encoding; binary mode (`'rb'`/`'wb'`)
gives raw `bytes`. You need binary mode for images, Parquet, gzip, etc. Knowing
the layer prevents `UnicodeDecodeError` surprises.
"""))
    c.append(code(
        "raw_bytes = customers.read_bytes()[:40]\n"
        "print('bytes:', raw_bytes)\n"
        "print('decoded:', raw_bytes.decode('utf-8'))\n"
        "\n"
        "# encode a str to bytes explicitly\n"
        "print('etl'.encode('utf-8'))"
    ))

    c.append(md("""
## Finding files with `glob`

`Path.glob` and `rglob` (recursive) find files by pattern — essential when
ingesting a folder of daily drops.
"""))
    c.append(code(
        "print('csv files in raw/:')\n"
        "for p in sorted(RAW.glob('*.csv')):\n"
        "    print(' ', p.name, f'({p.stat().st_size} bytes)')"
    ))

    c.append(md("""
### Recap

`Path` joins with `/` and inspects files; `read_text`/`read_bytes` for small
files, line iteration for big ones; always set `encoding='utf-8'`; `mkdir`,
write modes, and `glob` for real ingestion. Next: structured CSV parsing.
"""))
    return c


def nb_12():
    c = []
    c.append(md("""
# 12 · CSV & Delimited Data

CSV is the lingua franca of data exchange. Splitting on commas by hand *breaks*
the moment a value contains a comma or newline. The `csv` module parses it
correctly, handling quoting and escaping for you.
"""))
    c.append(DATA_BOOT)

    c.append(md("""
## Why not just `split(',')`?

A field like `"Smith, Ava"` contains a comma inside quotes. `str.split(',')`
would wrongly cut it in two. Use the `csv` module — always.
"""))
    c.append(code(
        "line = 'Smith, Ava,US,\"1,200.50\"'\n"
        "print('naive split:', line.split(','))   # 4 pieces, both wrong\n"
        "\n"
        "import csv, io\n"
        "parsed = next(csv.reader(io.StringIO(line)))\n"
        "print('csv.reader :', parsed)             # correct: 3 fields"
    ))

    c.append(md("""
## `csv.DictReader` — rows as dicts

`DictReader` uses the header row as keys, giving you one dict per record — the
natural shape for processing. Note every value comes back as a **string**;
converting types is your job.
"""))
    c.append(code(
        "import csv\n"
        "\n"
        "with open(RAW / 'orders.csv', encoding='utf-8', newline='') as f:\n"
        "    reader = csv.DictReader(f)\n"
        "    rows = list(reader)\n"
        "\n"
        "print('columns:', reader.fieldnames)\n"
        "print('total rows:', len(rows))\n"
        "print('first row:', rows[0])\n"
        "print('amount type:', type(rows[0]['amount']))   # str!"
    ))

    c.append(md("""
## Cleaning while you read

The real work: convert types, skip bad rows, normalize text. Below we compute
total completed revenue in one streaming pass, coercing `amount` to float and
guarding against bad values.
"""))
    c.append(code(
        "import csv\n"
        "\n"
        "revenue = 0.0\n"
        "skipped = 0\n"
        "with open(RAW / 'orders.csv', encoding='utf-8', newline='') as f:\n"
        "    for row in csv.DictReader(f):\n"
        "        if row['status'] != 'completed':\n"
        "            continue\n"
        "        try:\n"
        "            revenue += float(row['amount'])\n"
        "        except ValueError:\n"
        "            skipped += 1\n"
        "print(f'completed revenue: {revenue:,.2f}')\n"
        "print('skipped bad rows:', skipped)"
    ))

    c.append(md("""
## Writing CSV with `DictWriter`

`DictWriter` writes dicts back out, quoting anything that needs it. Here we
aggregate revenue by status and write a clean summary file.
"""))
    c.append(code(
        "import csv\n"
        "from collections import defaultdict\n"
        "\n"
        "totals = defaultdict(float)\n"
        "with open(RAW / 'orders.csv', encoding='utf-8', newline='') as f:\n"
        "    for row in csv.DictReader(f):\n"
        "        totals[row['status']] += float(row['amount'])\n"
        "\n"
        "out = DATA / 'staging' / 'revenue_by_status.csv'\n"
        "out.parent.mkdir(parents=True, exist_ok=True)\n"
        "with open(out, 'w', encoding='utf-8', newline='') as f:\n"
        "    w = csv.DictWriter(f, fieldnames=['status', 'revenue'])\n"
        "    w.writeheader()\n"
        "    for status, total in sorted(totals.items()):\n"
        "        w.writerow({'status': status, 'revenue': round(total, 2)})\n"
        "\n"
        "print(out.read_text(encoding='utf-8'))"
    ))

    c.append(md("""
## Dialects & delimiters

Not everything is comma-separated. TSV uses tabs; some European exports use
`;`. Pass `delimiter=` to match. The `newline=''` argument when opening is
important on Windows to avoid blank lines.
"""))
    c.append(code(
        "import csv, io\n"
        "tsv = 'id\\tname\\n1\\tAva\\n2\\tLiam'\n"
        "for row in csv.DictReader(io.StringIO(tsv), delimiter='\\t'):\n"
        "    print(row)"
    ))

    c.append(md("""
### Recap

Use the `csv` module (not `split`) to respect quoting; `DictReader` yields dicts
but all-string values you must cast; clean and aggregate in a streaming pass;
`DictWriter` writes clean output; set `delimiter=` and `newline=''`. Next: JSON
and semi-structured data.
"""))
    return c


def nb_13():
    c = []
    c.append(md("""
# 13 · JSON & Serialization

APIs, config, logs and event streams are overwhelmingly **JSON**. Python's
`json` module maps cleanly between JSON text and Python objects (dicts, lists,
str, int, float, bool, None). This notebook also covers **JSON Lines** — the
dominant format for event data — and `pickle`.
"""))
    c.append(DATA_BOOT)

    c.append(md("""
## `loads`/`dumps` vs `load`/`dump`

- `json.loads(s)` / `json.dumps(obj)` work with **strings** (the `s` = string).
- `json.load(f)` / `json.dump(obj, f)` work with **files**.

JSON objects become dicts; arrays become lists.
"""))
    c.append(code(
        "import json\n"
        "\n"
        "text = '{\"id\": 7, \"tags\": [\"vip\", \"eu\"], \"active\": true, \"note\": null}'\n"
        "obj = json.loads(text)\n"
        "print(type(obj), obj)\n"
        "print('tags:', obj['tags'], '| active:', obj['active'], '| note:', obj['note'])\n"
        "\n"
        "back = json.dumps(obj, indent=2)\n"
        "print(back)"
    ))

    c.append(md("""
## JSON Lines (`.jsonl`) — the event-stream format

One JSON object per line. It streams beautifully (parse a line at a time) and
appends cheaply — which is why clickstreams and logs use it. Our
`events.jsonl` is exactly this.
"""))
    c.append(code(
        "import json\n"
        "\n"
        "events = []\n"
        "with open(RAW / 'events.jsonl', encoding='utf-8') as f:\n"
        "    for line in f:\n"
        "        events.append(json.loads(line))\n"
        "\n"
        "print('events:', len(events))\n"
        "print('first event:', events[0])"
    ))

    c.append(md("""
## Navigating nested payloads

Event records have a nested `payload` object with **optional** keys. Use
`.get()` with defaults so missing keys don't crash the pipeline.
"""))
    c.append(code(
        "from collections import Counter\n"
        "\n"
        "types = Counter(e['event_type'] for e in events)\n"
        "print('event types:', dict(types))\n"
        "\n"
        "# Only 'search' events carry payload['query']\n"
        "queries = [e['payload'].get('query') for e in events if e['event_type'] == 'search']\n"
        "print('top searches:', Counter(queries).most_common(3))\n"
        "\n"
        "# Only 'add_to_cart' carries payload['qty']; default to 0 elsewhere\n"
        "cart_qty = sum(e['payload'].get('qty', 0) for e in events)\n"
        "print('total cart qty:', cart_qty)"
    ))

    c.append(md("""
## Writing JSON and JSON Lines

Serialize a summary to pretty JSON, and write records back out as `.jsonl`.
"""))
    c.append(code(
        "import json\n"
        "from collections import Counter\n"
        "\n"
        "summary = {\n"
        "    'total_events': len(events),\n"
        "    'by_type': dict(Counter(e['event_type'] for e in events)),\n"
        "}\n"
        "out = DATA / 'staging' / 'event_summary.json'\n"
        "out.parent.mkdir(parents=True, exist_ok=True)\n"
        "out.write_text(json.dumps(summary, indent=2), encoding='utf-8')\n"
        "print(out.read_text(encoding='utf-8'))"
    ))

    c.append(md("""
## Non-serializable types & custom encoders

`json` doesn't know how to serialize a `datetime`, `set`, or `Decimal` out of
the box — it raises `TypeError`. Provide a `default=` function to convert them.
"""))
    c.append(code(
        "import json\n"
        "from datetime import datetime\n"
        "\n"
        "record = {'id': 1, 'seen_at': datetime(2024, 6, 1, 9, 30)}\n"
        "\n"
        "def encode(obj):\n"
        "    if isinstance(obj, datetime):\n"
        "        return obj.isoformat()\n"
        "    raise TypeError(f'not serializable: {type(obj)}')\n"
        "\n"
        "print(json.dumps(record, default=encode))"
    ))

    c.append(md("""
## `pickle` — Python-native serialization (use with care)

`pickle` serializes almost any Python object to bytes. It's convenient for
caching intermediate results, but **never unpickle untrusted data** (it can
execute arbitrary code) and it isn't cross-language. Prefer JSON/Parquet for
interchange.
"""))
    c.append(code(
        "import pickle\n"
        "\n"
        "obj = {'model': 'v1', 'weights': [0.1, 0.2, 0.3], 'tags': {'a', 'b'}}\n"
        "blob = pickle.dumps(obj)\n"
        "print('pickled bytes:', len(blob))\n"
        "restored = pickle.loads(blob)\n"
        "print('restored:', restored)"
    ))

    c.append(md("""
### Recap

`loads/dumps` (strings) vs `load/dump` (files); JSON Lines streams event data;
navigate nested payloads defensively with `.get()`; supply `default=` for
`datetime`/`set`/`Decimal`; `pickle` is Python-only and unsafe on untrusted
input. Next: dates and times.
"""))
    return c


def nb_14():
    c = []
    c.append(md("""
# 14 · Dates & Times

Timestamps are everywhere in data — and a common source of bugs. This notebook
covers `date`, `datetime`, `timedelta`, parsing/formatting strings, epoch time,
and why timezones matter.
"""))

    c.append(md("""
## `date`, `datetime`, `timedelta`

`date` is a calendar day; `datetime` adds time of day; `timedelta` is a
duration you add or subtract. Differences between datetimes give timedeltas.
"""))
    c.append(code(
        "from datetime import date, datetime, timedelta\n"
        "\n"
        "today = date(2024, 6, 15)\n"
        "print('today:', today, '| weekday:', today.strftime('%A'))\n"
        "print('in 30 days:', today + timedelta(days=30))\n"
        "\n"
        "start = datetime(2024, 6, 1, 9, 0, 0)\n"
        "end = datetime(2024, 6, 1, 17, 30, 0)\n"
        "dur = end - start\n"
        "print('duration:', dur, '=', dur.total_seconds() / 3600, 'hours')"
    ))

    c.append(md("""
## Parsing strings → datetimes (`strptime`)

Ingested timestamps are strings. `strptime` parses them using **format codes**
(`%Y` year, `%m` month, `%d` day, `%H:%M:%S` time). Our data uses ISO-8601, and
`fromisoformat` is the fast path for that.
"""))
    c.append(code(
        "from datetime import datetime\n"
        "\n"
        "s = '2024-06-01 14:30:00'\n"
        "dt = datetime.strptime(s, '%Y-%m-%d %H:%M:%S')\n"
        "print(dt, '| year:', dt.year, '| hour:', dt.hour)\n"
        "\n"
        "iso = '2024-06-01T14:30:00'\n"
        "print('fromisoformat:', datetime.fromisoformat(iso))"
    ))

    c.append(md("""
## Formatting datetimes → strings (`strftime`)

The reverse: turn a datetime into a string for filenames, partitions, or
reports. Partition paths like `year=2024/month=06/day=01` come straight from
`strftime`.
"""))
    c.append(code(
        "from datetime import datetime\n"
        "\n"
        "dt = datetime(2024, 6, 1, 14, 30)\n"
        "print(dt.strftime('%Y-%m-%d'))\n"
        "print(dt.strftime('%Y%m%d_%H%M%S'))            # good for filenames\n"
        "print(dt.strftime('year=%Y/month=%m/day=%d'))  # Hive-style partition"
    ))

    c.append(md("""
## Real example: bucket orders by month

Parse the `order_ts` strings from the data and count orders per month — the kind
of time-bucketing you do constantly.
"""))
    c.append(code(
        "import csv\n"
        "from collections import Counter\n"
        "from datetime import datetime\n"
        "from pathlib import Path\n"
        "\n"
        "def find_data():\n"
        "    for base in (Path.cwd(), *Path.cwd().parents):\n"
        "        if (base / 'data' / 'raw').exists():\n"
        "            return base / 'data'\n"
        "    raise FileNotFoundError('run data/build_data.py')\n"
        "RAW = find_data() / 'raw'\n"
        "\n"
        "by_month = Counter()\n"
        "with open(RAW / 'orders.csv', encoding='utf-8', newline='') as f:\n"
        "    for row in csv.DictReader(f):\n"
        "        dt = datetime.fromisoformat(row['order_ts'])\n"
        "        by_month[dt.strftime('%Y-%m')] += 1\n"
        "for month, n in sorted(by_month.items())[:6]:\n"
        "    print(month, n)"
    ))

    c.append(md("""
## Epoch time and timezones

**Epoch** (Unix) time is seconds since 1970-01-01 UTC — how systems exchange
instants unambiguously. A **naive** datetime has no timezone; an **aware** one
does. Rule of thumb: store and compute in **UTC**, convert to local only for
display.
"""))
    c.append(code(
        "from datetime import datetime, timezone, timedelta\n"
        "\n"
        "aware = datetime(2024, 6, 1, 14, 30, tzinfo=timezone.utc)\n"
        "print('utc:', aware)\n"
        "print('epoch seconds:', aware.timestamp())\n"
        "print('back from epoch:', datetime.fromtimestamp(aware.timestamp(), tz=timezone.utc))\n"
        "\n"
        "ist = timezone(timedelta(hours=5, minutes=30))\n"
        "print('same instant in IST:', aware.astimezone(ist))"
    ))

    c.append(md("""
### Recap

`date`/`datetime`/`timedelta` model days, instants and durations; `strptime`
parses, `strftime` formats (and builds partition paths); `fromisoformat` is the
fast ISO path; store/compute in UTC and treat epoch as the interchange format.
Next: talking to HTTP APIs.
"""))
    return c


def nb_15():
    c = []
    c.append(md("""
# 15 · APIs & HTTP

A huge share of ingestion is pulling data from **REST APIs**. This notebook
covers the request/response model, status codes, JSON payloads, pagination,
and retry/backoff — using the `requests` library.

> To keep the course fully offline and deterministic, we run against a small
> **simulated API** defined in the next cell. The `requests` code you'd write
> against a real endpoint is shown in the markdown so you learn the real shape.
"""))

    c.append(md("""
## The HTTP model

A client sends a **request** (method + URL + headers) and gets a **response**
(status code + headers + body). For data work the method is usually `GET` and
the body is JSON. Status codes tell you what happened:

- `2xx` success (200 OK)
- `4xx` client error (401 unauthorized, 404 not found, 429 too many requests)
- `5xx` server error (500, 503) — usually worth **retrying**

With `requests` the real code is:

```python
import requests
resp = requests.get('https://api.example.com/orders',
                    params={'page': 1}, headers={'Authorization': 'Bearer TOKEN'},
                    timeout=10)
resp.raise_for_status()      # raise on 4xx/5xx
data = resp.json()           # parse JSON body -> dict
```
"""))
    c.append(code(
        "# A tiny in-memory API so this notebook runs offline.\n"
        "import math\n"
        "\n"
        "_ALL = [{'id': i, 'amount': (i * 13) % 200} for i in range(1, 48)]\n"
        "PAGE_SIZE = 10\n"
        "\n"
        "def fake_get(page):\n"
        "    '''Mimics GET /orders?page=N returning a JSON body + status code.'''\n"
        "    start = (page - 1) * PAGE_SIZE\n"
        "    chunk = _ALL[start:start + PAGE_SIZE]\n"
        "    total_pages = math.ceil(len(_ALL) / PAGE_SIZE)\n"
        "    status = 200 if chunk else 404\n"
        "    return status, {'page': page, 'total_pages': total_pages, 'results': chunk}\n"
        "\n"
        "status, body = fake_get(1)\n"
        "print('status:', status)\n"
        "print('page 1 of', body['total_pages'], '- got', len(body['results']), 'records')\n"
        "print('first:', body['results'][0])"
    ))

    c.append(md("""
## Pagination: fetch every page

APIs cap how many records they return per call. You loop, incrementing the page,
until the response tells you you're done. This `while` loop mirrors real
`requests`-based ingestion exactly.
"""))
    c.append(code(
        "all_records = []\n"
        "page = 1\n"
        "while True:\n"
        "    status, body = fake_get(page)\n"
        "    if status == 404 or not body['results']:\n"
        "        break\n"
        "    all_records.extend(body['results'])\n"
        "    if page >= body['total_pages']:\n"
        "        break\n"
        "    page += 1\n"
        "\n"
        "print('fetched', len(all_records), 'records across', page, 'pages')\n"
        "print('total amount:', sum(r['amount'] for r in all_records))"
    ))

    c.append(md("""
## Retries with exponential backoff

Transient `5xx` errors and rate limits (`429`) are normal. Robust clients
**retry** a few times, waiting longer each attempt (backoff), then give up.
Below is a reusable retry wrapper — the same logic you'd wrap around
`requests.get`.
"""))
    c.append(code(
        "import time\n"
        "\n"
        "_attempts = {'n': 0}\n"
        "def flaky_get():\n"
        "    '''Fails twice with 503, then succeeds — to demonstrate retries.'''\n"
        "    _attempts['n'] += 1\n"
        "    if _attempts['n'] < 3:\n"
        "        return 503, None\n"
        "    return 200, {'ok': True}\n"
        "\n"
        "def get_with_retry(fn, max_tries=5, base_delay=0.01):\n"
        "    for attempt in range(1, max_tries + 1):\n"
        "        status, body = fn()\n"
        "        if status == 200:\n"
        "            print(f'success on attempt {attempt}')\n"
        "            return body\n"
        "        wait = base_delay * (2 ** (attempt - 1))    # 1x, 2x, 4x, ...\n"
        "        print(f'attempt {attempt} got {status}; retrying in {wait:.3f}s')\n"
        "        time.sleep(wait)\n"
        "    raise RuntimeError('exhausted retries')\n"
        "\n"
        "print(get_with_retry(flaky_get))"
    ))

    c.append(md("""
## Being a good client

Real ingestion also: sets a `timeout` on every request (never hang forever),
respects rate limits (sleep between calls or honor `Retry-After`), reuses a
`requests.Session` for connection pooling, and stores secrets in env vars — not
in code (the logging & config notebook). These habits keep pipelines reliable and polite.
"""))
    c.append(code(
        "# Sketch of production-shaped ingestion (offline stand-in for the loop):\n"
        "import time\n"
        "\n"
        "def ingest_all():\n"
        "    records, page = [], 1\n"
        "    while True:\n"
        "        status, body = fake_get(page)\n"
        "        if status != 200 or not body['results']:\n"
        "            break\n"
        "        records.extend(body['results'])\n"
        "        page += 1\n"
        "        time.sleep(0.001)      # be polite between pages\n"
        "    return records\n"
        "\n"
        "print('ingested', len(ingest_all()), 'records')"
    ))

    c.append(md("""
### Recap

HTTP = request/response with status codes (`2xx/4xx/5xx`); parse JSON bodies to
dicts; paginate with a `while` loop until the API says stop; retry transient
failures with exponential backoff; always set timeouts and keep secrets in the
environment. Next: databases from Python.
"""))
    return c


def nb_16():
    c = []
    c.append(md("""
# 16 · Databases with Python

Pipelines read from and write to databases constantly. Python's **DB-API** gives
every database a common interface; `sqlite3` ships in the standard library so we
can practice with zero setup. We'll also meet **SQLAlchemy Core**, the toolkit
most data pipelines actually use.
"""))
    c.append(DATA_BOOT)

    c.append(md("""
## Connect, cursor, query (the DB-API)

The pattern is universal: `connect()` → `cursor()` → `execute()` →
`fetchall()`. It's identical for Postgres/MySQL/etc., just a different driver
and connection string.
"""))
    c.append(code(
        "import sqlite3\n"
        "\n"
        "con = sqlite3.connect(DATA / 'retail.db')\n"
        "cur = con.cursor()\n"
        "cur.execute('SELECT status, COUNT(*), ROUND(SUM(amount), 2) '\n"
        "            'FROM orders GROUP BY status')\n"
        "for row in cur.fetchall():\n"
        "    print(row)\n"
        "con.close()"
    ))

    c.append(md("""
## Parameterized queries — never format SQL by hand

Building SQL with f-strings invites **SQL injection** and breaks on quotes. Pass
values as parameters with `?` placeholders (SQLite) — the driver escapes them
safely.
"""))
    c.append(code(
        "import sqlite3\n"
        "con = sqlite3.connect(DATA / 'retail.db')\n"
        "cur = con.cursor()\n"
        "\n"
        "country = 'US'\n"
        "min_amount = 100\n"
        "cur.execute(\n"
        "    'SELECT o.order_id, o.amount FROM orders o '\n"
        "    'JOIN customers c ON c.customer_id = o.customer_id '\n"
        "    'WHERE c.country = ? AND o.amount >= ? LIMIT 5',\n"
        "    (country, min_amount),        # parameters as a tuple\n"
        ")\n"
        "for row in cur.fetchall():\n"
        "    print(row)\n"
        "con.close()"
    ))

    c.append(md("""
## Rows as dicts

By default rows are tuples. Set a `row_factory` to get name-based access — much
safer than remembering column positions.
"""))
    c.append(code(
        "import sqlite3\n"
        "con = sqlite3.connect(DATA / 'retail.db')\n"
        "con.row_factory = sqlite3.Row          # rows behave like dicts\n"
        "cur = con.cursor()\n"
        "cur.execute('SELECT customer_id, name, country FROM customers LIMIT 3')\n"
        "for row in cur.fetchall():\n"
        "    print(row['customer_id'], row['name'], '->', row['country'])\n"
        "con.close()"
    ))

    c.append(md("""
## Writing data: INSERT, transactions, bulk load

Use `executemany` for bulk inserts and **commit** to persist. Wrapping writes in
a transaction means either all rows land or none do — critical for correct
loads. Here we build a small aggregate table.
"""))
    c.append(code(
        "import sqlite3\n"
        "con = sqlite3.connect(DATA / 'retail.db')\n"
        "cur = con.cursor()\n"
        "\n"
        "cur.execute('DROP TABLE IF EXISTS revenue_by_country')\n"
        "cur.execute('CREATE TABLE revenue_by_country (country TEXT, revenue REAL)')\n"
        "\n"
        "rows = cur.execute(\n"
        "    'SELECT UPPER(c.country) AS country, ROUND(SUM(o.amount), 2) '\n"
        "    'FROM orders o JOIN customers c ON c.customer_id = o.customer_id '\n"
        "    \"WHERE o.status = 'completed' GROUP BY UPPER(c.country)\"\n"
        ").fetchall()\n"
        "\n"
        "cur.executemany('INSERT INTO revenue_by_country VALUES (?, ?)', rows)\n"
        "con.commit()                          # persist the transaction\n"
        "\n"
        "for r in cur.execute('SELECT * FROM revenue_by_country ORDER BY revenue DESC LIMIT 5'):\n"
        "    print(r)\n"
        "con.close()"
    ))

    c.append(md("""
## SQLAlchemy Core

Most Python data tools speak **SQLAlchemy**. An `engine` abstracts the database
behind one connection string, so the same code targets SQLite in dev and
Postgres in prod. `text()` runs SQL with named `:params`, and it integrates
directly with pandas (covered in the companion pandas-numpy bootcamp).
"""))
    c.append(code(
        "from sqlalchemy import create_engine, text\n"
        "\n"
        "engine = create_engine(f'sqlite:///{DATA / \"retail.db\"}')\n"
        "with engine.connect() as conn:\n"
        "    result = conn.execute(\n"
        "        text('SELECT category, COUNT(*) AS n FROM products '\n"
        "             'GROUP BY category ORDER BY n DESC'),\n"
        "    )\n"
        "    for row in result:\n"
        "        print(row.category, row.n)     # attribute access by column name"
    ))

    c.append(md("""
### Recap

DB-API pattern: connect → cursor → execute → fetch; always use `?`
parameterization (never f-string SQL); `row_factory = sqlite3.Row` for dict-like
rows; `executemany` + `commit` for transactional bulk loads; SQLAlchemy `engine`
+ `text()` is the portable, pandas-friendly way most pipelines connect. That completes
**Track 2**. Next: **Track 3** opens with typing and validation.
"""))
    return c


def nb_17():
    c = []
    c.append(md("""
# 17 · Typing & Pydantic

**Track 3 begins: production-grade craft.** Dirty input is the norm. **Type hints** document intent; **`dataclass`**
structures records; **pydantic** *validates and coerces* them at the boundary of
your pipeline — turning messy dicts into trustworthy typed objects or clear
errors.
"""))

    c.append(md("""
## Type hints in depth

Annotations describe expected types without enforcing them at runtime. Use
`list[int]`, `dict[str, float]`, `str | None` (optional), and `typing` helpers.
They power editors, `mypy`, and pydantic.
"""))
    c.append(code(
        "def total_revenue(amounts: list[float], tax: float = 0.0) -> float:\n"
        "    return round(sum(amounts) * (1 + tax), 2)\n"
        "\n"
        "print(total_revenue([10.0, 20.5, 3.25], tax=0.1))\n"
        "print(total_revenue.__annotations__)\n"
        "\n"
        "def find_email(customer: dict) -> str | None:   # may return None\n"
        "    return customer.get('email') or None\n"
        "print(find_email({'email': ''}))"
    ))

    c.append(md("""
## `dataclass`: structure without validation

`@dataclass` gives you a typed record with `__init__`/`__repr__`/`__eq__` for
free — but it does **not** validate: a wrong type slips right through.
"""))
    c.append(code(
        "from dataclasses import dataclass\n"
        "\n"
        "@dataclass\n"
        "class OrderDC:\n"
        "    order_id: int\n"
        "    amount: float\n"
        "\n"
        "bad = OrderDC(order_id='not-an-int', amount='oops')   # no error!\n"
        "print(bad)   # dataclass trusts you"
    ))

    c.append(md("""
## pydantic: validation + coercion at the boundary

A pydantic `BaseModel` checks types and **coerces** where sensible (`'42'` →
`42`), applies constraints, and raises a detailed `ValidationError` on bad
data. This is exactly what you want when ingesting external records.
"""))
    c.append(code(
        "from pydantic import BaseModel, field_validator\n"
        "\n"
        "class Order(BaseModel):\n"
        "    order_id: int\n"
        "    amount: float\n"
        "    status: str\n"
        "\n"
        "    @field_validator('amount')\n"
        "    @classmethod\n"
        "    def non_negative(cls, v):\n"
        "        if v < 0:\n"
        "            raise ValueError('amount must be >= 0')\n"
        "        return v\n"
        "\n"
        "# strings get coerced to the declared types\n"
        "o = Order(order_id='1042', amount='89.90', status='completed')\n"
        "print(o)\n"
        "print('typed amount:', o.amount, type(o.amount))"
    ))

    c.append(md("""
## Catching bad records cleanly

In a pipeline you validate each incoming record, routing good ones onward and
bad ones to a dead-letter list with a readable reason — no silent corruption.
"""))
    c.append(code(
        "from pydantic import ValidationError\n"
        "\n"
        "incoming = [\n"
        "    {'order_id': 1, 'amount': 100, 'status': 'completed'},\n"
        "    {'order_id': 'x', 'amount': 5, 'status': 'completed'},   # bad id\n"
        "    {'order_id': 3, 'amount': -9, 'status': 'returned'},     # bad amount\n"
        "]\n"
        "good, rejected = [], []\n"
        "for rec in incoming:\n"
        "    try:\n"
        "        good.append(Order(**rec))\n"
        "    except ValidationError as e:\n"
        "        rejected.append((rec, e.errors()[0]['msg']))\n"
        "\n"
        "print('accepted:', len(good))\n"
        "for rec, why in rejected:\n"
        "    print('rejected', rec['order_id'], '->', why)"
    ))

    c.append(md("""
## Nested models & defaults

Models compose, so nested JSON validates in one shot; fields can have defaults
and optional types.
"""))
    c.append(code(
        "from pydantic import BaseModel\n"
        "\n"
        "class Payload(BaseModel):\n"
        "    path: str\n"
        "    qty: int = 0                 # default when absent\n"
        "\n"
        "class Event(BaseModel):\n"
        "    event_id: int\n"
        "    event_type: str\n"
        "    payload: Payload\n"
        "\n"
        "e = Event(event_id=1, event_type='add_to_cart',\n"
        "          payload={'path': '/cart', 'qty': '2'})\n"
        "print(e)\n"
        "print('nested qty:', e.payload.qty, type(e.payload.qty))"
    ))

    c.append(md("""
### Recap

Type hints document; `dataclass` structures but does not validate; pydantic
validates and coerces at the ingestion boundary, raising detailed errors you can
route to a dead-letter queue; models nest for JSON. Next: concurrency.
"""))
    return c


def nb_18():
    c = []
    c.append(md("""
# 18 · Concurrency: threads, processes, async

Pipelines wait a lot — on network, disk, databases. **Concurrency** overlaps
that waiting to go faster. The right tool depends on whether work is **I/O-bound**
(waiting) or **CPU-bound** (computing), and Python's **GIL** shapes the choice.
"""))

    c.append(md("""
## The GIL in one paragraph

CPython's **Global Interpreter Lock** lets only one thread execute Python
bytecode at a time. So threads **do not** speed up CPU-bound Python — but they
*do* help I/O-bound work, because a thread releases the GIL while waiting on the
network or disk. For CPU parallelism you use multiple **processes**.

Rule of thumb:
- **I/O-bound** (API calls, DB, files) → **threads** or **asyncio**
- **CPU-bound** (parsing, math, compression) → **multiprocessing**
"""))

    c.append(md("""
## Threads for I/O-bound work

Fetching many URLs is mostly waiting. A `ThreadPoolExecutor` runs the waits
concurrently. Here we simulate I/O with `time.sleep` and show the speedup.
"""))
    c.append(code(
        "import time\n"
        "from concurrent.futures import ThreadPoolExecutor\n"
        "\n"
        "def fetch(url):\n"
        "    time.sleep(0.1)          # pretend network latency\n"
        "    return f'{url}: 200 OK'\n"
        "\n"
        "urls = [f'/page/{i}' for i in range(10)]\n"
        "\n"
        "t0 = time.perf_counter()\n"
        "serial = [fetch(u) for u in urls]\n"
        "t1 = time.perf_counter()\n"
        "with ThreadPoolExecutor(max_workers=10) as pool:\n"
        "    parallel = list(pool.map(fetch, urls))\n"
        "t2 = time.perf_counter()\n"
        "\n"
        "print(f'serial:   {(t1 - t0):.2f}s')\n"
        "print(f'threaded: {(t2 - t1):.2f}s')\n"
        "print('same results:', serial == parallel)"
    ))

    c.append(md("""
## asyncio for high-concurrency I/O

`asyncio` runs thousands of I/O tasks on a single thread using an event loop —
lighter than threads for large fan-out (e.g. many API calls). You `await`
coroutines and launch them together with `asyncio.gather`.

> Notebooks already run an event loop, so we use top-level `await` directly
> (in a plain `.py` script you'd wrap the entry point in `asyncio.run(main())`).
"""))
    c.append(code(
        "import asyncio, time\n"
        "\n"
        "async def fetch_async(url):\n"
        "    await asyncio.sleep(0.1)     # non-blocking wait\n"
        "    return f'{url}: 200 OK'\n"
        "\n"
        "urls = [f'/page/{i}' for i in range(10)]\n"
        "t0 = time.perf_counter()\n"
        "results = await asyncio.gather(*(fetch_async(u) for u in urls))\n"
        "print(f'async gathered {len(results)} in {time.perf_counter() - t0:.2f}s')\n"
        "print(results[0])"
    ))

    c.append(md("""
## CPU-bound work → multiprocessing

For heavy computation, spread work across **processes** to use multiple cores
(each process has its own GIL). The code pattern with
`ProcessPoolExecutor` looks like this:

```python
from concurrent.futures import ProcessPoolExecutor

def heavy(n):
    return sum(i * i for i in range(n))   # CPU-bound

if __name__ == '__main__':               # required guard on Windows/macOS
    with ProcessPoolExecutor() as pool:
        results = list(pool.map(heavy, [10_000_00] * 8))
```

> We show this as code rather than running it in the notebook: on Windows/macOS
> the worker processes must **import** the target function (spawn start method),
> which doesn't work for functions defined in a notebook cell. Put such
> functions in a `.py` module and call them from a script — as the capstone
> does.
"""))
    c.append(code(
        "# Demonstrate the CPU function itself (single-process) so you see the work:\n"
        "import time\n"
        "def heavy(n):\n"
        "    return sum(i * i for i in range(n))\n"
        "\n"
        "t0 = time.perf_counter()\n"
        "res = [heavy(200_000) for _ in range(4)]\n"
        "print('computed', len(res), 'results in', round(time.perf_counter() - t0, 3), 's')\n"
        "print('sample:', res[0])"
    ))

    c.append(md("""
### Recap

The GIL means threads help **I/O-bound** work, not CPU-bound; use
`ThreadPoolExecutor` or `asyncio` for network/disk fan-out (asyncio scales to
huge concurrency on one thread); use `multiprocessing`/`ProcessPoolExecutor` for
CPU parallelism, keeping worker functions in importable modules. Next: logging,
config and CLIs.
"""))
    return c


def nb_19():
    c = []
    c.append(md("""
# 19 · Logging, Config & CLI

Production pipelines don't `print` — they **log**. They don't hard-code
secrets — they read **config** and **environment variables**. And they're
runnable from the command line with **arguments**. This notebook covers all
three.
"""))

    c.append(md("""
## Logging instead of print

`logging` gives you levels (`DEBUG` < `INFO` < `WARNING` < `ERROR`), timestamps,
and the ability to route output to files or services — without changing your
code. Configure once; call `logger.info(...)` everywhere.
"""))
    c.append(code(
        "import logging, sys\n"
        "\n"
        "logger = logging.getLogger('pipeline')\n"
        "logger.handlers.clear()\n"
        "logger.setLevel(logging.INFO)\n"
        "handler = logging.StreamHandler(sys.stdout)\n"
        "handler.setFormatter(logging.Formatter(\n"
        "    '%(asctime)s | %(levelname)-7s | %(name)s | %(message)s',\n"
        "    datefmt='%H:%M:%S'))\n"
        "logger.addHandler(handler)\n"
        "\n"
        "logger.debug('you will NOT see this (below INFO)')\n"
        "logger.info('extract started')\n"
        "logger.warning('3 rows had blank emails')\n"
        "logger.error('failed to reach source API')"
    ))

    c.append(md("""
## Log structured context

Include machine-readable context (row counts, table names) so logs are
searchable. In real systems you'd emit JSON logs; here we show rich messages.
"""))
    c.append(code(
        "rows, table = 1523, 'orders'\n"
        "logger.info('loaded rows=%d table=%s', rows, table)   # %-style args, lazy\n"
        "\n"
        "try:\n"
        "    1 / 0\n"
        "except ZeroDivisionError:\n"
        "    logger.exception('transform crashed')   # logs the full traceback"
    ))

    c.append(md("""
## Configuration & environment variables

Secrets (DB passwords, API keys) and environment-specific settings belong in the
**environment**, not code. `os.environ` reads them; `python-dotenv` loads a
local `.env` file in development. Provide sensible defaults.
"""))
    c.append(code(
        "import os\n"
        "\n"
        "# In real code: from dotenv import load_dotenv; load_dotenv()\n"
        "os.environ.setdefault('BATCH_SIZE', '1000')     # pretend it came from .env\n"
        "os.environ.setdefault('ENV', 'dev')\n"
        "\n"
        "batch_size = int(os.environ.get('BATCH_SIZE', '500'))\n"
        "env = os.environ.get('ENV', 'dev')\n"
        "db_url = os.environ.get('DATABASE_URL', 'sqlite:///data/retail.db')  # default\n"
        "print(f'env={env} batch_size={batch_size}')\n"
        "print('db_url:', db_url)"
    ))

    c.append(md("""
## A config object

Bundle settings into one typed object (a `dataclass` or pydantic
`BaseSettings`) so the rest of the code depends on a clean interface, not scattered
`os.environ` calls.
"""))
    c.append(code(
        "import os\n"
        "from dataclasses import dataclass\n"
        "\n"
        "@dataclass(frozen=True)\n"
        "class Config:\n"
        "    env: str\n"
        "    batch_size: int\n"
        "    db_url: str\n"
        "\n"
        "    @classmethod\n"
        "    def from_env(cls):\n"
        "        return cls(\n"
        "            env=os.environ.get('ENV', 'dev'),\n"
        "            batch_size=int(os.environ.get('BATCH_SIZE', '500')),\n"
        "            db_url=os.environ.get('DATABASE_URL', 'sqlite:///data/retail.db'),\n"
        "        )\n"
        "\n"
        "cfg = Config.from_env()\n"
        "print(cfg)"
    ))

    c.append(md("""
## Command-line arguments with `argparse`

A pipeline script should accept parameters (which date to run, dry-run, etc.).
`argparse` parses `sys.argv` and generates `--help` for free. Here we parse an
explicit list so it runs in a notebook; a real script omits the list and reads
the actual command line.
"""))
    c.append(code(
        "import argparse\n"
        "\n"
        "parser = argparse.ArgumentParser(description='Run the daily ETL')\n"
        "parser.add_argument('--date', required=True, help='YYYY-MM-DD to process')\n"
        "parser.add_argument('--dry-run', action='store_true', help='validate only')\n"
        "parser.add_argument('--batch-size', type=int, default=1000)\n"
        "\n"
        "args = parser.parse_args(['--date', '2024-06-01', '--dry-run'])\n"
        "print('date:', args.date)\n"
        "print('dry_run:', args.dry_run)\n"
        "print('batch_size:', args.batch_size)"
    ))

    c.append(md("""
### Recap

Use `logging` (levels, formatters, `logger.exception`) instead of `print`; read
secrets/settings from the environment with `python-dotenv` and defaults; wrap
them in a typed `Config`; expose parameters via `argparse`. Next: testing with
pytest.
"""))
    return c


def nb_20():
    c = []
    c.append(md("""
# 20 · Testing with pytest

Untested pipelines break silently and corrupt data. **Tests** encode what
"correct" means and catch regressions. `pytest` is the standard: plain `assert`
statements, powerful fixtures, and parametrization. We run tests inside the
notebook with `ipytest`.
"""))
    c.append(code(
        "import ipytest\n"
        "ipytest.autoconfig()\n"
        "print('ipytest ready')"
    ))

    c.append(md("""
## The function under test

Realistic testing means testing your **transforms**. Here's a small, pure
cleaning function — pure functions are the easiest and most valuable to test.
"""))
    c.append(code(
        "def clean_country(value):\n"
        "    '''Normalize a country code: strip, upper, blank -> UNKNOWN.'''\n"
        "    if value is None:\n"
        "        return 'UNKNOWN'\n"
        "    v = value.strip().upper()\n"
        "    return v or 'UNKNOWN'\n"
        "\n"
        "print(clean_country('  us '), '|', clean_country(''), '|', clean_country(None))"
    ))

    c.append(md("""
## Writing tests: just `assert`

A pytest test is a function named `test_*` containing `assert`s. `pytest`
introspects a failing assert to show exactly what differed.
"""))
    c.append(code(
        "%%ipytest\n"
        "\n"
        "def test_strips_and_uppercases():\n"
        "    assert clean_country('  us ') == 'US'\n"
        "\n"
        "def test_blank_becomes_unknown():\n"
        "    assert clean_country('') == 'UNKNOWN'\n"
        "\n"
        "def test_none_becomes_unknown():\n"
        "    assert clean_country(None) == 'UNKNOWN'"
    ))

    c.append(md("""
## Parametrize: many cases, one test

`@pytest.mark.parametrize` runs the same test over many input/output pairs —
concise coverage of edge cases.
"""))
    c.append(code(
        "%%ipytest\n"
        "\n"
        "import pytest\n"
        "\n"
        "@pytest.mark.parametrize('raw, expected', [\n"
        "    ('us', 'US'),\n"
        "    ('  GB', 'GB'),\n"
        "    ('de  ', 'DE'),\n"
        "    ('', 'UNKNOWN'),\n"
        "    (None, 'UNKNOWN'),\n"
        "])\n"
        "def test_clean_country(raw, expected):\n"
        "    assert clean_country(raw) == expected"
    ))

    c.append(md("""
## Fixtures: reusable test setup

A **fixture** builds shared test data or resources (sample rows, a temp
database) and hands it to any test that names it as an argument. This keeps
tests clean and isolated. Here the rows are plain dicts — the same idea applies
to a DataFrame or a database connection.
"""))
    c.append(code(
        "%%ipytest\n"
        "\n"
        "import pytest\n"
        "\n"
        "def revenue_by_status(rows):\n"
        "    return sum(r['amount'] for r in rows if r['status'] == 'completed')\n"
        "\n"
        "@pytest.fixture\n"
        "def sample_orders():\n"
        "    return [\n"
        "        {'amount': 100.0, 'status': 'completed'},\n"
        "        {'amount': 50.0, 'status': 'returned'},\n"
        "        {'amount': 25.0, 'status': 'completed'},\n"
        "    ]\n"
        "\n"
        "def test_revenue_only_counts_completed(sample_orders):\n"
        "    assert revenue_by_status(sample_orders) == 125.0\n"
        "\n"
        "def test_revenue_empty_is_zero():\n"
        "    assert revenue_by_status([]) == 0"
    ))

    c.append(md("""
## Testing that errors are raised

Assert that bad input raises the *right* exception with `pytest.raises` — as
important as testing the happy path.
"""))
    c.append(code(
        "%%ipytest\n"
        "\n"
        "import pytest\n"
        "\n"
        "def parse_amount(s):\n"
        "    value = float(s)\n"
        "    if value < 0:\n"
        "        raise ValueError('amount must be non-negative')\n"
        "    return value\n"
        "\n"
        "def test_rejects_negative():\n"
        "    with pytest.raises(ValueError):\n"
        "        parse_amount('-5')\n"
        "\n"
        "def test_rejects_garbage():\n"
        "    with pytest.raises(ValueError):\n"
        "        parse_amount('abc')"
    ))

    c.append(md("""
> **Running tests outside notebooks:** put tests in `tests/test_*.py` and run
> `uv run pytest` at the project root. The notebook uses `ipytest` only so the
> examples are self-contained.

### Recap

Tests are `test_*` functions with `assert`s; `parametrize` covers many cases;
fixtures supply reusable setup; `pytest.raises` checks error paths. Test your
pure transforms first — they carry the most risk. Next: performance and memory.
"""))
    return c


def nb_21():
    c = []
    c.append(md("""
# 21 · Performance & Memory

At scale, *how* you write Python matters. This notebook covers measuring before
optimizing, the generators-vs-lists memory tradeoff, chunking big files,
vectorization, and picking efficient data structures.
"""))
    c.append(DATA_BOOT)

    c.append(md("""
## Measure first

Never guess at performance — **profile**. `time.perf_counter` times a block;
`timeit` averages many runs for micro-benchmarks. Optimize the actual
bottleneck, not what you assume it is.
"""))
    c.append(code(
        "import timeit\n"
        "\n"
        "setup = 'data = list(range(1000))'\n"
        "loop = timeit.timeit('[x*2 for x in data]', setup=setup, number=10000)\n"
        "vec = timeit.timeit('list(map(lambda x: x*2, data))', setup=setup, number=10000)\n"
        "print(f'comprehension: {loop:.3f}s')\n"
        "print(f'map:           {vec:.3f}s')"
    ))

    c.append(md("""
## Generators vs lists: memory

A list holds every element at once; a generator holds one. For large
intermediate data, generators slash memory. `sys.getsizeof` shows the
difference in the container itself.
"""))
    c.append(code(
        "import sys\n"
        "\n"
        "big_list = [x for x in range(1_000_000)]      # materialized\n"
        "big_gen = (x for x in range(1_000_000))        # lazy\n"
        "print('list bytes:', sys.getsizeof(big_list))\n"
        "print('generator bytes:', sys.getsizeof(big_gen))\n"
        "print('sum via generator (no big list):', sum(x for x in range(1_000_000)))"
    ))

    c.append(md("""
## Chunking / streaming large files

When a file is too big for memory, process it in a **streaming** pass — read
one row at a time and aggregate incrementally, never holding the whole file in
memory. Here we stream the CSV with the standard library.
"""))
    c.append(code(
        "import csv\n"
        "\n"
        "total = 0.0\n"
        "rows = 0\n"
        "with open(RAW / 'orders.csv', encoding='utf-8', newline='') as f:\n"
        "    for row in csv.DictReader(f):        # one row in memory at a time\n"
        "        rows += 1\n"
        "        if row['status'] == 'completed':\n"
        "            total += float(row['amount'])\n"
        "print(f'streamed {rows} rows; revenue={total:,.2f}')"
    ))

    c.append(md("""
## Choose the right data structure

Membership tests are O(n) in a list but O(1) in a set/dict. For repeated lookups
against a large collection, this is the difference between fast and unusable.
"""))
    c.append(code(
        "import time\n"
        "\n"
        "big = list(range(200_000))\n"
        "as_set = set(big)\n"
        "targets = [199_999, -1, 100_000]\n"
        "\n"
        "t0 = time.perf_counter()\n"
        "for _ in range(1000):\n"
        "    _ = [t in big for t in targets]        # list: scans each time\n"
        "t1 = time.perf_counter()\n"
        "for _ in range(1000):\n"
        "    _ = [t in as_set for t in targets]     # set: hash lookup\n"
        "t2 = time.perf_counter()\n"
        "print(f'list membership: {(t1 - t0)*1000:.1f} ms')\n"
        "print(f'set  membership: {(t2 - t1)*1000:.1f} ms')"
    ))

    c.append(md("""
### Recap

Measure with `timeit`/`perf_counter` before optimizing; generators save memory
on large intermediates; stream big files a row at a time; use sets/dicts for
O(1) membership. That completes the **Python bootcamp** — you can write fast,
correct, production-grade Python. For dataframe wrangling (NumPy + pandas) and a
full ETL capstone, continue to the companion **pandas-numpy-bootcamp**.
"""))
    return c


# ===========================================================================
# 07 - Decorators
# ===========================================================================

def nb_decorators():
    c = []
    c.append(md("""
# 07 · Decorators

A **decorator** is a function that *wraps* another function to add behavior —
without changing the wrapped function's code. It builds directly on closures
(the functions notebook). In data engineering you'll use decorators constantly: `@retry`,
timing, caching, logging, and framework hooks like `@pytest.fixture` or
pydantic's `@field_validator`.
"""))

    c.append(md("""
## Functions are objects

The key idea that makes decorators possible: a function can be passed to another
function, returned, and assigned to a variable — just like any value.
"""))
    c.append(code(
        "def shout(text):\n"
        "    return text.upper() + '!'\n"
        "\n"
        "f = shout               # assign the function to another name\n"
        "print(f('etl'))\n"
        "\n"
        "def apply(fn, value):   # pass a function as an argument\n"
        "    return fn(value)\n"
        "print(apply(shout, 'load'))"
    ))

    c.append(md("""
## Writing a decorator

A decorator takes a function and returns a new function that calls the original
with extra behavior around it. The `@decorator` line above a `def` is just
sugar for `func = decorator(func)`.
"""))
    c.append(code(
        "def announce(fn):\n"
        "    def wrapper(*args, **kwargs):\n"
        "        print(f'-> calling {fn.__name__}')\n"
        "        result = fn(*args, **kwargs)\n"
        "        print(f'<- {fn.__name__} returned {result!r}')\n"
        "        return result\n"
        "    return wrapper\n"
        "\n"
        "@announce                       # same as: add = announce(add)\n"
        "def add(a, b):\n"
        "    return a + b\n"
        "\n"
        "add(3, 4)"
    ))

    c.append(md("""
## Preserve metadata with `functools.wraps`

The wrapper replaces the original, so `__name__` and the docstring get lost.
`@functools.wraps(fn)` copies them across — always use it, or debugging and
tooling break.
"""))
    c.append(code(
        "import functools\n"
        "\n"
        "def announce(fn):\n"
        "    @functools.wraps(fn)        # copy fn's name/docstring onto wrapper\n"
        "    def wrapper(*args, **kwargs):\n"
        "        return fn(*args, **kwargs)\n"
        "    return wrapper\n"
        "\n"
        "@announce\n"
        "def add(a, b):\n"
        "    'Add two numbers.'\n"
        "    return a + b\n"
        "\n"
        "print(add.__name__)      # 'add', not 'wrapper'\n"
        "print(add.__doc__)"
    ))

    c.append(md("""
## A practical decorator: timing

A `@timed` decorator measures how long any function takes — drop it on a
pipeline stage to profile it with zero code changes.
"""))
    c.append(code(
        "import functools, time\n"
        "\n"
        "def timed(fn):\n"
        "    @functools.wraps(fn)\n"
        "    def wrapper(*args, **kwargs):\n"
        "        start = time.perf_counter()\n"
        "        try:\n"
        "            return fn(*args, **kwargs)\n"
        "        finally:\n"
        "            ms = (time.perf_counter() - start) * 1000\n"
        "            print(f'{fn.__name__} took {ms:.1f} ms')\n"
        "    return wrapper\n"
        "\n"
        "@timed\n"
        "def crunch(n):\n"
        "    return sum(i * i for i in range(n))\n"
        "\n"
        "print('result:', crunch(500_000))"
    ))

    c.append(md("""
## Decorators that take arguments

To configure a decorator (e.g. how many times to retry), add one more layer: a
function that takes the arguments and *returns* the decorator. Here's a real
`@retry` — the single most common decorator in ingestion code.
"""))
    c.append(code(
        "import functools, time\n"
        "\n"
        "def retry(times=3, delay=0.01):\n"
        "    def decorator(fn):\n"
        "        @functools.wraps(fn)\n"
        "        def wrapper(*args, **kwargs):\n"
        "            for attempt in range(1, times + 1):\n"
        "                try:\n"
        "                    return fn(*args, **kwargs)\n"
        "                except Exception as e:\n"
        "                    print(f'attempt {attempt} failed: {e}')\n"
        "                    if attempt == times:\n"
        "                        raise\n"
        "                    time.sleep(delay)\n"
        "        return wrapper\n"
        "    return decorator\n"
        "\n"
        "_calls = {'n': 0}\n"
        "\n"
        "@retry(times=3)\n"
        "def flaky():\n"
        "    _calls['n'] += 1\n"
        "    if _calls['n'] < 3:\n"
        "        raise ConnectionError('transient')\n"
        "    return 'ok'\n"
        "\n"
        "print('final:', flaky())"
    ))

    c.append(md("""
## `functools.lru_cache` — a built-in decorator

The standard library ships useful decorators. `@lru_cache` memoizes results so
repeated calls with the same arguments are instant — handy for expensive lookups.
"""))
    c.append(code(
        "import functools\n"
        "\n"
        "@functools.lru_cache(maxsize=None)\n"
        "def slow_square(n):\n"
        "    print(f'  computing {n}...')\n"
        "    return n * n\n"
        "\n"
        "print(slow_square(12))   # computes\n"
        "print(slow_square(12))   # cached — no 'computing' line\n"
        "print(slow_square(5))    # computes"
    ))

    c.append(md("""
### Recap

A decorator wraps a function to add behavior via a closure; `@name` means
`func = name(func)`; use `functools.wraps` to keep the wrapped function's
identity; add an outer layer for decorators with arguments (`@retry(times=3)`);
`functools.lru_cache` is a ready-made memoizer. Next: iterators and generators.
"""))
    return c


# ===========================================================================
# 14 - Regular expressions
# ===========================================================================

def nb_regex():
    c = []
    c.append(md("""
# 14 · Regular Expressions

A **regular expression** (regex) is a mini-language for matching patterns in
text. When data isn't cleanly delimited — log lines, free-text fields, IDs
embedded in strings — regex is how you extract and validate it. Python's `re`
module is the tool.
"""))

    c.append(md("""
## Always use raw strings

Write patterns as **raw strings** (`r'...'`) so backslashes mean regex
metacharacters, not Python escapes. `\\d` = digit, `\\w` = word char, `\\s` =
whitespace; `+` = one or more, `*` = zero or more, `?` = optional.
"""))
    c.append(code(
        "import re\n"
        "\n"
        "text = 'Order ORD-2024-0042 shipped'\n"
        "m = re.search(r'ORD-\\d{4}-\\d{4}', text)   # find pattern anywhere\n"
        "print('found:', m.group())\n"
        "print('span :', m.span())"
    ))

    c.append(md("""
## `match` vs `search` vs `fullmatch` vs `findall`

- `match` — anchored at the **start** of the string
- `search` — anywhere in the string (most common)
- `fullmatch` — the **whole** string must match (great for validation)
- `findall` — every non-overlapping match, as a list
"""))
    c.append(code(
        "import re\n"
        "\n"
        "print(bool(re.match(r'\\d+', '42 apples')))       # True: starts with digits\n"
        "print(bool(re.match(r'\\d+', 'apples 42')))       # False: doesn't start\n"
        "print(bool(re.search(r'\\d+', 'apples 42')))      # True: found later\n"
        "print(bool(re.fullmatch(r'\\d{4}', '2024')))      # True: exactly 4 digits\n"
        "print(re.findall(r'\\d+', 'a1 b22 c333'))          # ['1', '22', '333']"
    ))

    c.append(md("""
## Capturing groups

Parentheses `(...)` **capture** parts of a match so you can pull out fields.
`group(0)` is the whole match; `group(1)`, `group(2)`, ... are the captures.
"""))
    c.append(code(
        "import re\n"
        "\n"
        "code = 'ORD-2024-0042'\n"
        "m = re.match(r'(\\w+)-(\\d{4})-(\\d+)', code)\n"
        "print('all groups:', m.groups())\n"
        "print('type :', m.group(1))\n"
        "print('year :', int(m.group(2)))\n"
        "print('seq  :', int(m.group(3)))"
    ))

    c.append(md("""
## Named groups (readable extraction)

`(?P<name>...)` names a capture so you access it by key — far clearer than
numeric positions when parsing structured text like log lines.
"""))
    c.append(code(
        "import re\n"
        "\n"
        "log = '2024-06-01 14:30:05 ERROR database timeout'\n"
        "pat = r'(?P<date>\\d{4}-\\d\\d-\\d\\d) (?P<time>\\d\\d:\\d\\d:\\d\\d) (?P<level>\\w+) (?P<msg>.*)'\n"
        "m = re.match(pat, log)\n"
        "print(m.group('level'), '->', m.group('msg'))\n"
        "print(m.groupdict())"
    ))

    c.append(md("""
## `sub` — find and replace / redact

`re.sub` replaces every match. Use it to clean, normalize, or **redact**
sensitive data (a common data-governance task).
"""))
    c.append(code(
        "import re\n"
        "\n"
        "messy = 'Phone:  555-123-4567 , Alt: 555.987.6543'\n"
        "digits_only = re.sub(r'[^0-9]', '', 'ID: 00-1234')      # strip non-digits\n"
        "print('cleaned id:', digits_only)\n"
        "\n"
        "redacted = re.sub(r'\\d{3}[-.]\\d{3}[-.]\\d{4}', '[REDACTED]', messy)\n"
        "print(redacted)"
    ))

    c.append(md("""
## Compile once, reuse many times

When applying the same pattern to many rows, `re.compile` it once — clearer and
faster in a hot loop.
"""))
    c.append(code(
        "import re\n"
        "\n"
        "email_re = re.compile(r'^[\\w.+-]+@[\\w-]+\\.[\\w.-]+$')\n"
        "\n"
        "for addr in ['ava.smith@example.com', 'not-an-email', 'x@y.z']:\n"
        "    print(f'{addr:25s} valid={bool(email_re.fullmatch(addr))}')"
    ))

    c.append(md("""
> **Keep regex readable.** For anything complex, add comments with
> `re.VERBOSE`, and remember: if the data is truly tabular, the `csv` module is
> safer than a regex. Reach for regex when structure lives *inside* a text field.

### Recap

`re` matches patterns in text; use raw strings (`r'...'`); `match`/`search`/
`fullmatch`/`findall` differ by where they anchor; `(...)` captures and
`(?P<name>...)` names captures; `sub` replaces/redacts; `compile` once for reuse.
Next: JSON and serialization.
"""))
    return c


# ===========================================================================
# 24 - Packaging & uv
# ===========================================================================

def nb_packaging():
    c = []
    c.append(md("""
# 24 · Packaging & Project Structure with `uv`

Notebooks are for learning; **real pipelines live in `.py` modules** inside a
proper project you can import, test, version and run. This notebook shows how a
Python project is laid out, how `uv` manages it, and builds a tiny importable
package live so the ideas are concrete.
"""))

    c.append(md("""
## The standard layout

A typical data project looks like this:

```
my-pipeline/
├── pyproject.toml        # project metadata + dependencies (uv reads this)
├── uv.lock               # exact pinned versions (commit this)
├── README.md
├── .python-version       # which Python uv should use
├── src/
│   └── my_pipeline/
│       ├── __init__.py   # marks the folder as an importable package
│       ├── extract.py
│       ├── transform.py
│       └── load.py
└── tests/
    └── test_transform.py
```

The `src/` layout keeps importable code separate from config and tests. A
folder becomes a **package** when it contains `__init__.py`.
"""))

    c.append(md("""
## What `pyproject.toml` declares

`pyproject.toml` is the modern standard (it replaces `requirements.txt` +
`setup.py`). It names the project, the required Python, and dependencies:

```toml
[project]
name = "my-pipeline"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "pandas>=2.1.0",
    "requests>=2.31.0",
]

[project.scripts]
run-pipeline = "my_pipeline.load:main"   # creates a CLI command
```
"""))

    c.append(md("""
## The `uv` workflow

`uv` is a fast, all-in-one project and environment manager. The commands you'll
actually use:

| Command | What it does |
|---|---|
| `uv init my-pipeline` | scaffold a new project |
| `uv add pandas requests` | add dependencies (updates `pyproject.toml` + lock) |
| `uv sync` | create/refresh the `.venv` from the lock file |
| `uv run python -m my_pipeline` | run code inside the managed environment |
| `uv run pytest` | run your tests in that environment |

`uv` creates an isolated `.venv` per project, so dependencies never collide
between projects — and `uv.lock` makes installs reproducible for everyone.
"""))

    c.append(md("""
## Build a package live

Let's create a minimal package on disk, then **import and use it** — proving how
modules and packages actually work.
"""))
    c.append(code(
        "import sys, tempfile, textwrap\n"
        "from pathlib import Path\n"
        "\n"
        "root = Path(tempfile.mkdtemp()) / 'demo_pkg_project' / 'src'\n"
        "pkg = root / 'demo_pipeline'\n"
        "pkg.mkdir(parents=True)\n"
        "\n"
        "(pkg / '__init__.py').write_text('')      # makes it a package\n"
        "(pkg / 'transform.py').write_text(textwrap.dedent('''\n"
        "    def clean_country(value):\n"
        "        \"\"\"Normalize a country code.\"\"\"\n"
        "        return (value or \"\").strip().upper() or \"UNKNOWN\"\n"
        "'''))\n"
        "print('created:', *(p.name for p in pkg.iterdir()))"
    ))
    c.append(code(
        "# Put src/ on the import path (uv/editable installs do this for you),\n"
        "# then import the package like any real dependency.\n"
        "sys.path.insert(0, str(root))\n"
        "from demo_pipeline.transform import clean_country\n"
        "\n"
        "print(clean_country('  us '))\n"
        "print(clean_country(''))"
    ))

    c.append(md("""
## Running as a module: `__main__`

Give a package a `__main__.py` (or a function referenced in
`[project.scripts]`) and it runs with `python -m package` or your CLI command —
the entry point a scheduler calls. Combine with `argparse` (the logging & CLI notebook) for
parameters.
"""))
    c.append(code(
        "import textwrap\n"
        "(pkg / '__main__.py').write_text(textwrap.dedent('''\n"
        "    from demo_pipeline.transform import clean_country\n"
        "    def main():\n"
        "        print(\"pipeline running:\", clean_country(\" gb \"))\n"
        "    if __name__ == \"__main__\":\n"
        "        main()\n"
        "'''))\n"
        "\n"
        "import subprocess, sys\n"
        "out = subprocess.run([sys.executable, '-m', 'demo_pipeline'],\n"
        "                     cwd=str(root), capture_output=True, text=True)\n"
        "print(out.stdout.strip() or out.stderr.strip())"
    ))

    c.append(md("""
### Recap

Real code lives in an importable **package** (`src/my_pkg/` with `__init__.py`),
configured by **`pyproject.toml`** and managed by **`uv`** (`uv add`, `uv sync`,
`uv run`); `uv.lock` pins versions for reproducibility; `python -m package` (or
a `[project.scripts]` entry point) is how a pipeline is launched. That completes
the **Python bootcamp** — you can write, structure, test and ship real Python.
For dataframe wrangling and a full ETL capstone, continue to the companion
**pandas-numpy-bootcamp**.
"""))
    return c


# ===========================================================================
# registry + main
# ===========================================================================

NOTEBOOKS = [
    ("00_setup_and_how_to_run.ipynb", nb_00),
    ("01_variables_and_types.ipynb", nb_01),
    ("02_numbers_and_strings.ipynb", nb_02),
    ("03_collections.ipynb", nb_03),
    ("04_control_flow.ipynb", nb_04),
    ("05_comprehensions.ipynb", nb_05),
    ("06_functions.ipynb", nb_06),
    ("07_decorators.ipynb", nb_decorators),
    ("08_iterators_and_generators.ipynb", nb_07),
    ("09_modules_and_stdlib.ipynb", nb_08),
    ("10_oop.ipynb", nb_09),
    ("11_errors_and_context_managers.ipynb", nb_10),
    ("12_files_and_pathlib.ipynb", nb_11),
    ("13_csv_and_delimited.ipynb", nb_12),
    ("14_regex.ipynb", nb_regex),
    ("15_json_and_serialization.ipynb", nb_13),
    ("16_dates_and_times.ipynb", nb_14),
    ("17_apis_and_http.ipynb", nb_15),
    ("18_databases_with_python.ipynb", nb_16),
    ("19_typing_and_pydantic.ipynb", nb_17),
    ("20_concurrency.ipynb", nb_18),
    ("21_logging_config_cli.ipynb", nb_19),
    ("22_testing_with_pytest.ipynb", nb_20),
    ("23_performance_and_memory.ipynb", nb_21),
    ("24_packaging_and_uv.ipynb", nb_packaging),
]


def main() -> None:
    os.makedirs(NB_DIR, exist_ok=True)
    for filename, builder in NOTEBOOKS:
        write_nb(filename, builder())
    print(f"\nDone: wrote {len(NOTEBOOKS)} notebooks to {NB_DIR}")


if __name__ == "__main__":
    main()
