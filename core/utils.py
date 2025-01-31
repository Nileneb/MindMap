import logging
import os
from datetime import datetime

# loader
import glob
# Pfad für JSON-Dateien

import streamlit as st

#BASE_DIR = "data"  # Beispiel für Basisverzeichnis
#filepattern = os.path.join(BASE_DIR, "*.json")

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



def load_css():
    with open("style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
