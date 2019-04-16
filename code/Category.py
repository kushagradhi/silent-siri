from nltk.parse import CoreNLPParser
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
from enum import Enum

class DB(Enum):
    GEOGRAPHY = 0
    MOVIE = 1
    MUSIC = 2

ner_tagger = CoreNLPParser(url='http://localhost:9000', tagtype='ner')
queriesFile = '../data//input.txt'

def nerTagger(sentence):
    return list(ner_tagger.tag((sentence.split())))

def hasOnlyLocationTags(sentences):
    geoTags=['O', 'CITY', 'COUNTRY', 'LOCATION']
    tags = [0 for i in range(len(sentences))]
    for i, sentence in enumerate(sentences):
        onlyOTags = True
        for tagged in nerTagger(sentence):
            if tagged[1] not in geoTags:
                tags[i]=-2
                onlyOTags = False
                break
            if not tagged[1] =='O':
                onlyOTags = False
        if(onlyOTags):
            tags[i]=-3
    return tags

def getCategoryPredictions(sentences, tagIndicator):
    category = [['place', 'geographic', 'mountain', 'ocean', 'hill'],
                ['cinema', 'direct', 'oscar', 'movie'],
                ['pop', 'music', 'sing', 'album']]
    tags=[]
    for index, sentence in enumerate(sentences):        #for all sentences
        scores=[]
        for cat_i in category:      #for all categories
            for i in cat_i:     #for all subcategories
                score = 0
                cat_synset = wn.synsets(i)[0]
                for word in sentence.split():       #for all words in sentence
                    word_synsets = wn.synsets(word)
                    if(len(word_synsets)==0):
                        continue
                    word_synset = wn.synsets(word)[0]
                    if(word_synset.path_similarity(cat_synset) != None):
                        score += word_synset.path_similarity(cat_synset)
            scores.append(score/(len(cat_i)))
        tagPrediction = scores.index(max(scores))
        if(tagIndicator[index]==-2):
            if(scores[1]>scores[2]):
                tagPrediction=1
            else:
                tagPrediction=2
        tags.append(tagPrediction)
    return tags

def main():
    queries=[]
    with open(queriesFile) as f:
        queries=f.readlines()
    tags = hasOnlyLocationTags(queries)

    stop_words = set(stopwords.words('english')) 
    for i, query in enumerate(queries):
        queries[i] = " ".join([word for word in word_tokenize(query) if not word in stop_words])

    nonGeoIndices = [i for i,el in enumerate(tags) if el!=0]
    tagsOthers = getCategoryPredictions([queries[i] for i in nonGeoIndices], [tags[i] for i in nonGeoIndices])
    for i in range(len(tagsOthers)):
        tags[nonGeoIndices[i]] = tagsOthers[i]

    for i in range(len(tags)):
        print ("Sentence: ",queries[i])
        print ("Category: ",DB(tags[i]).name,"\n")
main()
