import sys
from dataclasses import dataclass

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from strenum import StrEnum


class ClientGeneration(StrEnum):
    NONE = "none"
    """Clients are not generated."""

    SYNC = "sync"
    """Only synchronous clients are generated."""

    ASYNC = "async"
    """Only asynchronous clients are generated."""

    SYNC_ASYNC = "sync_async"
    """Both synchronous and asynchronous clients are generated.

    Asynchronous clients are generated with the Async suffix."""

    ASYNC_SYNC = "async_sync"
    """Both synchronous and asynchronous clients are generated.

    Synchronous clients are generated with the Sync suffix."""

    SYNC_ASYNC_NO_DEFAULT = "sync_async_no_default"
    """Both synchronous and asynchronous clients are generated.

    Synchronous clients are generated with the Sync suffix, and asynchronous clients are generated with the Async
    suffix."""

    @property
    def is_sync_generated(self) -> bool:
        return self in {
            ClientGeneration.SYNC,
            ClientGeneration.SYNC_ASYNC,
            ClientGeneration.ASYNC_SYNC,
            ClientGeneration.SYNC_ASYNC_NO_DEFAULT,
        }

    @property
    def is_async_generated(self) -> bool:
        return self in {
            ClientGeneration.ASYNC,
            ClientGeneration.SYNC_ASYNC,
            ClientGeneration.ASYNC_SYNC,
            ClientGeneration.SYNC_ASYNC_NO_DEFAULT,
        }

    @property
    def is_sync_prefixed(self) -> bool:
        return self in {ClientGeneration.ASYNC_SYNC, ClientGeneration.SYNC_ASYNC_NO_DEFAULT}

    @property
    def is_async_prefixed(self) -> bool:
        return self in {ClientGeneration.SYNC_ASYNC, ClientGeneration.SYNC_ASYNC_NO_DEFAULT}


class ServerGeneration(StrEnum):
    NONE = "none"
    ASYNC = "async"


@dataclass
class Settings:
    pydantic_dataclasses: bool

    client_generation: ClientGeneration
    server_generation: ServerGeneration
