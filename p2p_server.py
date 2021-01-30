import json
import requests
from utils import RSA
from flask import Flash, request, Response
from block import Block

rsa = RSA()
rsa.create_keys()
# Ensembles de Peers
peers = set()

host = input("host: ")
port = input("port: ")
local_server = host + ':' + str(port)
peers.add(local_server)

# TODO: Broadcasting / Sync

app = Flask(__name__)

@app.route('/peer',method=['GET','POST'])
def peer_handler():
    if request.method == 'GET':
        dic_list = []
        for p in peers:
            dic_list.append(p)
        return Response(json.dumps(dic_list), mimetype='application/json')
    if request.method == 'POST':
        url = request.form['url']
        print("Receive: "+url)
        peers.add(url)
        return "OK"

@app.route('/mine',method=['GET'])
def mine_handler():
    transaction = 'Null'
    content = request.args.get('text')
    if content:
        transaction = content
    transaction += ' '
    encryp = rsa.encrypt(transaction)
    transaction += encryp.decode("utf-8")
    transaction += ' '+rsa.get_pk()

    # todo: block
    # broadcast block
    return 'OK'

app.run(host=host, port=port)