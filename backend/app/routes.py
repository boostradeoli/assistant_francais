from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.utils.security import verify_token
from app.services import (
    speech_recognition_nlp,
    text_to_speech,
    email as email_service,
    visio as visio_service,
    photo as photo_service,
    printing as printing_service,
)

router = APIRouter()

# Example Pydantic models for request/response
class CommandRequest(BaseModel):
    command: str

class CommandResponse(BaseModel):
    message: str
    data: dict = {}

@router.post("/activate-assistant", response_model=CommandResponse)
async def activate_assistant(token: str, command_request: CommandRequest, user=Depends(verify_token)):
    """
    Endpoint to process a command.
    This will route the command to the appropriate service based on intent.
    """
    command = command_request.command.lower()

    # Simplified intent detection (expand with your NLP logic)
    if "email" in command:
        email_service.email_module.compose_email()
        response = CommandResponse(message="Email module activated", data={"module": "email"})
    elif "speak" in command:
        text_to_speech.tts_module.say_text("Hello, this is your assistant.")
        response = CommandResponse(message="TTS module activated", data={"module": "tts"})
    elif "video" in command or "visio" in command:
        visio_service.visio_module.start_visio()
        response = CommandResponse(message="Visio module activated", data={"module": "visio"})
    elif "photo" in command:
        photo_service.photo_module.view_photos()
        response = CommandResponse(message="Photo module activated", data={"module": "photo"})
    elif "print" in command:
        printing_service.printing_module.print_document()
        response = CommandResponse(message="Printing module activated", data={"module": "printing"})
    else:
        raise HTTPException(status_code=400, detail="Command not recognized")

    return response
