import socket
import threading
import sys
from classes import Block,BlockChain

def handle_request(peers,port_server,request,block_chain):
    print(request)
    if request.startswith("Connected"):
        client_port=int(request.split()[-1])
        if client_port in peers:
            socket_client=peers[client_port]
        else:
            socket_client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_client.connect(("localhost",client_port))
            msg=f"List of peers of miner {port_server} : {';'.join([str(port) for port in peers.keys()])}"
            socket_client.send(msg.encode("ascii"))
            peers[client_port]=socket_client

        msg=f"New peer at port {client_port}"
        for peer_port,peer_socket in peers.items():
            if peer_port!=client_port and peer_port!=port_server:
                peer_socket.send(msg.encode("ascii"))

    elif request.startswith("List"):
        request=request.split(" : ")[-1]
        other_peers=[int(port) for port in request.split(";") if port!=""]
        for peer_port in other_peers:
            if peer_port!=port_server and peer_port not in peers:
                socket_client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket_client.connect(("localhost",peer_port))
                peers[peer_port]=socket_client
                print(f"Peer {peer_port} added") 

    elif request.startswith("New"):
        client_port=int(request.split()[-1])
        socket_client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_client.connect(("localhost",client_port))
        peers[client_port]=socket_client
        print(f"Peer {client_port} addedx")

    elif request=="show":
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
            if peer_port!=port_server:
                peer_socket.send(request.encode("ascii"))
    
    else:
        pass

def main():
    if len(sys.argv)!=3:
        print("Usage: python3 miner.py port miner_port")
    else:
        try:
            port_server=int(sys.argv[1])
            miner_port=sys.argv[2]
            peers={port_server:None}
            socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_server.bind(("localhost",port_server))

            block_chain=BlockChain()
            current_block=0

            if miner_port!="none":
                miner_port=int(miner_port)
                socket_client.connect(("localhost",miner_port))
                msg=f"Connected to peer at port {port_server}"
                socket_client.send(msg.encode("ascii"))
                peers[miner_port]=socket_client 

            print(f"Miner started at port {port_server}")
            while True:
                print("Peers: ",list(peers.keys()))
                socket_server.listen(5)
                client,address=socket_server.accept()
                request=client.recv(255).decode("ascii")
                handle_request(peers,port_server,request,block_chain)
        except Exception as e:
            print(f"Error in miner.py : {e}")
            sys.exit()

if __name__=="__main__":
    main()