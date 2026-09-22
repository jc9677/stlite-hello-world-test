import json
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


def decode_event(value):
    if not isinstance(value, dict):
        return {}
    if value.get("type") != "json":
        return value
    payload = value.get("value")
    if isinstance(payload, str):
        try:
            decoded = json.loads(payload)
        except json.JSONDecodeError:
            return {}
        return decoded if isinstance(decoded, dict) else {}
    return payload if isinstance(payload, dict) else {}


def result_rows(result):
    return result.get("rows", []) if isinstance(result, dict) else []


if "command_id" not in st.session_state:
    st.session_state.command_id = 0
if "pending_command" not in st.session_state:
    st.session_state.pending_command = None
if "last_event" not in st.session_state:
    st.session_state.last_event = {}

st.subheader("Browser data lab")
button_columns = st.columns(5)
command = st.session_state.pending_command
button_actions = (
    (button_columns[0], "Run weather summary", "summary"),
    (button_columns[1], "Preview rows", "preview"),
    (button_columns[2], "Cache summary to OPFS", "cache"),
    (button_columns[3], "Reset local database", "reset"),
    (button_columns[4], "Refresh OPFS", "opfs_refresh"),
)
for column, label, action in button_actions:
    if column.button(label, width="stretch"):
        st.session_state.command_id += 1
        command = {
            "id": st.session_state.command_id,
            "action": action,
        }
        st.session_state.pending_command = command

component_dir = Path(__file__).with_name("duckdb_component")
duckdb_component = components.declare_component(
    "duckdb_browser",
    path=component_dir,
)
event = decode_event(
    duckdb_component(
        command=command,
        key="weather-demo",
        default={},
    )
)
if event:
    st.session_state.last_event = event
    pending = st.session_state.pending_command
    if pending and event.get("command_id") == pending.get("id"):
        st.session_state.pending_command = None

event = st.session_state.last_event
event_type = event.get("type", "waiting")
st.caption(f"Browser event: {event_type}")

summary = event.get("summary") if event_type == "ready" else None
if summary is None:
    summary = event.get("result") if event_type in {"summary", "reset"} else None
summary_rows = result_rows(summary)
if summary_rows:
    summary_row = summary_rows[0]
    metric_columns = st.columns(4)
    metric_columns[0].metric("Rows", summary_row.get("rows", ""))
    metric_columns[1].metric("Average temperature", summary_row.get("avg_temp_3pm", ""))
    metric_columns[2].metric("Average humidity", summary_row.get("avg_humidity_3pm", ""))
    metric_columns[3].metric("Rain tomorrow", summary_row.get("rain_tomorrow", ""))

if event_type in {"preview", "cache"}:
    st.dataframe(result_rows(event.get("result")), hide_index=True, width="stretch")
elif summary_rows:
    st.dataframe(summary_rows, hide_index=True, width="stretch")

if event.get("opfs"):
    st.subheader("OPFS contents")
    st.dataframe(event["opfs"], hide_index=True, width="stretch")

if event_type == "error":
    st.error(event.get("message", "The browser component reported an error."))
elif event_type not in {"waiting", "ready"}:
    st.caption(f"Completed: {event_type}")