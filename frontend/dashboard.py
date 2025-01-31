import streamlit as st
from streamlit_file_browser import st_file_browser
from core.utils import logger
from agent.llm_rag import ChatLLM
from st_pages import add_page_title, get_nav_from_toml



chat_llm = ChatLLM()




def render_dashboard(app_handler):
    st.header("Respond 1")
    st.write(f"You are logged in as {st.session_state.role}.")
    
    elements = st.session_state.get("cytoscape_update", app_handler.get_elements())
    
    show_mindmap = st.session_state.get("show_mindmap", True)
    show_charts = st.session_state.get("show_charts", True)
    show_files = st.session_state.get("show_files", False)
    #show_preview = st.session_state.get("show_preview", True)
    #output_folder = app_handler.filepath  # Ensure this is correct
    input_folder = app_handler.filepath   # Ensure this is correct
    # 🎯 **Dashboard Layout**
    header_col1, header_col2 = st.columns([3, 2])
    main_col1, main_col2 = st.columns([3, 2])
    footer_col1, footer_col2 = st.columns([1, 1])

    
    # 📂 **File Browser (Fixes)**
    selected_file = None  # Standardwert setzen
    if show_files:
        with main_col2:
            st.subheader("📂 Dateien durchsuchen")
            try:
                event = st_file_browser(path=input_folder, key="A", show_choose_folder=True, use_static_file_server=True)
                selected_file = st.session_state.get("selected_elements", {"nodes": [], "edges": []})
                selected_file_path = selected_file.get("path") if isinstance(selected_file, dict) else selected_file
            except Exception as e:
                logger.error(f"❌ Fehler beim Dateibrowser: {e}")
    
    
    if st.sidebar.button("📜 JupyterLab öffnen"):
        with main_col1:
            from streamlit_extras.jupyterlite import jupyterlite
            jupyterlite(800, 600)
            st.sidebar.write("JupyterLab gestartet...")

    


