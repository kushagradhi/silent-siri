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
semAttachments = {"best": ([], "Oscar O "),
                "PERSON": ([], 'P.name like "%<entity>%"'),
                "MOVIE" : ([], 'M.name like "%<entity>%"'),
                "NATIONALITY" : {"FRENCH":"FRANCE", "ITALIAN":"ITALY", "AMERICAN":"USA", "BRITISH":"UK", "GERMAN":"GERMANY"},
                "POB" : ([], 'P.pob like "%<entity>%"')}


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
    query += " ".join(clauses["TEST"])
    query += " WHERE "
    for w in clauses["WHERE"]:
        query += w + " and "
    query = query.rsplit("and ",1)[0]
    query += " ;"
    print(f'\nquery concatenated:\n{query}')
    return query


def check(string,clauses,add=True):

    if (add):
        if (len(clauses) == 0):
            clauses.append(string)
            return


    for clause in clauses:
        if clause==string:
            return True
    if (add):
        clauses.append(string)
    return False

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
        elif type(child) is nltk.Tree and child.height()==2:          
            print(f'if type(child) is tree==2, at childLabel {child.label()}')
            semval = ''.join([c for c in child])
            clauses["SENT"].append(semval)
            print(f'leafVal: {semval}')
            if child.label() in ["VB", "VBD", "VBP","VBN"] and semval.upper() not in ["DID","IS","WAS"]:
                #semAttach = semAttachments[semval]
                if semval.upper() in ["WON",'WIN']:
                    check('From movie M', clauses["TEST"])
                    check('Join oscar O on M.id = O.movie_id',clauses["TEST"])
                if semval.upper() in ['DIRECTED','DIRECT']:
                    check('From movie M', clauses["TEST"])
                    check('Join Director D on M.id = D.movie_id',clauses["TEST"])
                    check('Join Person P on P.id = D.director_id', clauses["TEST"])
                if semval.upper() in ['STAR']:
                    check('From movie M', clauses["TEST"])
                    check('Join Actor A on M.id = A.movie_id',clauses["TEST"])
                    check ('Join Person P on P.id = A.actor_id',clauses["TEST"])
                if semval.upper() in ['BORN']:
                    check('From Person P',clauses["TEST"])
                awrd = None
                if "movie" in clauses["NER"].keys() and semval.upper() in ["WON",'WIN','BEST','OSCAR']:
                    awrd = "picture"
                elif "actor" in clauses["NER"].keys() and semval.upper() in ["WON",'WIN','BEST','OSCAR']:
                    awrd = "best-actor"
                    check('Join Person P on P.id = O.person_id', clauses["TEST"])
                elif "actress" in clauses["NER"].keys() and semval.upper() in ["WON",'WIN','BEST','OSCAR']:
                    awrd = "best-actress"
                    check('Join Person P on P.id = O.person_id', clauses["TEST"])
                elif "director" in clauses["NER"].keys() and semval.upper() in ["WON",'WIN','BEST','OSCAR']:
                    awrd = "director"
                    check('Join Person P on P.id = O.person_id', clauses["TEST"])
                elif "PERSON" in clauses["NER"].values() and semval.upper() in ["WON",'WIN','BEST','OSCAR']:
                    check('Join Person P on P.id = O.person_id', clauses["TEST"])
                if (awrd):
                    clauses["WHERE"].append('O.type like "%<award>%"'.replace("<award>", awrd))
            elif child.label() in ["NNP"]:
                if clauses["NER"][semval] == "PERSON":
                    semAttach = semAttachments["PERSON"][1]  
                    print(type(semval), type(semAttach), semAttach)  
                    semAttach = semAttach.replace("<entity>", semval)
                    print(semAttach)
                    clauses["WHERE"].append(semAttach)
                elif clauses["NER"][semval] in ["COUNTRY","CITY"]:
                    if "born" in clauses["NER"].keys():
                        clauses["WHERE"].append('P.POB like "%<place>%"'.replace("<place>", semval))
                else:                                           # if NNP is part of film name
                    semAttach = semAttachments["MOVIE"][1]
                    semAttach = semAttach.replace("<entity>", semval)
                    clauses["WHERE"].append(semAttach)
            elif child.label() in ["NN"]:
                if clauses["NER"][semval] in ['TITLE'] and clauses['SENT'][0] in ['Is','Was']:
                    if semval.upper() in ['ACTOR','ACTRESS']:
                        check('From movie M', clauses["TEST"])
                        check('JOIN Actor A on M.id = A.movie_id',clauses['TEST'])
                        check('JOIN Person P on P.id = A.actor_id', clauses['TEST'])
                    else:
                        check('From movie M', clauses["TEST"])
                        check('JOIN Director D on M.id = D.movie_id', clauses['TEST'])
                        check('JOIN Person P on P.id = D.director_id', clauses['TEST'])
            elif child.label() in ["IN"]:
                clauses["SEMVAL"].append("IN")
                if (semval == 'by'):
                    check('From movie M', clauses["TEST"])
                    check('Join Director D on M.id = D.movie_id', clauses["TEST"])
                    check('Join Person P on P.id = D.director_id', clauses["TEST"])
            elif child.label() in ["JJ","JJS"]:
                if clauses["NER"][semval] == "NATIONALITY":
                    c = semAttachments["NATIONALITY"][semval.upper()]
                    semAttach = semAttachments["POB"][1]
                    semAttach = semAttach.replace("<entity>", c)
                    clauses["WHERE"].append(semAttach)
                elif semval.upper() == "BEST":
                    check('From movie M', clauses["TEST"])
                    check('Join oscar O on M.id = O.movie_id',clauses["TEST"])
            elif child.label() in ["CD"]:
                if clauses["SENT"][-2].upper() == "IN":
                    if "born" in clauses["SENT"]:
                        clauses["WHERE"].append('P.dob like "%'+semval+'%"')
                    elif "win" in clauses["SENT"] or "won" in clauses["SENT"] or "directed" in clauses["SENT"]:
                        clauses["WHERE"].append('O.year like "%'+semval+'%"')
            elif child.label() in ["WP"]:        #Who question
                clauses["SELECT"].append("P.name")  #but need to account for Music which has tablename Artist
            elif child.label() in ["WDT", "WRB"]:      #Which question, need to account for name/movie
                if "When" in clauses["NER"].keys():
                    clauses["SELECT"].append("O.year")
                elif "PERSON" in clauses["NER"].values():
                    clauses["SELECT"].append("P.name")      #When question, need to account for name/movie
                elif "movie" in clauses["NER"].keys():
                    clauses["SELECT"].append("M.name")
            elif child.label() in ["VBD","VBZ"] and semval.upper() in ["DID"]:      #When question, need to account for name/movie
                if len(clauses["SELECT"]) == 0:
                    clauses["SELECT"].append("count(*)")
            elif child.label() in ["VBD","VBZ"] and semval.upper() in ["IS","WAS"]:
                if len(clauses["SELECT"]) == 0:
                    clauses["SELECT"].append("count(*)")
            elif child.label() in ["."]:
                pass
            
        
    

def getSQLQuery(sent):
    tree = next(getParseTree(sent))[0]         # get parse tree for query below "ROOT"
    # print(type(tree))
    # exit()
    clauses = {"FROM":[], "SELECT": [], "WHERE":[], "SEMVAL":[], "NER":{key:value for (key,value) in cnlp.getNERTags(sent)}, "SENT":[],
               "TEST":[]}
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

q=getSQLQuery("Is Kubrick a director?")

t=DBInterface()
t.start()
print(t.executeQuery(q, 'movie'))
t.closeConnections()

    

