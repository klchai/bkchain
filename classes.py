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
        self.NB_TRANSACTIONS_OF_BLOCK=5

    def get_size(self):
        return len(self.blocks)

    def calculate_hash_of_block(self,block):
        m = sha256()
        m.update(bytes(block))
        return m.digest()

    def add_transaction_in_last_block(self,payer,beneficiary,amount,timestamp):
        last_block = self.blocks[-1]
        if len(last_block.transactions) == self.NB_TRANSACTIONS_OF_BLOCK:
            self.mine_block(last_block)
            self.add_transaction_in_last_block(payer,beneficiary,amount,timestamp)
        else:
            last_block.transactions.append(Transaction(payer,beneficiary,amount,timestamp))
            if len(last_block.transactions) == self.NB_TRANSACTIONS_OF_BLOCK:
                self.mine_block(last_block)

    def mine_block(self,block):
        if self.check_blockchain_is_correct(block):
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

    def check_blockchain_is_correct(self,block):
        users_amounts = {"John":20,"Pierre":5,"Sylvain":4,"Mike":13}
        all_blocks = self.blocks+[block]
        for current_block in all_blocks:
            for transaction in current_block.transactions:
                users_amounts[transaction.payer] -= transaction.amount
                users_amounts[transaction.beneficiary] += transaction.amount
                if users_amounts[transaction.payer] < 0:
                    print("blockchain incorrect ",transaction.payer," has ",users_amounts[transaction.payer])
                    return False
        print("blockchain correct")
        return True


    def show_transactions(self):
        res=""
        for block in self.blocks:
            res+=f"Block {block.index}: \n"
            for transaction in block.transactions:
                res += f"From : {transaction.payer} - To : {transaction.beneficiary} - Amount : {transaction.amount} - Timestamp : {transaction.timestamp}\n"
            res+="\n"+"-"*30+"\n"
        return res