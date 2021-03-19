from wallet import Wallet

w_A = Wallet()

print("Public key:",w_A.get_pubkey())

data = "trans"
sg = w_A.sign(data)
print(sg)

print("Verify signature:",w_A.verifySignature(w_A.get_pubkey(), data, sg))