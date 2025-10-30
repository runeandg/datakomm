# server.py
import socket
import argparse
import threading
# from messages import parse_line, ProtocolError, InvalidArgumentError, UnknownCommandError
from ..protocol.commands import Command
from ..protocol.message import Message, TERMINATOR
from ..protocol.parser import parse_line, build
from ..protocol.renderer import render_reply, render_error
from ..protocol.errors import ProtocolError, UnknownCommandError, InvalidArgumentError

from ..domain.smart_tv import SmartTV

TERMINATOR = b"\n"

# Global client tracking
clients = set()
clients_lock = threading.Lock()

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

def broadcast_channel_change(sender_socket, channel_idx, channel_name):
    """Broadcast channel change notification to all clients except the sender."""
    notification = f"NOTIFY CHANNEL_CHANGED {channel_idx} {channel_name}"
    with clients_lock:
        for client_sock in clients:
            if client_sock != sender_socket:
                try:
                    send_line(client_sock, notification)
                except Exception as e:
                    print(f"Failed to broadcast to client: {e}")

def handle_client(client_socket, addr, tv):
    """Handle a single client connection in a separate thread."""
    print(f"Got connection from {addr}")

    # Register this client
    with clients_lock:
        clients.add(client_socket)

    try:
        with client_socket:
            # optional greeting when connecting
            send_line(client_socket, "WELCOME SmartTV. Type commands, e.g. POWER_ON, GET_CHANNELS, SET_CHANNELS 2, CHANNEL_UP, GET_STATUS, QUIT")
            while True:
                line = recv_line(client_socket)
                if line is None:
                    print(f"Client disconnected: {addr}")
                    break
                try:
                    msg = parse_line(line)
                    reply = tv.handle(msg.command, msg.args)

                    # Check if this was a channel change command
                    if msg.command in (Command.CHANNEL_UP, Command.CHANNEL_DOWN, Command.SET_CHANNEL):
                        if reply.startswith("OK"):
                            # Extract channel info from reply and broadcast to other clients
                            # Reply format: "OK CHANNEL_UP 3 TV3" or similar
                            parts = reply.split()
                            if len(parts) >= 4:
                                channel_idx = parts[2]
                                channel_name = parts[3]
                                broadcast_channel_change(client_socket, channel_idx, channel_name)

                except (ProtocolError, InvalidArgumentError, UnknownCommandError) as e:
                    reply = f"ERR PROTOCOL {e}"

                send_line(client_socket, reply)
                if reply.startswith("OK BYE"):  # QUIT
                    print(f"Session ended by client: {addr}")
                    break
    finally:
        # Unregister this client
        with clients_lock:
            clients.discard(client_socket)

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
        print("Socket is listening (multithreaded mode)")

        while True:
            c, addr = s.accept()
            # Create a new thread to handle this client
            client_thread = threading.Thread(target=handle_client, args=(c, addr, tv), daemon=True)
            client_thread.start()
            print(f"Started thread {client_thread.name} for client {addr}")

if __name__ == "__main__":
    main()
