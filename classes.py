from hashlib import sha256

class Transaction:
    def __init__(self,payer,beneficiary,amount,timestamp):
        self.payer = payer
        self.beneficiary = beneficiary
        self.amount = amount
        self.timestamp = timestamp

class Block:
    def __init__(self,previous_hash):
        self.index = 0
        self.previous_hash = previous_hash
        self.transactions = []

    def add_transaction(self,payer,beneficiary,amount,timestamp):
        self.transactions.append(Transaction(payer,beneficiary,amount,timestamp))

class BlockChain:
    def __init__(self):
        self.blocks = [Block(None)]

    def get_size(self):
        return len(self.blocks)

    def calculate_hash_of_block(self,block):
        m = sha256()
        m.update(bytes(block))
        return m.digest()

    def mine_block(self,block):
        prev_hash = self.calculate_hash_of_block(self.blocks[-1])
        nonce = 0
        s = f"{prev_hash}{block.transactions}{nonce}"
        m = sha256()
        m.update(s)
        res = m.digest()[2:-1]
        while not res.startswith("0000"):
            nonce += 1
            s = f"{prev_hash}{block.transactions}{nonce}"
            m = sha256()
            m.update(s)
            res = m.digest()[2:-1]
        print("Nonce : "+nonce)
        block.index = self.get_size()
        block.previous_hash = prev_hash
        self.blocks.append(block)

    def show_transactions(self):
        res=""
        for block in self.blocks:
            res+=f"Block {block.index}: \n"
            for transaction in block.transactions:
                res += f"From : {transaction.payer} - To : {transaction.beneficiary} - Amount : {transaction.amount} - Timestamp : {transaction.timestamp}\n"
            res+="\n"+"-"*30+"\n"
        return res