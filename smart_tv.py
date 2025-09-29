from messages import Command, render_reply, render_error

class SmartTV:
    def __init__(self) -> None:
        self.on = False
        self.channels = ["NRK1", "NRK2", "TV2", "TV3"]
        self.idx = 0 # Current channel index

    def handle(self, cmd: Command, args):
        if cmd == Command.POWER_ON:
            self.on = True
            return render_reply(Command.POWER_ON)
        
        if cmd == Command.POWER_OFF:
            self.on = False
            return render_reply(Command.POWER_OFF)

        if cmd == Command.GET_CHANNELS:
            if not self.on:
                return render_error("TV_OFF")
            return render_reply(Command.GET_CHANNELS, channels=",".join(self.channels))

        if cmd == Command.SET_CHANNEL:
            if not self.on:
                return render_error("TV_OFF")
            n = int(args[0])
            if not (0 <= n < len(self.channels)):
                return render_error("INVALID_CHANNEL")
            self.idx = n
            return render_reply(Command.SET_CHANNEL, index=self.idx, name=self.channels[self.idx])

        if cmd is Command.CHANNEL_UP:
            if not self.on:
                return render_error("TV_OFF")
            self.idx = (self.idx + 1) % len(self.channels)
            return render_reply(Command.CHANNEL_UP, index=self.idx, name=self.channels[self.idx])

        if cmd is Command.CHANNEL_DOWN:
            if not self.on:
                return render_error("TV_OFF")
            self.idx = (self.idx - 1) % len(self.channels)
            return render_reply(Command.CHANNEL_DOWN, index=self.idx, name=self.channels[self.idx])

        if cmd is Command.GET_STATUS:
            state = "ON" if self.on else "OFF"
            return render_reply(Command.GET_STATUS, state=state, index=self.idx, name=self.channels[self.idx])

        if cmd is Command.QUIT:
            return render_reply(Command.QUIT)

        return render_error("UNHANDLED")
