# SPDX-FileCopyrightText: 2015 Eric Larson
#
# SPDX-License-Identifier: Apache-2.0

"""
The cache object API for implementing caches. The default is a thread
safe in-memory dictionary.
"""
from threading import Lock
from typing import IO, TYPE_CHECKING, MutableMapping, Optional, Union

if TYPE_CHECKING:
    from datetime import datetime


class BaseCache(object):
    def get(self, key: str) -> Optional[bytes]:
        raise NotImplementedError()

    def set(
        self, key: str, value: bytes, expires: Optional[Union[int, "datetime"]] = None
    ) -> None:
        raise NotImplementedError()

    def delete(self, key: str) -> None:
        raise NotImplementedError()

    def close(self) -> None:
        pass


class DictCache(BaseCache):
    def __init__(self, init_dict: Optional[MutableMapping[str, bytes]] = None) -> None:
        self.lock = Lock()
        self.data = init_dict or {}

    def get(self, key: str) -> Optional[bytes]:
        return self.data.get(key, None)

    def set(
        self, key: str, value: bytes, expires: Optional[Union[int, "datetime"]] = None
    ) -> None:
        with self.lock:
            self.data.update({key: value})

    def delete(self, key: str) -> None:
        with self.lock:
            if key in self.data:
                self.data.pop(key)


class SeparateBodyBaseCache(BaseCache):
    """
    In this variant, the body is not stored mixed in with the metadata, but is
    passed in (as a bytes-like object) in a separate call to ``set_body()``.

    That is, the expected interaction pattern is::

        cache.set(key, serialized_metadata)
        cache.set_body(key)

    Similarly, the body should be loaded separately via ``get_body()``.
    """

    def set_body(self, key: str, body: bytes) -> None:
        raise NotImplementedError()

    def get_body(self, key: str) -> Optional["IO[bytes]"]:
        """
        Return the body as file-like object.
        """
        raise NotImplementedError()
