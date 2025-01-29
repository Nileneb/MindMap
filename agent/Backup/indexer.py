import os
import logging
from ..app import csv_file_path, binary_path, CHROME_OPTIONS, initialize_driver, LoggingConfig, process_query, StorageContext, SimpleDocumentStore

from ..scripts.driver_setup import Service, binary_path, CHROME_OPTIONS, webdriver
from typing import List
from .ollama_llm import setup_react_agent_with_tools, QueryEngineTool, ReActAgent
from .reader import process_crawled_data_with_pandas_reader
from .config import IndexerConfig, LLMConfig, StorageConfig  # Updated import
from .setup_helpers import setup_storage_context, setup_ollama_llm
from .data_storage import SimpleKVStore, SimpleDocumentStore, IndexDocumentSummary, VectorStoreIndex
from scripts.crawler.crawler import crawl_website, all_data_to_csv
from some_module import TreeSummarize  # Add this import
# 1. Erstellung von TreeIndex und SummaryIndex mit TreeSummarize

def create_summary_index(documents, llm, config: IndexerConfig = None):
    if config is None:
        config = IndexerConfig()
    try:
        summarizer = TreeSummarize(llm=llm)
        summary_index = IndexDocumentSummary()
        for doc in documents:
            summary = summarizer.get_response(query_str="Fasse zusammen.", text_chunks=[doc['text']])
            summary_index.add_summary_and_nodes(summary_node=summary, nodes=[doc])
        logging.info("SummaryIndex erfolgreich erstellt.")
        return summary_index
    except Exception as e:
        logging.error(f"Fehler beim Erstellen des SummaryIndex: {e}", exc_info=True)
        raise

def initialize_storage_context(config: StorageConfig = None):
    if config is None:
        config = StorageConfig()
    try:
        persist_dir = config.db_path_storage
        if not os.path.exists(persist_dir):
            os.makedirs(persist_dir)
            logging.info(f"Persistenzverzeichnis erstellt: {persist_dir}")

        if not os.path.exists(os.path.join(persist_dir, "docstore.json")):
            logging.info("Initialisiere leeren Speicher...")
            kv_store = SimpleKVStore()
            doc_store = SimpleDocumentStore(kvstore=kv_store)
            storage_context = StorageContext(doc_store=doc_store)
            storage_context.persist(persist_dir)
        else:
            logging.info("Speicher bereits vorhanden.")
        return StorageContext.from_defaults(persist_dir=persist_dir)
    except Exception as e:
        logging.error(f"Fehler beim Initialisieren des StorageContext: {e}", exc_info=True)
        raise

def create_storage_context(persist_dir, config=None):
    return initialize_storage_context(persist_dir, config=config)

def create_and_store_indices(documents, persist_dir, llm, config: IndexerConfig = None):
    """
    Erstellt und speichert Indizes in einem StorageContext.

    :param documents: Liste der Dokumente.
    :param persist_dir: Speicherverzeichnis.
    :param llm: Instanz des LLM.
    :param config: IndexerConfig-Objekt.
    """
    if config is None:
        config = IndexerConfig()
    try:
        storage_context = setup_storage_context(StorageConfig(base_dir=config.base_dir))
        summary_index = create_summary_index(documents, llm, config=config)
        vector_store = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
        storage_context.persist()
        logging.info("Indizes erfolgreich erstellt und gespeichert.")
        return summary_index, vector_store
    except Exception as e:
        logging.error(f"Fehler beim Erstellen und Speichern der Indizes: {e}", exc_info=True)
        raise

# Consolidate multiple calls to process_crawled_data_with_pandas_reader
def central_process_data(csv_file_path, config=None):
    return process_crawled_data_with_pandas_reader(csv_file_path, config=config)

# Replace individual calls with central_process_data
# Example change in process_and_store_indices function:
def process_and_store_indices(csv_file_path, llm, persist_dir, config=None):
    if config is None:
        config = IndexerConfig()
    documents = central_process_data(csv_file_path, config=config)
    storage_context = setup_storage_context(persist_dir, config=config)

    # Create and store indices
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context
    )
    
    storage_context.persist(persist_dir=persist_dir)
    return storage_context.index_store, storage_context.vector_store

# 2. Erweiterte Query-Engines mit Reranker
def initialize_reranker(model="cross-encoder/stsb-distilroberta-base", top_n=5):
    return SentenceTransformerRerank(
        model=model,
        top_n=top_n,
        device="cuda" if torch.cuda.is_available() else "cpu",
    )

def create_recursive_query_engine(documents, config: IndexerConfig = None):
    if config is None:
        config = IndexerConfig()  # Use IndexerConfig
    recursive_index = VectorStoreIndex.from_documents(documents)
    llm_reranker = LLMRerank(top_n=config.reranker_top_n, llm=setup_ollama_llm(config))

    recursive_query_engine = recursive_index.as_query_engine(
        similarity_top_k=config.query_similarity_top_k,
        node_postprocessors=[llm_reranker],
        verbose=True
    )
    return recursive_query_engine

# 3. Erweiterung: Chat-Engine mit Kontext
def create_chat_engine(tree_index, llm, config=None):
    """
    Erstellt eine Chat-Engine mit TreeIndex und Chat-Speicher.

    :param tree_index: TreeIndex-Objekt.
    :param llm: LLM-Objekt für die Verarbeitung.
    :param config: IndexerConfig-Objekt.
    """
    if config is None:
        config = IndexerConfig()

    memory = ChatMemoryBuffer.from_defaults(token_limit=config.chat_token_limit)

    chat_engine = CondensePlusContextChatEngine.from_defaults(
        retriever=tree_index.as_retriever(),
        memory=memory,
        llm=llm,
        context_prompt=(
            "You are a chatbot with access to relevant document data. "
            "Use the provided context and chat history to respond appropriately."
        ),
        verbose=True
    )
    return chat_engine

# Integration mit Ollama und Reader
def generate_rag_dataset(documents: List[Document], llm, config: LLMConfig = None):
    """
    Generiert ein RAG-Dataset basierend auf den gegebenen Dokumenten.

    :param documents: Liste von Dokumenten.
    :param llm: LLM zur Verarbeitung.
    :param config: LLMConfig-Objekt.
    :return: Generiertes RAG-Dataset.
    """
    if config is None:
        config = LLMConfig()  # Use LLMConfig
    generator = RagDatasetGenerator.from_documents(
        documents=documents,
        llm=llm,
        num_questions_per_chunk=config.num_questions_per_chunk  # Use config value
    )
    dataset = generator.generate_dataset_from_nodes()
    return dataset

def integrate_rag_dataset(csv_file_path, llm, persist_dir, config=None):
    """
    Integriert den RAG-Dataset-Generator in den Workflow.

    :param csv_file_path: Pfad zur CSV-Datei.
    :param llm: Das verwendete LLM.
    :param persist_dir: Verzeichnis zur Speicherung.
    :param config: IndexerConfig-Objekt.
    """
    if config is None:
        config = IndexerConfig()
    documents = central_process_data(csv_file_path, config=config)
    dataset = generate_rag_dataset(documents, llm)
    
    # Speichern Sie das Dataset als Pandas DataFrame
    dataset_df = dataset.to_pandas()
    dataset_path = os.path.join(persist_dir, "rag_dataset.csv")
    dataset_df.to_csv(dataset_path, index=False)
    logging.info(f"RAG-Dataset erfolgreich gespeichert unter: {dataset_path}")

def integrate_with_ollama_and_reader(csv_file_path, config: IndexerConfig = None):
    if config is None:
        config = IndexerConfig()
    try:
        components = integrate_with_system(csv_file_path, config=config)
        logging.info("Integration mit Ollama und Reader erfolgreich.")
        return components
    except Exception as e:
        logging.error(f"Fehler bei der Integration mit Ollama und Reader: {e}", exc_info=True)
        raise

# Anfrage verarbeiten
def process_query(query, components, config: IndexerConfig = None):
    """
    Verarbeitet eine Anfrage mit allen verfügbaren Komponenten.
    """
    if config is None:
        config = IndexerConfig()
    try:
        # Retrieve relevant summaries
        retriever = components['index_store'].as_retriever(retriever_mode="llm")
        summary_results = retriever.retrieve(query)

        # Chat-Engine-Abfrage anstelle von query_llama_stack
        react_results = components['chat_engine'].chat(query)

        results = {
            'recursive': components['recursive_query_engine'].query(query),
            'raw': components['raw_query_engine'].query(query),
            'chat': react_results,
            'summary': summary_results
        }

        logging.info(f"Abfrage '{query}' erfolgreich verarbeitet.")
        return results
    except Exception as e:
        logging.error(f"Fehler beim Verarbeiten der Abfrage '{query}': {e}", exc_info=True)
        raise
