import logging
import speech_recognition as sr
import spacy

# Load French NLP model
nlp = spacy.load("fr_core_news_sm")

def capture_and_process():
    """
    Capture audio from microphone and process it using NLP.
    Returns the recognized text and detected intent.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        logging.info("Listening for command...")
        audio = recognizer.listen(source, timeout=5)
    try:
        text = recognizer.recognize_google(audio, language="fr-FR")
        logging.info("Recognized speech: %s", text)
        # Use spaCy to process text; placeholder for intent detection
        doc = nlp(text)
        # Example: determine if command contains the word "email"
        intent = "email" if "email" in text.lower() else "unknown"
        return text, intent
    except Exception as e:
        logging.error("Error during speech recognition: %s", e)
        return "", "error"
