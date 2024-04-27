from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Iterable, TypeVar, cast

from typing_extensions import override

T_co = TypeVar("T_co", covariant=True)


class IProxy(Generic[T_co], ABC):
    """Implements data methods to pretend that an instance is another instance.

    This includes forwarding attribute access and othe methods.
    """

    # Note: we have to special case proxies that themselves return proxies
    # to support using a proxy as a catch-all for any random access, e.g. `proxy.foo.bar.baz`

    def __getattr__(self, attr: str) -> object:
        proxied = self.__get_proxied__()
        if isinstance(proxied, IProxy):
            return proxied  # pyright: ignore
        return getattr(proxied, attr)

    @override
    def __repr__(self) -> str:
        proxied = self.__get_proxied__()
        if isinstance(proxied, IProxy):
            return proxied.__class__.__name__
        return repr(self.__get_proxied__())

    @override
    def __str__(self) -> str:
        proxied = self.__get_proxied__()
        if isinstance(proxied, IProxy):
            return proxied.__class__.__name__
        return str(proxied)

    @override
    def __dir__(self) -> Iterable[str]:
        proxied = self.__get_proxied__()
        if isinstance(proxied, IProxy):
            return []
        return proxied.__dir__()

    @property  # type: ignore
    @override
    def __class__(self) -> type:  # type: ignore
        proxied = self.__get_proxied__()
        if issubclass(type(proxied), IProxy):
            return type(proxied)
        return proxied.__class__

    def __get_proxied__(self) -> T_co:
        return self.__load__()

    def __as_proxied__(self) -> T_co:
        """Helper method that returns the current proxy, typed as the loaded object"""
        return cast(T_co, self)

    @abstractmethod
    def __load__(self) -> T_co: ...
