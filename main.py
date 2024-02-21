import io
import tempfile
import time
from typing import Any, Optional

import numpy as np
import scipy.io.wavfile as wavfile
import torch
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from sse_starlette.sse import EventSourceResponse

from src import AudioPrompt, Music, TensorStream
from src.store import ObjectStorage
from src.utils import flat

router = TensorStream()
music = Music()
storage = ObjectStorage()


def music_gen_next(
    audio_prompt: Optional[AudioPrompt] = None,
) -> np.ndarray[np.float32, Any]:
    if audio_prompt:
        text = audio_prompt.text
        audio = audio_prompt.audio
        if audio:
            return flat(
                music.gen_continuation(text=text, value=torch.tensor([[audio]]))
            )
        return flat(music.gen_music(text=text))
    return flat(music.gen())


@router.post("/music", response_class=ORJSONResponse)
async def music_gen_post(key: str, audio_prompt: Optional[AudioPrompt] = None):
    start = time.perf_counter()
    this = music_gen_next(audio_prompt)
    await router.pub(key=key, data=torch.tensor([[this]]))
    return ORJSONResponse(
        {
            "time": time.perf_counter() - start,
            "audio": this,
            "duration": 30,
            "sample_rate": 16000,
        }
    )


async def upload_audio(key: str, audio: np.ndarray):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
        wavfile.write(temp.name, 16000, audio)
        return await storage.put(
            key=key,
            file=UploadFile(
                file=io.BytesIO(temp.read()),
                size=len(temp.read()),
                filename=temp.name,
                headers={"content-type": "audio/wav"},
            ),
        )


async def music_gen_event_source(key: str):
    async for tensor in router.sub(key=key):
        nd_array = tensor[0][0].cpu().numpy()
        upload_data = await upload_audio(key, nd_array)
        yield {
            "url": upload_data["url"],
            "key": key,
        }

@router.get("/music", response_class=EventSourceResponse)
async def music_gen_get(key: str):
    return EventSourceResponse(music_gen_event_source(key))


app = FastAPI()

app.include_router(router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
