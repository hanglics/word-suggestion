from models import *

def getWordSuggestions(word, size, pool):
    esRes = getESWordsRanking(word, size, pool)
    cui2vec = CUI2Vec(word)
    res = cui2vec.findAlternativeTerms(size)
    return {
        "ES" : esRes,
        "CUI" : res
    }