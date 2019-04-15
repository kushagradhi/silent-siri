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
pos_tagger = CoreNLPParser(url='http://localhost:9000', tagtype='pos')
queriesFile = '..//data//queries'

def nerTagger(sentence):
    return list(ner_tagger.tag((sentence.split())))

def hasOnlyLocationTags(sentences):
    geoTags=['O', 'CITY', 'COUNTRY', 'LOCATION']
    nonGeoTags=['PERSON', 'NATIONALITY']
    tags = [0 for i in range(len(sentences))]
    for i, sentence in enumerate(sentences):
        onlyOTags = True
        for tagged in nerTagger(sentence):
            # if(tagged[1] not in geoTags):
            #     tags[i]=-3
            #     continue
            if tagged[1] not in geoTags:
                tags[i]=-2
                onlyOTags = False
                break
            if not tagged[1] =='O':
                onlyOTags = False
        if(onlyOTags):
            tags[i]=-3
        
        # if(i==5):
        #     exit()
    # exit()
    return tags

def getCategoryPredictions(sentences, tagIndicator):
    # category = ['movie', 'music']
    # category = ['geographical', 'cinema', 'music']
    category = [['place', 'geographic', 'mountain', 'ocean', 'hill'], ['cinema', 'direct', 'oscar', 'movie'], ['pop', 'music', 'sing', 'album']]
    tags=[]
    for index, sentence in enumerate(sentences):        #for all sentences
        scores=[]
        for cat_i in category:      #for all categories
            # nullSynSetCount=0
            for i in cat_i:     #for all subcategories
                score = 0
                cat_synset = wn.synsets(i)[0]
                for word in sentence.split():       #for all words in sentence
                    word_synsets = wn.synsets(word)
                    if(len(word_synsets)==0):
                        continue
                    word_synset = wn.synsets(word)[0]
                    # print(f'{word}: {word_synset}')
                    if(word_synset.path_similarity(cat_synset) != None):
                        # score.append(word_synset.path_similarity(cat_synset))
                        score += word_synset.path_similarity(cat_synset)
                    # if(word_synset.lch_similarity(cat_synset) != None):
                    #     score += word_synset.lch_similarity(cat_synset)
                    # print(f'{word}: {score}')
            # scores.append(max(score))
            scores.append(score/(len(cat_i)))
        tagPrediction = scores.index(max(scores))
        # if(index==23):
        print(f'{sentence}, {scores}\n \n')
        if(tagIndicator[index]==-2):
            if(scores[1]>scores[2]):
                tagPrediction=1
            else:
                tagPrediction=2
        tags.append(tagPrediction)
    return tags
    # for i in range(len(category)):
    #     print(f'{category[i]}: {scores[i]}', end="\t")


def main():
    queries=[]
    labels=[]
    with open(queriesFile) as f:
        queries=f.readlines()
        # lines = f.readlines()
        # for line in lines:
        #     query, label = line.split(',') 
        #     queries.append(query)
        #     labels.append(label)
    # print(queries)
    tags = hasOnlyLocationTags(queries)

    stop_words = set(stopwords.words('english')) 
    for i, query in enumerate(queries):
        queries[i] = " ".join([word for word in word_tokenize(query) if not word in stop_words])
    # print(queries)

    nonGeoIndices = [i for i,el in enumerate(tags) if el!=0]
    tagsOthers = getCategoryPredictions([queries[i] for i in nonGeoIndices], [tags[i] for i in nonGeoIndices])
    for i in range(len(tagsOthers)):
        tags[nonGeoIndices[i]] = tagsOthers[i]


    
    for i in range(len(tags)):
        if i in nonGeoIndices:
            print(f'{DB(tags[i]).name}: {queries[i]}')
    print("\n\n From NER")
    for i in range(len(tags)):
        if i not in nonGeoIndices:
            print(f'{DB(tags[i]).name}: {queries[i]}')

main()
