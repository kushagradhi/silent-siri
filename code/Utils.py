from nltk.parse.corenlp import CoreNLPParser, CoreNLPDependencyParser

class CNLP:
    CNLPServerURL='http://localhost:9000'

    def __init__(self):
        self.parser = CoreNLPParser(url=self.CNLPServerURL)
        self.dep_parser = CoreNLPDependencyParser(url=self.CNLPServerURL)
        self.ner_tagger = CoreNLPParser(url=self.CNLPServerURL, tagtype='ner')
        self.pos_tagger = CoreNLPParser(url=self.CNLPServerURL, tagtype='pos')

    def getParse(self, sentence):
        if(type(sentence)==list):
            return self.parser.parse(sentence)
        else:
            return self.parser.raw_parse(sentence)

    def getDepParse(self, sentence):
        if(type(sentence)==list):
            return self.dep_parser.parse(sentence)
        else:
            return self.dep_parser.raw_parse(sentence)  

    def getNERTags(self, sentence):
        if(type(sentence)!=list):
            sentence=sentence.split()
        return self.ner_tagger.tag(sentence)

    def getPOSTags(self, sentence):
        if(type(sentence)==list):
            return self.pos_tagger.parse(sentence)
        else:
            return self.pos_tagger.raw_parse(sentence)     


