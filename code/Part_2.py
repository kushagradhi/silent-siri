from nltk.parse.corenlp import CoreNLPParser, CoreNLPDependencyParser
import nltk
from collections import OrderedDict
from Tree import Node, printTree
from DB_interface import DBInterface
from Utils import CNLP

cnlp=CNLP()


semAttachments = {"best": ([], "Oscar O "),
                "PERSON": ([], 'P.name like "%<entity>%"'),
                "MOVIE" : ([], 'M.name like "%<entity>%"'),
                "NATIONALITY" : {"FRENCH":"FRANCE", "ITALIAN":"ITALY", "AMERICAN":"USA", "BRITISH":"UK", "GERMAN":"GERMANY"},
                "POB" : ([], 'P.pob like "%<entity>%"'),
                "PLACEOFBITH" : ([], 'P.placeOfBith like "%<entity>%"')}
def getParseTree(sent):
    return cnlp.getParse(sent)

def getDependencyTree(sent):
    return cnlp.getDepParse(sent.split())

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

def semanticAttachmentVerbs(semval,clauses):
    awrd = None
    vbs = ["WON", 'WIN']
    ner_keys = clauses["NER"].keys()
    ner_values = clauses["NER"].values()
    sem_val = semval.upper()
    if sem_val in ["WON", 'WIN']:
        check('From movie M', clauses["TEST"])
        check('Join oscar O on M.id = O.movie_id', clauses["TEST"])
    if sem_val in ['DIRECTED', 'DIRECT']:
        check('From movie M', clauses["TEST"])
        check('Join Director D on M.id = D.movie_id', clauses["TEST"])
        check('Join Person P on P.id = D.director_id', clauses["TEST"])
    if sem_val in ['STAR']:
        check('From movie M', clauses["TEST"])
        check('Join Actor A on M.id = A.movie_id', clauses["TEST"])
        check('Join Person P on P.id = A.actor_id', clauses["TEST"])
    if sem_val in ['BORN']:
        if clauses["CAT"] == 'MOVIE':
            check('From Person P', clauses["TEST"])
        elif clauses["CAT"] == 'MUSIC':
            check('From Artist P', clauses["TEST"])

    if sem_val in vbs:
        if "movie" in ner_keys:
            awrd = "picture"
        elif "actor" in ner_keys:
            awrd = "best-actor"
            check('Join Person P on P.id = O.person_id', clauses["TEST"])
        elif "actress" in ner_keys:
            awrd = "best-actress"
            check('Join Person P on P.id = O.person_id', clauses["TEST"])
        elif "director" in ner_keys:
            awrd = "director"
            check('Join Person P on P.id = O.person_id', clauses["TEST"])
        elif "PERSON" in ner_values:
            check('Join Person P on P.id = O.person_id', clauses["TEST"])
    if (awrd):
        clauses["WHERE"].append('O.type like "%<award>%"'.replace("<award>", awrd))

def semanticAttachmentNounPhrase(semval,clauses):
    if clauses["NER"][semval] == "PERSON":
        semAttach = semAttachments["PERSON"][1]
        # print(type(semval), type(semAttach), semAttach)
        semAttach = semAttach.replace("<entity>", semval)
        # print(semAttach)
        clauses["WHERE"].append(semAttach)
    elif clauses["NER"][semval] in ["COUNTRY", "CITY"]:
        if "born" in clauses["NER"].keys():
            if clauses['CAT'] == 'MOVIE':
                colname = 'POB'
            elif clauses['CAT'] == 'MUSIC':
                colname = 'placeOfBith'
            clauses["WHERE"].append('P.'+ colname +' like "%<place>%"'.replace("<place>", semval))
    else:  # if NNP is part of film name
        semAttach = semAttachments["MOVIE"][1]
        semAttach = semAttach.replace("<entity>", semval)
        clauses["WHERE"].append(semAttach)

def semanticAttachmentNoun(semval,clauses):
    if clauses["NER"][semval] in ['TITLE'] and clauses['SENT'][0] in ['Is', 'Was']:
        if semval.upper() in ['ACTOR', 'ACTRESS']:
            check('From movie M', clauses["TEST"])
            check('JOIN Actor A on M.id = A.movie_id', clauses['TEST'])
            check('JOIN Person P on P.id = A.actor_id', clauses['TEST'])
        else:
            check('From movie M', clauses["TEST"])
            check('JOIN Director D on M.id = D.movie_id', clauses['TEST'])
            check('JOIN Person P on P.id = D.director_id', clauses['TEST'])

def semanticAttachmentIn(semval,clauses):
    if (semval == 'by'):
        check('From movie M', clauses["TEST"])
        check('Join Director D on M.id = D.movie_id', clauses["TEST"])
        check('Join Person P on P.id = D.director_id', clauses["TEST"])

def semanticAttachmentAdj(semval,clauses):
    if clauses["NER"][semval] == "NATIONALITY":
        c = semAttachments["NATIONALITY"][semval.upper()]
        semAttach = semAttachments["POB"][1]
        semAttach = semAttach.replace("<entity>", c)
        clauses["WHERE"].append(semAttach)
    elif semval.upper() == "BEST":
        check('From movie M', clauses["TEST"])
        check('Join oscar O on M.id = O.movie_id', clauses["TEST"])
        awrd = None
        if "movie" in clauses["NER"].keys():
            awrd = "picture"
        elif "actor" in clauses["NER"].keys():
            awrd = "best-actor"
        elif "actress" in clauses["NER"].keys():
            awrd = "best-actress"
        elif "director" in clauses["NER"].keys():
            awrd = "director"
        if (awrd):
            clauses["WHERE"].append('O.type like "%<award>%"'.replace("<award>", awrd))

def semanticAttachmentCD(semval,clauses):
    if clauses["SENT"][-2].upper() == "IN":
        if "born" in clauses["SENT"]:
            clauses["WHERE"].append('P.dob like "%' + semval + '%"')
        elif "win" in clauses["SENT"] or "won" in clauses["SENT"] or "directed" in clauses["SENT"]:
            clauses["WHERE"].append('O.year like "%' + semval + '%"')

def semanticAttachmentWH(semval,clauses):
    if "When" in clauses["NER"].keys():
        clauses["SELECT"].append("O.year")
    elif "PERSON" in clauses["NER"].values():
        clauses["SELECT"].append("P.name")  # When question, need to account for name/movie
    elif "movie" in clauses["NER"].keys():
        clauses["SELECT"].append("M.name")
    else:
        clauses["SELECT"].append("P.name")

'''Recursively build SQL Query'''
def buildQuery(parent, clauses):
    for child in parent:
        if type(child) is nltk.Tree and child.height()!=2:
            buildQuery(child, clauses)
        elif type(child) is nltk.Tree and child.height()==2:
            semval = ''.join([c for c in child])
            clauses["SENT"].append(semval)
            if child.label() in ["VB", "VBD", "VBP","VBN"] and semval.upper() not in ["DID","IS","WAS"]:
                semanticAttachmentVerbs(semval,clauses)
            elif child.label() in ["NNP"]:
                semanticAttachmentNounPhrase(semval,clauses)
            elif child.label() in ["NN"]:
                semanticAttachmentNoun(semval, clauses)
            elif child.label() in ["IN"]:
                semanticAttachmentIn(semval, clauses)
            elif child.label() in ["JJ","JJS"]:
                semanticAttachmentAdj(semval, clauses)
            elif child.label() in ["CD"]:
                semanticAttachmentCD(semval, clauses)
            elif child.label() in ["WP"]:
                clauses["SELECT"].append("P.name")
            elif child.label() in ["WDT", "WRB"]:
                semanticAttachmentWH(semval, clauses)
            elif child.label() in ["VBD","VBZ"] and semval.upper() in ["DID","IS","WAS"]:
                if len(clauses["SELECT"]) == 0:
                    clauses["SELECT"].append("count(*)")
            elif child.label() in ["."]:
                pass
            

def getSQLQuery(sent,category):
    tree = next(getParseTree(sent))[0]         # get parse tree for query below "ROOT"
    clauses = {"FROM":[], "SELECT": [], "WHERE":[], "SEMVAL":[],
               "NER":{key:value for (key,value) in cnlp.getNERTags(sent)},
               "SENT":[],"TEST":[],"CAT":category}
    buildQuery(tree, clauses)
    query = concatSQLClauses(clauses)
    return query


#Reading sentences from input file
file = open('../data//input.txt','r')
sentences = [line.strip() for line in file.readlines()]
file.close()
t=DBInterface()
t.start()
file = open("output.txt","w")
sentences = ['Was Beyonce born in the USA?']
for line in sentences:
    query = getSQLQuery(line,'MUSIC')
    out = '\n' + line + '\n' + query +'\n'
    file.write(out)
    eq = t.executeQuery(query, 'MUSIC')
    if type(eq) == int:
        file.write(str(eq))
    else:
        for item in eq:
            file.write(str(item[0]))
t.closeConnections()
file.close()

    

