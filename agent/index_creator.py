import os
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from config import FILE_EXTENSIONS_LIST, FAISS_INDEX_DIR



def create_document_index(apphandler=None, uploaded_file=None, output_folder=None):
    """Erstellt einen FAISS-Index aus allen Dokumenten in einem bestimmten Ordner."""
    
    file_path = output_folder
    # ✅ **Alle relevanten Dateien sammeln**
    documents = []
    for file in os.listdir(output_folder):
        if file.endswith(tuple(FILE_EXTENSIONS_LIST)):  
            full_file_path = os.path.join(output_folder, file)  # Vollständigen Pfad erstellen
            loader = TextLoader(full_file_path)  # Nur den vollständigen Pfad übergeben
            documents.extend(loader.load())  # Dateiinhalt einlesen

    if not documents:
        print("⚠️ Keine Dokumente gefunden!")
        return None

    # ✅ **Embeddings erstellen & FAISS-Index speichern**
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(documents, embeddings)
    
    faiss_index_path = os.path.join(FAISS_INDEX_DIR, os.path.basename(full_file_path))  # Indexpfad anpassen
    # **Speicher den Index**
    vectorstore.save_local(faiss_index_path)
    print(f"✅ FAISS-Index mit {len(documents)} Dokumenten erstellt!")
    
    return faiss_index_path


