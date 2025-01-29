
import time
import os
import logging
from datetime import datetime
from scripts.utils import sanitize_folder_name
from PIL import Image
from driver_setup import Service, binary_path, CHROME_OPTIONS, webdriver
from scripts.config import ImageVisionConfig, CrawlerConfig, StorageConfig  

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname=s - %(message)s')

# Konfiguration laden
vision_config = ImageVisionConfig()
crawler_config = CrawlerConfig()

# Initialisierung von BLIP und CLIP über die zentrale Konfiguration
logging.info(f"Initializing BLIP and CLIP Processors with models: {vision_config.model_name} and {vision_config.clip_model_name}")

def analyze_image_with_blip_and_clip(image_path):
    """
    Analysiert ein Bild mit BLIP und CLIP-Modellen und liefert eine Bildbeschreibung und Ähnlichkeitsbewertungen.

    :param image_path: Pfad zum zu analysierenden Bild.
    :return: Analyse-Ergebnisse.
    """
    try:
        image = Image.open(image_path).convert("RGB")

        # BLIP Bildbeschreibung
        logging.info("Starting BLIP image captioning.")
        blip_inputs = vision_config.blip_processor(
            images=image,
            text=None,
            return_tensors="pt",
            padding=True
        ).to(vision_config.device)
        blip_outputs = vision_config.blip_model.generate(**blip_inputs)
        blip_caption = vision_config.blip_processor.decode(blip_outputs[0], skip_special_tokens=True)  # Use blip_processor for decoding

        # CLIP Bildanalyse
        clip_inputs = vision_config.clip_processor(
            text=["a photo of a website", "a responsive design screenshot"],
            images=image,
            return_tensors="pt",
            padding=True
        ).to(vision_config.device)
        clip_outputs = vision_config.clip_model(**clip_inputs)
        clip_scores = clip_outputs.logits_per_image.softmax(dim=1).tolist()

        logging.info(f'BLIP-Analyse abgeschlossen: {blip_caption}')
        logging.info(f'CLIP-Scores: {clip_scores}')

        return {
            "image_path": image_path,
            "blip_caption": blip_caption,
            "clip_scores": clip_scores
        }
    except Exception as e:
        logging.error(f"Fehler bei der Bildanalyse mit BLIP und CLIP für {image_path}: {e}")
        return {
            "image_path": image_path,
            "error": f"Bild konnte nicht analysiert werden: {e}"
        }

def get_dynamic_output_dir(base_dir, project_name):
    """
    Erstellt ein dynamisches Ausgabeverzeichnis basierend auf Basisverzeichnis und Projektname.

    :param base_dir: Basisverzeichnis.
    :param project_name: Name des Projekts.
    :return: Pfad zum Ausgabeverzeichnis.
    """
    storage_config = StorageConfig(base_dir=base_dir)
    return os.path.join(storage_config.db_path_storage, sanitize_folder_name(project_name), 'screenshots')

def take_responsive_screenshots(driver, url, base_dir, project_name, config: CrawlerConfig):
    """
    Erstellt responsive Screenshots einer Webseite.
    """
    try:
        storage_config = StorageConfig(base_dir=base_dir)
        output_dir = os.path.join(storage_config.db_path_storage, sanitize_folder_name(project_name), 'screenshots')
        os.makedirs(output_dir, exist_ok=True)
        logging.debug(f'Screenshots-Verzeichnis erstellt: {output_dir}')

        viewports = [{'width': width, 'height': height} for width, height in config.screenshot_sizes]

        driver.get(url)  # Navigate to URL

        for viewport in viewports:
            driver.set_window_size(viewport['width'], viewport['height'])
            logging.debug(f'Setze Viewport auf {viewport["width"]}x{viewport["height"]}')
            time.sleep(2)  # Wait for page to load

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_name = os.path.join(output_dir, f'responsive_{viewport["width"]}x{viewport["height"]}_{timestamp}.png')
            driver.save_screenshot(screenshot_name)
            logging.debug(f'Responsive Screenshot gespeichert: {screenshot_name}')

            # Bildanalyse durchführen
            analyze_image_with_blip_and_clip(screenshot_name)
    except Exception as e:
        logging.error(f"Fehler beim Erstellen von responsiven Screenshots für {url}: {e}", exc_info=True)
        raise

def take_fullpage_screenshot(driver, url, base_dir, project_name):
    """
    Erstellt einen vollständigen Seiten-Screenshot einer Webseite.

    :param driver: Selenium WebDriver-Instanz.
    :param url: URL der Webseite.
    :param base_dir: Basisverzeichnis für die Speicherung.
    :param project_name: Name des Projekts.
    """
    output_dir = get_dynamic_output_dir(base_dir, project_name)
    os.makedirs(output_dir, exist_ok=True)
    logging.debug(f'Screenshots-Verzeichnis erstellt: {output_dir}')

    driver.get(url)
    width, height = 1920, 1080
    driver.set_window_size(width, height)
    logging.debug(f'Setze Viewport auf {width}x{height}')
    time.sleep(2)  # Warte, bis die Seite geladen ist

    total_height = driver.execute_script("return document.body.scrollHeight")
    scroll_position = 0
    part = 1

    while scroll_position < total_height:
        driver.execute_script(f"window.scrollTo(0, {scroll_position});")
        time.sleep(1)  # Warte, bis der Inhalt geladen ist

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_name = os.path.join(output_dir, f'fullpage_part{part}_{timestamp}.png')
        driver.save_screenshot(screenshot_name)
        if not os.path.exists(screenshot_name):
            return {"image_path": screenshot_name, "error": "Bild konnte nicht gespeichert werden."}

        logging.debug(f'Full-page Screenshot Teil {part} gespeichert: {screenshot_name}')

        # Bildanalyse durchführen
        analyze_image_with_blip_and_clip(screenshot_name)

        scroll_position += height
        part += 1

    logging.info("Full-page Screenshots abgeschlossen.")
