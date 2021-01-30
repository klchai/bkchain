import socket
import threading
import sys

if len(sys.argv)!=3:
    print("Usage: python3 miner.py port miner_port")
else:
    peers={}
    port_server=int(sys.argv[1])
    miner_port=sys.argv[2]
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_server.bind(("localhost",port_server))

    if miner_port!="none":
        miner_port=int(miner_port)
        socket_client.connect(("localhost",miner_port))
        msg=f"Connected to peer at port {port_server}"
        socket_client.send(msg.encode("ascii"))
        peers[miner_port]=socket_client 

    print(f"Start miner at port {port_server}")
    while True:
        print("Peers: ",list(peers.keys()))
        socket_server.listen(5)
        client,address=socket_server.accept()
        response = client.recv(255).decode("ascii")
        print(response)
        if response.startswith("Connected"):
            client_port=int(response.split()[-1])
            if client_port in peers:
                socket_client=peers[client_port]
            else:
                socket_client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket_client.connect(("localhost",client_port))
                msg=f"List of my peers : "
                for peer in peers:
                    msg+=f"{peer};"
                socket_client.send(msg.encode("ascii"))
                peers[client_port]=socket_client

            msg=f"New peer at port {client_port}"
            for peer_port,peer_socket in peers.items():
                if peer_port!=client_port:
                    peer_socket.send(msg.encode("ascii"))
        
        elif response.startswith("List"):
            response=response.split(" : ")[-1]
            print(response)
            other_peers=[int(port) for port in response.split(";") if port!=""]
            for peer_port in other_peers:
                if peer_port!=port_server and peer_port not in peers:
                    socket_client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    socket_client.connect(("localhost",peer_port))
                    peers[peer_port]=socket_client
                    print(f"Peer {peer_port} added") 

        elif response.startswith("New"):
            client_port=int(response.split()[-1])
            socket_client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_client.connect(("localhost",client_port))
            peers[client_port]=socket_client
            print(f"Peer {client_port} added")
        
        else:
            continue
        
