"""
This module contains utility functions and decorators.
"""

from __future__ import annotations

import asyncio
from functools import wraps
from typing import Any, Type, TypeVar, cast

import numpy as np
import torch
from numpy import ndarray
from typing_extensions import ParamSpec

T = TypeVar("T")
P = ParamSpec("P")


def singleton(cls: Type[T]) -> Type[T]:
    """
    Decorator that converts a class into a singleton.

    Args:
            cls (Type[T]): The class to be converted into a singleton.

    Returns:
            Type[T]: The singleton instance of the class.
    """
    instances: dict[Type[T], T] = {}

    @wraps(cls)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return cast(Type[T], wrapper)


def loop() -> asyncio.AbstractEventLoop:
    """
    Returns the current event loop.

    Returns:
            asyncio.AbstractEventLoop: The current event loop.
    """
    return asyncio.get_running_loop()


@torch.no_grad
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


@torch.no_grad
def detach(tensor: torch.Tensor) -> torch.Tensor:
    """
    Detaches a tensor from the computation graph and returns a new tensor.

    Args:
            tensor (torch.Tensor): The input tensor.

    Returns:
            torch.Tensor: The detached tensor.

    """
    return torch.tensor(tensor.detach().cpu().numpy())


@torch.no_grad
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
