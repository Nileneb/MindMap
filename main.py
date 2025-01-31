import streamlit as st

# 🔥 **set_page_config als allererste Streamlit-Funktion!**


import os
from core.app_handler import AppHandler
from frontend.Sidebar import render_sidebar
from config import stylesheet, layout
from frontend.dashboard import render_dashboard
#from core.utils import render_file_selector
import streamlit as st
from st_pages import add_page_title, get_nav_from_toml

filepath = "/home/nileneb/mind/"

def main(filepath=filepath, filepattern="*.json"):
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
    # Replace file_uploader with text_input for folder path
    
    
    # Automatically set project name based on folder name
    with st.sidebar.form("📂 **Project Name**"):
        project_name = os.path.basename(os.path.normpath(filepath))
        st.text_input("Projekt Name:", value=project_name, key="project_name")
        filepath = st.sidebar.text_input("Choose a folder", value=filepath)
        st.form_submit_button("Save")
    
    
    selected_folder = filepath 

    
    app_handler = AppHandler(selected_folder, stylesheet, layout, project_name=project_name)  # Pass data_dir
    app_handler.load_state()
    render_sidebar(app_handler)
    render_dashboard(app_handler)
    
if __name__ == "__main__":
    main()
