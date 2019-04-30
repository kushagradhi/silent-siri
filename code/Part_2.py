from nltk.parse import CoreNLPParser
import nltk
from collections import OrderedDict
from Tree import Node,printTree

# Creates object for CoreNLPParser
parser = CoreNLPParser(url='http://localhost:9000')

# Reading sentences from input file
# file = open('../data//input.txt','r')
# sentences = [line.strip().split() for line in file.readlines()]
# file.close()

sent = "Which movie won the Oscar in 2000?"
tokens = sent.split()
parseTree = list(parser.parse(tokens))
print (parseTree[0])
ROOT = 'ROOT'
tree = parseTree
label = []
value = []

def getNodes(parent,label,value,l):
    nodes = []
    for node in parent:
        if type(node) is nltk.Tree:
            nd = Node(node.label())
            nd.next = getNodes(node,label,value,node.label())
            nodes.append(nd)
        else:
            nodes.append(Node(node))
    return nodes

root = getNodes(tree,label,value,"ROOT")[0].next[0]
printTree(root)


