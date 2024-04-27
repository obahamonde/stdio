"""
This module contains utility functions and decorators.
"""

from __future__ import annotations

import asyncio
from typing import Any, TypeVar

import numpy as np
import torch
from numpy import ndarray
from typing_extensions import ParamSpec

T = TypeVar("T")
P = ParamSpec("P")


def get_loop() -> asyncio.AbstractEventLoop:
    """
    Returns the current event loop.

    Returns:
            asyncio.AbstractEventLoop: The current event loop.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


def splat(tensor: torch.Tensor | tuple[torch.Tensor, torch.Tensor]) -> torch.Tensor:
    """
    Extracts the first tensor from a tuple if the input is a tuple, otherwise returns the input tensor.

    Args:
            tensor (torch.Tensor | tuple[torch.Tensor, torch.Tensor]): The input tensor or a tuple of tensors.

    Returns:
            torch.Tensor: The first tensor from the input tuple, or the input tensor if it is not a tuple.
    """
    if isinstance(tensor, tuple):
        tensor = tensor[0]
    return tensor


def detach(tensor: torch.Tensor) -> torch.Tensor:
    """
    Detaches a tensor from the computation graph and returns a new tensor.

    Args:
            tensor (torch.Tensor): The input tensor.

    Returns:
            torch.Tensor: The detached tensor.

    """
    return torch.Tensor(tensor.detach().cpu().numpy())


def flat(tensor: torch.Tensor) -> ndarray[np.float32, Any]:
    """
    Converts a tensor to a numpy array.

    Args:
                    tensor (torch.Tensor): The input tensor.

    Returns:
                    ndarray: The numpy array.
    """
    return (
        tensor[0][0].cpu().numpy().astype(np.float32)
        if tensor.device.type == "cuda"
        else tensor[0][0].numpy().astype(np.float32)
    )
