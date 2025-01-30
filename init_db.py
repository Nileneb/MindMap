import os
import psycopg2
from psycopg2 import sql

# Lade die Umgebungsvariablen
DB_NAME = os.getenv("DB_NAME", "mindmap")
DB_USER = os.getenv("DB_USER", "mindmap_user")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")

if not DB_PASSWORD:
    raise ValueError("No DB_PASSWORD environment variable set.")

# Verbindung herstellen
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST
)
cursor = conn.cursor()

# SQL-Befehle zum Erstellen des Schemas
CREATE_TABLES_SQL = """
DROP TABLE IF EXISTS edges;
DROP TABLE IF EXISTS nodes;

CREATE TABLE nodes (
    id SERIAL PRIMARY KEY,
    label TEXT NOT NULL,
    mindmap_id TEXT NOT NULL,
    chunk_id TEXT,    
    index_id TEXT     
);

CREATE TABLE edges (
    id SERIAL PRIMARY KEY,
    source INT REFERENCES nodes(id) ON DELETE CASCADE,
    target INT REFERENCES nodes(id) ON DELETE CASCADE,
    mindmap_id TEXT NOT NULL,
    index_id TEXT  
);
"""

try:
    cursor.execute(CREATE_TABLES_SQL)
    conn.commit()
    print("✅ Datenbank erfolgreich initialisiert!")
except Exception as e:
    print(f"❌ Fehler beim Erstellen der Tabellen: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()
