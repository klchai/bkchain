import socket
import sys

if len(sys.argv)!=2:
    print("Usage: python3 wallet.py miner_port")
else:
    miner_port = int(sys.argv[1])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost",miner_port))
    while True:
        print("> ",end="")
        cmd = input()
        if cmd == "show":
            msg="Wallet"
            sock.send(msg.encode("ascii"))
        elif cmd == "end":
            sys.exit()
        else:
            print(f"Command '{cmd}' is incorrect")