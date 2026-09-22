# Stlite + DuckDB-Wasm static demo

This is a static GitHub Pages example of a Streamlit app that processes a
Parquet file in the browser with DuckDB-Wasm. There is no Python server:

```text
Streamlit elements -> Stlite -> Pyodide
														 |
														 +-> headless component -> DuckDB-Wasm worker -> OPFS
```

The Python app does not import `duckdb`. The `duckdb>=1.5.5` dependency in
`pyproject.toml` is the native DuckDB client used by the local `uv` environment
for checking the Parquet file and query results. It is not installed into the
Stlite/Pyodide runtime.

The browser component pins `@duckdb/duckdb-wasm@1.32.0`. This is intentional:
the OPFS article documents `1.32.0` as a working persistence version and warns
that some newer development builds can create OPFS files without persisting
writes. Upgrade the WASM client only after verifying its OPFS behavior.

## Run locally

Serve the repository over HTTP. OPFS is origin-scoped browser storage and is
not available from a `file://` page:

```sh
python3 -m http.server 8000
```

Open <http://localhost:8000/index.html> and use the native Streamlit controls:

- **Run weather summary** runs an aggregate query over the persisted table.
- **Preview rows** reads a small result set from DuckDB-Wasm.
- **Cache summary to OPFS** writes a derived Parquet file to OPFS and reads it
	back.
- **Reset local database** drops and rebuilds the demo table.
- **Refresh OPFS** lists the browser's persisted database and derived files.

The visible controls, metrics, and tables are Streamlit elements. The
headless browser component in `duckdb_component/index.html` receives commands,
runs DuckDB-Wasm in a worker, and returns only compact JSON result sets and
metadata. The source data and database never leave the browser.

The first load materializes `weather.parquet` into the
`opfs://weather-demo-v2.duckdb` database and calls `CHECKPOINT`. Later loads
reopen the local database without reloading the source table. OPFS is a browser cache and
working store, not a backup or cross-device data store.

The service worker caches the pinned Stlite and DuckDB-Wasm jsDelivr assets
after the first load. Subsequent loads reuse those assets from the browser's
Cache Storage; the first load still requires network access.

## Verify locally with native DuckDB

The local environment can inspect the same dataset without involving Pyodide:

```sh
uv run duckdb -c "SELECT count(*) FROM read_parquet('weather.parquet')"
```
