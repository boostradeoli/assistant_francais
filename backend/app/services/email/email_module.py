import webbrowser
import logging

def compose_email(recipient: str = ""):
    """
    Opens the default email client using a mailto URL.
    """
    try:
        if recipient:
            mailto_url = f"mailto:{recipient}"
        else:
            mailto_url = "mailto:"
        webbrowser.open(mailto_url)
        logging.info("Email client opened with URL: %s", mailto_url)
    except Exception as e:
        logging.error("Error opening email client: %s", e)
