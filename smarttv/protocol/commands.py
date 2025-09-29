# protocol/commands.py
from __future__ import annotations
from enum import Enum
from typing import Dict, Iterable

class Command(str, Enum):
    POWER_ON     = "POWER_ON"
    POWER_OFF    = "POWER_OFF"
    GET_CHANNELS = "GET_CHANNELS"
    SET_CHANNEL  = "SET_CHANNEL"   # expects 1 int arg
    CHANNEL_UP   = "CHANNEL_UP"
    CHANNEL_DOWN = "CHANNEL_DOWN"
    GET_STATUS   = "GET_STATUS"
    QUIT         = "QUIT"

# Canonical tokens (exact enum values)
VALID: set[str] = {c.value for c in Command}

# Friendly aliases (case-insensitive at parse time)
ALIASES: Dict[str, Command] = {
    # Power
    "POWER_ON": Command.POWER_ON, "ON": Command.POWER_ON, "TURN_ON": Command.POWER_ON,
    "POWER_OFF": Command.POWER_OFF, "OFF": Command.POWER_OFF, "TURN_OFF": Command.POWER_OFF,
    # Channels
    "GET_CHANNELS": Command.GET_CHANNELS, "LIST": Command.GET_CHANNELS, "CHANNELS": Command.GET_CHANNELS,
    "SET_CHANNEL": Command.SET_CHANNEL, "SET": Command.SET_CHANNEL,
    "CHANNEL_UP": Command.CHANNEL_UP, "UP": Command.CHANNEL_UP,
    "CHANNEL_DOWN": Command.CHANNEL_DOWN, "DOWN": Command.CHANNEL_DOWN,
    # Status / Quit
    "GET_STATUS": Command.GET_STATUS, "STATUS": Command.GET_STATUS,
    "QUIT": Command.QUIT, "EXIT": Command.QUIT,
}

def normalize(token: str) -> Command:
    """Map an inbound token to a canonical Command via alias table."""
    key = token.strip().upper()
    cmd = ALIASES.get(key)
    if cmd is None:
        from .errors import UnknownCommandError
        raise UnknownCommandError(f"Unknown command: {token!r}")
    return cmd

def arity(command: Command) -> int:
    """Number of required arguments for each command."""
    if command is Command.SET_CHANNEL:
        return 1
    return 0

def expects_args(command: Command) -> bool:
    return arity(command) > 0
