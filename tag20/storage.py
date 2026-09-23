import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

DATEI="produkte.json"

def lade_daten() -> dict:
    try:
        with open(DATEI, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logging.warning("Darei nicht gefunden oder leer. Neues Dictionary erstellt")
        return{}

def speichere_daten(daten: dict) -> None:
    with open(DATEI, "w", encoding="utf-8")as f:
        json.dump(daten, f, indent=4, ensure_ascii=False)
        logging.info("Daten erfolgreich in produkte.json gespeichert.")
