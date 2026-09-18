import streamlit as st

st.title("Hello, World!")

name = st.text_input("What's your name?")

if name:
    st.write(f"Hello, {name}!")