import requests
import json
import string
from pmisimilarity import *
from cui_methods import *
from nltk.corpus import stopwords
from threading import Thread
import nltk
nltk.download('stopwords')

# Construct the CUI matrix and store as a global variable
print("--------------------------------------------------")
print("Loading CUI Distance File...")
cuiDistanceFile = "data/cui2vec_precomputed.bin"
matrix = readCuiDistance(cuiDistanceFile)
print("CUI Distance File Loaded.")

# Construct the CUI to Title dict and store as a global variable
print("--------------------------------------------------")
print("Loading CUI To Term Dictionary...")
titleFile = "data/cuis.csv"
cui2titleDict = readCuiTitle(titleFile)
print("CUI To Term Dictionary Loaded.")

# Load the config file
print("--------------------------------------------------")
print("Loading Config File...")
with open('config.json') as configFile:
    config = json.load(configFile)
print("Config File Loaded.")
print("--------------------------------------------------")

class Index():
    """An index of the documents used. Stores information about documents and terms"""
    def __init__(self, word, pool):
        self.username = config["username"]
        self.secret = config["secret"]
        self.preurl = config["url"]
        self.indexName = config["index_name"]
        if pool is 0:
            self.pool = config["default_pool"]
        else :
            self.pool = pool
        url = self.preurl + "/" + self.indexName + "/_search"
        param = {
            "size" : self.pool,
            "q" : word
        }
        response = requests.get(url, params=param, auth=(self.username, self.secret))
        res = json.loads(response.content)
        self.res = res
        self.docs = []
        self.createDocuments()
        query = []
        self.D = self.getDocumentCount(query)
        self.wordsRanking = [{} for item in self.docs]
        
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

    def pmiSimilarity(self, s1, s2, index):
        """
        calculates the similarity of two words in the collection
        """
        D = self.D
        f1 = self.getDocumentCount([s1])
        f2 = self.getDocumentCount([s2])
        f12 = self.getDocumentCount([s1, s2])
        score = calculateSimilarity(D, f1, f2, f12)
        self.wordsRanking[index] = {
            "term" : s2,
            "score" : float("{0:.3f}".format(score))
        }

    def getESWordsRanking(self, word, size, pool):
        threads = []
        for i in range(len(self.docs)):
            process = Thread(target=self.pmiSimilarity, args=[word, self.docs[i], i])
            process.start()
            threads.append(process)
            
        for process in threads:
            process.join()
        
        totalResult = sorted(self.wordsRanking, key = lambda i : i["score"], reverse = True)
        returned = []
        count = 0
        if size is 0:
            size = config["default_retSize"]
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
        if size is 0:
            self.size = config["default_retSize"]
        else:
            self.size = size
        wordCUI = self.wordCUI
        intWordCUI = cui2int(wordCUI)
        alternatives = matrix[intWordCUI]
        res = convertCUI2Term(alternatives, self.size)
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