# server.py
import socket
import argparse
# from messages import parse_line, ProtocolError, InvalidArgumentError, UnknownCommandError
from ..protocol.commands import Command
from ..protocol.message import Message, TERMINATOR
from ..protocol.parser import parse_line, build
from ..protocol.renderer import render_reply, render_error
from ..protocol.errors import ProtocolError, UnknownCommandError, InvalidArgumentError

from ..domain.smart_tv import SmartTV

TERMINATOR = b"\n"

def recv_line(sock, bufsize: int = 4096):
    """Read until newline or connection close. Returns bytes or None on early close."""
    buf = bytearray()
    while True:
        chunk = sock.recv(bufsize)
        if not chunk:
            return None if not buf else bytes(buf)
        buf.extend(chunk)
        if buf.endswith(TERMINATOR):
            return bytes(buf)

def send_line(sock, text: str):
    sock.sendall((text + "\n").encode("utf-8"))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", nargs="?", type=int, default=1238, help="Port (1–65535, default: 1238)")
    args = parser.parse_args()
    port = args.port
    if not (1 <= port <= 65535):
        parser.error(f"Port out of range: {port}")

    tv = SmartTV()

    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("Socket created successfully")
        try:
            s.bind(('', port))
        except OSError as e:
            parser.error(f"Bind has failed at port {port}: {e}")

        print(f"Socket successfully bound to {port}")
        s.listen(5)
        print("Socket is listening")

        while True:
            c, addr = s.accept()
            print("Got connection from", addr)
            with c:
                # optional greeting when connecting
                send_line(c, "WELCOME SmartTV. Type commands, e.g. POWER_ON, GET_CHANNELS, SET_CHANNELS 2, CHANNEL_UP, GET_STATUS, QUIT")
                while True:
                    line = recv_line(c)
                    if line is None:
                        print("Client disconnected:", addr)
                        break
                    try:
                        msg = parse_line(line)
                        reply = tv.handle(msg.command, msg.args)
                    except (ProtocolError, InvalidArgumentError, UnknownCommandError) as e:
                        reply = f"ERR PROTOCOL {e}"

                    send_line(c, reply)
                    if reply.startswith("OK BYE"):  # QUIT
                        print("Session ended by client:", addr)
                        break

if __name__ == "__main__":
    main()
