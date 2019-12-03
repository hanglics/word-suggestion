from models import *

def getWordSuggestions(word, size):
    collection = Index(word)
    wordsRanking = []
    for term in collection.docs:
        similarityScore = collection.similarity(word, term)
        wordInfo = {
            "term" : term,
            "score" : similarityScore
        }
        wordsRanking.append(wordInfo)
    totalResult = sorted(wordsRanking, key = lambda i : i["score"], reverse = True)
    returned = []
    count = 0
    for item in totalResult:
        if count < size:
            count += 1
            returned.append(item)
    return {
        "ES" : returned
    }        