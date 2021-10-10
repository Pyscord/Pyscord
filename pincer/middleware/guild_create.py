# Copyright Pincer 2021-Present
# Full MIT License can be found in `LICENSE` at the project root.

"""sent when a guild is created/joined on the client"""
from __future__ import annotations

from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.dispatch import GatewayDispatch

from ..objects.guild import Guild

def guild_create_middleware(
    self,
    payload: GatewayDispatch
) -> Tuple[str, List[Guild]]:
    """Middleware for ``on_error`` event.

    Parameters
    ----------
    payload : GatewayDispatch
        The data received from the ready event.
    """
    return "on_guild_create", [
        Guild.from_dict(
            {"_client": self, "_http": self.http, **payload.data}
        )
    ]

def export():
    return guild_create_middleware
