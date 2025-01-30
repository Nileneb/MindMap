import streamlit as st
from core.app_handler import AppHandler
from frontend.Sidebar import render_sidebar
from config import UPLOADS_DIR, stylesheet, layout
from frontend.dashboard import render_dashboard
from core.utils import logger, filepattern, render_file_selector, load_css





def main():
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
    load_css()
    #LLM Logik
    #render_chat_window()
    
    # appHandler/mindmap
    selected_filepath = render_file_selector(filepattern)
    if not selected_filepath:
        st.stop()
    
    app_handler = AppHandler(filepath=UPLOADS_DIR, stylesheet=stylesheet, layout=layout)
    app_handler.load_state()
     
    st.title("Mindmap Dashboard")
    render_sidebar(app_handler)
    render_dashboard(app_handler)
    
    #render_folder_selection_sidebar(app_handler)
    
    
    

if __name__ == "__main__":
    main()


#sudo systemctl start postgresql