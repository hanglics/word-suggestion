import requests
import json
import string
from pmisimilarity import *
from cui_methods import *
from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')

# Construct the CUI matrix and store as a global variable
cuiDistanceFile = "data/cui2vec_precomputed.bin"
matrix = readCuiDistance(cuiDistanceFile)
print("CUI Distance File Loaded.")

# Construct the CUI to Title dict and store as a global variable
titleFile = "data/cuis.csv"
cui2titleDict = readCuiTitle(titleFile)
print("CUI To Term Dictionary Loaded.")

class Index():
    """An index of the documents used. Stores information about documents and terms"""
    def __init__(self, word):
        with open('config.json') as configFile:
            config = json.load(configFile)
        elasticsearchConfig = config["elasticsearch"]
        self.username = elasticsearchConfig["username"]
        self.secret = elasticsearchConfig["secret"]
        self.preurl = elasticsearchConfig["url"]
        self.indexName = elasticsearchConfig["index_name"]
        self.size = elasticsearchConfig["size"]
        url = self.preurl + "/" + self.indexName + "/_search"
        param = {
            "size" : self.size,
            "q" : word
        }
        response = requests.get(url, params=param, auth=(self.username, self.secret))
        res = json.loads(response.content)
        self.res = res
        self.docs = []
        self.createDocuments()
        query = []
        self.D = self.getDocumentCount(query)
        
    def getDocumentCount(self, query):
        url = self.preurl + "/" + self.indexName + "/_count"
        if len(query) is 1:
            response = requests.get(url, params={"q" : query}, auth=(self.username, self.secret))
        elif len(query) is 2:
            param = {
                "q" : "(" + str(query[0]) + ")AND(" + str(query[1]) + ")"
            }
            response = requests.get(url, params=param, auth=(self.username, self.secret))
        else:
            response = requests.get(url, auth=(self.username, self.secret))
        results = json.loads(response.content)
        return results["count"]
        
    def createDocuments(self):
        res = self.res
        docs = res["hits"]["hits"]
        absTitleStr = []
        documents = []
        translator = str.maketrans('','',string.punctuation)
        for item in docs:
            title = item["_source"]["title"]
            abstract = item["_source"]["abstract"]
            procTitle = title.translate(translator).lower()
            procAbs = abstract.translate(translator).lower()
            absTitleStr.append(procTitle.strip())
            absTitleStr.append(procAbs.strip())
            wordStr = " ".join(absTitleStr)
            words = wordStr.split(" ")
            result = list(filter(None, words))
            filteredRes = [term for term in result if term not in stopwords.words('english')]
            documents += filteredRes
        seen = set()
        finalRes = []
        for item in documents:
            if item not in seen:
                seen.add(item)
                finalRes.append(item)
        self.docs = finalRes

    def pmiSimilarity(self, s1, s2):
        """
        calculates the similarity of two words in the collection
        """
        D = self.D
        f1 = self.getDocumentCount([s1])
        f2 = self.getDocumentCount([s2])
        f12 = self.getDocumentCount([s1, s2])
        return calculateSimilarity(D, f1, f2, f12)

def getESWordsRanking(word, size):
    collection = Index(word)
    wordsRanking = []
    for term in collection.docs:
        similarityScore = collection.pmiSimilarity(word, term)
        wordInfo = {
            "term" : term,
            "score" : float("{0:.3f}".format(similarityScore))
        }
        wordsRanking.append(wordInfo)
    totalResult = sorted(wordsRanking, key = lambda i : i["score"], reverse = True)
    returned = []
    count = 0
    for item in totalResult:
        if count < size:
            count += 1
            returned.append(item)
    return returned
    
class CUI2Vec():
    
    def __init__(self, word):
        data = word
        response = requests.post('http://ielab-metamap.uqcloud.net/mm/candidates', data=data)
        content = json.loads(response.content)
        wordCUI = content[0]["CandidateCUI"]
        self.wordCUI = wordCUI
        
    def findAlternativeTerms(self, size):
        wordCUI = self.wordCUI
        intWordCUI = cui2int(wordCUI)
        alternatives = matrix[intWordCUI]
        res = convertCUI2Term(alternatives, size)
        return res
        
def convertCUI2Term(alternatives, size):
    infos = []
    for key in alternatives.keys():
        term = ""
        try:
            term = cui2titleDict[str(key)]
        except:
            term = ""
        if term is not "":
            info = {
                "score" : alternatives[key],
                "cui" : key,
                "term" : term
            }
            infos.append(info)
    returned = []
    count = 0
    rankedInfo = sorted(infos, key = lambda i : i["score"], reverse = True)
    for item in rankedInfo:
        if count < size:
            count += 1
            returned.append(item)
    return returned