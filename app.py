from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="Stlite + DuckDB-Wasm",
    layout="wide",
)

st.title("Stlite + DuckDB-Wasm")
st.write(
    "This Streamlit app runs in Pyodide. The query engine below runs in a "
    "DuckDB-Wasm worker, so the page can process data without a server."
)
st.caption(
    "DuckDB-Wasm is deliberately kept in JavaScript. The native DuckDB package "
    "in the local uv environment is for local verification, not for Stlite."
)

component_html = Path(__file__).with_name("duckdb_component.html").read_text()
components.html(component_html, height=940, scrolling=True)