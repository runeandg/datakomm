import socket
import argparse
import sys

TERMINATOR = b"\n"

def recv_line(sock, bufsize: int = 4096):
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

parser = argparse.ArgumentParser(description="SmartTV remote client (persistent)")
parser.add_argument("port", nargs="?", type=int, default=1238, help="Server port (default: 1238)")
parser.add_argument("host", nargs="?", default="127.0.0.1", help="Server host (default: 127.0.0.1)")
args = parser.parse_args()

with socket.socket() as s:
    s.connect((args.host, args.port))
    print(f"Connected to {args.host}:{args.port}")

    banner = recv_line(s)
    if banner:
        print(banner.decode("utf-8").rstrip())

    print("Type commands (POWER_ON, GET_CHANNELS, SET_CHANNELS 2, CHANNEL_UP, GET_STATUS, QUIT)")
    try:
        while True:
            try:
                line = input("> ").strip()
            except EOFError:
                line = "QUIT"

            if not line:
                continue

            send_line(s, line)
            resp = recv_line(s)
            if resp is None:
                print("Connection closed by server.")
                break

            text = resp.decode("utf-8").rstrip()
            print(text)
            if text.startswith("OK BYE"):
                break
    except KeyboardInterrupt:
        try:
            send_line(s, "QUIT")
        except OSError:
            pass
        print("\nBye.")
        sys.exit(0)
