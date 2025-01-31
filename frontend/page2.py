import streamlit as st
from st_pages import add_page_title, get_nav_from_toml
from core.utils import logger
from st_cytoscape import cytoscape
from frontend.Sidebar import show_chat
import matplotlib.pyplot as plt
from agent.llm_rag import ChatLLM


chat_llm = ChatLLM()

def render_page2(app_handler):
    nav = get_nav_from_toml("pages.toml")
    pg = st.navigation(nav)
    add_page_title(pg)
    
    elements = st.session_state.get("cytoscape_update", app_handler.get_elements())

    show_mindmap = st.session_state.get("show_mindmap", True)
    show_charts = st.session_state.get("show_charts", True)
    show_files = st.session_state.get("show_files", False)
    show_preview = st.session_state.get("show_preview", False)
    #output_folder = app_handler.filepath  # Ensure this is correct
    #input_folder = app_handler.filepath   # Ensure this is correct
    # 🎯 **Dashboard Layout**
    header_col1  = st.columns([3, 2])
    main_col1 = st.columns([3, 2])
    footer_col1 = st.columns([1, 1])

    show_mindmap_flag = st.session_state.get("show_mindmap", True)
    
    if show_mindmap_flag:
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

    # 💬 **Chat-Funktion**
    if show_chat:
        with footer_col1:
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
    
    # 📊 **Matplotlib-Graphen**
    if show_charts:
        with footer_col1:
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
    
    
    
    
    
    
    pg.run()