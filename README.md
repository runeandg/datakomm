Below is a quick guide how to run the assignment on your own PC.

Ensure you have python installed. You can check by running `python --version` in your terminal.

# How to run project
First grab the repo with git clone, then run the following commands in your terminal window.
## Start server:
`python -m smarttv.app.server <port, default=1238>` to get the server up.

## Connect with client:
`python -m smarttv.app.client <port, default=1238>` to connect to the server.

# Available commands:
# Friendly aliases (case-insensitive at parse time)
To turn the SmartTV on: write either of the following: `on`, `turn_on`, `power_on`.

To turn the SmartTV off: `off`, `turn_off`, `power_off`.

To get a list of all available channels: `get_channels`, `list`, `channels`.

To set channel a specific index, run either `set` or `set_channel` followed by `<index>`, so `set <index>`.

To increment the channel by one, write: `channel_up` or `up`.

To decrement the channel by one, write `channel_down` or `down`.

To get status, write `get_status` or `status`.

To quit, either `quit` or `exit`.

# Current goals:
* UDP
* Refactoring commands dictionary
* Multiple connections (async)
