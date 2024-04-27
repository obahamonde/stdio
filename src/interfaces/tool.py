from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Any, Generic, Literal, TypeAlias, TypeVar

from pydantic import BaseModel  # pylint: disable=E0401
from typing_extensions import Required, TypedDict

T = TypeVar("T")

Properties: TypeAlias = dict[str, object]


class AbstractTool(BaseModel, ABC, Generic[T]):
    """
    An abstract base class for tools.

    This class defines the common interface for all tools in the system.
    Subclasses should implement the `definition` and `run` methods.

    Attributes:
        None

    Methods:
        definition: Returns the definition of the tool.
        run: Executes the tool.

    """

    @classmethod
    @lru_cache
    @abstractmethod
    def definition(cls) -> T:
        """
        Returns the definition of the tool.

        :return: The definition of the tool.
        :rtype: T
        """
        raise NotImplementedError

    @abstractmethod
    async def run(self) -> Any:
        """
        This method is responsible for executing the tool's functionality.
        Subclasses must implement this method.

        Returns:
            Any: The result of the tool's execution.
        """
        raise NotImplementedError


class FunctionParameters(TypedDict, total=False):
    """
    Represents the parameters for a function.

    Attributes:
        type (Literal["object"]): The type of the function.
        properties (Properties): The properties of the function.
        required (list[str]): The required properties for the function.
    """

    type: Literal["object"]
    properties: Properties
    required: list[str]


class Function(TypedDict):
    """
    Represents a function with a name and description.

    Attributes:
        name (str): The name of the function.
        description (str): The description of the function.
    """

    name: Required[str]
    description: Required[str]


class IToolDefinition(Function):
    """
    Represents the definition of a Llama tool.

    Args:
        input_schema (FunctionParameters): The input schema for the tool.

    Attributes:
        input_schema (FunctionParameters): The input schema for the tool.
    """

    parameters: Required[FunctionParameters]


class ITool(AbstractTool[IToolDefinition]):
    """
    This class represents a Llama tool.

    It provides a definition method that returns an instance of `LlamaToolDefinition`.
    The `LlamaToolDefinition` contains information about the tool's name, description, and input schema.

    Subclasses of `LlamaTool` should implement the `run` method, which performs the actual functionality of the tool.
    """

    @classmethod
    @lru_cache
    def definition(cls) -> IToolDefinition:
        """
        Returns the definition of the Llama tool.

        :return: The definition of the Llama tool.
        :rtype: LlamaToolDefinition
        """
        assert cls.__doc__ is not None, f"Class {cls.__name__} is missing a docstring"
        _schema = cls.model_json_schema()
        fn = Function(
            name=cls.__name__.lower(),
            description=cls.__doc__,
        )
        return IToolDefinition(
            parameters={
                "type": "object",
                "properties": _schema.get("properties", {}),
                "required": _schema.get("required", []),
            },
            **fn,
        )

    @abstractmethod
    async def run(self) -> Any: ...
