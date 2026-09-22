# Stlite + DuckDB-Wasm static demo

This is a static GitHub Pages example of a Streamlit app that processes a
Parquet file in the browser with DuckDB-Wasm. There is no Python server:

```text
Streamlit app -> Stlite -> Pyodide
												 |
												 +-> HTML component -> DuckDB-Wasm worker -> OPFS
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

Open <http://localhost:8000> and use the controls in the Streamlit app:

- **Run weather summary** runs an aggregate query over the persisted table.
- **Preview rows** reads a small result set from DuckDB-Wasm.
- **Cache summary to OPFS** writes a derived Parquet file to OPFS and reads it
	back.
- **Reset local database** drops and rebuilds the demo table.

The first load materializes `weather.parquet` into
`opfs://weather-demo.duckdb` and calls `CHECKPOINT`. Later loads reopen the
local database without reloading the source table. OPFS is a browser cache and
working store, not a backup or cross-device data store.

## Verify locally with native DuckDB

The local environment can inspect the same dataset without involving Pyodide:

```sh
uv run duckdb -c "SELECT count(*) FROM read_parquet('weather.parquet')"
```
