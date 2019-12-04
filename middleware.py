from models import *

def getWordSuggestions(word, size):
    esRes = getESWordsRanking(word, size)
    cui2vec = CUI2Vec(word)
    res = cui2vec.findAlternativeTerms(size)
    return {
        "ES" : esRes,
        "CUI" : res
    }