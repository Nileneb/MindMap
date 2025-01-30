import streamlit as st
from streamlit_file_browser import st_file_browser
from core.utils import logger
from core.app_handler import AppHandler
#from frontend.llm import render_chat_window
# from core.utils import load_css
# Style
from streamlit_extras.stylable_container import stylable_container
# Jupyter
from streamlit_extras.jupyterlite import jupyterlite

# from frontend.dashboard import render_dashboard, render_folder_selection_sidebar, show_mindmap, show_charts, show_files, show_preview

# Define variables at module level
show_mindmap = True
show_charts = True
show_files = True
show_preview = True
show_chat = True

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

    st.sidebar.subheader("Add Node")
    with st.popover("Add_Node", icon=":material/chat:", help="Adding a Node"):
        st.write("Mögliche Node-Attribute:", app_handler.node_attributes)    
        st.markdown("### 🤖 Add Node")
        
        new_label = st.text_input("Label für neuen Node", "")
        if st.button("Knoten hinzufügen"):
            node_data = {"data": {"id": new_label, "label": new_label}}
            app_handler.add_node(node_data)
            st.rerun()

    st.sidebar.subheader("Add Edge")
    with st.popover("Add_Edge", icon=":material/thumb_up:", help="Add a new edge"):
        st.markdown("### 🔗 Add Edge")
        all_nodes = [node["data"]["id"] for node in app_handler.state["nodes"]]
        source = st.selectbox("Source", all_nodes, key="edge_source")
        target = st.selectbox("Target", all_nodes, key="edge_target")
        edge_label = st.text_input("Label (optional)", "", key="edge_label_input")
        if st.button("Kante hinzufügen", key="edge_add_btn"):
            edge_data = {
                "data": {
                    "id": f"{source}-{target}",
                    "source": source,
                    "target": target
                }
            }
            if edge_label:
                edge_data["data"]["label"] = edge_label
            app_handler.add_edge(edge_data)
            st.rerun()

    st.sidebar.subheader("jupyterlab")
    
    if st.sidebar.button("Jupyterlab öffnen"):
        jupyterlite(800, 600)
        st.write("Hier können Sie auf jupyterlab zugreifen")
    
    with st.sidebar:
        st.header("🔧 Einstellungen")

        global show_mindmap
        global show_charts
        global show_files
        global show_preview
        global show_chat

        # Variablen in Session speichern
        st.session_state["show_mindmap"] = st.checkbox("🌍 Mindmap anzeigen", value=st.session_state.get("show_mindmap", True))
        st.session_state["show_charts"] = st.checkbox("📊 Matplotlib-Diagramme anzeigen", value=st.session_state.get("show_charts", True))
        st.session_state["show_files"] = st.checkbox("📂 File Browser anzeigen", value=st.session_state.get("show_files", True))
        st.session_state["show_preview"] = st.checkbox("📝 Datei Vorschau anzeigen", value=st.session_state.get("show_preview", True))
        st.session_state["show_chat"] = st.checkbox("💬 Chat anzeigen", value=st.session_state.get("show_chat", True))

        #st.subheader("📁 Datei-Explorer")
        #event = st_file_browser(path="./", key="file_browser_sidebar", show_choose_folder=True)
        #st.write(event)


