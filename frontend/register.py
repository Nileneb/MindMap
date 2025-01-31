
import st_pages
from main import get_nav_from_toml
import streamlit as st
from streamlit import session_state as st_session

st.header("Request 1")
st.write(f"You are logged in as {st.session_state.role}.")

