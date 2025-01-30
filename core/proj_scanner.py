import os
import json
import streamlit as st
from core.utils import logger
from core.validator import validate_cytoscape_data
from core.db_connector import save_mindmap
from agent.index_creator import create_document_index
from config import MINDMAP_SCHEMA, FILE_EXTENSIONS, UPLOADS_DIR, FAISS_INDEX_DIR

def parse_folder_to_tree(folder_path: str) -> dict:
    """Erstellt eine hierarchische Mindmap mit FAISS-Index für Inhalte."""
    if not os.path.isdir(folder_path):
        raise ValueError(f"❌ Ungültiger Ordner: {folder_path}")

    nodes, edges, node_ids = [], [], set()
    faiss_index_paths = {}

    # CHUNK 1: Ordner als Hauptknoten indexieren
    for root, dirs, files in os.walk(folder_path):
        if "__pycache__" in root or "venv" in root:
            continue

        root_id = os.path.abspath(root)
        chunk_id = f"chunk_{hash(root_id)}"

        if root_id not in node_ids:
            nodes.append({
                "data": {
                    "id": root_id,
                    "label": os.path.basename(root),
                    "color": MINDMAP_SCHEMA["folder"]["color"],
                    "shape": MINDMAP_SCHEMA["folder"]["shape"],
                    "chunk_id": chunk_id  # Speichert die Chunk-Referenz
                }
            })
            node_ids.add(root_id)

        # CHUNK 2: Dateien als Subchunks hinzufügen
        for file_name in files:
            file_id = os.path.join(root, file_name)
            file_ext = os.path.splitext(file_name)[1]
            file_color = FILE_EXTENSIONS.get(file_ext, {}).get("color", "#9e9e9e")
            index_id = f"index_{hash(file_id)}"

            if file_id not in node_ids:
                nodes.append({
                    "data": {
                        "id": file_id,
                        "label": file_name,
                        "color": file_color,
                        "shape": MINDMAP_SCHEMA["file"]["shape"],
                        "chunk_id": chunk_id,  # Datei gehört zum übergeordneten Chunk
                        "index_id": index_id  # Individuelle Index-Referenz für Retrieval
                    }
                })
                node_ids.add(file_id)

            edges.append({
                "data": {
                    "source": root_id,
                    "target": file_id,
                    "index_id": index_id  # Relation zwischen Ordner-Chunk und Datei-Index
                }
            })

            # CHUNK 3: Datei-Inhalt vektorisieren und als FAISS-Index speichern
            if file_ext in FILE_EXTENSIONS.get(file_ext, {}).get("color", "#9e9e9e"):  #mit color??
                faiss_path = create_document_index(file_id)
                if faiss_path:
                    faiss_index_paths[file_id] = faiss_path

    return {"nodes": nodes, "edges": edges, "faiss_index_paths": faiss_index_paths}

def save_tree_to_json(tree: dict, output_path: str) -> None:
    """Speichert die generierte Mindmap als JSON."""
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
