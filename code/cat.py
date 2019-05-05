from nltk.parse import CoreNLPParser
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
from enum import Enum
from Utils import CNLP

class CategoryPredictor():
  
    def __init__(self):
        self.cnlp=CNLP()
        # self.

    # Returns - NER tagged sentence
    def nerTagger(self, sentence):
        return list(self.cnlp.getNERTags((sentence.split())))


    def getNERPrediction(self, sentence):
        """
        Returns  1. 0  - If certain that belongs to Geography
                    2. -2 - If certain that belongs to Music/Movie
                    3. -3 - If uncertain about the category
        """
        onlyOTags = True
        geoTags=['O', 'CITY', 'COUNTRY', 'LOCATION']
        tag = 0
        for tagged in self.nerTagger(sentence):
            if tagged[1] not in geoTags:
                tag=-2
                onlyOTags = False
                break
            if not tagged[1] =='O':
                onlyOTags = False
        if(onlyOTags):
            tag=-3
        return tag



    
