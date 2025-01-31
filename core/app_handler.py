import os
import json
import streamlit as st
from core.utils import logger


ROLES = [None, "Requester", "Responder", "Admin"]

@st.cache_data
def load_json_from_filepath(filepath):
    """Lädt JSON-Daten aus einer Datei."""
    try:
        abs_path = os.path.abspath(filepath)
        if not os.path.exists(abs_path):
            logger.warning(f"Datei nicht gefunden: {abs_path}. Initialisiere leeren Zustand.")
            return {"nodes": [], "edges": []}
        with open(abs_path, "r") as f:
            data = json.load(f)
        logger.info(f"JSON geladen: {len(data['nodes'])} Nodes, {len(data.get('edges', []))} Edges.")
        return data
    except Exception as e:
        logger.error(f"Fehler beim Laden der JSON-Datei: {e}")
        return {"nodes": [], "edges": []}

def extract_attributes_from_stylesheet(stylesheet, selector):
    """Extrahiert Attribute basierend auf dem Stylesheet-Selector."""
    style = next((entry["style"] for entry in stylesheet if entry["selector"] == selector), None)
    if not style:
        return []  # Fallback, falls kein gültiger Selector gefunden wird

    # Suche nach allen "data(...)"-Einträgen, die Attribute referenzieren
    attributes = [
        value.split("(")[1].split(")")[0]
        for key, value in style.items()
        if isinstance(value, str) and "data(" in value
    ]
    return attributes


class AppHandler:
    def __init__(self, filepath, stylesheet, layout, project_name, role=None):
        if not os.path.isdir(filepath):
            raise ValueError(f"❌ Der Pfad {filepath} ist kein gültiges Verzeichnis.")
        self.filepath = filepath
        self.stylesheet = stylesheet
        self.layout = layout
        self.role = role
        self.project_name = project_name
        self.state = {"nodes": [], "edges": []}
        self.node_attributes = extract_attributes_from_stylesheet(stylesheet, "node")
        self.edge_attributes = extract_attributes_from_stylesheet(stylesheet, "edge")
        self.initialize_session_state()

    def validate_elements(self, elements):
        """Stellt sicher, dass Nodes und Edges eine gültige Struktur haben."""
        validated_nodes = [
            node for node in elements.get("nodes", [])
            if isinstance(node, dict) and "data" in node and isinstance(node["data"], dict)
        ]
        validated_edges = [
            edge for edge in elements.get("edges", [])
            if isinstance(edge, dict) and "data" in edge and isinstance(edge["data"], dict)
        ]
        return {"nodes": validated_nodes, "edges": validated_edges}

    def transform_elements(self, elements):
        """Transformiert die von Cytoscape gelieferten Elemente in das erwartete Format."""
        transformed_nodes = [
            {"data": {"id": node, "label": node}} if isinstance(node, str) else node
            for node in elements.get("nodes", [])
        ]
        transformed_edges = [
            {"data": {"id": edge, "source": edge.split('-')[0], "target": edge.split('-')[1]}} 
            if isinstance(edge, str) else edge
            for edge in elements.get("edges", [])
        ]
        return {"nodes": transformed_nodes, "edges": transformed_edges}

    def set_selected_elements(self, selected_elements):
        """Setzt transformierte ausgewählte Elemente."""
        transformed_elements = self.transform_elements(selected_elements)
        st.session_state["selected_elements"] = transformed_elements
        logger.info(
            f"Ausgewählte Elemente aktualisiert: {len(transformed_elements['nodes'])} Nodes, "
            f"{len(transformed_elements['edges'])} Edges."
        )

    def get_selected_elements(self):
        """Gibt transformierte und validierte ausgewählte Elemente zurück."""
        selected_elements = st.session_state.get("selected_elements", {"nodes": [], "edges": []})
        return self.transform_elements(selected_elements)
    
    def trigger_cytoscape_update(self):
        """Stellt sicher, dass Cytoscape aktualisiert wird."""
        current_elements = self.get_elements()
        st.session_state["cytoscape_update"] = current_elements
        logger.info(f"Cytoscape wurde mit {len(current_elements)} Elementen aktualisiert.")
    def update_node(self, node_id, new_data):
        """Aktualisiert eine Node basierend auf gültigen Attributen."""
        for node in self.state["nodes"]:
            if node.get("data", {}).get("id") == node_id:
                # Filtere ungültige Attribute
                valid_data = {key: value for key, value in new_data.items() if key in self.node_attributes}
                if valid_data:
                    node["data"].update(valid_data)
                    self.save_state()
                    self.trigger_cytoscape_update()  # Cytoscape aktualisieren
                    logger.info(f"Node {node_id} aktualisiert: {valid_data}")
                    return True
        logger.warning(f"Node mit ID {node_id} nicht gefunden.")
        return False

    def update_edge(self, edge_id, new_data):
        """Aktualisiert eine Edge basierend auf gültigen Attributen."""
        for edge in self.state["edges"]:
            if edge.get("data", {}).get("id") == edge_id:
                # Filtere ungültige Attribute
                valid_data = {key: value for key, value in new_data.items() if key in self.edge_attributes}
                if valid_data:
                    edge["data"].update(valid_data)
                    self.save_state()
                    self.trigger_cytoscape_update()  # Cytoscape aktualisieren
                    logger.info(f"Edge {edge_id} aktualisiert: {valid_data}")
                    return True
        logger.warning(f"Edge mit ID {edge_id} nicht gefunden.")
        return False
    

    def load_state(self):
        """Lädt den Zustand und aktualisiert den Session-State."""
        # Entferne die doppelte Zuweisung und stelle sicher, dass der korrekte Pfad verwendet wird
        self.state = load_json_from_filepath(os.path.join(self.filepath, f"{self.project_name}.json") if self.project_name else self.filepath)
        st.session_state.state = self.state

    def save_state(self):
        """Speichert den aktuellen Zustand in die JSON-Datei."""
        try:
            abs_path = os.path.abspath(self.filepath)
            with open(abs_path, "w") as f:
                json.dump(self.state, f, indent=2)
            logger.info(f"State erfolgreich in {abs_path} gespeichert.")
        except Exception as e:
            logger.error(f"Fehler beim Speichern der JSON-Datei: {e}")

    def add_node(self, node_data):
        """Fügt einen Node hinzu."""
        self.state["nodes"].append(node_data)
        self.save_state()
        self.trigger_cytoscape_update()  # Cytoscape aktualisieren

    def add_edge(self, edge_data):
        """Fügt eine Edge hinzu."""
        self.state["edges"].append(edge_data)
        self.save_state()
        self.trigger_cytoscape_update()  # Cytoscape aktualisieren
    
    def get_elements(self):
        """Gibt die Liste der Nodes und Edges zurück."""
        return self.state.get("nodes", []) + self.state.get("edges", [])

    def update_selected_elements(self, selected_elements):
        """Aktualisiert die Nodes und Edges basierend auf den ausgewählten Elementen."""
        updated_nodes = selected_elements.get("nodes", [])
        updated_edges = selected_elements.get("edges", [])

        # Aktualisiere bestehende Nodes
        for updated_node in updated_nodes:
            self.update_node(updated_node["data"]["id"], updated_node["data"])

        # Aktualisiere bestehende Edges
        for updated_edge in updated_edges:
            self.update_edge(updated_edge["data"]["id"], updated_edge["data"])
    

    def initialize_session_state(self):
        """Initialisiert den Session State für die ausgewählten Elemente."""
        if "selected_elements" not in st.session_state:
            st.session_state["selected_elements"] = {"nodes": [], "edges": []}
        
        # Initialize conversation in session state
        if "conversation" not in st.session_state:
            st.session_state.conversation = []

        # Initialize role in session state
        if "role" not in st.session_state:
            st.session_state.role = None

    # Parsing-Helfer
    def save_tree_to_json(self, tree):
        """Speichert einen JSON-Baum in den zentralen filepath."""
        with open(self.filepath, "w") as f:
            json.dump(tree, f, indent=4)
        logger.info(f"JSON gespeichert: {self.filepath}")