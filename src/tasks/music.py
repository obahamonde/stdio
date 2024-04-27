"""
This module contains the `Music` class for generating music using the `MusicGen` model.
"""

# pylint: disable=E0402
from functools import cached_property
from typing import Any

import numpy as np
import torch
from audiocraft.models.musicgen import MusicGen
from fastapi.responses import ORJSONResponse
from pydantic import Field

from ..interfaces import Identifier, IRequest, ITask
from ..schemas import MusicRequest
from ..utils.handlers import asyncify, handle, singleton
from ..utils.tensor import detach, flat, splat

CHUNKSIZE = 1024 * 1024


@singleton
class Music(ITask[MusicRequest, ORJSONResponse]):
    """
    A generic class for generating music using the `MusicGen` model with a singleton instance.
    """

    identifier: Identifier = Field(default="facebook/musicgen-melody")

    @cached_property
    def model(self) -> MusicGen:
        return MusicGen.get_pretrained(
            self.identifier, device="cuda" if torch.cuda.is_available() else "cpu"
        )  # pylint: disable=E1101 # type: ignore

    @asyncify
    def gen(self) -> torch.Tensor:
        tensor = self.model.generate_unconditional(num_samples=1, progress=True)
        return splat(tensor)

    @asyncify
    def gen_music(self, *, text: str) -> torch.Tensor:
        tensor = self.model.generate(descriptions=[text], progress=True)
        return splat(tensor)

    @asyncify
    def gen_continuation(self, *, text: str, value: torch.Tensor) -> torch.Tensor:
        prompt = detach(value)
        prompt_sample_rate = 44100
        tensor = self.model.generate_continuation(
            prompt, prompt_sample_rate, [text], progress=True
        )
        return splat(tensor)

    async def _handler(
        self, audio_prompt: MusicRequest | None = None
    ) -> np.ndarray[np.float32, Any]:
        if audio_prompt:
            text = audio_prompt.text
            audio = audio_prompt.audio
            if audio:
                return flat(
                    tensor=await self.gen_continuation(
                        text=text, value=torch.Tensor([[audio]])
                    )
                )
            return flat(tensor=await self.gen_music(text=text))
        return flat(tensor=await self.gen())

    @handle
    async def handler(self, *, request: IRequest[MusicRequest]):
        return ORJSONResponse(content={"audio": await self._handler(request.input)})
