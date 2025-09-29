# protocol/renderer.py
from __future__ import annotations
from typing import Dict
from .commands import Command

# Human-facing descriptions (nice for HELP)
COMMAND_DESCRIPTIONS: Dict[Command, str] = {
    Command.POWER_ON:     "Turn the TV on",
    Command.POWER_OFF:    "Turn the TV off",
    Command.GET_CHANNELS: "List available channels",
    Command.SET_CHANNEL:  "Select channel by index: SET_CHANNEL <n>",
    Command.CHANNEL_UP:   "Go to next channel (wraps around)",
    Command.CHANNEL_DOWN: "Go to previous channel (wraps around)",
    Command.GET_STATUS:   "Show power state and current channel",
    Command.QUIT:         "Close the session",
}

# Wire protocol reply templates (server -> client)
REPLY_TEMPLATES: Dict[Command, str] = {
    Command.POWER_ON:     "OK POWER_ON",
    Command.POWER_OFF:    "OK POWER_OFF",
    Command.GET_CHANNELS: "CHANNELS {channels}",
    Command.SET_CHANNEL:  "OK CHANNEL {index} {name}",
    Command.CHANNEL_UP:   "OK CHANNEL {index} {name}",
    Command.CHANNEL_DOWN: "OK CHANNEL {index} {name}",
    Command.GET_STATUS:   "STATUS {state} CURRENT {index} {name}",
    Command.QUIT:         "OK BYE",
}

def render_reply(command: Command, **kwargs) -> str:
    """
    Render a reply string using REPLY_TEMPLATES.
    The app/domain layer supplies kwargs when needed:
      - GET_CHANNELS: channels="NRK1,NRK2"
      - SET/UP/DOWN/GET_STATUS: index=int, name=str, (state="ON"/"OFF" for GET_STATUS)
    """
    template = REPLY_TEMPLATES.get(command)
    if template is None:
        return "ERR UNHANDLED"
    try:
        return template.format(**kwargs)
    except KeyError:
        return "ERR TEMPLATE_MISSING_DATA"

def render_error(reason: str) -> str:
    return f"ERR {reason}"
