# SQL Zero-to-Hero Bootcamp 🎓

Learn SQL from scratch by **doing** — hands-on Jupyter notebooks you run and edit
locally. Every concept comes with runnable examples and practice exercises (with
solutions). All queries run against a small local **SQLite** database, so there's
nothing to install beyond Python + [uv](https://docs.astral.sh/uv/).

You write real SQL directly in notebook cells using
[JupySQL](https://jupysql.ploomber.io/) (`%%sql` magic) and see results instantly
as tables.

## What you'll learn (30 modules across three tracks)

### Core Track (00–16) — zero to solid

| # | Notebook | Topics |
|---|----------|--------|
| 00 | `setup_and_foundations` | how it works, the sample DB, set-based thinking, logical query order |
| 01 | `select_basics` | columns, aliases, `DISTINCT`, calculated columns, `LIMIT` |
| 02 | `filtering_where` | `WHERE`, `AND/OR`, `BETWEEN`, `IN`, `LIKE`, `NULL` |
| 03 | `sorting_and_limiting` | `ORDER BY`, `LIMIT`, `OFFSET` |
| 04 | `aggregations_group_by` | `COUNT/SUM/AVG/MIN/MAX`, `GROUP BY`, `HAVING` |
| 05 | `joins` | `INNER`/`LEFT`/self/cross joins, anti-joins |
| 06 | `subqueries` | scalar, `IN`, `EXISTS`, correlated, derived tables |
| 07 | `set_operations` | `UNION`, `INTERSECT`, `EXCEPT` |
| 08 | `string_and_date_functions` | text, number & date/time functions |
| 09 | `case_and_conditional` | `CASE`, `COALESCE`, `NULLIF`, conditional aggregation |
| 10 | `window_functions` | `ROW_NUMBER`, `RANK`, `LAG/LEAD`, running totals |
| 11 | `ctes` | `WITH`, multiple & **recursive** CTEs |
| 12 | `ddl_create_tables` | `CREATE TABLE`, types, constraints, `ALTER`, `DROP` |
| 13 | `dml_insert_update_delete` | `INSERT`, `UPDATE`, `DELETE`, `UPSERT` |
| 14 | `views_and_indexes` | views, indexes, `EXPLAIN QUERY PLAN` |
| 15 | `transactions` | `BEGIN/COMMIT/ROLLBACK`, ACID |
| 16 | `capstone_project` | 5 analytics challenges combining the core track |

### Advanced Track (17–26) — solid to strong engineer

| # | Notebook | Topics |
|---|----------|--------|
| 17 | `advanced_joins` | `RIGHT`/`FULL OUTER`, `USING`, non-equi joins, semi/anti-joins, `ON` vs `WHERE` |
| 18 | `advanced_aggregation` | `COUNT(DISTINCT)`, `GROUP_CONCAT`, `FILTER`, pivots, `ROLLUP` emulation |
| 19 | `advanced_window_functions` | frame clauses, moving averages, `NTILE`, `FIRST/LAST_VALUE`, `PERCENT_RANK` |
| 20 | `nulls_and_three_valued_logic` | 3-valued logic, `NOT IN`+NULL trap, NULLs in aggregates, `COALESCE/NULLIF` |
| 21 | `data_modeling_and_normalization` | keys, relationships, 1NF/2NF/3NF, anomalies, `ON DELETE CASCADE` |
| 22 | `indexing_and_performance` | reading query plans, composite/covering/unique indexes, when indexes fail |
| 23 | `json_in_sqlite` | `json_extract`/`->>`, `json_each`, `json_group_array`, `json_set`, JSON indexes |
| 24 | `triggers_and_advanced_views` | `AFTER`/`BEFORE` triggers, `RAISE`, audit logs, updatable views (`INSTEAD OF`) |
| 25 | `query_patterns_and_recipes` | top-N per group, dedup, gaps & islands, pivot/unpivot, running %, date spine |
| 26 | `advanced_capstone` | 5 harder challenges: MoM growth, RFM, JSON payloads, leaderboards |

### Theory Track (27–29) — the concepts underneath

Deeper conceptual grounding — the "understand it cold in a design review or
interview" layer. Theory-rich, with runnable demonstrations.

| # | Notebook | Topics |
|---|----------|--------|
| 27 | `theory_relational_model` | relations/tuples/domains, key hierarchy, relational algebra ↔ SQL, division, closure |
| 28 | `theory_transactions_and_isolation` | ACID in depth, read anomalies, ANSI isolation levels, locking vs MVCC, SQLite WAL & `SQLITE_BUSY` (live demos) |
| 29 | `theory_storage_indexes_and_optimizer` | pages & B-trees, what an index really is, cost-based planner & `ANALYZE`, nested-loop joins, SQLite type affinity |

> A few advanced features need a recent SQLite (`FULL/RIGHT JOIN` ≥ 3.39, JSON
> `->>` ≥ 3.38). The Python 3.12 that `uv` installs bundles SQLite 3.45+, so
> everything runs out of the box. All 30 notebooks are verified end-to-end on
> SQLite 3.51 (279 SQL cells + the concurrency demos).

## 🚀 Step-by-step: how to start

### One-time setup (steps 1–4)

**1. Install prerequisites** (skip any you already have)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [VS Code](https://code.visualstudio.com/)
- In VS Code, install two extensions: **Python** and **Jupyter**
  (the project prompts you to install these when you open the folder)

**2. Open a terminal in this project folder**
- In VS Code: `File → Open Folder →` this `sql-bootcamp` folder, then open a
  terminal with `` Ctrl+` `` (it opens already inside the project). Or:
  ```bash
  cd D:\Claude\Learning\sql-bootcamp
  ```

**3. Create the environment and install dependencies**
```bash
uv sync
```
This reads `pyproject.toml` and builds an isolated `.venv` with JupySQL,
SQLAlchemy, pandas, and Jupyter.

**4. Build the sample database** ⚠️ note the file is `build_database.py` inside
the `data/` folder (a common mistake is running `build_notebooks.py` here — that
is a different, optional script in the project root):
```bash
uv run python data/build_database.py
```
You should see row counts print and `data/retail.db` get created.

### Running the notebooks (steps 5–8, repeat each session)

**5. Open the first notebook** — in VS Code's Explorer open
`notebooks/00_setup_and_foundations.ipynb`.

**6. Select the kernel** — click **Select Kernel** (top-right of the notebook) →
**Python Environments** → pick the one showing **`.venv`**
(`.venv\Scripts\python.exe` on Windows).

**7. Run the first cell** — every notebook's first cell loads JupySQL and
connects to the database. Press `Shift+Enter`; you should see
`Connected to data/retail.db`.

**8. Work through the cells top to bottom** — `Shift+Enter` runs a cell and moves
on. Read the explanation, run the example, see the result table.

> Prefer Jupyter Lab? `uv run jupyter lab` also works.

### 📚 Recommended learning order

Go in numbered order — each module builds on the previous one. Finish the **Core
Track (00–16)** first; it makes you productive. Then the **Advanced Track
(17–26)** takes you to a strong-engineer level.

Core: `00_setup` → `01_select` → `02_filtering` → `03_sorting` →
`04_aggregations` → `05_joins` → `06_subqueries` → `07_set_operations` →
`08_string_date` → `09_case` → `10_window` → `11_ctes` → `12_ddl` → `13_dml` →
`14_views_indexes` → `15_transactions` → `16_capstone`

Advanced: `17_advanced_joins` → `18_advanced_aggregation` →
`19_advanced_window_functions` → `20_nulls` → `21_data_modeling` →
`22_indexing_performance` → `23_json` → `24_triggers_views` →
`25_query_patterns` → `26_advanced_capstone`

Theory (read alongside or after the above): `27_theory_relational_model` →
`28_theory_transactions_and_isolation` → `29_theory_storage_indexes_and_optimizer`

**Always run the first cell of each new notebook before anything else.**

### ✏️ How the exercises work

Each exercise has a **practice cell** (edit it, write your own query, run it)
followed by a **worked solution** cell right below (run it to check). Nothing is
hidden — attempt it first, then compare.

## 🔧 Troubleshooting

- **`can't open file ...build_notebooks.py: No such file or directory`** — you
  ran the wrong script/path. To build the database use
  `uv run python data/build_database.py`. `build_notebooks.py` is in the project
  **root** and is optional.
- **`no such table` / `unable to open database`** — you skipped step 4. Run
  `uv run python data/build_database.py`.
- **`%%sql` cell errors / "magic not found"** — you didn't run the notebook's
  **first cell**, or the wrong kernel is selected (pick the `.venv` one).
- **No kernel appears** — install the VS Code **Python** and **Jupyter**
  extensions, then reopen the notebook.

## The sample database

A fictional retail company: `categories`, `suppliers`, `products`, `customers`,
`employees` (with a self-referencing `manager_id`), `orders`, and `order_items`.
It's small enough to eyeball and rich enough for joins, aggregation, window
functions, and recursive queries. Full schema is described in notebook `00`.

## Resetting

- Rebuild the database anytime: `uv run python data/build_database.py`
- Regenerate/reset the notebooks to their original state:
  `uv run python build_notebooks.py`

Happy querying! 🚀
