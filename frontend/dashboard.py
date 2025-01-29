import streamlit as st
import st_cytoscape
from st_cytoscape import cytoscape
import json
import os
from core.utils import logger
from core.app_handler import AppHandler
#from config import filepath, stylesheet, layout



def render_dashboard(app_handler):
    elements = st.session_state.get("cytoscape_update", app_handler.get_elements())
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

    # Debugging: Zeige ausgewählte Elemente
    st.subheader("Ausgewählte Elemente")
    st.write("Knoten:")
    st.json(app_handler.get_selected_elements()["nodes"])
    st.write("Kanten:")
    st.json(app_handler.get_selected_elements()["edges"])
    st.subheader(f"Debugging - Anzahl Elemente: {len(elements)}")

#Elements= Daten INHALT
#stylesheet= Stylesheet WIE werden daten dargestellt
#layout= WIE werden daten angeordnet
