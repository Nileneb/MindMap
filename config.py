import os

# Pfad-Konfiguration



filepattern = "data/Backup/*.json" #(Suchmuster für JSON-Dateien)
#selected_file = st.selectbox("Verfügbare JSON-Dateien:", filenames) (Dateiauswahl über Streamlit
Projectname = "Projectname"
PROJECTS_BASE_DIR = "data/Projects"
UPLOADS_DIR = os.path.join(PROJECTS_BASE_DIR, "{Projectname}/uploads/")
FAISS_INDEX_DIR = os.path.join(PROJECTS_BASE_DIR, "{Projectname}/faiss_index/")
MINDMAPS_DIR = os.path.join(PROJECTS_BASE_DIR, "{Projectname}/mindmaps/")
PARSED_DIR = os.path.join(PROJECTS_BASE_DIR, "{Projectname}/parsed/")

#filepath = "data/Projects/{Projectname}"
#faiss_index_path = "data/Projects/{Projectname}/faiss_index"
#MINDMAP_OUTPUT_PATH = "data/Projects/{Projectname}/mindmaps/"
#Uploads = "data/Projects/{Projectname}/uploads/"
#JSON-Mindmaps = "data/Projects/{Projectname}/mindmaps/"
#Parsed_Files = "data/Projects/{Projectname}/parsed/"
#WORKING_DIR = "data/Projects"


layout = {
    "name": "cose",
    "fit": True,
    "directed": True,
    "padding": 10,
    "spacingFactor": 1.75,
    "animate": False
}
# Alternativen: "grid", "circle", "cose", "dagre" "breadthfirst" "preset"
# Verfügbare Node-Shapes
AVAILABLE_SHAPES = ["ellipse", "rectangle", "triangle", "diamond"]
stylesheet = [
    {
        "selector": "node",
        "style": {
            "label": "data(label)",
            "background-color": "data(color)",
            "shape": "data(shape)",
            "color": "black",
            "font-size": "12px",
            "text-valign": "center",
            "text-halign": "center",
            "width": "60px",
            "height": "60px"
        }
    },
    {
        "selector": "edge",
        "style": {
            "label": "data(label)",
            "width": 2,
            "line-color": "gray",
            "target-arrow-color": "black",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier"
        }
    }
]
MINDMAP_SCHEMA = {
    "root": {"color": "#f44336", "shape": "rectangle"},  # 🔴 Root-Folder hebt sich ab
    "folder": {"color": "#90caf9", "shape": "rectangle"},
    "file": {"color": "#e57373", "shape": "ellipse"},
}

FILE_EXTENSIONS = {
    ".py": {"color": "#9CF18A"},
    ".json": {"color": "#81c784"},
    ".txt": {"color": "#ffb74d"},
    ".md": {"color": "#9575cd"},
    ".sh": {"color": "#ff9800"},
    ".html": {"color": "#f44336"},
    ".css": {"color": "#3f51b5"},
    ".js": {"color": "#ffeb3b"},
}

# Falls ein Skript nur die Endungen (ohne Farben) braucht:
FILE_EXTENSIONS_LIST = list(FILE_EXTENSIONS.keys())

        
# Elements= Daten INHALT
# stylesheet= Stylesheet WIE werden daten dargestellt
# layout= WIE werden daten angeordnet
