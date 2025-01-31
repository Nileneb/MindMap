import streamlit as st
from menu import menu_with_redirect

# Redirect to app.py if not logged in, otherwise show the navigation menu
menu_with_redirect()

st.title("This page is available to all users")
st.markdown(f"You are currently logged in with the role of {st.session_state.role}.")

# Optional: Halt the app if the user's role is not authorized
# authorized_roles = ["user", "admin", "super-admin"]
# if st.session_state.role not in authorized_roles:
#     st.error("You do not have permission to view this page.")
#     st.stop()
