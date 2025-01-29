import streamlit as st
from core.app_handler import AppHandler
from frontend.Sidebar import render_sidebar
from config import filepath, stylesheet, layout
from frontend.dashboard import render_dashboard
from core.utils import logger, filepattern, render_file_selector, load_css
#tktinker
from frontend.tkinter_integration import render_folder_selection_sidebar
#RAG
from agent.core import load_index_from_mindmap
#LLM
from frontend.llm import render_chat_window

def main():
    st.set_page_config(page_title="Mindmap Dashboard", page_icon="🧠", layout="centered")
    load_css()
    #LLM Logik
    render_chat_window()
    
    # appHandler/mindmap
    selected_filepath = render_file_selector(filepattern)
    if not selected_filepath:
        st.stop()
    
    app_handler = AppHandler(filepath=selected_filepath, stylesheet=stylesheet, layout=layout)
    app_handler.load_state()
     
    st.title("Mindmap Dashboard")
    
    render_dashboard(app_handler)
    render_sidebar(app_handler)
    render_folder_selection_sidebar(app_handler)
    #RAG Logik
    #index = load_index_from_mindmap(filepath)
    #query_engine = index.as_query_engine()
    

if __name__ == "__main__":
    main()


#sudo systemctl start postgresql