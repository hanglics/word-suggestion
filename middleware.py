from models import *

"""
# a middleware method to take input from router and return output to frontend
# size is the return size
# word is the user input word
# pool is the number of documents retrieved from ES index
"""
def getWordSuggestions(word, size, pool, merged, sources):
    splitedSource = sources.split(",")
    splitedSource = [x.upper() for x in splitedSource]
    merge = True if merged == "true" else False
    res = {}
    for source in splitedSource:
        if source == "ES":
            collection = Index(word, pool)
            esRes = collection.getESWordsRanking(word, size, pool)
            res[source] = esRes
        elif source == "CUI":
            cui2vec = CUI2Vec(word)
            cuiRes = cui2vec.findAlternativeTerms(size)
            res[source] = cuiRes
    if merge and len(splitedSource) > 1:
        normalizedScoreRes = minmax(res, size)
        return normalizedScoreRes
    else:
        return res

def getSettings():
    default_pool = ESConfig["default_pool"]
    default_retSize = ESConfig["default_retSize"]
    max_retSize = ESConfig["max_retSize"]
    max_pool = ESConfig["max_pool"]
    merged = ESConfig["merged"]
    sources = ESConfig["sources"]
    res = {
        "default_pool": default_pool,
        "default_retSize": default_retSize,
        "max_retSize": max_retSize,
        "max_pool": max_pool,
        "merged": merged,
        "sources": sources
    }

    return res