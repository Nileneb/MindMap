

# Pfad-Konfiguration
filepath = ("data/Backup/python_basic.json")
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

