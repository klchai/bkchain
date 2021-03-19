import socket
import sys
from hashlib import sha256
from ecdsa import SigningKey, VerifyingKey
from ecdsa.curves import SECP256k1

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


def applySig(prikey, inputs):
    return prikey.sign(inputs)

def verifySig(pubkey, data, signature):
        return pubkey.verify(signature, data)

class Wallet:
    def __init__(self):
        # un compte unique
        self.private_key = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.private_key.get_verifying_key()

    def get_pubkey(self):
        return self.public_key.to_pem()
        
    def sign(self, msg):
        h = sha256(msg.encode('utf8'))
        return self.private_key.sign(h.digest())

    def verifySignature(self, pubkey, msg, signature):
        vf = VerifyingKey.from_pem(pubkey)
        h = sha256(msg.encode('utf8'))
        return vf.verify(signature, h.digest())