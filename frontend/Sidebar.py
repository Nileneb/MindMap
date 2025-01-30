import os
import streamlit as st
import tempfile
from streamlit_file_browser import st_file_browser
from core.utils import logger
from core.app_handler import AppHandler
from core.proj_scanner import parse_folder_to_tree, save_tree_to_json
from config import FILE_EXTENSIONS, FAISS_INDEX_DIR

# Style
#from streamlit_extras.stylable_container import stylable_container
# Jupyter
from streamlit_extras.jupyterlite import jupyterlite

faiss_index_path = FAISS_INDEX_DIR

# Module-Level Settings
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
    output_folder = app_handler.filepath
    
    ### 📂 **Datei-Explorer & Upload**
    #st.sidebar.subheader("📂 Datei-Explorer")
    #event = st_file_browser(path="./", key="file_browser_sidebar", show_choose_folder=True)
    #st.write(event)

    uploaded_file = st.sidebar.file_uploader("📁 Datei hochladen", type=list(FILE_EXTENSIONS.keys()))
    if uploaded_file:    
        #temp_dir = tempfile.gettempdir()
        #temp_file_path = output_folder
        with open(output_folder, "wb") as f:
            f.write(uploaded_file.getbuffer())
    
        st.session_state["uploaded_file_path"] 
        st.sidebar.success(f"✅ Datei gespeichert unter: {output_folder}")

    ### 📂 **Ordner Auswahl**
    input_folder = st.sidebar.text_input("📁 Input-Ordner:", value="", placeholder="Pfad zum Ordner eingeben")
    st.session_state["input_folder"] = output_folder

    ### 📂 **Output-Folder anzeigen**
    
    #st.sidebar.write(f"📂 Output-Ordner: `{output_folder}`")

    ### 📂 **Ordner analysieren und speichern**
    if st.sidebar.button("🚀 Ordner analysieren & speichern"):
        if input_folder:
            folder_name = os.path.basename(input_folder.rstrip(os.sep))
            output_folder = os.path.dirname(app_handler.filepath)

            if not os.path.isdir(output_folder):
                st.sidebar.error(f"❌ Output-Ordner ungültig: `{output_folder}`")
            else:
                output_file = os.path.join(output_folder, f"{folder_name}.json")
                try:
                    tree = parse_folder_to_tree(input_folder)
                    save_tree_to_json(tree, output_file)
                    st.sidebar.success(f"✅ JSON gespeichert: `{output_file}`")
                except ValueError as e:
                    st.sidebar.error(str(e))
                except Exception as e:
                    st.sidebar.error(f"❌ Fehler: {e}")
        else:
            st.sidebar.error("❌ Bitte einen gültigen Ordnerpfad eingeben!")

    ### 🛠 **Node- & Edge-Bearbeitung**
    st.sidebar.subheader("🔧 Knoten bearbeiten:")
    if selected_nodes:
        for idx, node in enumerate(selected_nodes):
            with st.sidebar.expander(f"Knoten {idx + 1}: {node['data'].get('label', '')}"):
                node_label = st.text_input("Label", value=node["data"].get("label", ""), key=f"node_label_{idx}")
                node_color = st.color_picker("Farbe", value=node["data"].get("color", "#90caf9"), key=f"node_color_{idx}")
                node_shape = st.selectbox("Shape", ["ellipse", "rectangle", "diamond"], index=0, key=f"node_shape_{idx}")

                if st.button(f"Speichern {idx + 1}", key=f"node_save_{idx}"):
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
        st.sidebar.write("⚠️ Keine Knoten ausgewählt.")

    st.sidebar.subheader("🔗 Kanten bearbeiten:")
    if selected_edges:
        for idx, edge in enumerate(selected_edges):
            with st.sidebar.expander(f"Kante {idx + 1}"):
                edge_label = st.text_input("Label", value=edge["data"].get("label", ""), key=f"edge_label_{idx}")
                edge_color = st.color_picker("Linienfarbe", value=edge["data"].get("line-color", "#000000"), key=f"edge_color_{idx}")

                if st.button(f"Kante speichern {idx + 1}", key=f"edge_save_{idx}"):
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
        st.sidebar.write("⚠️ Keine Kanten ausgewählt.")

    ### 🛠 **JupyterLab & Einstellungen**
    st.sidebar.subheader("⚙️ Einstellungen")
    st.session_state["show_mindmap"] = st.sidebar.checkbox("🌍 Mindmap anzeigen", value=st.session_state.get("show_mindmap", True))
    st.session_state["show_charts"] = st.sidebar.checkbox("📊 Charts anzeigen", value=st.session_state.get("show_charts", True))
    st.session_state["show_files"] = st.sidebar.checkbox("📂 File Browser", value=st.session_state.get("show_files", True))
    st.session_state["show_preview"] = st.sidebar.checkbox("📝 Datei Vorschau", value=st.session_state.get("show_preview", True))
    st.session_state["show_chat"] = st.sidebar.checkbox("💬 Chat", value=st.session_state.get("show_chat", True))

    if st.sidebar.button("📜 JupyterLab öffnen"):
        jupyterlite(800, 600)
        st.sidebar.write("JupyterLab gestartet...")
