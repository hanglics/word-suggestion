from models import *

"""
# a middleware method to take input from router and return output to frontend
# size is the return size
# word is the user input word
# pool is the number of documents retrieved from ES index
"""
def getWordSuggestions(word, size, pool):
    collection = Index(word, pool)
    esRes = collection.getESWordsRanking(word, size, pool)
    cui2vec = CUI2Vec(word)
    res = cui2vec.findAlternativeTerms(size)
    return {
        "ES" : esRes,
        "CUI" : res
    }