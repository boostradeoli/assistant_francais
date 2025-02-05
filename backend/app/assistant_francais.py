import threading
import logging
import speech_recognition as sr
import pyttsx3

# Import des modules de gestion (assurez-vous que ces modules existent et qu'ils comportent les fonctions correspondantes)
from app.services.email import email_module
from app.services.visio import visio_module
from app.services.photo import photo_module
from app.services.printing import printing_module
from app.services.text_to_speech import tts_module

# Initialisation de la synthèse vocale avec pyttsx3
engine = pyttsx3.init()
engine.setProperty("rate", 150)
engine.setProperty("volume", 1.0)

def speak(text: str):
    """
    Affiche et prononce le texte passé en paramètre.
    """
    logging.info("Assistant: " + text)
    print("Assistant:", text)
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        logging.error("Erreur TTS: %s", e)

def listen_for_command(timeout: int = 5) -> str:
    """
    Écoute la commande vocale pendant un temps donné et renvoie le texte reconnu.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Écoute...")
        try:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=timeout)
        except sr.WaitTimeoutError:
            speak("Temps d'attente écoulé, je n'ai rien entendu.")
            return ""
    try:
        # Reconnaissance vocale avec Google (langue française)
        command = recognizer.recognize_google(audio, language="fr-FR")
        print("Vous avez dit:", command)
        return command.lower()
    except sr.UnknownValueError:
        speak("Je n'ai pas compris, pouvez-vous répéter ?")
    except sr.RequestError as e:
        speak("Erreur du service de reconnaissance vocale.")
        logging.error("RequestError: %s", e)
    return ""

def execute_command(command: str):
    """
    Détermine l'action à réaliser en fonction de la commande vocale.
    """
    if "email" in command or "courriel" in command or "mail" in command:
        speak("J'ouvre votre messagerie pour écrire un email.")
        email_module.compose_email()
    elif "visio" in command or "visioconférence" in command or "appel vidéo" in command:
        speak("Je démarre la visioconférence.")
        visio_module.start_visio()
    elif "photo" in command or "image" in command:
        speak("J'ouvre votre dossier de photos.")
        photo_module.view_photos()
    elif "imprimer" in command:
        speak("Je prépare l'impression du document.")
        printing_module.print_document()
    else:
        speak("Commande non reconnue, veuillez réessayer.")

def ask_continue() -> bool:
    """
    Demande à l'utilisateur s'il souhaite continuer et renvoie True si la réponse contient 'oui'.
    """
    speak("Voulez-vous faire autre chose ?")
    answer = listen_for_command(timeout=3)
    return "oui" in answer

def assistant_loop():
    """
    Boucle principale de l'assistant vocal.
    """
    speak("Bonjour, comment puis-je vous aider ?")
    while True:
        command = listen_for_command()
        if command:
            execute_command(command)
        if not ask_continue():
            speak("D'accord, à bientôt !")
            break

def run_assistant():
    """
    Fonction d'activation de l'assistant vocal.
    """
    assistant_thread = threading.Thread(target=assistant_loop, daemon=True)
    assistant_thread.start()
    assistant_thread.join()  # On attend que la boucle se termine

if __name__ == "__main__":
    run_assistant()
