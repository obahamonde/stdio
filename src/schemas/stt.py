from pydantic import BaseModel


class VoiceFile(BaseModel):
    voice: str
