from nltk.parse import CoreNLPParser
from nltk.corpus import wordnet as wn
from enum import Enum

class DB(Enum):
    GEOGRAPHY = 0
    MOVIE = 1
    MUSIC = 2

ner_tagger = CoreNLPParser(url='http://localhost:9000', tagtype='ner')

queriesFile = '..//data//queries.txt'

def nerTagger(sentence):
    return list(ner_tagger.tag((sentence.split())))

def hasOnlyLocationTags(sentences):
    acceptedTags=['O', 'CITY', 'COUNTRY', 'LOCATION']
    tags = [0 for i in range(len(sentences))]
    for i, sentence in enumerate(sentences):
        onlyOTags = True
        for tagged in nerTagger(sentence):
            if(tagged[1] not in acceptedTags):
                tags[i]=-1
                continue
            if(tagged[1]!='O'):
                onlyOTags = False
        if(onlyOTags):
            tags[i]=-1
    return tags

def getCategoryPredictions(sentences):
    category = ['movie', 'music']
    # category = ['geography', 'movie', 'music']
    # list_sentences=['Which pop artist sings CrazyInLove?', 
    #                 'Which is the deepest ocean?']
    # a='Did Neeson star in Schindler’sList'#.lower()
    tags=[]
    for sentence in sentences:
        scores=[]
        for i in category:
            score = 0
            cat_synset = wn.synsets(i)[0]
            for word in sentence.split():
                word_synsets = wn.synsets(word)
                if(len(word_synsets)==0):
                    continue
                word_synset = wn.synsets(word)[0]
                # print(f'{word}: {word_synset}')
                if(word_synset.path_similarity(cat_synset) != None):
                    score += word_synset.path_similarity(cat_synset)
                # if(word_synset.lch_similarity(cat_synset) != None):
                #     score += word_synset.lch_similarity(cat_synset)
                # print(f'{word}: {score}')
            scores.append(score)
        tags.append(1+scores.index(max(scores)))
    return tags
    # for i in range(len(category)):
    #     print(f'{category[i]}: {scores[i]}', end="\t")


def main():
    with open(queriesFile) as f:
        queries = f.readlines()
    # print(queries)
    tags = hasOnlyLocationTags(queries)
    nonGeoIndices = [i for i,el in enumerate(tags) if el==-1]
    tagsOthers = getCategoryPredictions([queries[i] for i in nonGeoIndices])
    for i in range(len(tagsOthers)):
        tags[nonGeoIndices[i]] = tagsOthers[i]
    
    for i in range(len(tags)):
        print(f'{DB(tags[i]).name}: {queries[i]}')

main()
