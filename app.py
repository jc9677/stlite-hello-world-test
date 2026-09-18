import streamlit as st
import duckdb

st.title("Stlite + DuckDB")

result = duckdb.sql("""
    SELECT
        42 AS answer,
        'Hello from DuckDB!' AS message
""")

st.dataframe(result.df())