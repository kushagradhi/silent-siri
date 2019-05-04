from nltk.parse.corenlp import CoreNLPParser, CoreNLPDependencyParser
import nltk
from collections import OrderedDict
from Tree import Node, printTree
from DB_interface import DBInterface
from Utils import CNLP

#CoreNLP wrapper
cnlp=CNLP()

# Reading sentences from input file
# file = open('../data//input.txt','r')
# sentences = [line.strip().split() for line in file.readlines()]
# file.close()

queries = ["Did Neeson star in Schindler’s List?"]#, "Did Allen direct Mighty Aphrodite?", "Is Kubrick a director?", "Was Loren born in Italy?", "Was Birdman the best movie in 2015?"
        #    "Is Mighty Aphrodite by Allen?", "Did Neeson star in Schindler’s List?", "Did Swank win the oscar in 2000?", "Did a French actor win the oscar in 2012?",
        #    "Did a movie with Neeson win the oscar for best film?", "Who directed Schindler’s List?", "Who won the oscar for best actor in 2005?", "Who directed the best movie in 2010?",
        #    "Which American actress won the oscar in 2012?", "Which movie won the oscar in 2000?", "When did Blanchett win an oscar for best actress?"
        # ]
semAttachments = {"direct": (['P', 'M'],"Person P inner join Director D on D.director_id=P.id inner join Movie M on M.id=D.movie_id"),
                "star" : ([], "Person P inner join Actor A on P.id=A.actor_id inner join Movie M on A.movie_id=M.id"),
                "win" : ([], "Oscar O inner join Movie M on O.movie_id=M.id inner join Person P on P.id=O.person_id"),
                "won" : ([], "Oscar O inner join Movie M on O.movie_id=M.id inner join Person P on P.id=O.person_id"),
                "PERSON": ([], 'P.name like "%<entity>%"'),
                "MOVIE" : ([], 'M.name like "%<entity>%"')
                }


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


def getGrammarRules(sent):
    grammar=[]
    parseTree = getParseTree(sent)
    tree=next(parseTree)[0]
    # grammar.append([rule.unicode_repr() for rule in tree.productions()])
    for rule in tree.productions():
        grammar.append(rule.unicode_repr())
    return grammar


def getProduction(node):
    '''
        Get the grammar production at parameter node, in the form: node -> child1 child2...
    '''
    production = node.label() + " -> "
    for child in node:
        production += child.label() + " "
    return production.strip()


def concatSQLClauses(clauses):
    query = "SELECT "
    for s in clauses["SELECT"]:
        query += s + " "
    query += " FROM "
    for f in clauses["FROM"]:
            query += f + " "
    query += " WHERE "
    for w in clauses["WHERE"]:
        query += w + " and "
    query = query.rsplit("and ",1)[0]
    query += " ;"
    print(f'\nquery concatenated:\n{query}')
    return query


'''Recursively build SQL Query'''
def buildQuery(parent, clauses):
    try:
        print(f'processing node {parent.label()}, children: ', end=" ")
        for node in parent:
            print(node.label(), end=', ')
        print()
    except AttributeError:
        print(f'processing leaf {parent}')

    for child in parent:
        if type(child) is nltk.Tree and child.height()!=2:
            print(f'if type(child) is tree>2, going down childLabel {child.label()}')
            buildQuery(child, clauses)
            # productionAtCurrentNode=getProduction(child)
        elif type(child) is nltk.Tree and child.height()==2:          
            print(f'if type(child) is tree==2, at childLabel {child.label()}')
            semval = ''.join([c for c in child])
            clauses["SENT"].append(semval)
            print(f'leafVal: {semval}')
            if child.label() in ["VB", "VBD"]:
                semAttach = semAttachments[semval]
                clauses["FROM"].append(semAttach[1])
            elif child.label() in ["NNP"]:
                if clauses["NER"][semval] == "PERSON":    #if NNP is director/actor etc
                    semAttach = semAttachments["PERSON"][1]  
                    print(type(semval), type(semAttach), semAttach)  
                    semAttach = semAttach.replace("<entity>", semval)
                    print(semAttach)
                    clauses["WHERE"].append(semAttach)   
                elif clauses["NER"][semval] == "LOCATION":       
                    pass
                else:                                           # if NNP is part of film name
                    semAttach = semAttachments["MOVIE"][1]
                    semAttach = semAttach.replace("<entity>", semval)
                    clauses["WHERE"].append(semAttach)
            elif child.label() in ["IN"]:
                clauses["SEMVAL"].append("IN")
            elif child.label() in ["CD"]:
                if clauses["SENT"][-1].upper() == "IN":
                    if "born" in clauses["SENT"]:
                        clauses["WHERE"].append("P.dob")
                    elif "win" in clauses["SENT"]:
                        clauses["WHERE"].append("O.year")
            elif child.label() in ["WP"]:        #Who question
                clauses["SELECT"].append("P.name")  #but need to account for Music which has tablename Artist
            elif child.label() in ["WDT", "WRB"]:      #Which question, need to account for name/movie 
                clauses["SELECT"].append("P.name")      #When question, need to account for name/movie
            elif child.label() in ["VBD"] and semval.upper() in ["DID"]:      #When question, need to account for name/movie
                clauses["SELECT"].append("count(*)") 
            elif child.label() in ["."]:
                pass
            
        
        
        
        
        

            
    

def getSQLQuery(sent):
    tree = next(getParseTree(sent))[0]         # get parse tree for query below "ROOT"
    # print(type(tree))
    # exit()
    clauses = {"FROM":[], "SELECT": [], "WHERE":[], "SEMVAL":[], "NER":{key:value for (key,value) in cnlp.getNERTags(sent)}, "SENT":[]}
    for node in tree:
        print(node.label(), end=', ')
    print(f'\nbefore: {clauses}\n')
    buildQuery(tree, clauses)
    print(f'\nafter: {clauses}\n')
    q=concatSQLClauses(clauses)
    return q
    
         

    
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

q=getSQLQuery("Which movie won the oscar in 2000?")

t=DBInterface()
t.start()
print(t.executeQuery(q, 'movie'))
t.closeConnections()

    

