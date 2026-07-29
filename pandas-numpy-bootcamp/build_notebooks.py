"""
Generator for the pandas & NumPy Bootcamp notebooks.

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


def nb_00():
    c = []
    c.append(md('''
# 00 · Setup & How to Run

Welcome to the **pandas & NumPy Bootcamp** (data-engineering focus) 📊

This course teaches **dataframe wrangling** — the daily work of transforming and
analysing tabular data in Python. It is the companion to the **Python Bootcamp**;
if you are new to Python, do that one first (at least Track 1). Here we assume you
can read Python and want to master **NumPy** and **pandas**.

Like its sibling, every notebook is explanation-first: a concept, then runnable
sample code that prints a result. Run every cell and experiment.
'''))
    c.append(md('''
## What you\'ll learn (7 notebooks)

| # | Notebook | Topics |
|---|----------|--------|
| 00 | `setup_and_how_to_run` | environment check, the sample data |
| 01 | `numpy_foundations` | `ndarray`, vectorization, broadcasting, boolean masks |
| 02 | `pandas_fundamentals` | `Series`/`DataFrame`, IO, selecting, deriving columns |
| 03 | `pandas_transform` | `groupby`, `merge`, reshape, cleaning, missing data |
| 04 | `pandas_timeseries` | datetime index, resampling, rolling windows, shifting |
| 05 | `file_formats_parquet` | columnar storage, compression, partitioning (PyArrow) |
| 06 | `capstone_etl_pipeline` | a full extract → validate → transform → load pipeline |

> The capstone validates with **pydantic**, which is taught in the Python
> bootcamp\'s typing notebook — a quick read if it is new to you.
'''))
    c.append(md('''
## The sample data

The same fictional retail company as the other bootcamps, delivered as raw files.
If the next cell errors, run `uv run python data/build_data.py` in a terminal
first.
'''))
    c.append(DATA_BOOT)
    c.append(md('''
## A 30-second taste

NumPy and pandas operate on whole columns at once — no loops. Here is the
flavour; the notebooks explain every piece.
'''))
    c.append(code(
        "import numpy as np, pandas as pd\n"
        "\n"
        "prices = np.array([19.99, 5.0, 120.0])\n"
        "print('with tax:', np.round(prices * 1.2, 2))     # vectorized, no loop\n"
        "\n"
        "df = pd.read_csv(RAW / 'orders.csv')\n"
        "print('orders:', len(df))\n"
        "print(df.groupby('status')['amount'].sum().round(2))"
    ))
    c.append(md('''
Work through the notebooks in order. Onward to `01_numpy_foundations`. 🚀
'''))
    return c


def nb_01():
    c = []
    c.append(md("""
# 01 · NumPy Foundations

**NumPy** is the numerical core under pandas and most of the data stack. Its
`ndarray` stores numbers in a compact, contiguous block and runs operations in
fast C loops — **vectorization**. Understanding it explains *why* pandas is fast
and how to avoid slow Python loops.
"""))

    c.append(md("""
## Arrays vs lists

A NumPy array holds one dtype and supports element-wise math directly. The same
operation on a Python list needs a loop or comprehension.
"""))
    c.append(code(
        "import numpy as np\n"
        "\n"
        "prices = np.array([19.99, 5.0, 120.0, 3.5])\n"
        "print('array:', prices, '| dtype:', prices.dtype)\n"
        "\n"
        "# vectorized: no loop, applies to every element\n"
        "with_tax = prices * 1.2\n"
        "print('with tax:', np.round(with_tax, 2))\n"
        "print('sum:', prices.sum(), '| mean:', prices.mean(), '| max:', prices.max())"
    ))

    c.append(md("""
## Why vectorization matters (speed)

The same computation, loop vs vectorized. On big arrays the vectorized version
is often 10–100x faster because it avoids per-element Python overhead.
"""))
    c.append(code(
        "import numpy as np, time\n"
        "\n"
        "n = 1_000_000\n"
        "data = np.arange(n, dtype='float64')\n"
        "\n"
        "t0 = time.perf_counter()\n"
        "loop_total = 0.0\n"
        "for x in data.tolist():\n"
        "    loop_total += x * 2\n"
        "t1 = time.perf_counter()\n"
        "vec_total = (data * 2).sum()\n"
        "t2 = time.perf_counter()\n"
        "\n"
        "print(f'loop:       {(t1 - t0)*1000:7.1f} ms')\n"
        "print(f'vectorized: {(t2 - t1)*1000:7.1f} ms')\n"
        "print('same result:', round(loop_total, 1) == round(vec_total, 1))"
    ))

    c.append(md("""
## Boolean masks & filtering

Comparisons produce boolean arrays you can use to select elements — the engine
behind pandas filtering (`df[df.amount > 100]`).
"""))
    c.append(code(
        "import numpy as np\n"
        "amounts = np.array([120, -5, 89, 0, 240, -12, 60])\n"
        "\n"
        "mask = amounts > 0\n"
        "print('mask:', mask)\n"
        "print('valid values:', amounts[mask])\n"
        "print('count valid:', mask.sum())          # True == 1\n"
        "print('mean of valid:', amounts[mask].mean())\n"
        "\n"
        "# np.where: vectorized if/else\n"
        "labels = np.where(amounts >= 100, 'big', 'small')\n"
        "print('labels:', labels)"
    ))

    c.append(md("""
## Broadcasting

NumPy stretches shapes so arrays of different sizes combine without explicit
loops. A scalar applies to every element; a row vector applies across each row.
"""))
    c.append(code(
        "import numpy as np\n"
        "\n"
        "matrix = np.array([[1, 2, 3],\n"
        "                   [4, 5, 6]])\n"
        "print('add scalar 10:\\n', matrix + 10)\n"
        "\n"
        "col_weights = np.array([1.0, 0.5, 2.0])   # one weight per column\n"
        "print('weighted columns:\\n', matrix * col_weights)   # broadcast across rows"
    ))

    c.append(md("""
## Aggregations along axes

2-D arrays aggregate by row (`axis=1`) or column (`axis=0`) — the mental model
for pandas `groupby` reductions.
"""))
    c.append(code(
        "import numpy as np\n"
        "sales = np.array([[100, 120, 90],     # product A over 3 days\n"
        "                  [ 40,  35, 60]])    # product B over 3 days\n"
        "print('total per product (axis=1):', sales.sum(axis=1))\n"
        "print('total per day     (axis=0):', sales.sum(axis=0))\n"
        "print('grand total:', sales.sum())"
    ))

    c.append(md("""
### Recap

`ndarray` is compact and typed; vectorized operations replace Python loops and
run far faster; boolean masks filter; broadcasting combines mismatched shapes;
`axis=0/1` aggregates columns/rows. This is the machinery under pandas — up
next.
"""))
    return c


def nb_02():
    c = []
    c.append(md("""
# 02 · pandas Fundamentals

**pandas** is the workhorse of Python data engineering: a `DataFrame` is a typed,
labeled table you can filter, transform and aggregate with concise code. This
notebook loads the raw files and covers selecting, filtering and deriving
columns.
"""))
    c.append(DATA_BOOT)

    c.append(md("""
## Reading data into a DataFrame

`read_csv` infers types and returns a `DataFrame`. `head`, `shape`, `dtypes` and
`info` are your first look at any dataset.
"""))
    c.append(code(
        "import pandas as pd\n"
        "\n"
        "orders = pd.read_csv(RAW / 'orders.csv', parse_dates=['order_ts'])\n"
        "print('shape:', orders.shape)\n"
        "print('dtypes:\\n', orders.dtypes)\n"
        "orders.head()"
    ))

    c.append(md("""
## Series vs DataFrame

A **column** is a `Series` (a labeled 1-D array, NumPy underneath). A
**DataFrame** is a dict-like collection of aligned Series sharing an index.
"""))
    c.append(code(
        "amounts = orders['amount']          # a Series\n"
        "print(type(amounts))\n"
        "print(amounts.describe())           # count/mean/std/min/quartiles/max"
    ))

    c.append(md("""
## Selecting columns and rows

Select columns by name; select rows by boolean condition (the pandas equivalent
of the NumPy masks from notebook 01). `.loc` selects by label, `.iloc` by
position.
"""))
    c.append(code(
        "# columns\n"
        "print(orders[['order_id', 'amount']].head(3))\n"
        "print('---')\n"
        "# rows by position\n"
        "print(orders.iloc[0])\n"
        "print('--- big completed orders ---')\n"
        "# rows by condition\n"
        "big = orders[(orders['amount'] >= 200) & (orders['status'] == 'completed')]\n"
        "print(big[['order_id', 'amount', 'status']].head())"
    ))

    c.append(md("""
## Deriving new columns (vectorized)

Assign a new column from an expression over existing ones — applied to the whole
column at once, no loop. `np.where` and `.dt`/`.str` accessors handle
conditionals, dates and text.
"""))
    c.append(code(
        "import numpy as np\n"
        "\n"
        "orders['amount_tier'] = np.where(orders['amount'] >= 200, 'big', 'small')\n"
        "orders['order_month'] = orders['order_ts'].dt.to_period('M').astype(str)\n"
        "orders['is_completed'] = orders['status'].eq('completed')\n"
        "print(orders[['order_id', 'amount', 'amount_tier', 'order_month', 'is_completed']].head())"
    ))

    c.append(md("""
## Quick aggregations

Series methods give instant summaries; `value_counts` tallies categories.
"""))
    c.append(code(
        "print('total revenue:', round(orders.loc[orders.is_completed, 'amount'].sum(), 2))\n"
        "print('avg order:', round(orders['amount'].mean(), 2))\n"
        "print('\\nstatus counts:')\n"
        "print(orders['status'].value_counts())"
    ))

    c.append(md("""
## Reading from SQL directly

`pandas.read_sql` runs a query against a SQLAlchemy engine and returns a
DataFrame — the bridge between the database module and analysis.
"""))
    c.append(code(
        "import pandas as pd\n"
        "from sqlalchemy import create_engine\n"
        "\n"
        "engine = create_engine(f'sqlite:///{DATA / \"retail.db\"}')\n"
        "products = pd.read_sql('SELECT * FROM products', engine)\n"
        "print(products.shape)\n"
        "products.head()"
    ))

    c.append(md("""
## `.loc` vs `.iloc` — label vs position

Two explicit selectors you'll use constantly:

- **`.loc[rows, cols]`** selects by **label** (index values and column names)
  and is **inclusive** of the end in a slice.
- **`.iloc[rows, cols]`** selects by **integer position** (0-based, end
  exclusive, like normal Python slicing).

Being explicit avoids the ambiguity of chained `[]` indexing.
"""))
    c.append(code(
        "# .iloc — by position\n"
        "print('first row, first 3 cols:')\n"
        "print(orders.iloc[0, :3])\n"
        "print('rows 0-2, columns 0 and 4:')\n"
        "print(orders.iloc[0:3, [0, 4]])\n"
        "\n"
        "# .loc — by label + boolean mask, selecting specific columns\n"
        "print('\\nbig completed orders (label-based):')\n"
        "print(orders.loc[orders['amount'] >= 200, ['order_id', 'amount', 'status']].head(3))"
    ))

    c.append(md("""
## Categorical dtype — memory & speed

A column with few distinct values (status, country, category) stored as
`category` uses far less memory and speeds up grouping — pandas stores each label
once and keeps small integer codes per row. A key optimization on large tables.
"""))
    c.append(code(
        "before = orders['status'].memory_usage(deep=True)\n"
        "orders['status'] = orders['status'].astype('category')\n"
        "after = orders['status'].memory_usage(deep=True)\n"
        "print('dtype now:', orders['status'].dtype)\n"
        "print('categories:', list(orders['status'].cat.categories))\n"
        "print(f'memory: {before} -> {after} bytes')"
    ))

    c.append(md("""
### Recap

`read_csv`/`read_sql` load tables; a column is a `Series`, a table a
`DataFrame`; select columns by name and rows by boolean mask; `.loc` is
label-based (end-inclusive), `.iloc` position-based (end-exclusive); derive
columns vectorized with `np.where` and `.dt`/`.str`; `describe`/`value_counts`
summarize; `category` dtype saves memory on low-cardinality columns. Next:
grouping, joining and reshaping.
"""))
    return c


def nb_03():
    c = []
    c.append(md("""
# 03 · pandas Transform: groupby, join, reshape, clean

The heart of ELT in pandas: aggregate with `groupby`, combine tables with
`merge`, reshape with `pivot`/`melt`, and clean missing/dirty values. These four
skills cover most transformation work.
"""))
    c.append(DATA_BOOT)

    c.append(code(
        "import pandas as pd, numpy as np\n"
        "orders = pd.read_csv(RAW / 'orders.csv', parse_dates=['order_ts'])\n"
        "customers = pd.read_csv(RAW / 'customers.csv')\n"
        "items = pd.read_csv(RAW / 'order_items.csv')\n"
        "products = pd.read_csv(RAW / 'products.csv')\n"
        "print('loaded:', orders.shape, customers.shape, items.shape, products.shape)"
    ))

    c.append(md("""
## `groupby` — split, apply, combine

Group rows by a key, compute an aggregate per group, get a result table. `agg`
runs several aggregations at once and names the outputs.
"""))
    c.append(code(
        "by_status = (orders\n"
        "    .groupby('status')\n"
        "    .agg(n_orders=('order_id', 'count'),\n"
        "         revenue=('amount', 'sum'),\n"
        "         avg_amount=('amount', 'mean'))\n"
        "    .round(2)\n"
        "    .reset_index())\n"
        "print(by_status)"
    ))

    c.append(md("""
## Cleaning dirty data first

The `customers` file is deliberately messy: inconsistent country casing and some
blank emails. Clean before joining, or your groups will split (`US` vs `us`).
"""))
    c.append(code(
        "print('before:', sorted(customers['country'].unique()))\n"
        "\n"
        "customers['country'] = customers['country'].str.strip().str.upper()\n"
        "# treat blank emails as missing and flag them\n"
        "customers['email'] = customers['email'].replace('', np.nan)\n"
        "customers['has_email'] = customers['email'].notna()\n"
        "\n"
        "print('after :', sorted(customers['country'].unique()))\n"
        "print('missing emails:', int((~customers['has_email']).sum()))"
    ))

    c.append(md("""
## `merge` — SQL-style joins

Combine tables on a key. `how=` picks the join type (`inner`, `left`, `right`,
`outer`) exactly like SQL. Here we attach each order's customer country.
"""))
    c.append(code(
        "orders_enriched = orders.merge(\n"
        "    customers[['customer_id', 'country']],\n"
        "    on='customer_id', how='left')\n"
        "\n"
        "revenue_by_country = (orders_enriched\n"
        "    .query(\"status == 'completed'\")\n"
        "    .groupby('country')['amount'].sum()\n"
        "    .round(2).sort_values(ascending=False))\n"
        "print(revenue_by_country)"
    ))

    c.append(md("""
## Multi-table join + line-item revenue

Real metrics span several tables. Join line items to products to get category
revenue — the kind of star-schema roll-up you build constantly.
"""))
    c.append(code(
        "line_rev = items.merge(products, on='product_id', how='left')\n"
        "line_rev['line_amount'] = line_rev['quantity'] * line_rev['unit_price_x']\n"
        "\n"
        "by_category = (line_rev\n"
        "    .groupby('category')['line_amount'].sum()\n"
        "    .round(2).sort_values(ascending=False))\n"
        "print(by_category)"
    ))

    c.append(md("""
## Reshaping: `pivot_table` and `melt`

**Wide** vs **long** format. `pivot_table` spreads a key into columns (great for
reports); `melt` collapses columns back into rows (great for tidy storage).
"""))
    c.append(code(
        "orders_enriched['month'] = orders_enriched['order_ts'].dt.to_period('M').astype(str)\n"
        "wide = pd.pivot_table(\n"
        "    orders_enriched.query(\"status == 'completed'\"),\n"
        "    index='country', columns=None, values='amount',\n"
        "    aggfunc='sum', fill_value=0).round(0)\n"
        "print('pivot (revenue by country):')\n"
        "print(wide.head())\n"
        "\n"
        "long = wide.reset_index().melt(id_vars='country', value_name='revenue')\n"
        "print('\\nmelted back to long:')\n"
        "print(long.head())"
    ))

    c.append(md("""
## Handling missing values

`isna`, `fillna`, `dropna` are the core tools. Decide per column whether missing
means drop, fill with a default, or flag.
"""))
    c.append(code(
        "print('nulls per column:\\n', customers.isna().sum())\n"
        "filled = customers.assign(email=customers['email'].fillna('UNKNOWN'))\n"
        "print('\\nafter fillna, nulls:', int(filled['email'].isna().sum()))"
    ))

    c.append(md("""
## `apply` and `map` — custom functions

When a transformation isn't a built-in vectorized op, `map` applies a function
element-wise to a **Series**, and `apply` applies one along a **DataFrame**'s
rows or columns. Prefer vectorized operations when you can (they're faster), but
these handle the arbitrary cases.
"""))
    c.append(code(
        "# map: element-wise on a Series (here, bucket each amount)\n"
        "orders['band'] = orders['amount'].map(\n"
        "    lambda a: 'high' if a >= 200 else 'mid' if a >= 50 else 'low')\n"
        "print(orders['band'].value_counts())\n"
        "\n"
        "# apply along rows (axis=1): combine several columns per row\n"
        "def label(row):\n"
        "    return f\"{row['status'][:4]}:{row['band']}\"\n"
        "orders['tag'] = orders.apply(label, axis=1)\n"
        "print(orders[['amount', 'status', 'band', 'tag']].head())"
    ))

    c.append(md("""
## `concat` — stacking DataFrames

`merge` joins tables *side by side* on a key; `concat` **stacks** them — rows on
top of each other (same columns) or columns beside each other (same index).
Stacking rows is how you union daily files or append a new batch.
"""))
    c.append(code(
        "jan = orders[orders['order_ts'].dt.month == 1].head(2)\n"
        "feb = orders[orders['order_ts'].dt.month == 2].head(2)\n"
        "\n"
        "stacked = pd.concat([jan, feb], ignore_index=True)   # union rows\n"
        "print('rows:', len(jan), '+', len(feb), '->', len(stacked))\n"
        "print(stacked[['order_id', 'order_ts', 'amount']])"
    ))

    c.append(md("""
## Duplicates: `duplicated` and `drop_duplicates`

Duplicate rows creep in from re-runs and bad joins. `duplicated` flags them;
`drop_duplicates` removes them. Use `subset=` to define "duplicate" by specific
columns and `keep=` to choose which copy to keep — essential for idempotent
loads.
"""))
    c.append(code(
        "raw = pd.DataFrame({\n"
        "    'customer_id': [1, 1, 2, 2, 2],\n"
        "    'email': ['a@x.com', 'a@x.com', 'b@x.com', 'b@x.com', 'b2@x.com'],\n"
        "})\n"
        "print('duplicated rows:', raw.duplicated().sum())\n"
        "print('after drop_duplicates:')\n"
        "print(raw.drop_duplicates())\n"
        "print('\\none row per customer (keep last):')\n"
        "print(raw.drop_duplicates(subset='customer_id', keep='last'))"
    ))

    c.append(md("""
### Recap

`groupby().agg()` is split-apply-combine; clean keys (casing, blanks) before
joining; `merge(how=...)` does SQL joins; chain joins for star-schema roll-ups;
`pivot_table`/`melt` switch wide↔long; `isna`/`fillna`/`dropna` handle missing
data; `map`/`apply` run custom functions; `concat` stacks frames;
`drop_duplicates` dedups for idempotent loads. Next: time-series operations.
"""))
    return c


def nb_04():
    c = []
    c.append(md("""
# 04 · pandas Time Series

Most data engineering is time-oriented: daily loads, monthly revenue, rolling
averages. pandas has first-class time-series support built on a **datetime
index**. This notebook covers resampling, rolling windows and shifting.
"""))
    c.append(DATA_BOOT)

    c.append(code(
        "import pandas as pd\n"
        "orders = pd.read_csv(RAW / 'orders.csv', parse_dates=['order_ts'])\n"
        "orders = orders[orders['status'] == 'completed'].copy()\n"
        "print('completed orders:', len(orders))\n"
        "print('date range:', orders['order_ts'].min(), '->', orders['order_ts'].max())"
    ))

    c.append(md("""
## A datetime index

Setting the timestamp as the index unlocks time-based selection and resampling.
Once indexed by time, you can slice by date strings directly.
"""))
    c.append(code(
        "ts = orders.set_index('order_ts').sort_index()\n"
        "print(ts.loc['2024-03', 'amount'].sum().round(2), 'revenue in March 2024')\n"
        "print(ts.loc['2024-03-01':'2024-03-07', 'amount'].count(), 'orders in first week of March')"
    ))

    c.append(md("""
## Resampling: change the time grain

`resample` is `groupby` for time — roll rows up to daily, weekly, monthly
buckets. `'D'`, `'W'`, `'ME'` (month-end) are common rules.
"""))
    c.append(code(
        "monthly = ts['amount'].resample('ME').agg(['sum', 'count', 'mean']).round(2)\n"
        "print('monthly revenue:')\n"
        "print(monthly.head())"
    ))

    c.append(md("""
## Rolling windows (moving averages)

A **rolling** window smooths noisy series — e.g. a 7-day moving average of daily
revenue. This is a staple of dashboards and anomaly detection.
"""))
    c.append(code(
        "daily = ts['amount'].resample('D').sum()\n"
        "rolling = daily.rolling(window=7, min_periods=1).mean().round(2)\n"
        "compare = pd.DataFrame({'daily': daily, 'ma_7d': rolling})\n"
        "print(compare.head(10))"
    ))

    c.append(md("""
## Shifting & period-over-period change

`shift` moves values by N periods so you can compare each period to the previous
one — the basis of month-over-month growth metrics.
"""))
    c.append(code(
        "mom = monthly[['sum']].rename(columns={'sum': 'revenue'})\n"
        "mom['prev'] = mom['revenue'].shift(1)\n"
        "mom['mom_pct'] = ((mom['revenue'] - mom['prev']) / mom['prev'] * 100).round(1)\n"
        "print(mom.head())"
    ))

    c.append(md("""
### Recap

A datetime index enables time slicing; `resample` rolls rows to a coarser grain
(`D`/`W`/`ME`); `rolling` computes moving averages; `shift` powers
period-over-period change. Next: columnar file formats and Parquet.
"""))
    return c


def nb_05():
    c = []
    c.append(md("""
# 05 · File Formats & Parquet

CSV is human-readable but
slow, untyped and bulky. **Parquet** is the standard for analytical data:
**columnar**, **compressed**, and **typed**. This notebook shows the difference
and how to read/write Parquet with PyArrow and pandas.
"""))
    c.append(DATA_BOOT)

    c.append(md("""
## Row vs columnar storage

CSV stores data **row by row**. Parquet stores it **column by column**, so a
query touching 2 of 20 columns reads only those 2, and each column compresses
well because similar values sit together. That's why analytics engines love it.
"""))
    c.append(code(
        "import pandas as pd\n"
        "orders = pd.read_csv(RAW / 'orders.csv', parse_dates=['order_ts'])\n"
        "print(orders.dtypes)\n"
        "print('rows:', len(orders))"
    ))

    c.append(md("""
## Write & read Parquet

pandas reads/writes Parquet via PyArrow in one call. Types (dates, ints, floats)
are preserved exactly — no re-parsing strings like CSV.
"""))
    c.append(code(
        "out_dir = DATA / 'warehouse'\n"
        "out_dir.mkdir(parents=True, exist_ok=True)\n"
        "pq_path = out_dir / 'orders.parquet'\n"
        "\n"
        "orders.to_parquet(pq_path, engine='pyarrow', compression='snappy')\n"
        "back = pd.read_parquet(pq_path)\n"
        "print('types preserved:', back['order_ts'].dtype)   # still datetime64\n"
        "print('rows:', len(back))"
    ))

    c.append(md("""
## Size comparison

On real data Parquet is typically several times smaller than CSV. Even on this
tiny sample you can see the effect (and the gap widens with scale).
"""))
    c.append(code(
        "csv_path = RAW / 'orders.csv'\n"
        "csv_bytes = csv_path.stat().st_size\n"
        "pq_bytes = pq_path.stat().st_size\n"
        "print(f'CSV:     {csv_bytes:>7} bytes')\n"
        "print(f'Parquet: {pq_bytes:>7} bytes')\n"
        "print(f'ratio:   {csv_bytes / pq_bytes:.2f}x')"
    ))

    c.append(md("""
## Column pruning

Reading only the columns you need is a big speed win with columnar files. Pass
`columns=` to skip the rest entirely at the storage layer.
"""))
    c.append(code(
        "slim = pd.read_parquet(pq_path, columns=['order_id', 'amount'])\n"
        "print(slim.columns.tolist())\n"
        "print('total:', round(slim['amount'].sum(), 2))"
    ))

    c.append(md("""
## Partitioning

Splitting output into folders by a key (e.g. `status=`) lets engines skip whole
partitions — **partition pruning**. PyArrow writes a partitioned dataset; the
partition value becomes a folder, not a stored column.
"""))
    c.append(code(
        "import pyarrow as pa\n"
        "import pyarrow.parquet as pq\n"
        "\n"
        "table = pa.Table.from_pandas(orders)\n"
        "dataset_dir = out_dir / 'orders_by_status'\n"
        "pq.write_to_dataset(table, root_path=str(dataset_dir), partition_cols=['status'])\n"
        "\n"
        "from pathlib import Path\n"
        "print('partitions written:')\n"
        "for p in sorted(Path(dataset_dir).glob('status=*')):\n"
        "    print(' ', p.name)\n"
        "\n"
        "# reading back can filter to one partition cheaply\n"
        "completed = pd.read_parquet(dataset_dir, filters=[('status', '==', 'completed')])\n"
        "print('completed rows read:', len(completed))"
    ))

    c.append(md("""
## Inspecting metadata without reading data

Parquet stores a schema and row-group statistics in its footer. You can read the
schema and row count **without** loading the data — handy for validation.
"""))
    c.append(code(
        "import pyarrow.parquet as pq\n"
        "meta = pq.read_metadata(pq_path)\n"
        "print('num_rows:', meta.num_rows)\n"
        "print('num_columns:', meta.num_columns)\n"
        "print('schema:\\n', pq.read_schema(pq_path))"
    ))

    c.append(md("""
### Recap

Parquet is columnar, compressed and typed — the analytics default; pandas
reads/writes it via PyArrow with types preserved; `columns=` prunes columns and
partitioning prunes rows; footer metadata gives schema/row-count without a full
read. Next: the capstone ETL pipeline that ties it all together.
"""))
    return c


def nb_06():
    c = []
    c.append(md("""
# 06 · Capstone: A Full ETL Pipeline

Time to combine everything into one small but **production-shaped** pipeline:

**Extract** raw CSV/JSONL → **Validate** with pydantic → **Transform** with
pandas → **Load** to Parquet + SQLite, with **logging**, **idempotency**, and a
**test**. This is the shape of real data-engineering code.
"""))
    c.append(DATA_BOOT)

    c.append(md("""
## 1. Logging setup

Every run should be observable. We configure a logger once and use it through
each stage.
"""))
    c.append(code(
        "import logging, sys\n"
        "logger = logging.getLogger('capstone')\n"
        "logger.handlers.clear()\n"
        "logger.setLevel(logging.INFO)\n"
        "h = logging.StreamHandler(sys.stdout)\n"
        "h.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-5s | %(message)s',\n"
        "                                 datefmt='%H:%M:%S'))\n"
        "logger.addHandler(h)\n"
        "logger.info('pipeline configured')"
    ))

    c.append(md("""
## 2. Extract

Read the raw orders and customers. Extraction just *gets bytes into memory* —
no business logic yet.
"""))
    c.append(code(
        "import pandas as pd\n"
        "\n"
        "def extract():\n"
        "    orders = pd.read_csv(RAW / 'orders.csv', parse_dates=['order_ts'])\n"
        "    customers = pd.read_csv(RAW / 'customers.csv')\n"
        "    logger.info('extracted orders=%d customers=%d', len(orders), len(customers))\n"
        "    return orders, customers\n"
        "\n"
        "orders, customers = extract()\n"
        "orders.head(3)"
    ))

    c.append(md("""
## 3. Validate

Enforce data quality at the boundary. We validate order rows with pydantic,
separating good records from a **dead-letter** list — bad data never silently
enters the warehouse.
"""))
    c.append(code(
        "from pydantic import BaseModel, ValidationError, field_validator\n"
        "\n"
        "class OrderRow(BaseModel):\n"
        "    order_id: int\n"
        "    customer_id: int\n"
        "    status: str\n"
        "    amount: float\n"
        "\n"
        "    @field_validator('amount')\n"
        "    @classmethod\n"
        "    def non_negative(cls, v):\n"
        "        if v < 0:\n"
        "            raise ValueError('amount < 0')\n"
        "        return v\n"
        "\n"
        "def validate(orders_df):\n"
        "    good, dead = [], []\n"
        "    for rec in orders_df.to_dict('records'):\n"
        "        try:\n"
        "            OrderRow(**{k: rec[k] for k in ('order_id','customer_id','status','amount')})\n"
        "            good.append(rec)\n"
        "        except ValidationError as e:\n"
        "            dead.append((rec.get('order_id'), e.errors()[0]['msg']))\n"
        "    logger.info('validated good=%d dead_letter=%d', len(good), len(dead))\n"
        "    return pd.DataFrame(good), dead\n"
        "\n"
        "valid_orders, dead_letter = validate(orders)\n"
        "print('dead-letter sample:', dead_letter[:3])"
    ))

    c.append(md("""
## 4. Transform

Clean keys, join, and build the analytics table: completed revenue by country
and month. This is the business logic — the reason the pipeline exists.
"""))
    c.append(code(
        "def transform(orders_df, customers_df):\n"
        "    cust = customers_df.copy()\n"
        "    cust['country'] = cust['country'].str.strip().str.upper()   # clean keys\n"
        "    enriched = orders_df.merge(cust[['customer_id', 'country']],\n"
        "                               on='customer_id', how='left')\n"
        "    enriched = enriched[enriched['status'] == 'completed'].copy()\n"
        "    enriched['month'] = pd.to_datetime(enriched['order_ts']).dt.to_period('M').astype(str)\n"
        "    result = (enriched.groupby(['country', 'month'])\n"
        "              .agg(orders=('order_id', 'count'),\n"
        "                   revenue=('amount', 'sum'))\n"
        "              .round(2).reset_index())\n"
        "    logger.info('transformed rows=%d', len(result))\n"
        "    return result\n"
        "\n"
        "mart = transform(valid_orders, customers)\n"
        "mart.sort_values('revenue', ascending=False).head()"
    ))

    c.append(md("""
## 5. Load (idempotent)

Write the result to **Parquet** (for the lake) and **SQLite** (for querying).
**Idempotency** matters: re-running must not duplicate data. We overwrite the
target table/file, so running the pipeline twice yields the same state — a core
production property.
"""))
    c.append(code(
        "from sqlalchemy import create_engine\n"
        "\n"
        "def load(df):\n"
        "    wh = DATA / 'warehouse'\n"
        "    wh.mkdir(parents=True, exist_ok=True)\n"
        "    df.to_parquet(wh / 'revenue_by_country_month.parquet', index=False)\n"
        "    engine = create_engine(f'sqlite:///{DATA / \"retail.db\"}')\n"
        "    df.to_sql('mart_revenue', engine, if_exists='replace', index=False)  # idempotent\n"
        "    logger.info('loaded rows=%d to parquet + sqlite', len(df))\n"
        "\n"
        "load(mart)\n"
        "load(mart)   # run twice on purpose...\n"
        "\n"
        "check = pd.read_sql('SELECT COUNT(*) AS n FROM mart_revenue', \n"
        "                    create_engine(f'sqlite:///{DATA / \"retail.db\"}'))\n"
        "print('rows after running load() twice:', int(check['n'][0]), '(no duplication)')"
    ))

    c.append(md("""
## 6. Orchestrate

A single entry point runs the stages in order — the function a scheduler
(cron, Airflow) would call. Notice how each stage is small, named, and testable.
"""))
    c.append(code(
        "def run_pipeline():\n"
        "    logger.info('=== pipeline start ===')\n"
        "    orders_df, customers_df = extract()\n"
        "    valid, dead = validate(orders_df)\n"
        "    mart_df = transform(valid, customers_df)\n"
        "    load(mart_df)\n"
        "    logger.info('=== pipeline done: %d mart rows, %d rejected ===',\n"
        "                len(mart_df), len(dead))\n"
        "    return mart_df\n"
        "\n"
        "final = run_pipeline()\n"
        "print('\\nTop 5 country-months by revenue:')\n"
        "print(final.sort_values('revenue', ascending=False).head())"
    ))

    c.append(md("""
## 7. Test the transform

The most valuable test targets the business logic. We verify the transform only
counts completed orders and rolls up correctly — on a tiny, hand-built input.
"""))
    c.append(code(
        "import ipytest, pandas as pd\n"
        "ipytest.autoconfig()"
    ))
    c.append(code(
        "%%ipytest\n"
        "\n"
        "def test_transform_only_completed_and_rolls_up():\n"
        "    orders_df = pd.DataFrame({\n"
        "        'order_id': [1, 2, 3],\n"
        "        'customer_id': [10, 10, 20],\n"
        "        'status': ['completed', 'returned', 'completed'],\n"
        "        'order_ts': pd.to_datetime(['2024-01-05', '2024-01-06', '2024-01-20']),\n"
        "        'amount': [100.0, 999.0, 50.0],\n"
        "    })\n"
        "    customers_df = pd.DataFrame({\n"
        "        'customer_id': [10, 20],\n"
        "        'country': ['us', 'GB '],\n"
        "    })\n"
        "    out = transform(orders_df, customers_df)\n"
        "    # returned order (999) must be excluded; keys cleaned to US/GB\n"
        "    assert out['revenue'].sum() == 150.0\n"
        "    assert set(out['country']) == {'US', 'GB'}\n"
        "    assert out['orders'].sum() == 2"
    ))

    c.append(md("""
## 🎓 You made it

You built a validated, logged, idempotent, tested ETL pipeline — and along the
way learned Python from variables to production data engineering.

**Where to go next:** move these stages into a `src/` package with real
`tests/`, run it with `uv run python -m pipeline --date ...` (the Python bootcamp\'s
logging & CLI notebook), swap SQLite for Postgres via the SQLAlchemy engine (the
Python bootcamp\'s databases notebook), schedule it, and partition the Parquet
output by month (notebook 05). The patterns are identical
at scale.

Happy shipping! 🚀
"""))
    return c


# ===========================================================================
# registry + main
# ===========================================================================

NOTEBOOKS = [
    ("00_setup_and_how_to_run.ipynb", nb_00),
    ("01_numpy_foundations.ipynb", nb_01),
    ("02_pandas_fundamentals.ipynb", nb_02),
    ("03_pandas_transform.ipynb", nb_03),
    ("04_pandas_timeseries.ipynb", nb_04),
    ("05_file_formats_parquet.ipynb", nb_05),
    ("06_capstone_etl_pipeline.ipynb", nb_06),
]


def main() -> None:
    os.makedirs(NB_DIR, exist_ok=True)
    for filename, builder in NOTEBOOKS:
        write_nb(filename, builder())
    print(f"\nDone: wrote {len(NOTEBOOKS)} notebooks to {NB_DIR}")


if __name__ == "__main__":
    main()
