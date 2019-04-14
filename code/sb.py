from nltk.parse import CoreNLPParser
from nltk.corpus import wordnet as wn

ner_tagger = CoreNLPParser(url='http://localhost:9000', tagtype='ner')

queriesFile = 'queries.txt'
with open(queriesFile) as f:
    queries = f.readlines()

def nerTagger(sentence):
    return list(ner_tagger.tag((sentence.split())))

def hasOnlyLocation(sentence):
    acceptedTags=['O', 'CITY', 'COUNTRY', 'LOCATION']
    for tagged in nerTagger(sentence):
        if(tagged[1] not in acceptedTags):
            return False
    return True


category=['geography', 'movie', 'music']
list_sentences=['Which pop artist sings CrazyInLove?', 
                'Which is the deepest ocean?']
a='Did Neeson star in Schindler’sList'#.lower()
scores=[]
for i in category:
    score = 0
    cat_synset = wn.synsets(i)[0]
    for word in a.split():
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

for i in range(len(category)):
    print(f'{category[i]}: {scores[i]}', end="\t")
