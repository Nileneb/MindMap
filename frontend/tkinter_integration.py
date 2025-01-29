import os
import tkinter as tk
from tkinter import filedialog
import streamlit as st
from core.proj_scanner import parse_folder_to_tree, save_tree_to_json



def render_folder_selection_sidebar(app_handler):
    """Erstellt das UI für die Ordnerauswahl (headless-kompatibel)."""
    st.sidebar.subheader("Ordner auswählen")

    # Eingabe für den Input-Folder
    input_folder = st.text_input("Input-Ordner auswählen:", value="", placeholder="Pfad zum Ordner eingeben")
    st.session_state["input_folder"] = input_folder

    # Output-Folder anzeigen
    output_folder = app_handler.filepath
    st.sidebar.write(f"Output-Ordner: {output_folder}")

    # Parsing starten
    if st.button("Ordner auslesen und speichern"):
        if input_folder:
            folder_name = os.path.basename(input_folder.rstrip(os.sep))
            # Extrahiere den Ordner aus dem app_handler.filepath
            output_folder = os.path.dirname(app_handler.filepath)

            if not os.path.isdir(output_folder):
                st.error(f"Output-Ordner ist kein gültiges Verzeichnis: {output_folder}")
            else:
                output_file = os.path.join(output_folder, f"{folder_name}.json")
                try:
                    tree = parse_folder_to_tree(input_folder, layout=app_handler.layout)
                    save_tree_to_json(tree, output_file)
                    st.success(f"JSON gespeichert: {output_file}")
                except ValueError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Fehler beim Speichern des JSON: {e}")
        else:
            st.error("Bitte einen gültigen Ordnerpfad eingeben!")




