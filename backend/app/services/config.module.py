import os
import json
import logging

CONFIG_FILE = "assistant_config.json"

default_config = {
    "email_recipient": "",
    "accent": "féminin",
    "printer": None
}

def load_config():
    """Charge la configuration utilisateur depuis un fichier JSON."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                user_config = json.load(f)
            logging.info("Configuration chargée.")
            return user_config
        except Exception as e:
            logging.error("Erreur lors du chargement de la configuration: " + str(e))
            return default_config
    else:
        return default_config

def save_config(config):
    """Sauvegarde la configuration utilisateur."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        logging.info("Configuration sauvegardée.")
    except Exception as e:
        logging.error("Erreur lors de la sauvegarde de la configuration: " + str(e))

# Charger la config
CONFIG = load_config()
