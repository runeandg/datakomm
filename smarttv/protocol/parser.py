# protocol/parser.py
from __future__ import annotations
from typing import List
from .errors import ProtocolError, InvalidArgumentError
from .commands import Command, normalize, arity
from .message import Message

def build(command: Command | str, *args: str) -> Message:
    """Create a message with validation (also accepts alias strings)."""
    cmd = normalize(command) if isinstance(command, str) else command
    _validate(cmd, list(args))
    return Message(command=cmd, args=list(args))

def parse_line(line: bytes) -> Message:
    """bytes -> Message. Accepts 'COMMAND\\n' or 'COMMAND arg ... \\n'."""
    try:
        text = line.decode("utf-8").strip()
    except UnicodeDecodeError as e:
        raise ProtocolError(f"Invalid UTF-8: {e}") from e

    if not text:
        raise ProtocolError("Empty line")

    parts = text.split()
    cmd_token, *args = parts
    cmd = normalize(cmd_token)
    _validate(cmd, args)
    return Message(command=cmd, args=args)

def _validate(command: Command, args: List[str]) -> None:
    required = arity(command)
    if required != len(args):
        if required == 0 and args:
            raise InvalidArgumentError(f"{command.value} takes no arguments")
        raise InvalidArgumentError(f"{command.value} requires exactly {required} argument(s)")

    # Per-command argument types
    if command is Command.SET_CHANNEL:
        if not _is_nonnegative_int(args[0]):
            raise InvalidArgumentError("SET_CHANNEL argument must be a non-negative integer")

def _is_nonnegative_int(s: str) -> bool:
    try:
        return int(s) >= 0
    except ValueError:
        return False
