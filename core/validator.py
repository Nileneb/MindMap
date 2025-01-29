import json
from jsonschema import validate, ValidationError

def load_schema(schema_path="core/cytoscape_schema.json"):
    """Lädt das Cytoscape-JSON-Schema aus einer Datei."""
    try:
        with open(schema_path, "r") as schema_file:
            return json.load(schema_file)
    except FileNotFoundError:
        print(f"⚠️ Schema-Datei nicht gefunden: {schema_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"⚠️ Fehler beim Laden des JSON-Schemas: {e}")
        return None

def validate_cytoscape_data(data, schema_path="cytoscape_schema.json"):
    """
    Validiert die Cytoscape-Daten basierend auf dem offiziellen JSON-Schema.
    :param data: Die zu validierenden Daten.
    :param schema_path: Pfad zur JSON-Schema-Datei.
    :return: True, wenn die Daten gültig sind, sonst False.
    """
    schema = load_schema(schema_path)
    if schema is None:
        print("⚠️ Kein gültiges Schema gefunden. Überspringe Validierung.")
        return False

    try:
        validate(instance=data, schema=schema)
        print("✅ Die generierten Cytoscape-Daten sind gültig.")
        return True
    except ValidationError as e:
        print(f"❌ Ungültige Cytoscape-Daten: {e.message}")
        return False
