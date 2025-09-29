# messages.py
# Handles all valid commands'
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict

TERMINATOR = b"\n" # Each message is one line ending with with \n

# --- Errors --- 

class ProtocolError(Exception):
    """Base class for protocol-level errors"""

class UnknownCommandError(ProtocolError):
    """Raised when a command is not valid"""

class InvalidArgumentError(ProtocolError):
    """Raised when args are missing or wrong type"""

# --- Commands --- 

class Command(str, Enum):
    POWER_ON    = "POWER_ON"
    POWER_OFF   = "POWER_OFF"
    GET_CHANNELS= "GET_CHANNELS"
    SET_CHANNEL= "SET_CHANNELS"    # Expects 1 int arg
    CHANNEL_UP  = "CHANNEL_UP"
    CHANNEL_DOWN= "CHANNEL_DOWN"
    GET_STATUS  = "GET_STATUS"      # debugging
    QUIT        = "QUIT"

VALID = {c.value for c in Command}

# --- Messages ---

@dataclass(frozen=True)
class Message:
    command: Command
    args: List[str]

    def to_line(self) -> bytes:
        if self.args:
            text = f"{self.command.value} {' '.join(self.args)}\n"
        else:
            text = f"{self.command.value}\n"
        return text.encode("utf-8")

# --- Builder (with validation) ---

def build(command: Command | str, *args: str) -> Message:
    """
    Create a Message, validating arity, and basic types for known commands
    """
    if isinstance(command, str):
        cmd_upper = command.upper()
        if cmd_upper not in VALID:
            raise UnknownCommandError(f"Unknown command: {command!r}")
        command = Command(cmd_upper)

    _validate(command, list(args))
    return Message(command=command,args=list(args))

# --- Parser --- 

def parse_line(line: bytes) -> Message:
    """
    Parse bytes -> Message. Accepts 'COMMAND\\n' or 'COMMAND arg ... \\n'
    """
    try: 
        text = line.decode("utf-8").strip()
    except UnicodeDecodeError as e:
        raise ProtocolError(f"Invald UTF-8: {e}") from e

    if not text:
        raise ProtocolError("Empty line")

    parts = text.split()
    cmd = parts[0].upper()
    if cmd not in VALID:
        raise UnknownCommandError(f"Unknown command error: {cmd!r}")

    command = Command(cmd)
    args = parts[1:]
    _validate(command, args)
    return Message(command=command, args=args)

# --- Validation ---

def _validate(command: Command, args: List[str]) -> None:
    """Enforce argument counts and simple type checks per command."""
    if command is Command.SET_CHANNEL:
        if len(args) != 1:
            raise InvalidArgumentError("SET_CHANNEL requires exactly 1 argument")
        if not _is_nonnegative_int(args[0]):
            raise InvalidArgumentError("SET_CHANNEL argument must be a non-negative integer")
        return

    # all others take no args
    if command in (
        Command.POWER_ON, Command.POWER_OFF, Command.GET_CHANNELS,
        Command.CHANNEL_UP, Command.CHANNEL_DOWN, Command.GET_STATUS, Command.QUIT
    ):
        if args:
            raise InvalidArgumentError(f"{command.value} takes no arguments")

def _is_nonnegative_int(s: str) -> bool:
    try:
        return int(s) >= 0
    except ValueError:
        return False   

# --- Command descriptions ----------------

COMMAND_DESCRIPTIONS: Dict[Command, str] = {  # ADDED
    Command.POWER_ON:     "Turn the TV on",
    Command.POWER_OFF:    "Turn the TV off",
    Command.GET_CHANNELS: "List all available channels",
    Command.SET_CHANNEL: "Select channel by index: SET_CHANNEL <n>",
    Command.CHANNEL_UP:   "Go to next channel (wraps around)",
    Command.CHANNEL_DOWN: "Go to previous channel (wraps around)",
    Command.GET_STATUS:   "Show power state and current channel",
    Command.QUIT:         "Close the session",
}

# ---Reply templates and helpers -----------------------------------

# templates for server replies; format kwargs supplied by domain layer (smart_tv)
REPLY_TEMPLATES: Dict[Command, str] = {
    Command.POWER_ON:     "OK POWER_ON",
    Command.POWER_OFF:    "OK POWER_OFF",
    Command.GET_CHANNELS: "CHANNELS {channels}",
    Command.SET_CHANNEL: "OK CHANNEL {index} {name}",
    Command.CHANNEL_UP:   "OK CHANNEL {index} {name}",
    Command.CHANNEL_DOWN: "OK CHANNEL {index} {name}",
    Command.GET_STATUS:   "STATUS {state} CURRENT {index} {name}",
    Command.QUIT:         "OK BYE",
}

def render_reply(command: Command, **kwargs) -> str:
    """
    Render a reply string for a command using REPLY_TEMPLATES.
    The domain (smart_tv) supplies context via kwargs when needed:
      - GET_CHANNELS: channels="NRK1,NRK2"
      - SET_CHANNEL/CHANNEL_UP/CHANNEL_DOWN/GET_STATUS: index=int, name=str, (state="ON"/"OFF" for GET_STATUS)
    """
    template = REPLY_TEMPLATES.get(command)
    if template is None:
        return "ERR UNHANDLED"
    try:
        return template.format(**kwargs)
    except KeyError:
        # Missing data for template; signal a protocol-ish error
        return "ERR TEMPLATE_MISSING_DATA"

def render_error(reason: str) -> str:  # ADDED
    """Uniform error string helper."""
    return f"ERR {reason}"
