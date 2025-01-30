import json
import psycopg2
import os
from dotenv import load_dotenv  # Add this import

load_dotenv()  # Load environment variables

def save_mindmap(json_path, mindmap_id):
    """Speichert eine Mindmap aus einer JSON-Datei in PostgreSQL."""
    
    # ✅ Verbindung zur PostgreSQL-Datenbank aufbauen
    conn = psycopg2.connect(
        dbname=os.getenv("dbname"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        host=os.getenv("host")
    )
    cursor = conn.cursor()

    # ✅ JSON-Datei einlesen
    with open(json_path, "r") as file:
        data = json.load(file)

    # ✅ Sicherstellen, dass `mindmap_id` ein STRING ist (keine Pfadangabe)
    mindmap_id = os.path.basename(json_path).replace(".json", "")  # Nur Dateiname als ID nehmen

    # ✅ Nodes speichern
    node_map = {}  # Mapping für IDs erstellen
    for node in data["nodes"]:
        cursor.execute(
            "INSERT INTO nodes (label, mindmap_id) VALUES (%s, %s) RETURNING id;",
            (node["data"]["label"], mindmap_id),
        )
        node_id = cursor.fetchone()[0]
        node_map[node["data"]["id"]] = node_id  # Mappe alte ID auf neue SQL-ID

    # ✅ Edges speichern (IDs müssen übersetzt werden!)
    for edge in data["edges"]:
        source_id = node_map.get(edge["data"]["source"])
        target_id = node_map.get(edge["data"]["target"])

        if source_id and target_id:
            cursor.execute(
                "INSERT INTO edges (source, target, mindmap_id) VALUES (%s, %s, %s);",
                (source_id, target_id, mindmap_id)
            )

    # ✅ Änderungen speichern & Verbindung schließen
    conn.commit()
    conn.close()
    print(f"✅ Mindmap '{mindmap_id}' erfolgreich in PostgreSQL gespeichert!")


