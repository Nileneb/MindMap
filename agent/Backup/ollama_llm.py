import logging
from llama_index.core.indices.tree.select_leaf_embedding_retriever import TreeSelectLeafEmbeddingRetriever
from llama_index.core.schema import QueryBundle
from llama_index.core.agent.react import ReActAgent
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.llama_pack.base import BaseLlamaPack
from llama_index.core.indices.document_summary.base import DocumentSummaryIndex
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core.storage.index_store.keyval_index_store import KVIndexStore
from llama_index.core.storage.kvstore.simple_kvstore import SimpleKVStore
from llama_index.core.storage.docstore.keyval_docstore import KVDocumentStore
from pydantic import BaseModel
from typing import Dict, Any

from .reader import process_crawled_data_with_pandas_reader
from .setup_helpers import setup_llm_memory, setup_ollama_llm
from .config import IndexerConfig, LLMConfig

from llama_index.core.storage.index_store.simple_index_store import SimpleIndexStore  # Add this import

class Document(BaseModel):
    text: str
    metadata: Dict[str, Any] = {"source": "unknown"}

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# TreeSelectLeafEmbeddingRetriever erstellen
def create_tree_embedding_retriever(tree_index, embed_model, child_branch_factor=2):
    """
    Erstellt einen TreeSelectLeafEmbeddingRetriever.

    :param tree_index: Der TreeIndex, der verwendet wird.
    :param embed_model: Das Embedding-Modell.
    :param child_branch_factor: Anzahl der Kindknoten, die pro Ebene geprüft werden.
    :return: TreeSelectLeafEmbeddingRetriever-Instanz.
    """
    retriever = TreeSelectLeafEmbeddingRetriever(
        index=tree_index,
        embed_model=embed_model,
        child_branch_factor=child_branch_factor,
        verbose=True
    )
    return retriever

def setup_react_agent(tree_select_leaf_retriever, llm, config: IndexerConfig):
    """
    Erstellt einen ReActAgent, der mit dem TreeSelectLeafEmbeddingRetriever arbeitet.

    :param tree_select_leaf_retriever: TreeSelectLeafEmbeddingRetriever-Instanz.
    :param llm: Ollama LLM-Instanz.
    :param config: IndexerConfig-Instanz.
    :return: ReActAgent-Instanz.
    """
    try:
        # Tool mit Retriever verbinden
        retriever_tool = QueryEngineTool(
            tree_select_leaf_retriever,
            metadata=ToolMetadata(
                name="tree_select_embedding_tool",
                description="Führt semantische Abfragen auf dem TreeIndex durch."
            )
        )

        # ReAct-Agent erstellen
        agent = ReActAgent.from_tools(
            tools=[retriever_tool],
            llm=llm,
            verbose=True
        )

        logging.info("ReActAgent erfolgreich eingerichtet.")
        return agent
    except Exception as e:
        logging.error(f"Fehler beim Einrichten des ReActAgent für Konfiguration {config}: {e}", exc_info=True)
        return None

def create_query_tools(summary_index, sql_table):
    summary_tool = QueryEngineTool(
        summary_index.as_query_engine(),
        metadata={"name": "summary_tool", "description": "Zusammenfassungsabfragen."}
    )
    sql_tool = QueryEngineTool(
        sql_table.as_query_engine(),
        metadata={"name": "sql_tool", "description": "SQL-Abfragen für Kontext."}
    )
    return [summary_tool, sql_tool]

def setup_react_agent_with_tools(tools, llm):
    agent = ReActAgent.from_tools(tools=tools, llm=llm, verbose=True)
    return agent



def create_and_store_indices(documents, persist_dir, config, llm):
    """
    Erstellt TreeIndex und SummaryIndex und speichert sie in StorageContext.

    :param documents: Liste von Dokumenten.
    :param persist_dir: Verzeichnis für persistente Speicherung.
    :param config: IndexerConfig-Instanz.
    :param llm: Das verwendete LLM.
    """
    storage_context = setup_storage_context(config)  # Ensure correct parameter

    tree_summarizer = TreeSummarize(llm=llm)
    summarized_documents = [
        {"text": tree_summarizer.get_response(query_str="Fasse zusammen.", text_chunks=[doc['text']]), "metadata": doc.get("metadata", {})}
        for doc in documents
    ]

    vector_store = storage_context.vector_store
    index_store = storage_context.index_store

    for doc in summarized_documents:
        index_store.add(doc)
        vector_store.add_document(doc)

    storage_context.persist()
    logging.info(f"Indizes erfolgreich in {persist_dir} gespeichert.")
    return index_store, vector_store


def store_crawled_data(data):
    pandas_table = PandasStructTable()
    for item in data:
        pandas_table.add_entry(item)
    sql_table = SQLStructTable(context_dict={entry['URL']: entry['Content'] for entry in data})
    return pandas_table, sql_table

def save_crawled_data_to_csv(data, project_folder):
    csv_file_path = os.path.join(project_folder, 'website_overview.csv')
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    logging.info(f"Ergebnisse in {csv_file_path} gespeichert.")
    return csv_file_path

# Integration der Komponenten
from transformers import AutoModel  

class CustomLlamaPack(BaseLlamaPack):
    def __init__(self, base_url, max_tokens=1024, tokenizer=None):
        self.base_url = base_url
        self.max_tokens = max_tokens
        self.tokenizer = tokenizer
        # ...existing code using tokenizer...
        if self.base_url in MODEL_TOKENIZER_MAP:
            try:
                self.model = AutoModel.from_pretrained(self.base_url)
            except Exception as e:
                raise ValueError(f"Error initializing model {self.base_url}: {e}")
        else:
            raise ValueError(f"Unsupported model: {self.base_url}")

    def get_modules(self):
        return {"base_url": self.base_url, "max_tokens": self.max_tokens}

    def run(self, prompt):
        # Hier implementieren Sie Ihre LLM-Logik
        return f"Processed prompt: {prompt} with {self.base_url}"

def integrate_with_system(csv_file_path, config: IndexerConfig):
    """
    Integriert die LLM-Komponenten mit den Indizes und Abfragemodulen.

    :param csv_file_path: Pfad zur CSV-Datei
    :param config: IndexerConfig-Instanz
    :return: Dictionary mit allen Komponenten
    """
    try:
        # Daten laden
        documents = process_crawled_data_with_pandas_reader(csv_file_path, config=config)

        # Indizes erstellen und speichern
        index_store, vector_store = create_and_store_indices(
            documents, config.db_path_tree, llm=config.llm_config, config=config
        )

        # Embedding-Modell initialisieren
        embed_model = CustomLlamaPack(
            base_url=config.llm_config.ollama_model,
            max_tokens=config.llm_config.chat_token_limit,
            config=config
        )

        # TreeSelectLeafEmbeddingRetriever erstellen
        tree_select_leaf_embedding_retriever = create_tree_embedding_retriever(index_store, embed_model, config=config)

        # Recursive Query Engines erstellen
        recursive_query_engine, raw_query_engine = create_recursive_query_engine(documents, config=config)

        # Ollama LLM initialisieren
        llm = setup_ollama_llm(config)

        if not llm:
            raise RuntimeError("Fehler beim Initialisieren des Ollama LLM. Abbruch.")

        # Memory für temporäre Kontexte einbinden
        memory = setup_llm_memory(llm, token_limit=config.llm_config.chat_token_limit)

        # Store crawled data in PandasStructTable and SQLStructTable
        pandas_table, sql_table = store_crawled_data(documents)

        # Create query tools
        query_tools = create_query_tools(index_store, sql_table)

        # ReActAgent erstellen
        react_agent = setup_react_agent_with_tools(query_tools, llm)

        # Komponenten-Dictionary aktualisieren
        components = {
            'index_store': index_store,
            'vector_store': vector_store,
            'tree_select_leaf_embedding_retriever': tree_select_leaf_embedding_retriever,
            'recursive_query_engine': recursive_query_engine,
            'raw_query_engine': raw_query_engine,
            'react_agent': react_agent,
            'pandas_table': pandas_table,
            'sql_table': sql_table,
            'summary_tool': query_tools[0],
            'sql_tool': query_tools[1],
            'memory': memory,
        }

        logging.info("Systemintegration erfolgreich abgeschlossen.")
        return components
    except Exception as e:
        logging.error(f"Fehler bei der Systemintegration mit Konfiguration {config}: {e}", exc_info=True)
        raise

# Anfrage verarbeiten
def process_query(query, components):
    """
    Verarbeitet eine Anfrage basierend auf den verfügbaren Komponenten.

    :param query: Abfragetext.
    :param components: Dictionary mit den Systemkomponenten.
    :return: Ergebnisse aus den verschiedenen Engines.
    """
    # Retrieve mit TreeSelectLeafEmbeddingRetriever
    tree_select_results = components['tree_select_leaf_embedding_retriever'].retrieve(
        QueryBundle(query_str=query)
    )

    # Zusammenfassungsabfrage
    summary_results = components['summary_tool'].retrieve(query)

    # SQL-Abfrage
    sql_results = components['sql_tool'].retrieve(query)

    # ReAct-Agent-Abfrage
    react_results = components['react_agent'].chat(query) if components['react_agent'] else "ReActAgent nicht verfügbar"

    # Ergebnisse zusammenführen
    results = {
        'tree_select_embedding': tree_select_results,
        'summary': summary_results,
        'sql_results': sql_results,
        'react': react_results,
    }
    return results

def evaluate_query(query, components):
    tree_results = components['tree_select_leaf_embedding_retriever'].retrieve(
        QueryBundle(query_str=query)
    )
    summary_results = components['summary_tool'].retrieve(query)
    sql_results = components['sql_tool'].retrieve(query)
    return {
        "tree_select_embedding": tree_results,
        "summary": summary_results,
        "sql_results": sql_results
    }

def setup_ollama_llm(config: IndexerConfig):
    tokenizer = config.llm_config.tokenizer
    model_name = config.llm_config.ollama_model
    
    try:
        model = AutoModel.from_pretrained(model_name)
        return model
    except Exception as e:
        raise ValueError(f"Error initializing model {model_name}: {e}")

def get_tokenizer(model_name):
    # Supported models:
    # - Salesforce/blip2-opt-2.7b (with BertTokenizerFast)
    # - t5-base (with AutoTokenizer)
    # - BAAI/bge-reranker-large (with AutoTokenizer)
    tokenizer_class = MODEL_TOKENIZER_MAP.get(model_name)
    if tokenizer_class:
        return tokenizer_class.from_pretrained(model_name)
    raise ValueError(f"No tokenizer available for model {model_name}")

# Integration tests recommendation:
# - Ensure each tokenizer loads correctly.
# - Verify models initialize with their respective tokenizers.
