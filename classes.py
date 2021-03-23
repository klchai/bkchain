import socket
import threading
from hashlib import sha256
from merkle import build_merkle_tree
from wallet import load_configuration_users

class Miner:
    def __init__(self, host, port, other_miner_port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.peers = {}
        self.block_chain = BlockChain()
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

        elif request.startswith("blockchain"):
            miner_port, size_blockchain, content = request.split(" - ")[1:]
            print(f"Blockain of miner {miner_port} received (size: {size_blockchain} blocks)")
            try:
                if int(size_blockchain) > self.block_chain.size():
                    self.parse_blockchain_received(content)
                else:
                    print(f"It's blockain is not bigger, update canceled (have {self.block_chain.size()} blocks and received {size_blockchain} blocks)")
            except Exception as e:
                print(f"Error in request '{request}' : {e}")

        elif request == "show":
            print(self.block_chain.show_blocks())
            
        else:
            print(f"Incorrect request '{request}', request ignored")

    def mine_block(self, last_block, payer, beneficiary, amount, timestamp):
        nonce = 0
        s = ""
        for transaction in last_block.transactions:
            s += f"{transaction.payer}{transaction.beneficiary}{transaction.amount}{transaction.timestamp}"
        s.encode("utf-8")
        hash_of_last_block = sha256(s).hexdigest()
        while not hash_of_last_block.startswith("0000"):
            nonce += 1
            y = f"{s}{nonce}".encode("utf-8")
            hash_of_last_block = sha256(y).hexdigest()
        last_block.hash = hash_of_last_block
        print(f"Block {last_block.index} is mined")
        self.block_chain.add_block(hash_of_last_block, payer, beneficiary, amount, timestamp)
        msg = f"blockchain - {self.port} - {self.block_chain.size()} - {self.block_chain.show_blocks()}"
        for peer_socket in self.peers.values():
            print("Broadcast blockchain to all peers...")
            peer_socket.send(msg.encode("ascii"))

    def parse_blockchain_received(self, content): 
        last_index_block = self.block_chain.size() - 1
        current_index_block = last_index_block
        content = content.split(f"Block")[last_index_block + 1:]
        HASH_LENGTH = 64
        for block in content:
            if "(hash: None)" in block:
                break
            else:
                index_hash = block.index("(hash: ") + 7 
                hash_of_block = block[index_hash:index_hash + HASH_LENGTH]
                new_block = Block(current_index_block)
                new_block.hash = hash_of_block
                new_block.previous_hash = self.block_chain.blocks[-1].hash
                for transaction in block.split("\n"+"-"*50+"\n")[1:-1][0].split("\n"):
                    payer, beneficiary, amount, timestamp = transaction.split("\t|")
                    new_block.add_transaction(payer, beneficiary, amount, timestamp)
                if current_index_block == last_index_block:
                    self.block_chain.blocks.pop()
                self.block_chain.blocks.append(new_block)
                print(f"Block {current_index_block} added")
                current_index_block += 1

class Transaction:
    def __init__(self, payer, beneficiary, amount, timestamp):
        self.payer = payer
        self.beneficiary = beneficiary
        self.amount = amount
        self.timestamp = timestamp
    
    def trans_hash(self):
        s = f"{self.payer}{self.beneficiary}{self.amount}{self.timestamp}".encode("utf-8")
        return sha256(s).hexdigest()

class Block:
    def __init__(self, index, previous_hash=None):
        self.index = index
        self.hash = None
        self.previous_hash = previous_hash
        self.transactions = []

    def add_transaction(self, payer, beneficiary, amount, timestamp):
        self.transactions.append(Transaction(payer, beneficiary, float(amount), timestamp))

    def block_hash(self):
        s = " ".join([t.trans_hash() for t in self.transactions])
        return sha256(s.encode("utf-8")).hexdigest()

class BlockChain:
    def __init__(self):
        self.blocks = [Block(0)]
        self.users_accounts = load_configuration_users()
        self.hash_of_transactions = []
        self.merkle_tree = None
        self.NB_TRANSACTIONS_IN_BLOCK = 2

    def size(self):
        return len(self.blocks)

    def add_transaction(self, miner, payer, beneficiary, amount, timestamp):
        if self.is_correct(payer, beneficiary, float(amount), timestamp):
            last_block = self.blocks[-1]
            if len(last_block.transactions) == self.NB_TRANSACTIONS_IN_BLOCK:
                print(f"Block {last_block.index} is full, mining this block...")
                threading.Thread(
                    target=miner.mine_block,
                    args=(last_block, payer, beneficiary, amount, timestamp)
                ).start()
            else:
                last_block.add_transaction(payer,beneficiary,amount,timestamp)
            print("Transaction added")

    def add_block(self, hash_of_last_block, payer, beneficiary, amount, timestamp):
        self.hash_of_transactions.append(hash_of_last_block)
        self.merkle_tree = build_merkle_tree(self.hash_of_transactions)
        nb_blocks = self.size()
        new_block = Block(nb_blocks, previous_hash=hash_of_last_block)
        new_block.add_transaction(payer,beneficiary,amount,timestamp)
        self.blocks.append(new_block)

    def is_correct(self, payer, beneficiary, amount, timestamp):
        copy_users_accounts = self.users_accounts.copy()
        copy_users_accounts[payer] -= amount
        copy_users_accounts[beneficiary] += amount
        if copy_users_accounts[payer] < 0:
            print(f"The blockchain is incorrect, {payer} has {copy_users_accounts[payer]}. Transaction canceled")
            return False
        self.users_accounts = copy_users_accounts
        print(f"The blockchain is correct, users accounts updated : {self.users_accounts}")
        return True

    def show_blocks(self):
        str_blocks = ""
        for block in self.blocks:
            str_blocks += f"Block {block.index} (hash: {block.hash}): \nFrom \t | To \t | Amount \t | Timestamp\n" + "-"*50
            for transaction in block.transactions:
                str_blocks += f"\n{transaction.payer}\t|{transaction.beneficiary}\t|{transaction.amount}\t|{transaction.timestamp}"
            str_blocks += "\n"+"-"*50+"\n"
        return str_blocks