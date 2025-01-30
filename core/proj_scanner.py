import os
import json
import streamlit as st
from core.utils import logger
from core.validator import validate_cytoscape_data
from core.db_connector import save_mindmap
from agent.index_creator import create_document_index
from config import MINDMAP_SCHEMA, FILE_EXTENSIONS

def parse_folder_to_tree(folder_path: str) -> dict:
    """Parst einen Ordner und erstellt eine Mindmap."""
    if not os.path.isdir(folder_path):
        raise ValueError(f"❌ Ungültiger Ordner: {folder_path}")

    nodes, edges, node_ids = [], [], set()
    faiss_index_paths = {}

    for root, dirs, files in os.walk(folder_path):
        if "__pycache__" in root or "venv" in root:
            continue

        root_id = os.path.abspath(root)
        if root_id not in faiss_index_paths:
            faiss_path = create_document_index(root)
            if faiss_path:
                faiss_index_paths[root_id] = faiss_path

        if root_id not in node_ids:
            nodes.append({
                "data": {"id": root_id, "label": os.path.basename(root), "color": MINDMAP_SCHEMA["folder"]["color"],
                         "shape": MINDMAP_SCHEMA["folder"]["shape"]}})
            node_ids.add(root_id)

        for file_name in files:
            file_id = os.path.join(root, file_name)
            file_ext = os.path.splitext(file_name)[1]
            file_color = FILE_EXTENSIONS.get(file_ext, {}).get("color", "#9e9e9e")

            if file_id not in node_ids:
                nodes.append({"data": {"id": file_id, "label": file_name, "color": file_color, "shape": MINDMAP_SCHEMA["file"]["shape"]}})
                node_ids.add(file_id)

            edges.append({"data": {"source": root_id, "target": file_id}})

    return {"nodes": nodes, "edges": edges, "faiss_index_paths": faiss_index_paths}

def save_tree_to_json(tree: dict, output_path: str) -> None:
    """Speichert die generierte Baumstruktur als JSON."""
    if not validate_cytoscape_data(tree):
        logger.error("❌ Fehler: Ungültige Mindmap-Daten!")
        return

    try:
        with open(output_path, "w") as json_file:
            json.dump(tree, json_file, indent=4)
        logger.info(f"✅ Mindmap gespeichert: {output_path}")
        st.success(f"✅ JSON gespeichert: {output_path}")

        save_mindmap(output_path, "w")
        st.rerun()
    except Exception as e:
        logger.error(f"❌ Fehler beim Speichern: {e}")
