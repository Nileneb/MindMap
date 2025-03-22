import streamlit as st
import frontend
import frontend.dashboard
import pages.role.login
import frontend.page2
import pages.role.register
import admin.admin
import admin.admin2
import pages.personal.settings as settings
import st_pages
import streamlit as st
from streamlit import session_state as st_session
import pages.personal.user
st.header("Settings")
st.write(f"You are logged in as {st.session_state.role}.")





def settings():
    st.write("Settings page")

    account_pages = [settings, frontend.user]
    request_pages = [pages.logout, pages.role.register()]
    respond_pages = [pages.login, pages.home]
    admin_pages = [admin.admin, admin.admin2]

    page_dict = {}
    if st.session_state.role in ["Requester", "Admin"]:
        page_dict["Request"] = request_pages
    if st.session_state.role in ["Responder", "Admin"]:
        page_dict["Respond"] = respond_pages
    if st.session_state.role == "Admin":
        page_dict["Admin"] = admin_pages
    
    if len(page_dict) > 0:
        pg = st.navigation({"Account": account_pages} | page_dict)
    else:
        pg = st.navigation([st.Page(frontend.login)])
    
