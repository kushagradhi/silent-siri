from nltk.parse import CoreNLPParser
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
from DB_interface import DBInterface
from Utils import CNLP, DB



cnlp=CNLP()

# Returns - NER tagged sentence
def nerTagger(sentence):
    return list(cnlp.getNERTags((sentence.split())))

"""Returns  1. 0  - If certain that belongs to Geography
            2. -2 - If certain that belongs to Music/Movie
            3. -3 - If uncertain about the category"""
def getNERPrediction(sentences):
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

""" Returns - Category to which each sentence belongs"""
def getCategoryPredictions(sentences, tagIndicator):
    # Subcategories for each category Geography, Movie, Music
    category = [['place', 'geographic', 'mountain', 'ocean', 'hill'],
                ['cinema', 'direct', 'oscar', 'movie'],
                ['pop', 'music', 'sing', 'album']]
    tags=[]
    # Loop over every sentence in the input file
    for index, sentence in enumerate(sentences):
        scores=[]
        # Calculating Score for each Category
        for cat_i in category:
            # Calculating Score for each Sub Category
            for i in cat_i:
                score = 0
                cat_synset = wn.synsets(i)[0]   # Synset of subcategory
                # Computing word sysnset for each word in the sense
                for word in sentence.split():
                    word_synsets = wn.synsets(word)
                    if(len(word_synsets)==0):
                        continue
                    word_synset = wn.synsets(word)[0]
                    if(word_synset.path_similarity(cat_synset) != None):
                        score += word_synset.path_similarity(cat_synset) 
            scores.append(score/(len(cat_i)))   # Taking average over all subcategories
        tagPrediction = scores.index(max(scores))   # Selecting Category with highest score
        if(tagIndicator[index]==-2):
            if(scores[1]>scores[2]):
                tagPrediction=1
            else:
                tagPrediction=2
        tags.append(tagPrediction)
    return tags

def getCategory(queries):
    tags = getNERPrediction(queries)    # Getting all catefgory prediction from NER

    # Removing stopwords
    stop_words = set(stopwords.words('english')) 
    for i, query in enumerate(queries):
        queries[i] = " ".join([word for word in word_tokenize(query) if not word in stop_words])

    # Computing category for each sentence
    nonGeoIndices = [i for i,el in enumerate(tags) if el!=0]
    tagsOthers = getCategoryPredictions([queries[i] for i in nonGeoIndices], [tags[i] for i in nonGeoIndices])
    for i in range(len(tagsOthers)):
        tags[nonGeoIndices[i]] = tagsOthers[i]
    
    return tags

def main():
    queries=[]
    sentences = []
    # Reading the input file
    with open(queriesFile) as f:
        queries=f.readlines()
        sentences = [sent.strip() for sent in queries]

    tags = getCategory(queries)

    # Printing the result to console
    for i in range(len(tags)):
        print ("Sentence: ",sentences[i])
        print ("Category: ",DB(tags[i]).name,"\n")
# main()
