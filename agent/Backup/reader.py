import logging
from llama_index.core import GPTVectorStoreIndex  # Updated from GPTSimpleVectorIndex
from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import ImageDocument
from pathlib import Path
from typing import Dict, List, Optional
from llama_index.core.indices.document_summary.base import DocumentSummaryIndex
import logging
from llama_index.core.storage.index_store.keyval_index_store import KVIndexStore
from llama_index.core.storage.kvstore.simple_kvstore import SimpleKVStore
from llama_index.core.storage.docstore.keyval_docstore import KVDocumentStore
from llama_index.core.storage.storage_context import StorageContext
import os
import csv
import pandas as pd
from llama_index.core.schema import Document
from .setup_helpers import setup_storage_context
from .config import IndexerConfig, ImageVisionConfig
from ..config import IndexerConfig  # Updated import

class PandasCSVReader:
    """
    Ein einfacher CSV-Reader, der CSV-Daten in Dokumente transformiert.
    """

    def __init__(self, config: IndexerConfig = None):
        self.sep = config.csv_separator if config else ","
        self.header = config.csv_header if config else 0
        self.encoding = config.csv_encoding if config else "utf-8"
        logging.info(f"CSV-Reader initialisiert mit Separator '{self.sep}', Header '{self.header}' und Encoding '{self.encoding}'")

    def load_data(self, file_path):
        """
        Liest eine CSV-Datei und transformiert sie in Dokumente.

        :param file_path: Pfad zur CSV-Datei.
        :return: Liste von Dokumenten.
        """
        if not os.path.exists(file_path):
            logging.error(f"CSV-Datei {file_path} wurde nicht gefunden.")
            raise FileNotFoundError(f"Die Datei {file_path} existiert nicht.")

        try:
            df = pd.read_csv(file_path, sep=self.sep, header=self.header, encoding=self.encoding)
            documents = []

            # Transformieren der CSV-Daten in Dokumente
            for _, row in df.iterrows():
                row_text = ", ".join([f"{col}: {val}" for col, val in row.items()])
                document = Document(
                    text=row_text,
                    metadata={"source": file_path}
                )
                documents.append(document)

            return documents
        except pd.errors.ParserError as e:
            logging.error(f"Fehler beim Parsen der CSV-Datei {file_path}: {e}")
            raise ValueError(f"Ungültiges CSV-Format in Datei {file_path}: {e}")
        except Exception as e:
            logging.error(f"Unbekannter Fehler beim Lesen der Datei {file_path}: {e}")
            raise ValueError(f"Fehler beim Lesen der Datei {file_path}: {e}")

# Remove the two separate functions and add a consolidated function
def process_crawled_data(csv_file_path, config: IndexerConfig, use_summary=False):
    """
    Verarbeitet die gecrawlten Daten aus der CSV-Datei und erstellt gegebenenfalls Indizes.

    :param csv_file_path: Pfad zur CSV-Datei.
    :param config: IndexerConfig für Einstellungen.
    :param use_summary: Boolean flag to create summary index.
    :return: Erstellte Indizes wenn use_summary ist True, sonst nur der Hauptindex.
    """
    reader = PandasCSVReader(config=config)
    documents = reader.load_data(csv_file_path)

    # Setup StorageContext
    storage_context = setup_storage_context(config=config.storage_config)

    # Indizes erstellen
    index = GPTVectorStoreIndex.from_documents(documents, storage_context=storage_context)
    
    if use_summary:
        summary_index = DocumentSummaryIndex.from_documents(documents=documents, storage_context=storage_context)
        logging.info("Indizes erfolgreich erstellt.")
        return index, summary_index

    logging.info("Hauptindex erfolgreich erstellt.")
    return index

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

class ImageVisionLLMReader(BaseReader):
    """Image parser using Blip2 VisionLLM."""
    
    def __init__(self, config: ImageVisionConfig):
        """Initialize with ImageVisionConfig."""
        self._config = config
        self._parser_config = self._get_default_config()
        self._prompt = config.prompt
        self._keep_image = config.keep_image

    def _get_default_config(self) -> Dict:
        """Get default configuration from ImageVisionConfig with robust error handling."""
        try:
            from transformers import Blip2Processor, Blip2ForConditionalGeneration
            import torch

            processor = Blip2Processor.from_pretrained(self._config.model_name)
            model = Blip2ForConditionalGeneration.from_pretrained(
                self._config.model_name, torch_dtype=getattr(torch, self._config.dtype)
            )
            model.to(self._config.device)

            return {
                "model": model,
                "processor": processor,
                "device": self._config.device,
                "dtype": getattr(torch, self._config.dtype),
            }
        except ImportError as e:
            raise ImportError(
                f"Fehler beim Importieren der notwendigen Bibliotheken: {e}. "
                f"Bitte installieren Sie transformers und torch."
            )
        except Exception as e:
            logging.error(f"Fehler beim Laden des Modells: {e}")
            raise

    def load_data(
        self, file: Path, extra_info: Optional[Dict] = None
    ) -> List[ImageDocument]:
        """Parse file."""
        from llama_index.core.img_utils import img_2_b64
        from PIL import Image

        # load document image
        try:
            image = Image.open(file)
        except Exception as e:
            logging.error(f"Fehler beim Laden des Bildes: {file}. Fehler: {e}")
            return []
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Encode image into base64 string and keep in document
        image_str: Optional[str] = None
        if self._keep_image:
            image_str = img_2_b64(image)

        # Parse image into text
        model = self._parser_config["model"]
        processor = self._parser_config["processor"]

        device = self._parser_config["device"]
        dtype = self._parser_config["dtype"]
        model.to(device)

        # unconditional image captioning
        inputs = processor(image, self._prompt, return_tensors="pt").to(device, dtype)

        out = model.generate(**inputs)
        text_str = processor.decode(out[0], skip_special_tokens=True)

        return [
            ImageDocument(
                text=text_str,
                image=image_str,
                image_path=str(file),
                metadata=extra_info or {},
            )
        ]
