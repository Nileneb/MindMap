import os
from langchain.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


# 📂 **Ordner mit Skripten und Dokumenten**
DOCUMENTS_DIR = (None)

def create_document_index(DOCUMENTS_DIR):
    """Erstellt einen FAISS-Index aus allen Dokumenten in einem bestimmten Ordner."""
    
    # ✅ **Alle relevanten Dateien sammeln**
    documents = []
    for file in os.listdir(DOCUMENTS_DIR):
        if file.endswith((".md", ".txt", ".json", ".py")):  # Wähle relevante Formate
            file_path = os.path.join(DOCUMENTS_DIR, file)
            loader = TextLoader(file_path)
            documents.extend(loader.load())  # Dateiinhalt einlesen

    if not documents:
        print("⚠️ Keine Dokumente gefunden!")
        return None

    # ✅ **Embeddings erstellen & FAISS-Index speichern**
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(documents, embeddings)
    
    faiss_index_path = "faiss_index"
    # **Speicher den Index**
    vectorstore.save_local(faiss_index_path)
    print(f"✅ FAISS-Index mit {len(documents)} Dokumenten erstellt!")

    return faiss_index_path


