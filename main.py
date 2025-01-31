import streamlit as st

# 🔥 **set_page_config als allererste Streamlit-Funktion!**


import os
from core.app_handler import AppHandler
from frontend.Sidebar import render_sidebar
from config import stylesheet, layout
from frontend.dashboard import render_dashboard
#from core.utils import render_file_selector
#from frontend.project_initializer import initialize_project



def main(filepath="/home/nileneb/mind/data", filepattern="*.json"):
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
    
    project_name = None  # Initialize project_name

    selected_folder = filepath  # Separate data directory
    #selected_filepath = render_file_selector(filepattern)
    #selected_folder = app_handler.filepath
    # Entferne die folgende fehlerhafte Zeile
    # selected_folder.name = project_name
    #project_name = None
    
    app_handler = AppHandler(selected_folder, stylesheet, layout, project_name=project_name)  # Pass data_dir
    app_handler.load_state()
    render_sidebar(app_handler)
    render_dashboard(app_handler)

if __name__ == "__main__":
    main()
