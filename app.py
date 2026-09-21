import streamlit as st

st.title("Stlite + DuckDB-Wasm")

st.write("This Streamlit app runs in Pyodide through Stlite.")
st.info(
    "DuckDB queries run separately in the browser via the DuckDB-Wasm "
    "JavaScript module loaded by index.html."
)

st.code("SELECT 42 AS answer, 'Hello from DuckDB-Wasm!' AS message", language="sql")