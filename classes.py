import socket
import threading
from hashlib import sha256
from merkle import build_merkle_tree

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
            print(f"Peers: {list(self.peers.keys())}")

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
            print(f"Peers: {list(self.peers.keys())}")

        elif request.startswith("New"):
            new_miner_port = int(request.split()[-1])
            new_miner_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_miner_socket.connect(("localhost", new_miner_port))
            self.peers[str(new_miner_port)] = new_miner_socket
            print(f"Peers: {list(self.peers.keys())}")

        elif request.startswith("transaction"):
            payer, beneficiary, amount, timestamp = request.split()[1:]
            self.block_chain.add_transaction(self, payer, beneficiary, amount, timestamp)
            print("transaction added")

        elif request.startswith("blockchain"):
            size_blockchain, content = request.split(" - ")[1:]
            print("blockain received ",size_blockchain," ",content)
            try:
                if int(size_blockchain) > self.block_chain.size():
                    self.parse_blockchain_received(content)
                else:
                    print(f"blockain is not bigger ({self.block_chain.size()} - {size_blockchain})")
            except Exception as e:
                print(f"Error in request '{request}' : {e}")

        elif request == "show":
            print(self.block_chain.show_blocks())
            
        else:
            print(f"Incorrect request '{request}', request ignored")

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
        self.block_chain.merkle_tree = build_merkle_tree([block.hash for block in self.block_chain.blocks])
        print("Merkle ",self.block_chain.merkle_tree)
        self.block_chain.add_block(hash_of_last_block, payer, beneficiary, amount, timestamp)
        msg = f"blockchain - {self.block_chain.size()} - {self.block_chain.show_blocks()}"
        for peer_socket in self.peers.values():
            peer_socket.send(msg.encode("ascii"))

    def parse_blockchain_received(self, content): 
        last_index_block = self.block_chain.size() - 1
        content = content.split(f"Block {last_index_block}")[1]
        new_index_block = last_index_block + 1
        for block in content.split("hash: "):
            hash_of_block = block.split()[0][:-1]
            print(f"hash of block {new_index_block-1} : {hash_of_block}")
            new_block = Block(new_index_block)
            new_block.hash = hash_of_block
            new_block.previous_hash = self.block_chain.blocks[-1].hash
            for transaction in block.split("\n"+"-"*50+"\n"):
                payer, beneficiary, amount, timestamp = transaction.split("\t|")
                new_block.add_transaction(payer, beneficiary, amount, timestamp)
            self.block_chain.blocks.append(new_block)
            print(f"block {new_index_block} added")
            new_index_block += 1
        print("end of parse")

class Transaction:
    def __init__(self, payer, beneficiary, amount, timestamp):
        self.payer = payer
        self.beneficiary = beneficiary
        self.amount = amount
        self.timestamp = timestamp

class Block:
    def __init__(self, index, previous_hash=None):
        self.index = index
        self.hash = None
        self.previous_hash = previous_hash
        self.nonce = None
        self.transactions = []

    def add_transaction(self, payer, beneficiary, amount, timestamp):
        self.transactions.append(Transaction(payer, beneficiary, amount, timestamp))

class BlockChain:
    def __init__(self, accounts):
        self.blocks = [Block(0)]
        self.accounts = accounts
        self.merkle_tree = None
        self.NB_TRANSACTIONS_IN_BLOCK = 2

    def size(self):
        return len(self.blocks)

    def add_transaction(self, miner, payer, beneficiary, amount, timestamp):
        last_block = self.blocks[-1]
        if len(last_block.transactions) == self.NB_TRANSACTIONS_IN_BLOCK:
            print(f"Block {last_block.index} is full, mining this block...")
            threading.Thread(
                target=miner.mine_block,
                args=(last_block, payer, beneficiary, amount, timestamp)
            ).start()
        else:
            last_block.add_transaction(payer,beneficiary,amount,timestamp)

    def add_block(self, hash_of_last_block, payer, beneficiary, amount, timestamp):
        nb_blocks = self.size()
        new_block = Block(nb_blocks, previous_hash=hash_of_last_block)
        new_block.add_transaction(payer,beneficiary,amount,timestamp)
        self.blocks.append(new_block)

    def is_correct(self, block):
        all_blocks = self.blocks + [block]
        for current_block in all_blocks:
            for transaction in current_block.transactions:
                self.accounts[transaction.payer] -= transaction.amount
                self.accounts[transaction.beneficiary] += transaction.amount
                if self.accounts[transaction.payer] < 0:
                    print(f"blockchain incorrect, {transaction.payer} has {self.initial_amounts[transaction.payer]}")
                    return False
        print("blockchain correct")
        return True

    def show_blocks(self):
        str_blocks = ""
        for block in self.blocks:
            str_blocks += f"Block {block.index} (hash: {block.hash}): \nFrom \t | To \t | Amount \t | Timestamp\n" + "-"*50
            for transaction in block.transactions:
                str_blocks += f"\n{transaction.payer}\t|{transaction.beneficiary}\t|{transaction.amount}\t|{transaction.timestamp}"
            str_blocks += "\n"+"-"*50+"\n"
        return str_blocks