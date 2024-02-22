import time
from typing import Optional

from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

from .music import music_gen_next
from .schemas import AudioPrompt, AudioResponse
from .store import upload_audio

router = APIRouter(prefix="/api")


@router.post("/music/{key}", response_class=ORJSONResponse)
async def music_gen_post(key: str, audio_prompt: Optional[AudioPrompt] = None):
    start = time.perf_counter()
    audio = music_gen_next(audio_prompt)
    url, key = await upload_audio(key=key, audio=audio)
    return ORJSONResponse(
        AudioResponse(
            {
                "time": time.perf_counter() - start,
                "audio": audio,
                "duration": 30,
                "sample_rate": 16000,
                "url": url,
                "key": key,
            }
        )
    )
