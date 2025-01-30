import json
from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# ✅ **Lokaler HuggingFace Embedder**
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# 📂 **Mindmap laden & Index automatisch erstellen**
def load_index_from_mindmap(json_path):
    with open(json_path, "r") as file:
        data = json.load(file)
    
    docs = []
    for node in data["nodes"]:
        text = f"Knoten: {node['data']['label']} ({node['data']['id']})"
        docs.append(Document(text=text))  
    
    for edge in data["edges"]:
        connection = f"Verbindung: {edge['data']['source']} → {edge['data']['target']}"
        docs.append(Document(text=connection))  

    # 🔍 **Automatisch den Index aus den Dokumenten erstellen**
    index = VectorStoreIndex.from_documents(docs)
    
    return index  # ✅ Rückgabe des Index direkt!

def query_index(index, question):
    return index.query(question)
