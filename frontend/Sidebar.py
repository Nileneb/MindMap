import streamlit as st
from core.utils import logger
from core.app_handler import AppHandler
#from config import stylesheet, filepath, AVAILABLE_SHAPES, layout
from frontend.llm import render_chat_window


def render_sidebar(app_handler):
    st.sidebar.title("Mindmap Einstellungen")
    
    selected_elements = app_handler.get_selected_elements()
    selected_nodes = selected_elements.get("nodes", [])
    selected_edges = selected_elements.get("edges", [])
    
    st.sidebar.subheader("Ausgewählte Knoten bearbeiten:")
    if selected_nodes:
        for idx, node in enumerate(selected_nodes):
            with st.sidebar.expander(f"Knoten {idx + 1}: {node['data'].get('label', '')}"):
                node_label = st.text_input("Label", value=node["data"].get("label", ""), key=f"node_label_{idx}")
                node_color = st.color_picker("Farbe", value=node["data"].get("color", "#90caf9"), key=f"node_color_{idx}")
                node_shape = st.selectbox("Shape", ["ellipse", "rectangle", "diamond"], index=0, key=f"node_shape_{idx}")

                if st.button(f"Knoten {idx + 1} speichern", key=f"node_save_{idx}"):
                    node["data"].update({
                        "label": node_label,
                        "color": node_color,
                        "shape": node_shape
                    })
                    selected_elements["nodes"][idx] = node
                    app_handler.set_selected_elements(selected_elements)
                    app_handler.update_selected_elements(selected_elements)
                    app_handler.trigger_cytoscape_update()
                    st.sidebar.success(f"Knoten {idx + 1} aktualisiert!")
    else:
        st.sidebar.write("Keine Knoten ausgewählt.")

    st.sidebar.subheader("Ausgewählte Kanten bearbeiten:")
    if selected_edges:
        for idx, edge in enumerate(selected_edges):
            with st.sidebar.expander(f"Kante {idx + 1}"):
                edge_label = st.text_input("Label", value=edge["data"].get("label", ""), key=f"edge_label_{idx}")
                edge_color = st.color_picker("Linienfarbe", value=edge["data"].get("line-color", "#000000"), key=f"edge_color_{idx}")

                if st.button(f"Kante {idx + 1} speichern", key=f"edge_save_{idx}"):
                    edge["data"].update({
                        "label": edge_label,
                        "line-color": edge_color
                    })
                    selected_elements["edges"][idx] = edge
                    app_handler.set_selected_elements(selected_elements)
                    app_handler.update_selected_elements(selected_elements)
                    app_handler.trigger_cytoscape_update()
                    st.sidebar.success(f"Kante {idx + 1} aktualisiert!")
    else:
        st.sidebar.write("Keine Kanten ausgewählt.")

    st.sidebar.button("Add_Node", key="add_node")



