from classes import Miner
import sys

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
            initial_amounts_blockchain = {"a": 20, "b": 13, "c": 89, "d":53}
            miner = Miner("localhost", miner_port, other_miner_port, initial_amounts_blockchain)
            print(f"Miner {miner_port} created")
            miner.listen()
        except Exception as e:
            print(f"Error in miner.py : {e}")
            sys.exit()

if __name__ == "__main__":
    main()