import socket
import sys
from hashlib import sha256
from ecdsa import SigningKey, VerifyingKey
from ecdsa.curves import SECP256k1
from classes import Transaction
import time

def main():
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
            if cmd == "transaction":
                print("Your wallet ID:")
                payer = input()
                print("Destination wallet ID:")
                beneficary = input()
                print("The amount of transaction:")
                amount = input()
                msg = Transaction(payer, beneficary, amount, str(time.time()))
            if cmd == "end":
                sys.exit()
            else:
                print(f"Command '{cmd}' is incorrect")