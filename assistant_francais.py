import os
import subprocess
import platform
import json
import threading
import time
import webbrowser
import logging
import tkinter as tk
from tkinter import ttk, messagebox
from typing import TextIO
import speech_recognition as sr
import pyttsx3
import spacy

# Charger le modèle français spaCy
nlp = spacy.load("fr_core_news_sm")

# ---------------------------
# Configuration persistante
# ---------------------------
CONFIG_FILE = "assistant_config.json"

def load_config():
    default_config = {
        "email_recipient": "",
        "accent": "Neutre",  # options : Neutre, Parisien, Marseillais
        "printer": None
    }
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
    try:
        f: TextIO
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        logging.info("Configuration sauvegardée.")
    except Exception as e:
        logging.error("Erreur lors de la sauvegarde de la configuration: " + str(e))

user_config = load_config()

# ---------------------------
# Configuration OS-dépendante
# ---------------------------
home_dir = os.path.expanduser("~")
if platform.system() == "Windows":
    OS_CONFIG = {
        "photo_folder": os.path.join(home_dir, "Pictures"),
        "document_to_print": os.path.join(home_dir, "Documents", "sample_document.pdf"),
        "scanned_document": os.path.join(home_dir, "Documents", "scanned_document.pdf"),
        "visio_app": os.path.join(home_dir, "AppData", "Roaming", "Zoom", "bin", "Zoom.exe")
    }
elif platform.system() == "Darwin":
    OS_CONFIG = {
        "photo_folder": os.path.join(home_dir, "Pictures"),
        "document_to_print": os.path.join(home_dir, "Documents", "sample_document.pdf"),
        "scanned_document": os.path.join(home_dir, "Documents", "scanned_document.pdf"),
        "visio_app": "/Applications/zoom.us.app"
    }
else:
    raise Exception("Ce script est uniquement supporté sur Windows et macOS.")

# Fusionner la config persistante avec la config spécifique à l'OS
CONFIG = {**OS_CONFIG, **user_config}

# ---------------------------
# Journalisation
# ---------------------------
logging.basicConfig(
    level=logging.INFO,
    filename="assistant.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---------------------------
# Initialisation de la synthèse vocale (TTS)
# ---------------------------
engine = pyttsx3.init()
engine.setProperty("rate", 150)
engine.setProperty("volume", 1.0)

def speak(text):
    """Affiche, log et prononce le texte."""
    logging.info("Speak: " + text)
    print("Assistant:", text)
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        logging.error("Erreur TTS: " + str(e))

# ---------------------------
# Gestion des accents et de la voix
# ---------------------------
def get_accent_options():
    """
    Parcourt les voix disponibles et associe quelques accents.
    Options proposées : "Neutre", "Parisien" et "Marseillais".
    """
    voices = engine.getProperty('voices')
    accent_dict = {"Neutre": None, "Parisien": None, "Marseillais": None}
    for voice in voices:
        name = voice.name.lower()
        if "paris" in name:
            accent_dict["Parisien"] = voice.id
        elif "marseille" in name:
            accent_dict["Marseillais"] = voice.id
        else:
            if accent_dict["Neutre"] is None:
                accent_dict["Neutre"] = voice.id
    return accent_dict

def select_accent_gui():
    accent_options = get_accent_options()
    accent_window = tk.Toplevel()
    accent_window.title("Sélection de l'accent")
    accent_window.geometry("300x200")
    label = ttk.Label(accent_window, text="Sélectionnez l'accent désiré :", font=("Arial", 14))
    label.pack(pady=10)
    listbox = tk.Listbox(accent_window, font=("Arial", 12))
    for accent in accent_options.keys():
        listbox.insert(tk.END, accent)
    listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def validate_accent():
        selection = listbox.curselection()
        if selection:
            accent_choice = listbox.get(selection[0])
            chosen_voice = accent_options[accent_choice]
            if chosen_voice:
                engine.setProperty("voice", chosen_voice)
                speak(f"L'accent {accent_choice} a été sélectionné.")
                user_config["accent"] = accent_choice
                CONFIG["accent"] = accent_choice
                save_config(user_config)
            else:
                speak(f"Aucune voix n'est associée à l'accent {accent_choice}.")
            accent_window.destroy()
        else:
            speak("Veuillez sélectionner un accent.")

    btn_validate = ttk.Button(accent_window, text="Valider", command=validate_accent)
    btn_validate.pack(pady=10)
    accent_window.grab_set()
    accent_window.wait_window()

def set_default_voice():
    """
    Définit par défaut une voix féminine en français, sans faire de sortie vocale.
    Si aucune voix féminine n'est trouvée, on sélectionne la première voix française disponible,
    ou la première voix si aucune voix française n'est identifiée.
    """
    voices = engine.getProperty("voices")
    french_female_voice = None

    for voice in voices:
        try:
            languages = [lang.decode("utf-8").lower() if isinstance(lang, bytes) else lang.lower() for lang in voice.languages]
        except Exception:
            languages = []
        if (any("fr" in lang for lang in languages) or "fr" in voice.name.lower()) and ("female" in voice.name.lower() or "femme" in voice.name.lower()):
            french_female_voice = voice
            break

    if french_female_voice:
        engine.setProperty("voice", french_female_voice.id)
        print(f"Voix par défaut féminine sélectionnée : {french_female_voice.name}")
    else:
        # Si aucune voix féminine n'est trouvée, utiliser une voix française quelconque
        for voice in voices:
            try:
                languages = [lang.decode("utf-8").lower() if isinstance(lang, bytes) else lang.lower() for lang in voice.languages]
            except Exception:
                languages = []
            if any("fr" in lang for lang in languages) or "fr" in voice.name.lower():
                french_female_voice = voice
                break
        if french_female_voice:
            engine.setProperty("voice", french_female_voice.id)
            print(f"Voix par défaut (française) sélectionnée : {french_female_voice.name}")
        else:
            engine.setProperty("voice", voices[0].id)
            print(f"Voix par défaut sélectionnée : {voices[0].name}")

# Appeler la fonction pour définir la voix par défaut (sans annonce vocale)
set_default_voice()

# ---------------------------
# Reconnaissance vocale (avec timeout)
# ---------------------------
recognizer = sr.Recognizer()
def listen_for_command(prompt=True, timeout=10):
    if prompt:
        speak("Que puis-je faire pour vous aider ?")
    with sr.Microphone() as source:
        if prompt:
            print("Écoute...")
        try:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=timeout)
            command = recognizer.recognize_google(audio, language="fr-FR").lower()
            logging.info("Commande reconnue: " + command)
            print("Vous avez dit :", command)
            return command
        except sr.WaitTimeoutError:
            speak("Temps d'attente écoulé, je n'ai rien entendu. Veuillez réessayer.")
        except sr.UnknownValueError:
            speak("Désolé, je n'ai pas compris. Veuillez réessayer.")
        except sr.RequestError as e:
            speak("Erreur de reconnaissance vocale.")
            logging.error("RequestError: " + str(e))
    return ""

# NLP: Détection d'intention avec spaCy
def get_intent(command):
    doc = nlp(command)
    if any(token.text in ["email", "courriel", "mail"] for token in doc):
        return "EMAIL"
    elif any(token.text in ["visio", "visioconférence", "appel"] for token in doc):
        return "VISIO"
    elif any(token.text in ["photo", "image"] for token in doc):
        return "PHOTO"
    elif any(token.text in ["imprimer", "impression"] for token in doc):
        return "PRINT"
    elif any(token.text in ["scanner", "numériser"] for token in doc) and any(token.text in ["email", "courriel", "envoyer"] for token in doc):
        return "SCAN_EMAIL"
    else:
        return "UNKNOWN"

def execute_command(command):
    intent = get_intent(command)
    if intent == "EMAIL":
        compose_email()
    elif intent == "VISIO":
        start_visio()
    elif intent == "PHOTO":
        view_photos()
    elif intent == "PRINT":
        print_document()
    elif intent == "SCAN_EMAIL":
        scan_and_email()
    else:
        speak("Ooops ! Commande non reconnue. Veuillez réessayer.")


# ---------------------------
# Fonctions des commandes vocales
# ---------------------------
def compose_email():
    speak("J'ouvre votre messagerie pour écrire un email.")
    recipient = CONFIG.get("email_recipient", "")
    mailto_url = f"mailto:{recipient}"
    webbrowser.open(mailto_url)

def start_visio():
    speak("Je démarre la visioconférence.")
    visio_app = CONFIG.get("visio_app", "")
    if visio_app and os.path.exists(visio_app):
        if platform.system() == "Windows":
            subprocess.Popen([visio_app])
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", visio_app])
    else:
        speak("L'application de visioconférence n'a pas été trouvée.")

def view_photos():
    speak("J'ouvre votre dossier de photos.")
    folder_path = CONFIG.get("photo_folder", "")
    if os.path.exists(folder_path):
        if platform.system() == "Windows":
            subprocess.Popen(["explorer", folder_path])
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", folder_path])
    else:
        speak("Le dossier de photos n'a pas été trouvé.")

def print_document():
    speak("Préparation de l'impression du document.")
    document_path = CONFIG.get("document_to_print", "")
    if not os.path.exists(document_path):
        speak("Le document à imprimer n'a pas été trouvé.")
        return
    if platform.system() == "Windows":
        try:
            import win32print
            printer_name = select_printer_windows()
            hPrinter = win32print.OpenPrinter(printer_name)
            try:
                doc_info = ("Document", None, "RAW")
                win32print.StartDocPrinter(hPrinter, 1, doc_info)
                win32print.StartPagePrinter(hPrinter)
                with open(document_path, "rb") as f:
                    data = f.read()
                    win32print.WritePrinter(hPrinter, data)
                win32print.EndPagePrinter(hPrinter)
                win32print.EndDocPrinter(hPrinter)
                speak("Le document a été envoyé à l'imprimante.")
            finally:
                win32print.ClosePrinter(hPrinter)
        except Exception as e:
            speak("Une erreur est survenue lors de l'impression sur Windows.")
            logging.error("Erreur d'impression Windows: " + str(e))
    elif platform.system() == "Darwin":
        try:
            printer_name = select_printer_mac()
            if printer_name is None:
                speak("Aucune imprimante n'a été sélectionnée.")
                return
            subprocess.Popen(["lp", "-d", printer_name, document_path])
            speak("Le document a été envoyé à l'imprimante.")
        except Exception as e:
            speak("Une erreur est survenue lors de l'impression sur macOS.")
            logging.error("Erreur d'impression macOS: " + str(e))

def scan_and_email():
    speak("Je scanne le document. Veuillez patienter...")
    scanned_file = CONFIG.get("scanned_document", "")
    if os.path.exists(scanned_file):
        speak("Le document scanné est prêt. J'ouvre votre messagerie pour que vous puissiez joindre le fichier.")
        compose_email()
        speak("N'oubliez pas de joindre le document scanné.")
    else:
        speak("Le document scanné n'a pas été trouvé.")

# ---------------------------
# Sélection d'imprimante (spécifique à chaque OS)
# ---------------------------
if platform.system() == "Windows":
    import win32print
    def select_printer_windows():
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        printer_names = [printer[2] for printer in printers]
        speak("Voici les imprimantes disponibles :")
        for i, name in enumerate(printer_names):
            print(f"{i + 1}. {name}")
        choice = input("Sélectionnez une imprimante par numéro (appuyez sur Entrée pour utiliser celle par défaut) : ")
        if choice.strip() == "":
            default = win32print.GetDefaultPrinter()
            speak(f"Utilisation de l'imprimante par défaut : {default}")
            return default
        else:
            try:
                index = int(choice) - 1
                printer_name = printer_names[index]
                speak(f"Vous avez sélectionné : {printer_name}")
                return printer_name
            except Exception as e:
                logging.error("Erreur de sélection d'imprimante: " + str(e))
                default = win32print.GetDefaultPrinter()
                speak(f"Choix invalide. Utilisation de l'imprimante par défaut : {default}")
                return default
elif platform.system() == "Darwin":
    def select_printer_mac():
        try:
            result = subprocess.run(["lpstat", "-p"], capture_output=True, text=True)
            lines = result.stdout.splitlines()
            printer_names = []
            for line in lines:
                if line.startswith("printer "):
                    parts = line.split()
                    if len(parts) >= 2:
                        printer_names.append(parts[1])
            if not printer_names:
                speak("Aucune imprimante détectée.")
                return None
            speak("Voici les imprimantes disponibles :")
            for i, name in enumerate(printer_names):
                print(f"{i + 1}. {name}")
            choice = input("Sélectionnez une imprimante par numéro (appuyez sur Entrée pour utiliser celle par défaut) : ")
            if choice.strip() == "":
                result_default = subprocess.run(["lpstat", "-d"], capture_output=True, text=True)
                if "system default destination:" in result_default.stdout:
                    printer_name = result_default.stdout.split("system default destination:")[1].strip()
                    speak(f"Utilisation de l'imprimante par défaut : {printer_name}")
                    return printer_name
                else:
                    speak(f"Utilisation de l'imprimante : {printer_names[0]}")
                    return printer_names[0]
            else:
                try:
                    index = int(choice) - 1
                    printer_name = printer_names[index]
                    speak(f"Vous avez sélectionné : {printer_name}")
                    return printer_name
                except Exception as e:
                    logging.error("Erreur de sélection d'imprimante: " + str(e))
                    speak(f"Choix invalide. Utilisation de l'imprimante : {printer_names[0]}")
                    return printer_names[0]
        except Exception as e:
            logging.error("Erreur lors de la détection des imprimantes: " + str(e))
            return None

# ---------------------------
# Exécution de la commande en fonction de la commande vocale
# ---------------------------
def execute_command(command):
    if (("écrire" in command or "composer" in command or "envoyer" in command or "faire" in command)
        and ("email" in command or "courriel" in command or "mail" in command)):
        compose_email()
    elif "visio" in command or "visioconférence" in command or "appel vidéo" in command:
        start_visio()
    elif "photo" in command or "image" in command:
        view_photos()
    elif "imprimer" in command:
        print_document()
    elif "scanner" in command and ("email" in command or "envoyer" in command or "courriel" in command):
        scan_and_email()
    else:
        speak("Ooops ! Commande non reconnue. Veuillez réessayer.")

# ---------------------------
# Demande à l'utilisateur s'il souhaite effectuer une nouvelle commande
# ---------------------------
def ask_continue():
    speak("Voulez-vous faire autre chose ?")
    response = listen_for_command(prompt=False).strip().lower()
    if "oui" in response:
        speak("Super, comment puis-je vous aider ?")
        return True
    elif "non" in response:
        speak("Très bien, au besoin vous pouvez m'activer en cliquant sur le bouton 'Parler'.")
        return False
    else:
        speak("Je ne suis pas sûr d'avoir compris, veuillez répondre par 'oui' ou 'non'.")
        return ask_continue()

# ---------------------------
# Boucle d'assistance vocale
# ---------------------------
def assistant_loop():
    while True:
        command = listen_for_command()  # Prompt par défaut
        if command:
            execute_command(command)
        if not ask_continue():
            break

# ---------------------------
# Activation via le bouton de l'interface graphique
# ---------------------------
def activate_assistant():
    # Exécute l'assistant dans un thread pour ne pas bloquer l'UI
    threading.Thread(target=assistant_loop, daemon=True).start()

# ---------------------------
# Interface graphique principale
# ---------------------------
def create_gui():
    root = tk.Tk()
    root.title("Assistant Vocal")
    root.geometry("400x250")

    style = ttk.Style()
    style.theme_use("clam")

     # Bouton "Parler" avec symbole micro (l'utilisateur pourra également cliquer)
    btn_activate = ttk.Button(root, text="🎤", command=activate_assistant, width=5)
    btn_activate.pack(pady=20)

    btn_voice = ttk.Button(root, text="Modifier l'accent", command=select_accent_gui)
    btn_voice.pack(pady=10)

    # Lancer automatiquement l'assistant 1 seconde après le démarrage de l'interface
    root.after([1000, activate_assistant])  # Lancer automatiquement l'assistant après 1 seconde
    root.mainloop()

# ---------------------------
# Lancement de l'assistant
# ---------------------------
if __name__ == "__main__":
    create_gui()
