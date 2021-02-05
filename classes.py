from hashlib import sha256

class Transaction:
    def __init__(self,payer,beneficiary,amount,timestamp):
        self.payer = payer
        self.beneficiary = beneficiary
        self.amount = amount
        self.timestamp = timestamp

class Block:
    def __init__(self,index,previous_hash):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = []

    def add_transaction(self,payer,beneficiary,amount,timestamp):
        self.transactions.append(Transaction(payer,beneficiary,amount,timestamp))

class BlockChain:
    def __init__(self):
        self.blocks=[Block(0,None)]

    def get_size(self):
        return len(self.blocks)

    def calculate_hash_of_block(self,block):
        return sha256(block.encode())

    def mine_block(self,block):
        prev_hash=self.calculate_hash_of_block(self.blocks[-1])
        block.previous_hash=prev_hash
        self.blocks.append(block)


        