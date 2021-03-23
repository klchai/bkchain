class MerkleTreeNode:
    def __init__(self,value):
        self.left = None
        self.right = None
        self.value = value
    
def build_merkle_tree(leaves):
    nodes = []
    for i in leaves:
        nodes.append(MerkleTreeNode(i))
    while len(nodes) != 1:
        temp = []
        for i in range(0,len(nodes),2):
            node1 = nodes[i]
            if i + 1 < len(nodes):
                node2 = nodes[i+1]
            else:
                temp.append(nodes[i])
                break
            concatenated_hash = node1.value + node2.value
            parent = MerkleTreeNode(concatenated_hash)
            parent.left = node1
            parent.right = node2
            temp.append(parent)
        nodes = temp 
    return nodes[0]