import logging
import os
from datetime import datetime

#loader
import glob
# Pfad für JSON-Dateien
filepattern = "data/Backup/*.json"
import streamlit as st


log_dir = "logs"  # Could also pull from config.py if you prefer
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

if not logging.getLogger().hasHandlers():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'{log_dir}/mindmap_{datetime.now().strftime("%Y%m%d")}.log'),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)



def render_file_selector(filepattern):
    """Listet alle JSON-Dateien auf und gibt die Auswahl zurück."""
    # Alle Dateien suchen
    json_files = glob.glob(filepattern)
    if not json_files:
        st.error("Keine JSON-Dateien gefunden!")
        return None

    # Nur Dateinamen für Dropdown anzeigen
    filenames = [os.path.basename(file) for file in json_files]
    
    # Dropdown-Menü für die Auswahl
    selected_file = st.selectbox("Verfügbare JSON-Dateien:", filenames)
    full_path = os.path.join(os.path.dirname(filepattern), selected_file)
    st.success(f"Ausgewählte Datei: {full_path}")
    return full_path


def load_css():
    with open("style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
