# Databricks Data Engineering — Learning Track 🧱⚡

A hands-on path for learning **data engineering on Databricks**. Import these
notebooks into your Databricks workspace, attach compute, and work through them in
order.

This track is a **Databricks specialization layer**. It assumes you already know
**SQL and Python basics** — if you need those from scratch, the sibling courses in
`de-bootcamp-course` (`sql-bootcamp`, `python-bootcamp`, `pandas-numpy-bootcamp`,
`dbt-bootcamp`) teach them in depth. Here we focus on what makes Databricks
*Databricks*: Unity Catalog, Delta Lake, ingestion, transformations, streaming,
declarative pipelines, orchestration, and an end-to-end capstone.

## How to use

1. **Import:** *Workspace → Import → File* (import each `.ipynb`), or point a Git
   folder at this directory.
2. **Attach compute:** serverless, an all-purpose cluster, or a SQL warehouse (for
   `%sql`-heavy notebooks). Databricks **Free Edition** works for everything here.
3. **Run in order** — the core notebooks build on one shared dataset created in
   notebook 6.

> **Databricks Free Edition notes:** everything runs on serverless with Unity
> Catalog. If a `CREATE SCHEMA`/`CREATE VOLUME` fails on permissions, set the
> `CATALOG` variable in notebook 6 to a catalog you can write to (often
> `workspace` or your personal catalog) — the notebooks read the current catalog
> automatically.

## Learning path

Work through the notebooks in number order. **1–5 are foundations** (concepts +
languages); **6–15 are the Databricks-native data-engineering core**, built on
one shared **BrewBox** dataset created in notebook 6.

### Foundations (1–5)
| # | Notebook | What it covers | Status |
|---|---|---|---|
| 1 | `Databricks_Data_Engineering_Introduction` | Concepts: OLTP/OLAP, warehouse/lake/lakehouse, dimensional modeling (star & snowflake), ETL/ELT, Spark, pipelines, Medallion, tech landscape | ✅ available |
| 2 | `Databricks_SQL_Bootcamp` | SQL on Databricks (Spark SQL) — all core SQL concepts | ✅ available |
| 3 | `Databricks_Python_Bootcamp` | Core Python | ✅ available |
| 4 | `Databricks_Pandas_Bootcamp` | pandas + NumPy | ✅ available |
| 5 | `Databricks_PySpark_Bootcamp` | PySpark — the DataFrame API the core track builds on | ✅ available |

> New to SQL/Python/pandas? The deep, multi-notebook versions live in the sibling
> courses under `de-bootcamp-course` (`sql-bootcamp`, `python-bootcamp`,
> `pandas-numpy-bootcamp`). Notebooks 2–4 here are compact Databricks refreshers.

### Databricks DE core (6–15) — one shared BrewBox dataset
| # | Notebook | What it covers | Status |
|---|---|---|---|
| 6 | Platform & Unity Catalog | Workspace, compute, magic commands, `dbutils`, Unity Catalog (catalog/schema/table/**Volume**), and **setup of the shared BrewBox dataset** | ✅ available |
| 7 | Data ingestion | Reading formats, **Auto Loader** (`cloudFiles`), `COPY INTO`, schema evolution → **Bronze** | ✅ available |
| 8 | Delta Lake deep dive | `MERGE`/**SCD 1 & 2**, `OPTIMIZE`/Z-order/liquid clustering, `VACUUM`, schema evolution, Change Data Feed, time travel + `RESTORE` | ✅ available |
| 9 | Transformations (PySpark + SQL) | Bronze→Silver cleaning, joins, windows, functions — both syntaxes side by side; pandas-vs-PySpark aside | ✅ available |
| 10 | Data modeling on the lakehouse | Fact & dimension tables, star/snowflake, SCD dims → **Gold** marts | ✅ available |
| 11 | Structured Streaming | `readStream`/`writeStream`, checkpoints, triggers, watermarks, streaming medallion | ✅ available |
| 12 | Declarative pipelines + data quality | Lakeflow Declarative Pipelines (DLT), expectations, streaming tables & materialized views | ✅ available |
| 13 | Orchestration & operations | Databricks Workflows / Lakeflow Jobs, scheduling, dependencies, retries, Asset Bundles | ✅ available |
| 14 | Performance & cost | Photon, AQE, partitioning vs Z-order vs liquid clustering, file sizing, skew, the Spark UI | ✅ available |
| 15 | **Capstone project** | End-to-end: ingest → Bronze → Silver (SCD2) → Gold (star schema) → data quality → orchestrated job → serve | ✅ available |

## The shared dataset — BrewBox ☕

Notebook 6 creates a fictional coffee-chain dataset in Unity Catalog (schema
`brewbox`) that **every core notebook reuses**:

- **Reference tables:** `customers`, `stores`, `products`, `order_items`
- **Raw landing files** (in a Volume, for the ingestion notebook): `orders/` (JSON),
  `events/` (JSON)

Build it once in notebook 6, then the rest of the track reads from it — no more
per-notebook sample data.

## Notes

- **Names evolve fast on Databricks.** DLT is now *Lakeflow Declarative Pipelines*
  and Workflows is *Lakeflow Jobs*; the notebooks use current naming and note the
  older names where helpful.
- These notebooks run on **Databricks compute** (Spark/Delta/streaming can't run
  locally). Code is authored and syntax-checked; run it in Databricks to see
  results.
