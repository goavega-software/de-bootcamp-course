# pandas & NumPy Zero-to-Hero Bootcamp 📊 (Data-Engineering focus)

Learn **dataframe wrangling** — the daily work of transforming and analysing
tabular data in Python — by **reading and running** hands-on Jupyter notebooks.
Every concept is explained and immediately demonstrated with runnable sample
code you can execute and tweak.

This is the companion to the **[`python-bootcamp`](../python-bootcamp/)**. It
assumes you can already read Python; if you can't yet, do that course first (at
least Track 1). Splitting the two keeps each focused — language fluency and
dataframe fluency are different skills, and you'll come back to pandas on its
own for years.

There are **no hidden exercises** — each notebook is a guided walkthrough:
short explanation → runnable code cell → printed result → next concept.

Everything runs locally on NumPy, pandas, PyArrow, SQLAlchemy and pydantic. No
cloud account or external service is required.

## What you'll learn (7 modules)

| # | Notebook | Topics |
|---|----------|--------|
| 00 | `setup_and_how_to_run` | how it works, the sample data, a 30-second taste |
| 01 | `numpy_foundations` | `ndarray`, dtypes, vectorization, boolean masks, broadcasting, axes |
| 02 | `pandas_fundamentals` | `Series`/`DataFrame`, `read_csv`/`read_sql`, selecting, `.loc`/`.iloc`, categorical dtype |
| 03 | `pandas_transform` | `groupby`, `merge`/joins, `pivot`/`melt`, `apply`/`map`, `concat`, `drop_duplicates`, missing data |
| 04 | `pandas_timeseries` | datetime index, `resample`, rolling windows, `shift`, period-over-period |
| 05 | `file_formats_parquet` | CSV vs Parquet, columnar storage, compression, partitioning with PyArrow |
| 06 | `capstone_etl_pipeline` | a full extract → validate → transform → load pipeline, idempotent & tested |

> The capstone validates records with **pydantic**, which is taught in the
> Python bootcamp's `17_typing_and_pydantic` notebook — a quick read if it's new.

## 🚀 Step-by-step: how to start

### One-time setup (steps 1–4)

**1. Install prerequisites** (skip any you already have)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [VS Code](https://code.visualstudio.com/)
- In VS Code, install the **Python** and **Jupyter** extensions

**2. Open a terminal in this project folder**
```bash
cd D:\Claude\Learning\de-bootcamp-course\pandas-numpy-bootcamp
```

**3. Create the environment and install dependencies**
```bash
uv sync
```
This builds an isolated `.venv` with numpy, pandas, pyarrow, SQLAlchemy,
pydantic and Jupyter.

**4. Build the sample datasets**
```bash
uv run python data/build_data.py
```
Row counts print and files appear under `data/raw/` plus `data/retail.db`.

### Running the notebooks (steps 5–8, repeat each session)

**5. Open the first notebook** — `notebooks/00_setup_and_how_to_run.ipynb`.

**6. Select the kernel** — **Select Kernel** → **Python Environments** → the
one showing **`.venv`**.

**7. Run the cells top to bottom** — `Shift+Enter`.

**8. Experiment** — change values, re-run, build intuition.

> Prefer Jupyter Lab? `uv run jupyter lab` also works.

### 📚 Recommended learning order

Go in numbered order: `00_setup` → `01_numpy` → `02_pandas_fundamentals` →
`03_pandas_transform` → `04_pandas_timeseries` → `05_file_formats_parquet` →
`06_capstone_etl_pipeline`. NumPy first because pandas is built on it; the
capstone last because it combines everything.

## The sample data

The same fictional retail company as the other bootcamps, delivered as raw
files (`data/raw/*.csv`, `events.jsonl`) plus `data/retail.db`. Rebuild anytime
with `uv run python data/build_data.py`.

## Resetting

- Rebuild the sample data: `uv run python data/build_data.py`
- Regenerate the notebooks: `uv run python build_notebooks.py`

Happy wrangling! 🚀
