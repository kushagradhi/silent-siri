import nltk
from nltk.parse import CoreNLPParser

parser = CoreNLPParser(url='http://localhost:9000')

file = open('../data//input.txt','r')
sentences = [line.strip().split() for line in file.readlines()]
file.close()

file = open('../output.txt','w')

with file as out:
    for sent in sentences:
        tokens = sent
        parsetree = list(parser.parse(tokens))
        file.write(" ".join(sent) + "\n\n")
        file.write(str(parsetree[0]))
        file.write("\n\n=================================================================================\n\n")
file.close()