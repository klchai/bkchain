import socket
import threading
import sys
from classes import Block,BlockChain

def handle_request(peers, miner_port, request, block_chain):
    print("REQ ",request)
    if "wants to connect" in request:
        new_miner_port = int(request.split()[1])
        msg = f"New miner {new_miner_port}"
        for peer_socket in peers.values():
            peer_socket.send(msg.encode("ascii"))
        new_miner_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        new_miner_socket.connect(("localhost", new_miner_port))
        msg = f"Other peers of miner {miner_port} : {';'.join(peers.keys())}"
        new_miner_socket.send(msg.encode("ascii"))
        peers[str(new_miner_port)] = new_miner_socket
   
    elif request.startswith("Other peers"):
        new_miner_port = int(request.split()[4])
        new_miner_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        new_miner_socket.connect(("localhost", new_miner_port))
        peers[str(new_miner_port)] = new_miner_socket
        request = request.split(" : ")[-1]
        other_peers = [port for port in request.split(";") if port!=""]
        for peer_port in other_peers:
            if peer_port not in peers:
                socket_peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket_peer.connect(("localhost", int(peer_port)))
                peers[peer_port] = socket_peer
                print(f"Peer {peer_port} added") 

    elif request.startswith("New"):
        new_miner_port = int(request.split()[-1])
        new_miner_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        new_miner_socket.connect(("localhost", new_miner_port))
        peers[str(new_miner_port)] = new_miner_socket
        print(f"Peer {new_miner_port} added")

    elif request == "show":
        """
        block_chain.add_transaction_in_last_block(self,payer,beneficiary,amount,timestamp)
        msg=block_chain.show_transactions()
        block=Block():
        for :
            block.add_transaction(payer,beneficiary,amount,timestamp)
        block_chain.mine_block(block)
        """
        print("Peers: ",list(peers.keys()))
        for peer_port,peer_socket in peers.items():
            if peer_port!=miner_port:
                peer_socket.send(request.encode("ascii"))
    
    else:
        pass

def main():
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print("Usage: python3 miner.py miner_port [other_miner_port]")
    else:
        try:
            miner_port = int(sys.argv[1])
            if len(sys.argv) == 3: 
                other_miner_port = int(sys.argv[2])
            else:
                other_miner_port = None
            peers = {}
            socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_server.bind(("localhost", miner_port))
            print(f"Miner {miner_port} created")
            block_chain = BlockChain()
            if other_miner_port is not None:
                socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket_client.connect(("localhost", other_miner_port))
                msg = f"Miner {miner_port} wants to connect to miner {other_miner_port}"
                socket_client.send(msg.encode("ascii"))
            while True:
                print("Peers: ",list(peers.keys()))
                socket_server.listen(5)
                client, _ = socket_server.accept()
                request = client.recv(255).decode("ascii")
                handle_request(peers, miner_port, request, block_chain)
        except Exception as e:
            print(f"Error in miner.py : {e}")
            sys.exit()

if __name__ == "__main__":
    main()