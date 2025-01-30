import os
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from config import FILE_EXTENSIONS_LIST, FAISS_INDEX_DIR

# 📂 **Ordner mit Skripten und Dokumenten**

def create_document_index(FAISS_INDEX_DIR):
    """Erstellt einen FAISS-Index aus allen Dokumenten in einem bestimmten Ordner."""
    
    # ✅ **Alle relevanten Dateien sammeln**
    documents = []
    for file in os.listdir(FAISS_INDEX_DIR):
        if file.endswith(tuple(FILE_EXTENSIONS_LIST)):  
            file_path = os.path.join(FAISS_INDEX_DIR, file)
            loader = TextLoader(file_path)
            documents.extend(loader.load())  # Dateiinhalt einlesen

    if not documents:
        print("⚠️ Keine Dokumente gefunden!")
        return None

    # ✅ **Embeddings erstellen & FAISS-Index speichern**
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(documents, embeddings)
    
    faiss_index_path = FAISS_INDEX_DIR
    # **Speicher den Index**
    vectorstore.save_local(faiss_index_path)
    print(f"✅ FAISS-Index mit {len(documents)} Dokumenten erstellt!")

    return faiss_index_path


