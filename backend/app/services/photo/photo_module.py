import subprocess
import platform
import logging
import os

def view_photos():
    """
    Opens the photo folder.
    """
    photo_folder = os.path.expanduser("~/Pictures")
    try:
        if platform.system() == "Windows":
            subprocess.Popen(["explorer", photo_folder])
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", photo_folder])
        logging.info("Photo folder opened: %s", photo_folder)
    except Exception as e:
        logging.error("Error opening photo folder: %s", e)
