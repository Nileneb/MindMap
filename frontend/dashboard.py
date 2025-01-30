import streamlit as st
import st_cytoscape
from st_cytoscape import cytoscape
import matplotlib.pyplot as plt
from streamlit_file_browser import st_file_browser
import json
import os
from core.utils import logger
from core.app_handler import AppHandler
from frontend.Sidebar import show_mindmap, show_charts, show_files, show_preview, show_chat
from agent.llm_rag import ChatLLM
from config import UPLOADS_DIR

chat_llm = ChatLLM()

def render_dashboard(app_handler):
    elements = st.session_state.get("cytoscape_update", app_handler.get_elements())

    show_mindmap = st.session_state.get("show_mindmap", True)
    show_charts = st.session_state.get("show_charts", True)
    show_files = st.session_state.get("show_files", True)
    show_preview = st.session_state.get("show_preview", True)

    # 🎯 **Dashboard Layout**
    header_col1, header_col2 = st.columns([3, 2])
    main_col1, main_col2 = st.columns([3, 2])
    footer_col1, footer_col2 = st.columns([1, 1])

    if show_mindmap:
        with main_col1:
            st.subheader("🌍 Mindmap")
            selected_elements = cytoscape(
                elements=elements,
                stylesheet=app_handler.stylesheet,
                layout=app_handler.layout,
                width="100%",
                height="800px",
                key="cytoscape_mindmap"
            )
            logger.info(f"Ausgewählte Elemente von Cytoscape: {selected_elements}")
            app_handler.set_selected_elements(selected_elements)
            st.json(app_handler.get_selected_elements()["edges"])
            st.subheader(f"Debugging - Anzahl Elemente: {len(elements)}")

    # 📂 **File Browser (Fixes)**
    selected_file = None  # Standardwert setzen
    if show_files:
        with main_col2:
            st.subheader("📂 Dateien durchsuchen")
            try:
                #filepath = "filepath"  # Replace with your default path or environment variable name
                event = st_file_browser(path=UPLOADS_DIR, key="A", show_choose_folder=True, use_static_file_server=True)
                selected_file = event.get("selected_file", None)
            except Exception as e:
                logger.error(f"❌ Fehler beim Dateibrowser: {e}")

    # 📝 **Datei Vorschau (Fixes)**
    if show_preview:
        with footer_col1:
            st.subheader("📝 Datei Vorschau")
            preview_text = ""
            if selected_file:
                try:
                    with open(selected_file, "r") as f:
                        preview_text = f.read()
                except Exception as e:
                    preview_text = f"Fehler beim Lesen der Datei: {e}"
            st.text_area("Inhalt der Datei", preview_text)

    # 📊 **Matplotlib-Graphen**
    if show_charts:
        with footer_col2:
            st.subheader("📊 Data Analysis")
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3, 4], [10, 20, 25, 30], marker="o")
            ax.set_title("Beispiel-Plot")
            st.pyplot(fig)

            if hasattr(chat_llm, "figures") and chat_llm.figures:
                st.subheader("Generated Charts")
                for fig in chat_llm.figures:
                    st.pyplot(fig)
                chat_llm.figures.clear()

    # 💬 **Chat-Funktion**
    if show_chat:
        with footer_col2:
            for speaker, message in st.session_state.get("conversation", []):
                if speaker == "You":
                    st.markdown(f'<p><strong>You:</strong> {message}</p>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<p style="color:green;"><strong>Bot:</strong> {message}</p>', unsafe_allow_html=True)

            if hasattr(chat_llm, "figures") and chat_llm.figures:
                for fig in chat_llm.figures:
                    st.pyplot(fig)
                chat_llm.figures.clear()

            with st.form("chat_form", clear_on_submit=True):
                user_input = st.text_input("Nachricht eingeben:", key="chat_input")
                submitted = st.form_submit_button("Senden")

                if submitted and user_input:
                    response = chat_llm.get_response(user_input)
                    st.session_state.setdefault("conversation", []).append(("You", user_input))
                    st.session_state.setdefault("conversation", []).append(("Bot", response))
                    st.rerun()
