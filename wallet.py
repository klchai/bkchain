import socket
import sys
import datetime

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 wallet.py miner_port")
    else:
        miner_port = int(sys.argv[1])
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("localhost", miner_port))
        while True:
            print("> ",end="")
            cmd = input()
            if cmd == "show":
                msg = "show"
                sock.send(msg.encode("ascii"))
            elif cmd == "transaction":
                print("Payer: ")
                payer = input()
                print("Beneficary: ")
                beneficary = input()
                print("Amount: ")
                amount = input()
                now = datetime.datetime.now()
                msg = f"transaction {payer} {beneficary} {amount} {now.strftime('%Y-%m-%dT%H:%M:%S')}"
                sock.send(msg.encode("ascii"))
            elif cmd == "end":
                sock.close()
                sys.exit()
            else:
                print(f"Command '{cmd}' is incorrect")

if __name__ == "__main__":
    main()