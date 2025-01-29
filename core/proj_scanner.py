import os
import json
import streamlit as st
from core.utils import logger
from core.validator import validate_cytoscape_data
from core.script_parser import parse_scripts_from_folder, save_updated_json
from core.db_connector import save_mindmap
from agent.index_creator import create_document_index

def parse_folder_to_tree(folder_path: str, layout: dict, schema: dict = None) -> dict:
    """
    Parst einen Ordner und erstellt Nodes und Edges basierend auf der Ordnerstruktur.
    - Root-Ordner bekommt als einziges Label den vollständigen Folderpath.
    - Edges haben kein Label für bessere Lesbarkeit.
    - Root-Ordner wird farblich hervorgehoben.
    """
    if not os.path.isdir(folder_path):
        raise ValueError(f"Der angegebene Pfad ist kein gültiger Ordner: {folder_path}")

    if schema is None:
        schema = {
            "root": {"color": "#f44336", "shape": "rectangle"},  # 🔴 Root-Folder hebt sich ab
            "folder": {"color": "#90caf9", "shape": "rectangle"},
            "file": {"color": "#e57373", "shape": "ellipse"},
            "extensions": {
                ".py": {"color": "#64b5f6"},
                ".json": {"color": "#81c784"},
                ".txt": {"color": "#ffb74d"},
                ".md": {"color": "#9575cd"}
            }
        }

    nodes = []
    edges = []
    node_ids = set()

    x_offset = 3
    y_offset = 3
    level_positions = {}

    def calculate_position(level: int) -> dict:
        if level not in level_positions:
            level_positions[level] = 0
        x = level_positions[level]
        level_positions[level] += x_offset
        y = level * y_offset
        return {"x": x, "y": y}

    root_folder_id = os.path.abspath(folder_path)
    faiss_index_paths = {}  # Speichert Index-Pfade für jeden Ordner
    
    for root, dirs, files in os.walk(folder_path):
        if "__pycache__" in root or "venv" in root:
            continue

        root_id = os.path.abspath(root)
        level = root.count(os.sep)

        # **FAISS-Index für diesen Ordner erstellen**
        faiss_path = create_document_index(root)  # 🔥 Index für den aktuellen Ordner erstellen
        if faiss_path:
            faiss_index_paths[root] = faiss_path  # Speichern
        # Setze Root-Ordner-Farbe und Label
        folder_color = schema["root"]["color"] if root_id == root_folder_id else schema["folder"]["color"]
        folder_label = root_id if root_id == root_folder_id else os.path.basename(root)

        if root_id not in node_ids:
            nodes.append({
                "data": {
                    "id": root_id,
                    "label": folder_label,  # ✅ Root-Ordner hat vollständigen Pfad als Label
                    "color": folder_color,
                    "shape": schema["folder"]["shape"]
                },
                "position": calculate_position(level)
            })
            node_ids.add(root_id)

        for dir_name in dirs:
            dir_id = os.path.join(root, dir_name)
            if "__pycache__" in dir_id or "venv" in dir_id:
                continue
            if dir_id not in node_ids:
                nodes.append({
                    "data": {
                        "id": dir_id,
                        "label": dir_name,  # ✅ Subfolder haben NUR ihren Namen als Label
                        "color": schema["folder"]["color"],
                        "shape": schema["folder"]["shape"]
                    },
                    "position": calculate_position(level + 1)
                })
                node_ids.add(dir_id)
            create_document_index(dir_name)  # 🔥 **Index für jeden Subfolder erstellen**
            st.success(f"✅ Index für Subfolder erstellt: {dir_name}")

            # ✅ Edges haben **kein** Label mehr
            edges.append({
                "data": {
                    "source": root_id,
                    "target": dir_id
                }
            })

    return {"nodes": nodes, "edges": edges, "faiss_index_paths": faiss_index_paths}


def save_tree_to_json(tree: dict, output_path: str) -> None:
    """
    Speichert die Baumstruktur als JSON-Datei, nachdem sie validiert wurde.
    Anschließend werden die Skripte erfasst und integriert.
    """
    if not validate_cytoscape_data(tree):
        logger.error("❌ Die generierten Daten sind ungültig und werden NICHT gespeichert!")
        return

    try:
        with open(output_path, "w") as json_file:
            json.dump(tree, json_file, indent=4)
        logger.info(f"✅ JSON erfolgreich gespeichert: {output_path}")

        # ✅ 🔥 Skript-Nodes hinzufügen
        updated_tree = parse_scripts_from_folder(output_path)
        save_updated_json(updated_tree, output_path)
        # ✅ 🔥 **Cache leeren, damit die neue Mindmap geladen wird**
        st.cache_data.clear()

        # ✅ 🔥 **Seite automatisch neu laden, um die neue Mindmap anzuzeigen!**
        st.success(f"✅ JSON gespeichert: {output_path}")
        save_mindmap(output_path, "w")  # 📁 Datenbank speichern
        
        st.rerun()  # 🔄 Seite neu laden

    except Exception as e:
        logger.error(f"❌ Fehler beim Speichern des JSON: {e}")
        raise