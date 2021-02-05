from hashlib import sha256

class Node:
    def __init__(self, left, right, value):
        self.left = left
        self.right = right
        if not (self.left) and not (self.right):
            self.value = sha256(value.encode('utf-8')).hexdigest()
        else:
            value = self.left.value + self.right.value
            self.value = sha256(value.encode('utf-8')).hexdigest()
    
class MerkleTree:
    def __init__(self, values):
        hash_nodelist = []
        for v in values:
            node = Node(None, None, v)
            hash_nodelist.append(node)

        if len(hash_nodelist) % 2 == 1:
            hash_nodelist.append(hash_nodelist[-1:][0])

        self.root_node = self.grow(hash_nodelist)

    def grow(self, leaves):
        pairnum = len(leaves)//2

        if len(leaves)==2:
            return Node(leaves[0], leaves[1], None)
        
        leftRec = self.grow(leaves[:pairnum])
        rightRec = self.grow(leaves[pairnum:])
        return Node(leftRec, rightRec, None)

    def get_root_hash(self):
        return self.root_node.value

def test():
    items = ["Test","Merkel"]
    t = MerkleTree(items)
    print(t.get_root_hash())

test()