# protocol/message.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List
from .commands import Command

TERMINATOR = b"\n"  # one message per line, '\n' terminated

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
