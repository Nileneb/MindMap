import streamlit as st
st.set_page_config(
    page_title="Mindmap Dashboard",
    page_icon="🧠",
    layout="wide",
    menu_items={
        'Get Help': 'https://www.linn.games',
        'Report a bug': "https://www.linn.games",
        'About': "# MindUreMap!"
    }
)
from st_pages import add_page_title, get_nav_from_toml
from streamlit_login_auth_ui.widgets import __login__

# 🔥 **set_page_config als allererste Streamlit-Funktion!**


    
    
import os
from core.app_handler import AppHandler
from frontend.Sidebar import render_sidebar
from config import stylesheet, layout
from frontend.dashboard import render_dashboard
# Remove or comment out: from streamlit import session_state as st




filepath = "/home/nileneb/mind/"
project_name = None
#role = st.session_state.role



def main(filepath=filepath, filepattern="*.json", role=None):
    # Initialize role in session state if not already set
    nav = get_nav_from_toml("pages.toml")
    pg = st.navigation(nav)
    

    selected_folder = filepath    
    app_handler = AppHandler(selected_folder, stylesheet, layout, project_name=project_name)  # Pass data_dir
    app_handler.load_state()
    render_sidebar(app_handler)
    render_dashboard(app_handler)
    
if __name__ == "__main__":
    main()
