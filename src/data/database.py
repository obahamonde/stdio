from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Any, Generic, Type, TypeVar
from uuid import uuid4

import hnswlib
import orjson
from pydantic import BaseModel, Field  # pylint: disable=E0401
from typing_extensions import Self

from ..integration.rocksdb import Collection  # type: ignore
from ..interfaces.tool import Properties
from ..utils.handlers import asyncify


class CosimResult(BaseModel):
    """
    Represents the result of a cosine similarity search.

    Attributes:
            id (str): The id of the document.
            score (float): The cosine similarity score.
    """

    id: str
    score: float
    content: str


class Base(BaseModel):
    """
    Base class for the schema.

    Attributes:
            id (str): The ID of the object.
            content (str): The content of the object.
            metadata (list[dict[str, object]]): The metadata associated with the object.
            model_config (dict): Configuration for the model.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    model_config = {
        "arbitrary_types_allowed": True,
    }

    @cached_property
    def store(self) -> Store[Self]:
        """
        Returns the store associated with the API instance.

        Returns:
                Store: The store object.
        """
        return Store[Self]("db/" + self.__class__.__name__.lower())


T = TypeVar("T", bound=Base)


@dataclass
class Store(Generic[T]):
    """
    A class to represent a Vector Capable Store.
    A `Store` is a data store that can store and retrieve instances of a class that inherits from `Base` and support the `Vector` type.
    It's intended to be used with the `Collection` class from the `rocksdb_wrapper` module which is a C++ extension for RocksDB..
    It takes a generic type `T` that is a subclass of `Base` and represents the type of document being stored.
    A `document` is a `pydantic` BaseModel instance that inherits from the `Base` class and has a `value` of type `Vector`, a content of type `str`, and an optional metadata array of `JSON` objects.
    Each Store has a path within the filesystem where the data is stored with `rocksdb` as the underlying storage engine.
    Encompasses the basic CRUD operations for a data store with the ability to store and retrieve vectorized documents.
    It's compatible with `numpy` data types and by default stores vectors by default supports dimensionalities of 512, 768, 1536, 3072, and 4096.
    [TODO] Document why the dimensionalities are chosen and how they are used.
    """

    path: str

    @cached_property
    def col(self) -> Collection:
        """
        The collection being used by the store defined by the path.
        [TODO] Support compatibility with s3 and gcs `fuse` filesystems.
        [TODO] Support integration within Kubernetes as a `PersistentVolume` or `PersistentVolumeClaim`.
        """
        return Collection(self.path)  # type: ignore

    @asyncify
    def create(self, instance: T) -> None:
        """
        Creates a new instance in the store.

        Args:
                instance (T): The instance to be created.

        Returns:
                None
        """
        self.col.create(instance.id, instance.model_dump())

    @asyncify
    def update(self: Store[T], instance: T) -> None:
        """
        Update the document in the collection with the given instance.

        Args:
                instance (T): The instance to update.

        Returns:
                None
        """
        kwargs = instance.model_dump()
        _id = kwargs.pop("id")
        self.col.update(_id, kwargs)

    @asyncify
    def delete_(self, key: str) -> None:
        """
        Deletes the item with the specified key from the store.

        Args:
                key (str): The key of the item to delete.

        Returns:
                None
        """
        self.col.delete(key)

    @asyncify
    def find_one(self, key: str) -> T:
        """
        Finds and returns a single document from the collection based on the given key.

        Args:
                key (str): The key to search for in the collection.

        Returns:
                T: The document found, or None if no document matches the key.
        """
        return self.col.find_one(key)

    @asyncify
    def find_many(self, **kwargs: Any) -> list[T]:
        """
        Find multiple documents in the collection based on the given key-value pairs.
        """
        return [
            doc for doc in self.col.find_many(kwargs)  # pylint: disable=E1101
        ]  # pylint: disable=E1101

    @asyncify
    def find_first(self) -> T:
        """
        Find the first document in the collection based on the given key-value pairs.
        """
        return orjson.loads(self.col.find_first())  # pylint: disable=E1101

    @asyncify
    def find_last(self) -> T:
        """
        Find the last document in the collection based on the given key-value pairs.
        """
        return orjson.loads(self.col.find_last())  # pylint: disable=E1101

    @asyncify
    def find_all(self) -> list[T]:
        """
        Retrieves all items from the collection.

        Returns:
                A list of items from the collection.
        """
        return [doc for doc in self.col.find_all()]

    @asyncify
    def count(self) -> int:
        """
        Returns the number of items in the collection.

        Returns:
                int: The number of items in the collection.
        """
        return self.col.count()

    @asyncify
    def _cosim_search(
        self, vector: list[float], world: list[Properties], top_k: int
    ) -> list[CosimResult]:
        """
        Search for the top `k` most similar items to the given vector.

        Args:
                vector (list[float]): The vector to search for.
                world (list[dict]): The list of items to search within, each item is a dict containing an 'id' and a 'vector'.
                top_k (int): The number of items to return.

        Returns:
                list[dict[float, T]]: A list of dicts with similarity percentages and corresponding items, sorted by decreasing similarity.
        """
        if not world:
            return []

        dim = len(vector)
        p = hnswlib.Index(space="cosine", dim=dim)  # type: ignore
        p.init_index(max_elements=len(world), ef_construction=200, M=16)
        world = [orjson.loads(doc) for doc in world]  # pylint: disable=E1101
        items = [doc["value"] for doc in world]
        p.add_items(items)
        labels, distances = p.knn_query(vector, k=top_k)
        world = [world[label] for label in labels[0]]
        return [
            CosimResult(
                **{
                    "score": 1 - distance,
                    "content": world[i]["content"],
                    "id": world[i]["id"],
                }  # type: ignore
            )
            for i, distance in enumerate(distances[0])
        ]

    async def cosim(
        self, vector: list[float], top_k: int, **kwargs: Any
    ) -> list[CosimResult]:
        """
        Search for the top `k` most similar items to the given vector.

        Args:
                vector (list[float]): The vector to search for.
                top_k (int): The number of items to return.

        Returns:
                list[str]: A list of keys of the most similar items.
        """
        if kwargs:
            world = await self.find_many(**kwargs)
        else:
            world = await self.find_all()
        print(len(vector))
        return [
            CosimResult(**item)
            for item in await self._cosim_search(vector, world, top_k)
        ]


R = TypeVar("R", bound="RocksDBModel")


class RocksDBModel(Base):
    """
    A class to represent a document that can be stored in a RocksDB collection.
    A `RockDBModel` is a `Base` document that can be stored in a RocksDB collection.
    It's intended to be used with the `Store` class to store and retrieve vectorized documents.
    A `RockDBModel` is a `Base` document that can be stored in a RocksDB collection.
    It has a `value` of type `Vector`, a content of type `str`, and an optional metadata array of `JSON` objects.
    Each `RockDBModel` has a path within the filesystem where the data is stored with `rocksdb` as the underlying storage engine.
    Encompasses the basic CRUD operations for a data store with the ability to store and retrieve vectorized documents.
    It's compatible with `numpy` data types and by default stores vectors by default supports dimensionalities of 512, 768, 1536, 3072, and 4096.
    [TODO] Document why the dimensionalities are chosen and how they are used.
    """

    @classmethod
    def __init_subclass__(cls: Type[Self], **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)  # type: ignore
        cls.store = Store[Self]("db/" + cls.__name__.lower())

    @cached_property
    def store(self) -> Store[Self]:
        return Store[Self]("db/" + self.__class__.__name__.lower())

    async def save(self: Self) -> None:
        if not self.store.col.exists(self.id):
            await self.store.create(self)
        else:
            await self.store.update(self)

    async def update(self: Self, instance: Self) -> None:
        await self.store.update(instance)

    @classmethod
    async def find_one(cls: Type[Self], key: str) -> Self:
        data = await cls.store.find_one(key)
        return cls(**data)

    @classmethod
    async def find_many(cls: Type[Self], **kwargs: Any) -> list[Self]:
        res = await cls.store.find_many(**kwargs)
        return [cls(**data) for data in res]

    @classmethod
    async def find_first(cls: Type[Self]) -> Self:
        return cls(**await cls.store.find_first())

    @classmethod
    async def find_last(cls: Type[Self]) -> Self:
        return cls(**await cls.store.find_last())

    @classmethod
    async def find_all(cls: Type[Self]) -> list[Self]:
        return [cls(**data) for data in await cls.store.find_all()]

    @classmethod
    async def count(cls) -> int:
        return await cls.store.count()

    @classmethod
    async def cosim(cls, vector: list[float], top_k: int) -> list[CosimResult]:
        return await cls.store.cosim(vector, top_k)

    @classmethod
    async def delete(cls, key: str) -> None:
        await cls.store.delete_(key)
