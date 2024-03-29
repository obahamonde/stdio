"""
This module contains the `Music` class for generating music using the `MusicGen` model.
"""

from functools import cached_property
from typing import Any, Optional

import numpy as np
import torch
from audiocraft.models.musicgen import MusicGen

from .schemas import AudioPrompt
from .utils import detach, flat, singleton, splat


@singleton
class Music:
    """
    A generic class for generating music using the `MusicGen` model with a singleton instance.
    """

    @cached_property
    def model(self) -> MusicGen:
        """
        The `MusicGen` model for generating music.

        Returns:
                                        MusicGen: The `MusicGen` model.
        """
        return MusicGen.get_pretrained()  # pylint: disable=E1101 # type: ignore

    @torch.no_grad  # type: ignore
    def gen(self) -> torch.Tensor:
        """
        Generates unconditional music using the `generate_unconditional` method.

        Returns:
                                        torch.Tensor: The generated music as a tensor.
        """
        tensor = self.model.generate_unconditional(num_samples=1, progress=True)
        return splat(tensor)

    @torch.no_grad  # type: ignore
    def gen_music(self, *, text: str) -> torch.Tensor:
        """
        Generates music based on the given text using the `generate` method.

        Args:
                                        text (str): The text description for generating music.

        Returns:
                                        torch.Tensor: The generated music as a tensor.
        """
        tensor = self.model.generate(descriptions=[text], progress=True)
        return splat(tensor)

    @torch.no_grad  # type: ignore
    def gen_continuation(self, *, text: str, value: torch.Tensor) -> torch.Tensor:
        """
        Generates music continuation based on the given text and value using the `generate_continuation` method.

        Args:
                                        text (str): The text description for generating music continuation.
                                        value (torch.Tensor): The value tensor for generating music continuation.

        Returns:
                                        torch.Tensor: The generated music continuation as a tensor.
        """
        prompt = detach(value)
        prompt_sample_rate = 44100
        tensor = self.model.generate_continuation(
            prompt, prompt_sample_rate, [text], progress=True
        )
        return splat(tensor)


music = Music()


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
