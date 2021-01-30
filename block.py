import json
from hashlib import sha256

class Block:
    def __init(self, id, transaction, time, prev_hash):
        self.id = id
        self.transaction = transaction
        self.time = time
        self.prev_hash = prev_hash

    def calculate_hash(self):
        block_js = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_js.encode())

    def dic2block(block):
        return Block(block['id'],
                     block['transaction'],
                     block['time'],
                     block['prev_hash'])