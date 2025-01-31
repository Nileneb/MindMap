import json
import psycopg2
import os
from dotenv import load_dotenv
#from config import MINDMAPS_DIR  # 🔥 Einheitliche Pfade aus der Config nutzen!

load_dotenv()

def save_mindmap(apphandler):
    """Speichert eine Mindmap aus einer JSON-Datei in PostgreSQL."""
    
    # ✅ PostgreSQL-Verbindung herstellen
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")

    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST
    )
    cursor = conn.cursor()

    # ✅ Einheitlichen Mindmap-Pfad nutzen!
    
    json_path = apphandler.filepath

    if not os.path.isfile(json_path):
        print(f"❌ Mindmap-Datei nicht gefunden oder ist ein Verzeichnis: {json_path}")
        return


    if not os.path.exists(json_path):
        print(f"❌ Mindmap-Datei nicht gefunden: {json_path}")
        return

    # ✅ JSON einlesen
    with open(json_path, "r") as file:
        data = json.load(file)

    # ✅ Sicherstellen, dass `mindmap_id` sich aus dem Projektnamen ableitet
    mindmap_id = apphandler.project_name.replace(".json", "")

    # ✅ Nodes speichern
    node_map = {}  
    # ✅ Nodes speichern (mit chunk_id!)
    for node in data["nodes"]:
        cursor.execute(
            "INSERT INTO nodes (label, mindmap_id, chunk_id) VALUES (%s, %s, %s) RETURNING id;",
            (node["data"]["label"], mindmap_id, node["data"].get("chunk_id", None))
        )
        node_id = cursor.fetchone()[0]
        node_map[node["data"]["id"]] = node_id  

    # ✅ Edges speichern (mit index_id!)
    for edge in data["edges"]:
        source_id = node_map.get(edge["data"]["source"])
        target_id = node_map.get(edge["data"]["target"])
        index_id = edge["data"].get("index_id", None)

        if source_id and target_id:
            cursor.execute(
                "INSERT INTO edges (source, target, mindmap_id, index_id) VALUES (%s, %s, %s, %s);",
                (source_id, target_id, mindmap_id, index_id)
            )

    # ✅ Änderungen speichern & Verbindung schließen
    conn.commit()
    conn.close()
    print(f"✅ Mindmap '{mindmap_id}' erfolgreich in PostgreSQL gespeichert!")
