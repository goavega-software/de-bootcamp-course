# Python Zero-to-Hero Bootcamp 🐍 (Data-Engineering focus)

Learn Python from scratch by **reading and running** — hands-on Jupyter
notebooks where every concept is explained and immediately demonstrated with
runnable sample code you can execute and tweak. The course starts at true zero
(what a variable is) and takes you through the **language**, the **standard
library** for real data work, and the **engineering craft** (typing,
concurrency, logging, testing, performance) that makes code production-grade.

> **Dataframes live next door.** NumPy, pandas, Parquet and a full ETL capstone
> are in the companion **[`pandas-numpy-bootcamp`](../pandas-numpy-bootcamp/)**.
> Take this course first (at least Tracks 1–2), then that one. Keeping them
> separate means each stays focused — the same way SQL has its own bootcamp.

There are **no hidden exercises** — each notebook is a guided walkthrough:
short explanation → runnable code cell → printed result → next concept. Read
top to bottom, run every cell, change things and re-run to build intuition.

Everything runs on plain Python plus a few standard libraries (requests,
SQLAlchemy, pydantic, pytest). No cloud account or external service is required
— API examples run against local data or are fully self-contained.

## What you'll learn (25 modules across three tracks)

### Track 1 · Python Core (00–11) — true zero to solid

| # | Notebook | Topics |
|---|----------|--------|
| 00 | `setup_and_how_to_run` | how the course works, the sample data, running Python, `uv` |
| 01 | `variables_and_types` | objects, references, `int/float/bool/str`, dynamic typing, mutability |
| 02 | `numbers_and_strings` | arithmetic, operators, f-strings, string methods, slicing |
| 03 | `collections` | `list`, `tuple`, `set`, `dict`, `namedtuple`, `deque`, nesting |
| 04 | `control_flow` | `if/elif/else`, truthiness, `for`/`while`, `enumerate`, `zip`, `match`, walrus |
| 05 | `comprehensions` | list/dict/set comprehensions, generator expressions |
| 06 | `functions` | params, defaults, `*args`/`**kwargs`, scope, closures, type hints |
| 07 | `decorators` | functions as objects, writing decorators, `functools.wraps`, `@retry`, `lru_cache` |
| 08 | `iterators_and_generators` | the iterator protocol, `yield`, lazy pipelines, `itertools` |
| 09 | `modules_and_stdlib` | `import`, packages, `__main__`, a tour of the standard library |
| 10 | `oop` | classes, dunder methods, `@dataclass`, inheritance, properties |
| 11 | `errors_and_context_managers` | exceptions, `try/except/else/finally`, custom errors, `with` |

### Track 2 · Working with Data in Pure Python (12–18) — the stdlib toolkit

| # | Notebook | Topics |
|---|----------|--------|
| 12 | `files_and_pathlib` | reading/writing text & bytes, `pathlib`, encodings, streaming large files |
| 13 | `csv_and_delimited` | the `csv` module, dialects, `DictReader/DictWriter`, messy data |
| 14 | `regex` | the `re` module, `match/search/findall/sub`, groups, named groups, compiling |
| 15 | `json_and_serialization` | `json`, JSON Lines, nested payloads, `pickle`, custom encoders |
| 16 | `dates_and_times` | `datetime`, `timedelta`, parsing/formatting, timezones, epoch |
| 17 | `apis_and_http` | REST, `requests`, status codes, pagination, retries (mocked, offline) |
| 18 | `databases_with_python` | `sqlite3` DB-API, parameterization, SQLAlchemy Core, bulk load |

### Track 3 · Production-grade Python (19–24) — ship it reliably

| # | Notebook | Topics |
|---|----------|--------|
| 19 | `typing_and_pydantic` | type hints in depth, `dataclass` vs `pydantic`, validating dirty input |
| 20 | `concurrency` | the GIL, threads for I/O, `multiprocessing` for CPU, `asyncio` |
| 21 | `logging_config_cli` | `logging`, config & env vars, `argparse`, `.env` with `python-dotenv` |
| 22 | `testing_with_pytest` | `assert`, `pytest`, fixtures, parametrize, testing a transform |
| 23 | `performance_and_memory` | profiling, generators vs lists, streaming, data-structure choice |
| 24 | `packaging_and_uv` | project layout, `pyproject.toml`, `src/` packages, entry points, `uv` workflow |

> The Python 3.12 that `uv` installs bundles a modern SQLite and everything the
> notebooks use. All notebooks are explanation-first with runnable examples and
> are verified to execute end-to-end.

## 🚀 Step-by-step: how to start

### One-time setup (steps 1–4)

**1. Install prerequisites** (skip any you already have)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [VS Code](https://code.visualstudio.com/)
- In VS Code, install two extensions: **Python** and **Jupyter**

**2. Open a terminal in this project folder**
```bash
cd D:\Claude\Learning\de-bootcamp-course\python-bootcamp
```

**3. Create the environment and install dependencies**
```bash
uv sync
```
This reads `pyproject.toml` and builds an isolated `.venv` with requests,
SQLAlchemy, pydantic, pytest and Jupyter.

**4. Build the sample datasets**
```bash
uv run python data/build_data.py
```
You should see row counts print and files appear under `data/raw/` plus
`data/retail.db`.

### Running the notebooks (steps 5–8, repeat each session)

**5. Open the first notebook** — `notebooks/00_setup_and_how_to_run.ipynb`.

**6. Select the kernel** — click **Select Kernel** (top-right) → **Python
Environments** → pick the one showing **`.venv`**.

**7. Run the cells top to bottom** — `Shift+Enter` runs a cell and moves on.

**8. Experiment** — change values, re-run, break things on purpose.

> Prefer Jupyter Lab? `uv run jupyter lab` also works.

### 📚 Recommended learning order

Go in numbered order — each module builds on the previous one. Finish **Track 1
(00–11)** first; it makes you fluent in the language. **Track 2 (12–18)** is the
daily standard-library data toolkit. **Track 3 (19–24)** is what turns a script
into a production pipeline. Then continue to the companion
**`pandas-numpy-bootcamp`** for dataframe wrangling and a full ETL capstone.

## The sample data

A fictional retail company, delivered as **raw files** the way real ingestion
sees them (shared with the other bootcamps):

- `data/raw/customers.csv` — customer master, deliberately messy.
- `data/raw/products.csv` — product catalog.
- `data/raw/orders.csv` + `data/raw/order_items.csv` — orders fact and line items.
- `data/raw/events.jsonl` — semi-structured clickstream, one JSON object per line.
- `data/retail.db` — the same tables in SQLite for the database module.

## Resetting

- Rebuild the sample data anytime: `uv run python data/build_data.py`
- Regenerate the notebooks to their original state:
  `uv run python build_notebooks.py`

Happy shipping! 🚀
