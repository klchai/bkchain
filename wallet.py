import socket
import sys
import datetime
import json

def load_configuration_users():
    CONFIG_FILENAME = "users_accounts.json"
    users = {}
    try:    
        with open(CONFIG_FILENAME, "r") as conf_file:
            conf = json.load(conf_file)
            for user in conf:
                users[user["name"]] = user["account"]
        print(f"Initial users accounts : {users}")
        return users
    except FileNotFoundError:
        print(f"The configuration file '{CONFIG_FILENAME}' has not been found")
        sys.exit(1)
    except Exception as e:
        print(f"Error while reading the configuration file '{CONFIG_FILENAME}' : {e}")
        sys.exit(2)

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 wallet.py miner_port")
    else:
        users = load_configuration_users()
        miner_port = int(sys.argv[1])
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("localhost", miner_port))
        print(f"Wallet created and connected to the miner {miner_port}")
        while True:
            print("> ", end="")
            cmd = input()
            if cmd == "show":
                msg = "show"
                sock.send(msg.encode("ascii"))
            elif cmd == "transaction":
                print("Payer: ", end="")
                payer = input()
                if payer not in users:
                    print(f"The user {payer} is not registered, please select a valid user (among {', '.join(users.keys())})")
                    continue
                print("Beneficary: ", end="")
                beneficary = input()
                if beneficary not in users:
                    print(f"The user {beneficary} is not registered, please select a valid user (among {', '.join(users.keys())})")
                    continue
                elif payer == beneficary:
                    print("The payer and the benficiary must not be the same")
                    continue
                print("Amount: ", end="")
                amount = input()
                try:
                    amount = float(amount)
                    if amount <= 0:
                        print(f"The amount '{amount}' is not valid, it must be a strictly positive float")
                        continue
                    now = datetime.datetime.now()
                    msg = f"transaction {payer} {beneficary} {amount} {now.strftime('%Y-%m-%dT%H:%M:%S')}"
                    sock.send(msg.encode("ascii"))
                except:
                    print(f"The amount '{amount}' is not valid, it must be a strictly positive float")
                    continue
            elif cmd == "end":
                sock.close()
                sys.exit()
            else:
                print(f"The command '{cmd}' is incorrect")

if __name__ == "__main__":
    main()