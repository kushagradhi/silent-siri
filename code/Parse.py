import nltk
from nltk.parse import CoreNLPParser

# Creates object for CoreNLPParser
parser = CoreNLPParser(url='http://localhost:9000')

# Reading sentences from input file
file = open('../data//input.txt','r')
sentences = [line.strip().split() for line in file.readlines()]
file.close()

# Creating output file to write result
file = open('../output.txt','w')

with file as out:
    for sent in sentences:
        tokens = sent
        parsetree = list(parser.parse(tokens))
        file.write(" ".join(sent) + "\n\n")
        file.write(str(parsetree[0]))
        file.write("\n\n=================================================================================\n\n")
file.close()