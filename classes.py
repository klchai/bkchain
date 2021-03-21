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
            
        else:
            print(f"Incorrect request '{request}', request ignored")

class Transaction:
    def __init__(self, payer, beneficiary, amount, timestamp):
        self.payer = payer
        self.beneficiary = beneficiary
        self.amount = amount
        self.timestamp = timestamp

class Block:
    def __init__(self, data=None, previous_hash=None):
        self.index = 0
        self.data = data
        self.nonce = None
        self.previous_hash = previous_hash
        self.timestamp = str(time.time())
        self.transactions = []
        if isinstance(data, list):
            self.mtree = MerkleTree(data)
            self.m_root = str(self.mtree.get_root_hash())
        else:
            self.mtree = list()
            self.m_root = "None"

    def add_transaction(self, payer, beneficiary, amount, timestamp):
        self.transactions.append(Transaction(payer, beneficiary, amount, timestamp))

    def show_block(self):
        return "Block <Hash: {}, Nonce: {}>".format(self.block_hash(self.nonce), self.nonce)

    def block_hash(self, nonce=None):
        msg = sha256()
        msg.update(str(self.previous_hash).encode('utf-8'))
        msg.update(self.timestamp.encode('utf-8'))
        msg.update(str(nonce).encode('utf-8'))
        msg.update(str(self.m_root).encode('utf-8'))
        return msg.digest()

class BlockChain:
    def __init__(self, initial_amounts):
        self.blocks = [Block()]
        self.initial_amounts = initial_amounts
        self.NB_TRANSACTIONS_IN_BLOCK = 5

    def get_size(self):
        return len(self.blocks)

    """
    def calculate_hash_of_block(self,block):
        m = sha256()
        m.update(bytes(block))
        return m.digest()
    """

    def add_transaction(self, payer, beneficiary, amount, timestamp):
        last_block = self.blocks[-1]
        if len(last_block.transactions) == self.NB_TRANSACTIONS_IN_BLOCK:
            print("mine block")
            threading.Thread(target=self.mine_block, args=(last_block,)).start()
            self.add_transaction(payer,beneficiary,amount,timestamp)
        else:
            last_block.transactions.append(Transaction(payer,beneficiary,amount,timestamp))
            if len(last_block.transactions) == self.NB_TRANSACTIONS_IN_BLOCK:
                self.mine_block(last_block)

    def mine_block(self, block):
        prev_hash = self.blocks[-1].block_hash()
        nonce = 0
        s = f"{prev_hash}{block.transactions}{nonce}".encode("utf-8")
        m = sha256()
        m.update(s)
        res = m.digest()[2:-1]
        print("type dd ",type(res))
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
        print("end of mine")

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
            res += f"Block {block.index}: \nFrom \t | To \t | Amount \t | Timestamp\n" + "-"*50
            for transaction in block.transactions:
                res += f"\n{transaction.payer} \t | {transaction.beneficiary} \t | {transaction.amount} \t | {transaction.timestamp}"
            res += "\n"+"-"*50+"\n"
        print(res)