import socket
import threading
from hashlib import sha256
from merkle import Node, MerkleTree
import time

class Miner:
    def __init__(self, host, port, other_miner_port, initial_amounts_blockchain):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.peers = {}
        self.block_chain = BlockChain(initial_amounts_blockchain)
        if other_miner_port is not None:
            socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_client.connect(("localhost", other_miner_port))
            msg = f"Miner {port} wants to connect to miner {other_miner_port}"
            socket_client.send(msg.encode("ascii"))

    def listen(self):
        self.sock.listen(5)
        while True:
            print(f"Peers: {list(self.peers.keys())}")
            client, _ = self.sock.accept()
            client.settimeout(300)
            threading.Thread(target=self.listen_to_client, args=(client,)).start()

    def listen_to_client(self, client):
        MSG_MAX_SIZE = 1024
        while True:
            try:
                request = client.recv(MSG_MAX_SIZE).decode("ascii")
                if request:
                    self.handle_request(request)
                else:
                    raise Exception("Client disconnected")
            except:
                client.close()
                return False

    def handle_request(self, request):
        if "wants to connect" in request:
            new_miner_port = int(request.split()[1])
            msg = f"New miner {new_miner_port}"
            for peer_socket in self.peers.values():
                peer_socket.send(msg.encode("ascii"))
            new_miner_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_miner_socket.connect(("localhost", new_miner_port))
            msg = f"Other peers of miner {self.port} : {';'.join(self.peers.keys())}"
            new_miner_socket.send(msg.encode("ascii"))
            self.peers[str(new_miner_port)] = new_miner_socket

        elif request.startswith("Other peers"):
            new_miner_port = int(request.split()[4])
            new_miner_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_miner_socket.connect(("localhost", new_miner_port))
            self.peers[str(new_miner_port)] = new_miner_socket
            request = request.split(" : ")[-1]
            other_peers = [port for port in request.split(";") if port != ""]
            for peer_port in other_peers:
                if peer_port not in self.peers:
                    socket_peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    socket_peer.connect(("localhost", int(peer_port)))
                    self.peers[peer_port] = socket_peer
                    print(f"Peer {peer_port} added") 

        elif request.startswith("New"):
            new_miner_port = int(request.split()[-1])
            new_miner_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_miner_socket.connect(("localhost", new_miner_port))
            self.peers[str(new_miner_port)] = new_miner_socket
            print(f"Peer {new_miner_port} added")

        elif request.startswith("transaction"):
            payer, beneficiary, amount, timestamp = request.split()[1:]
            self.block_chain.add_transaction(payer,beneficiary,amount,timestamp)
            print("transaction added")

        elif request == "show":
            self.block_chain.show_transactions()

        elif request == "broadcast":
            my_chain = self.block_chain
            msg = f"Send {my_chain}"
            self.sock.send(msg.encode("ascii"))

        elif request.startswith("Send"):
            other_chain = request.split()[-1]
            if self.block_chain.last_block_index() >= other_chain.last_block_index():
                print("Other blockchain smaller than mine, no update")
            if other_chain.startswith("0000"):
                self.block_chain = other_chain
                print("Update my blockchain")
            
        else:
            print(f"Incorrect request '{request}', request ignored")

class Transaction:
    def __init__(self, payer, beneficiary, amount, timestamp):
        self.payer = payer
        self.beneficiary = beneficiary
        self.amount = amount
        self.timestamp = timestamp

class Block:
    def __init__(self, index, data=None, previous_hash=None):
        self.index = index
        self.data = data
        self.nonce = None
        self.previous_hash = previous_hash
        self.transactions = []
        self.hash = None
        if isinstance(data, list):
            self.mtree = MerkleTree(data)
            self.m_root = str(self.mtree.get_root_hash())
        else:
            self.mtree = []
            self.m_root = "None"

    def add_transaction(self, payer, beneficiary, amount, timestamp):
        self.transactions.append(Transaction(payer, beneficiary, amount, timestamp))

    def show_block(self):
        return "Block <Hash: {}, Nonce: {}>".format(self.block_hash(self.nonce), self.nonce)

    def block_hash(self, nonce=None):
        msg = sha256()
        msg.update(str(self.previous_hash).encode('utf-8'))
        msg.update(str(nonce).encode('utf-8'))
        msg.update(str(self.m_root).encode('utf-8'))
        return msg.digest()

class BlockChain:
    def __init__(self, initial_amounts):
        self.blocks = [Block(0)]
        self.initial_amounts = initial_amounts
        self.NB_TRANSACTIONS_IN_BLOCK = 2

    def add_transaction(self, payer, beneficiary, amount, timestamp):
        last_block = self.blocks[-1]
        if len(last_block.transactions) == self.NB_TRANSACTIONS_IN_BLOCK:
            print(f"Block {last_block.index} is full, mining this block...")
            threading.Thread(
                target=self.mine_block,
                args=(last_block, payer, beneficiary, amount, timestamp)
            ).start()
        else:
            last_block.add_transaction(payer,beneficiary,amount,timestamp)

    def mine_block(self, last_block, payer, beneficiary, amount, timestamp):
        prev_hash = last_block.previous_hash
        nonce = 0
        s = f"{prev_hash}{last_block.transactions}{nonce}".encode("utf-8")
        hash_of_last_block = sha256(s).hexdigest()
        while not hash_of_last_block.startswith("0000"):
            nonce += 1
            s = f"{prev_hash}{last_block.transactions}{nonce}".encode("utf-8")
            hash_of_last_block = sha256(s).hexdigest()
        last_block.hash = hash_of_last_block
        last_block.nonce = nonce
        print(f"Block {last_block.index} is mined")
        self.add_block(hash_of_last_block, payer, beneficiary, amount, timestamp)

    def add_block(self, hash_of_last_block, payer, beneficiary, amount, timestamp):
        nb_blocks = len(self.blocks)
        new_block = Block(nb_blocks, previous_hash=hash_of_last_block)
        new_block.add_transaction(payer,beneficiary,amount,timestamp)
        self.blocks.append(new_block)

    def is_correct(self, block):
        all_blocks = self.blocks + [block]
        for current_block in all_blocks:
            for transaction in current_block.transactions:
                self.initial_amounts[transaction.payer] -= transaction.amount
                self.initial_amounts[transaction.beneficiary] += transaction.amount
                if self.initial_amounts[transaction.payer] < 0:
                    print(f"blockchain incorrect, {transaction.payer} has {self.initial_amounts[transaction.payer]}")
                    return False
        print("blockchain correct")
        return True

    def show_transactions(self):
        res = ""
        for block in self.blocks:
            res += f"Block {block.index} (hash: {block.hash}): \nFrom \t | To \t | Amount \t | Timestamp\n" + "-"*50
            for transaction in block.transactions:
                res += f"\n{transaction.payer} \t | {transaction.beneficiary} \t | {transaction.amount} \t | {transaction.timestamp}"
            res += "\n"+"-"*50+"\n"
        print(res)

    def last_block_index(self):
        if len(self.blocks)==0:
            return 0
        return self.blocks[-1].index