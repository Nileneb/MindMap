import os
import json
from core.utils import logger
from config import FILE_EXTENSIONS, MINDMAP_SCHEMA
def parse_scripts_from_folder(json_path: str, ) -> dict:  #schema: dict = None //2.Argument?? 
    """
    Ergänzt Skriptnodes zur bestehenden JSON-Struktur basierend auf den vorhandenen Ordnern.
    SKRIPT ANHÄNGEN AN PROJ_SCANNER.PY???!!!!!!
    :param json_path: Pfad zur gespeicherten JSON-Datei mit Ordnerstruktur.
    :param schema: Optionales Farbschema für Dateitypen.
    :return: Aktualisierte Nodes und Edges mit Skriptdaten.
    """

    # JSON-Struktur laden
    with open(json_path, "r") as json_file:
        tree = json.load(json_file)

    
    nodes = tree["nodes"]
    edges = tree["edges"]
    node_ids = {node["data"]["id"] for node in nodes}  # Schnellere Überprüfung vorhandener Nodes

    # Iteriere über die Ordner und suche Skripte
    for node in nodes:
        node_id = node["data"]["id"]
        if os.path.isdir(node_id):
            # Alle Skripte im aktuellen Ordner auflisten
            try:
                files = [f for f in os.listdir(node_id) if os.path.isfile(os.path.join(node_id, f))]
            except Exception as e:
                logger.error(f"Fehler beim Lesen des Ordners {node_id}: {e}")
                continue  # Ignoriere fehlerhafte Ordner

            for file_name in files:
                file_id = os.path.join(node_id, file_name)
                file_ext = os.path.splitext(file_name)[1]
                
                 # Farbe aus FILE_EXTENSIONS oder Standardfarbe setzen
                file_color = FILE_EXTENSIONS.get(file_ext, {}).get("color", "#9e9e9e")

                # Skript-Node erstellen, falls noch nicht vorhanden
                if file_id not in node_ids:
                    nodes.append({
                        "data": {
                            "id": file_id,
                            "label": file_name,
                            "type": "file",
                            "extension": file_ext,
                            "color": file_color,
                            "shape": MINDMAP_SCHEMA["file"]["shape"],
                            "group": node_id  # Gruppiert nach Ordner
                        }
                    })
                    node_ids.add(file_id)

                # Edge zwischen Ordner und Skript hinzufügen
                edges.append({
                    "data": {
                        "source": node_id,
                        "target": file_id
                    }
                })

    return {"nodes": nodes, "edges": edges}


def save_updated_json(tree: dict, output_path: str) -> None:
    """
    Speichert die aktualisierte JSON-Struktur nach dem Parsing der Skripte.
    """
    try:
        with open(output_path, "w") as json_file:
            json.dump(tree, json_file, indent=4)
        logger.info(f"✅ Aktualisierte JSON gespeichert: {output_path}")
    except Exception as e:
        logger.error(f"❌ Fehler beim Speichern der aktualisierten JSON: {e}")
        raise
