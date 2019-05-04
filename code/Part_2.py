from nltk.parse.corenlp import CoreNLPParser, CoreNLPDependencyParser
import nltk
from collections import OrderedDict
from Tree import Node, printTree
from DB_interface import DBInterface
from Utils import CNLP

cnlp=CNLP()

# # Creates objects for CoreNLPParser
# CNLPServerURL='http://localhost:9000'
# parser = CoreNLPParser(url=CNLPServerURL)
# dep_parser = CoreNLPDependencyParser(url=CNLPServerURL)
# ner_tagger = CoreNLPParser(url=CNLPServerURL, tagtype='ner')
# pos_tagger = CoreNLPParser(url=CNLPServerURL, tagtype='pos')

# Reading sentences from input file
# file = open('../data//input.txt','r')
# sentences = [line.strip().split() for line in file.readlines()]
# file.close()

queries = ["Did Allen direct Mighty Aphrodite?"]#, "Is Kubrick a director?", "Was Loren born in Italy?", "Was Birdman the best movie in 2015?"
        #    "Is Mighty Aphrodite by Allen?", "Did Neeson star in Schindler’s List?", "Did Swank win the oscar in 2000?", "Did a French actor win the oscar in 2012?",
        #    "Did a movie with Neeson win the oscar for best film?", "Who directed Schindler’s List?", "Who won the oscar for best actor in 2005?", "Who directed the best movie in 2010?",
        #    "Which American actress won the oscar in 2012?", "Which movie won the oscar in 2000?", "When did Blanchett win an oscar for best actress?"
        # ]
semAttachments = {"direct": (['P', 'M'],"Person P inner join Director D on D.director_id=P.id inner join Movie M on M.id=D.movie_id")}


def getParseTree(sent):
    return cnlp.getParse(sent)

def getDependencyTree(sent):
    return cnlp.getDepParse(sent.split())

# tree=next(getParseTree('This is good.'))
# tree.pretty_print()
# tree = list(getParseTree(sent))
# print (tree[0],end='\n\n\n')
ROOT = 'ROOT'
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

# root = getNodes(tree,label,value,"ROOT")[0].next[0]
# printTree(root)
# print('\n\n\n')


primaryLogicDict={
    "direct": (['P', 'M'],"Person P inner join Director D on D.director_id=P.id inner join Movie M on M.id=D.movie_id"),
    "PERSON": ([], '<tableName>.name like "%<entity>%"'),
    "MOVIE" : ([], '<tableName>.name like "%<entity>%"')
    }
where= '.name like %<NP.sem>%'

def getGrammarRules(sent):
    grammar=[]
    parseTree = getParseTree(sent)
    tree=next(parseTree)[0]
    # grammar.append([rule.unicode_repr() for rule in tree.productions()])
    for rule in tree.productions():
        grammar.append(rule.unicode_repr())
    return grammar

'''Get the grammar production at parameter node, in the form: node -> child1 child2...'''
def getProduction(node):
    production = node.label().append(" -> ")
    for child in node:
        production.append(child.label()).append(" ")
    return production.strip()


'''Recursively build SQL Query'''
def buildQuery(parent, clauses):
    for node in parent:
        if type(node) is nltk.Tree:
            buildQuery(node, clauses)
        else:                           #at leaf nodes
            clauses["SEMVAL"].append(node.label())
            return
        productionAtCurrentNode=getProduction(node)

        if node.height()==2:
            if node.label() in ["VB"]:
                semAttach = semAttachments[clauses["SEMVAL"].pop()]
                clauses["FROM"].append(semAttach)
            elif node.label() in ["NNP"]:
                if clauses["NER"][node.label()] is "PERSON":    #if NNP is director/actor etc
                    semAttach = semAttachments["PERSON"][1]    
                    semAttach.replace("<entity>", clauses["SEMVAL"].pop())
                    clauses["WHERE"].append(semAttach)   
                elif clauses["NER"][node.label()] is "LOCATION":       
                    pass
                else:                                           # if NNP is part of film name
                    semAttach = semAttachments["MOVIE"][1]
                    semAttach.replace("<entity>", clauses["SEMVAL"].pop())
                    clauses["WHERE"].append(semAttach)
            elif node.label() in ["IN"]:
                pass
            return
        
        
        
        

            
    

def getSQLQuery(sent):
    tree = next(getParseTree(sent))[0]         # get parse tree for query below "ROOT"
    print(type(tree))
    exit()
    clauses = {"FROM":[], "SELECT": [], "WHERE":[], "SEMVAL":[], "NER":{key:value for (key,value) in cnlp.getNERTags(sent)}}
    buildQuery(tree, clauses)
    
         

    
grammarSet=[]
for query in queries:
    newRules = getGrammarRules(query)
    # print(newRules)
    for rule in newRules:
        grammarSet.append(rule)
        
with open('..//data//grammar.txt', 'w') as writer:
    grammarSet.sort()
    writer.write("\n".join(rule.replace("'", "") for rule in grammarSet))

# print(getGrammarRules(sent))

q = getSQLQuery('Did Allen direct Mighty Aphrodite?')



    

