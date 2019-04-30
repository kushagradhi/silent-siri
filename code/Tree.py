class Node:
    def __init__(self,value):
        self.value = value
        self.next = None

def printTree(node,space=''):
    print (space,node.value)
    if node.next:
        for child in node.next:
            printTree(child,space+'  ')

