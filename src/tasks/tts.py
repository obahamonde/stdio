import re
import tempfile
from typing import Any

import httpx
import numpy as np
import pydub
import pytube
import torch
from pydantic import Field
from sse_starlette import EventSourceResponse
from whisper import load_model, transcribe

from ..interfaces import Identifier, IRequest, ITask
from ..schemas import YoutubeVideoRequest
from ..utils.handlers import asyncify, handle

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")
MODEL = "large" if torch.cuda.is_available() else "small"
SAMPLE_RATE = 16000
CHUNK_DURATION = 3
CHUNKSIZE = SAMPLE_RATE * CHUNK_DURATION
model = load_model(MODEL).to(DEVICE)


class YoutubeToText(ITask[YoutubeVideoRequest, EventSourceResponse]):
    identifier: Identifier = Field(default="openai/whisper-large-v3")

    @asyncify
    def transcribe_youtube(self, *, url: str):
        yt = pytube.YouTube(url)
        stream = yt.streams.filter(only_audio=True).first()
        with tempfile.TemporaryDirectory() as tmpdir:
            stream.download(output_path=tmpdir)
            audio_file_path = f"{tmpdir}/{stream.default_filename}"
            audio = pydub.AudioSegment.from_file(audio_file_path)
            audio = audio.set_channels(1).set_frame_rate(SAMPLE_RATE)
            audio_samples = np.array(audio.get_array_of_samples(), dtype=np.float32) / (
                2**15
            )
            return audio_samples

    async def generator(self, *, audio_samples: np.ndarray[np.float32, Any]):
        for i in range(0, len(audio_samples), CHUNKSIZE):
            chunk = audio_samples[i : i + CHUNKSIZE]
            if len(chunk) < CHUNKSIZE:
                chunk = np.pad(chunk, (0, CHUNKSIZE - len(chunk)), mode="constant")
            text = transcribe(model, chunk)
            _text = text["text"]
            assert isinstance(_text, str)
            yield _text

    async def search_videos(self, *, query: str):
        search_url = f"https://www.youtube.com/results?search_query={query}"
        async with httpx.AsyncClient() as client:
            response = await client.get(
                search_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
                },
            )
            data = response.text
            pattern = re.compile(r"watch\?v=(\S{11})")
            videos = set[str]()
            for video_id in pattern.findall(data):
                videos.add(f"https://www.youtube.com/watch?v={video_id}")
            for url in videos:
                yt = pytube.YouTube(url)
                yield {
                    "title": yt.title,
                    "url": url,
                    "thumbnail": yt.thumbnail_url,
                    "author": yt.author,
                    "length": yt.length,
                    "views": yt.views,
                    "rating": yt.rating,
                }

    @handle
    async def handler(self, *, request: IRequest[YoutubeVideoRequest]):
        audio_samples = await self.transcribe_youtube(url=request.input.url)
        return EventSourceResponse(self.generator(audio_samples=audio_samples))

    @handle
    async def search(self, *, query: str):
        return [video async for video in self.search_videos(query=query)]
