import pyttsx3
import logging

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty("rate", 150)
engine.setProperty("volume", 1.0)

def say_text(text: str):
    """
    Convert text to speech.
    """
    logging.info("Saying: %s", text)
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        logging.error("TTS error: %s", e)
