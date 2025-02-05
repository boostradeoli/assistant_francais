# ==========================================
# 🚀 AGENT IA AVEC RÉFLEXION & VALIDATION
# ==========================================

import logging
import time
import threading
import pyttsx3
import speech_recognition as sr
import ollama  # 📌 Utilisation d'Ollama pour interagir avec le LLM

from services.email import email_module
from services.visio import visio_module
from services.photo import photo_module
from services.printing import printing_module

# ==========================================
# 🔹 INITIALISATION
# ==========================================

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 150)
tts_engine.setProperty("volume", 1.0)

recognizer = sr.Recognizer()
speech_lock = threading.Lock()

# 🔹 Modèle Ollama utilisé (assure-toi qu'il est bien installé)
LLM_MODEL_NAME = "tinyllama"

# ==========================================
# 🔹 FONCTIONS UTILITAIRES
# ==========================================

def speak(text: str):
    """ 🔊 L’agent IA parle et attend la fin avant de continuer. """
    global tts_engine
    with speech_lock:
        logging.info(f"🗣️ Agent IA dit : {text}")

        # 🔴 Réinitialisation du moteur pour éviter les blocages
        tts_engine = pyttsx3.init()
        tts_engine.setProperty("rate", 150)
        tts_engine.setProperty("volume", 1.0)

        tts_engine.say(text)
        tts_engine.runAndWait()
        time.sleep(1)

def listen() -> str:
    """ 🎤 Écoute et retourne le texte transcrit. """
    global recognizer
    with speech_lock:
        with sr.Microphone() as source:
            logging.info("🎤 Écoute...")
            try:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=5)
            except sr.WaitTimeoutError:
                logging.warning("⏳ Aucun son détecté.")
                return ""

    try:
        text = recognizer.recognize_google(audio, language="fr-FR")
        logging.info(f"✅ Reconnu : {text}")
        return text.lower()
    except sr.UnknownValueError:
        logging.warning("🔇 Impossible de comprendre.")
        return ""
    except sr.RequestError as e:
        logging.error(f"❌ Erreur de reconnaissance vocale : {e}")
        return ""

# ==========================================
# 🔹 INTERACTION AVEC LE LLM (OLLAMA)
# ==========================================

def query_llm(text: str) -> dict:
    """ 🧠 Envoie la requête au modèle Ollama et récupère la réponse. """
    try:
        response = ollama.generate(
            model=LLM_MODEL_NAME,
            prompt=f"""Tu es un assistant qui aide les utilisateurs à accomplir des tâches. 
            Donne une réponse claire et directe en un paragraphe court. 
            Identifie l'intention parmi : email, visio, photo, imprimer. 
            Si aucune intention claire n'est détectée, réponds normalement.
            
            Utilisateur : {text}
            Assistant :"""
        )

        response_text = response.get("response", "").strip()
        logging.info(f"🤖 Réponse du LLM : {response_text}")

        # 🔹 Détection des intentions avec des mots-clés
        if any(word in response_text.lower() for word in ["email", "mail"]):
            return {"intention": "email", "response": response_text}
        elif any(word in response_text.lower() for word in ["visioconférence", "appel vidéo"]):
            return {"intention": "visio", "response": response_text}
        elif "photo" in response_text.lower():
            return {"intention": "photo", "response": response_text}
        elif any(word in response_text.lower() for word in ["impression", "imprimer"]):
            return {"intention": "imprimer", "response": response_text}
        else:
            return {"intention": "unknown", "response": response_text}

    except Exception as e:
        logging.error(f"❌ Erreur avec Ollama : {e}")
        return {"intention": "unknown", "response": "Je ne peux pas traiter cette requête pour le moment."}

def verify_response(response_text: str) -> str:
    """ 🧐 Vérifie la réponse générée pour s'assurer qu'elle est correcte. """
    try:
        response = ollama.generate(
            model=LLM_MODEL_NAME,
            prompt=f"Peux-tu vérifier et corriger cette réponse si nécessaire ? {response_text}"
        )

        validated_response = response.get("response", "").strip()
        logging.info(f"✅ Réponse validée : {validated_response}")

        return validated_response if validated_response else response_text

    except Exception as e:
        logging.error(f"❌ Erreur de validation avec Ollama : {e}")
        return response_text

# ==========================================
# 🔹 EXÉCUTION DES COMMANDES
# ==========================================

def execute_command(intent: str):
    """ ⚡ Exécute l'action correspondant à l'intention détectée. """
    logging.info(f"🚀 Exécution de l'action pour l'intention : {intent}")

    if intent == "email":
        speak("J'ouvre votre messagerie pour écrire un email.")
        time.sleep(1)
        email_module.compose_email()
    elif intent == "visio":
        speak("Je démarre la visioconférence.")
        time.sleep(1)
        visio_module.start_visio()
    elif intent == "photo":
        speak("J'ouvre votre dossier de photos.")
        time.sleep(1)
        photo_module.view_photos()
    elif intent == "imprimer":
        speak("Je prépare l'impression du document.")
        time.sleep(1)
        printing_module.print_document()
    else:
        speak("Désolé, cette action n’est pas encore supportée.")

# ==========================================
# 🔹 BOUCLE PRINCIPALE
# ==========================================

def run_agent():
    """ 🔄 Agent IA : Écoute → Envoie au LLM → Vérifie → Répond → Agit. """
    speak("Bonjour, comment puis-je vous aider ?")

    while True:
        user_input = listen()
        if not user_input:
            speak("Je ne vous ai pas bien entendu. Pouvez-vous répéter ?")
            continue

        # 🔹 Envoie au LLM principal
        llm_response = query_llm(user_input)
        intent = llm_response["intention"]
        response_text = llm_response["response"]

        # 🔹 Vérification de la réponse
        validated_response = verify_response(response_text)

        # 🔹 L'agent IA parle uniquement après validation
        speak(validated_response)

        if intent != "unknown":
            execute_command(intent)

        # 🔹 Vérifie si l'utilisateur veut continuer
        speak("Voulez-vous faire autre chose ?")
        continue_input = listen()
        if "non" in continue_input:
            speak("D'accord, à bientôt !")
            break

# ==========================================
# 🔹 LANCEMENT
# ==========================================

if __name__ == "__main__":
    run_agent()
