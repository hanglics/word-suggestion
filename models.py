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
ESConfig = config["ES"]
waitressConfig = config["Waitress"]
print("Config File Loaded.")
print("--------------------------------------------------")

class Index():
    """
    # An index of the documents used (retrieved from elastic search index). 
    # calling createDocuments() to get the terms and scores
    # word: the input word from user to get alternatives
    # pool: specifies how many documents to be retrieved from the elastic search index
    """
    def __init__(self, word, pool):
        # Get all configurations from the config file for elastic search index
        self.username = ESConfig["username"]
        self.secret = ESConfig["secret"]
        self.preurl = ESConfig["url"]
        self.indexName = ESConfig["index_name"]
        # Avoid pool to be 0 which retrieves none documents from the ES index
        # If pool is 0, set pool to be the default pool size
        # If pool is larger than the max pool size specified in the configuration
        # Set pool size to be the max pool size
        if pool is 0:
            self.pool = ESConfig["default_pool"]
        elif pool > ESConfig["max_pool"]:
            self.pool = ESConfig["max_pool"]
        else:
            self.pool = pool
        # Construct the elastic search index url
        url = self.preurl + "/" + self.indexName + "/_search"
        # Construct the params for the url
        param = {
            "size" : self.pool,
            "q" : word
        }
        # Make the request and get response from the ES index
        # The response is documents retrieved from ES index
        response = requests.get(url, params=param, auth=(self.username, self.secret))
        res = json.loads(response.content)
        self.res = res
        self.docs = []
        # Assemble the retrieved documents in desired format
        self.createDocuments()
        query = []
        # Get the count for how many relevant documents in total
        self.D = self.getDocumentCount(query)
        # Construct the empty total result list, the length is the length of docs
        self.wordsRanking = [{} for item in self.docs]
    
    """
    # query is a list of word(s) that passed into the ES index to get the count
    # query length can be 1 or 2
    # if query length is 1, then get number of relevant documents from ES index based on this single word
    # if query length is 2, then get the intersection number of relevant documents from ES index based on the two words
    """
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
        # result["count"] can be 0
        return results["count"]
    
    """ 
    # process the documents retrieved from the ES index
    # the original documents retrieved contain a lot redundent information
    # we only need title and abstract
    # concat title and abstract together then split into words
    # assign a list of candicate words as finalRes to self.docs
    """
    def createDocuments(self):
        res = self.res
        docs = res["hits"]["hits"]
        absTitleStr = []
        documents = []
        translator = str.maketrans('','',string.punctuation)
        for item in docs:
            title = item["_source"]["title"]
            abstract = item["_source"]["abstract"]
            # convert all words into lowercase
            procTitle = title.translate(translator).lower()
            procAbs = abstract.translate(translator).lower()
            absTitleStr.append(procTitle.strip())
            absTitleStr.append(procAbs.strip())
            wordStr = " ".join(absTitleStr)
            words = wordStr.split(" ")
            # filter empty words
            result = list(filter(None, words))
            # filter stopwords
            filteredRes = [term for term in result if term not in stopwords.words('english')]
            documents += filteredRes
        seen = set()
        finalRes = []
        # filter duplicate words
        for item in documents:
            if item not in seen:
                seen.add(item)
                finalRes.append(item)
        self.docs = finalRes

    """
    # calculates the similarity of two words in the collection
    # s1 is the input word from user to get the alternative words
    # s2 is the word from self.docs to compare with s1
    # index is the number passed in to allocate position in self.wordsRanking
    """
    def pmiSimilarity(self, s1, s2, index):
        D = self.D
        # to get f1 f2 and f12, three requests to the ES index are made
        # which heavily depend on the internet speed
        # implemented multithreading to speed up
        f1 = self.getDocumentCount([s1])
        f2 = self.getDocumentCount([s2])
        f12 = self.getDocumentCount([s1, s2])
        score = calculateSimilarity(D, f1, f2, f12)
        self.wordsRanking[index] = {
            "term" : s2,
            "score" : score
        }

    """
    # calculate the pmi similarity score for input word and words in self.docs
    # word is the input word
    # size is the return size which means how many terms to be returned
    # pool is the number of documents to be retrieved from the ES index
    """
    def getESWordsRanking(self, word, size, pool):
        threads = []
        # use multithreading to speed up the process
        for i in range(len(self.docs)):
            process = Thread(target=self.pmiSimilarity, args=[word, self.docs[i], i])
            process.start()
            threads.append(process)
        for process in threads:
            process.join()
        # sort the items in descending order by scores
        totalResult = sorted(self.wordsRanking, key = lambda i : i["score"], reverse = True)
        returned = []
        count = 0
        # similar to pool, check the size constraints
        if size is 0:
            size = ESConfig["default_retSize"]
        elif size > ESConfig["max_retSize"]:
            size = ESConfig["max_retSize"]
        for item in totalResult:
            if count < size:
                count += 1
                returned.append(item)
        return returned
    
"""
# A CUI 2 Vec module that adopt CUI and distance measure to get the similar words as alternatives
# word is the input word from user
# size is the returned number of words
# we are using a pre-computed cui distance bin file with compressed size
# the bin file contains 10 cuis with minimum distance for each cui
# so the max return size is 10 in this case
# if larger return size is required, need to regenerate the bin file
"""
class CUI2Vec():
    def __init__(self, word):
        wordCUI = ""
        data = word
        response = requests.post('http://ielab-metamap.uqcloud.net/mm/candidates', data=data)
        content = json.loads(response.content)
        # use try block to avoid the exceptions when there is no CandidateCUI exists for a word
        try:
            wordCUI = content[0]["CandidateCUI"]
        except:
            self.wordCUI = ""
        if wordCUI is not "":
            self.wordCUI = wordCUI
    
    """
    # from a word's cui, find the 10 relevant cuis in the pre-loaded matrix
    # /data/cui2vec_precomputed.bin
    # size is the returned size
    """
    def findAlternativeTerms(self, size):
        alternatives = ""
        res = []
        # the size should be > 0 and < max size
        if size is 0:
            self.size = ESConfig["default_retSize"]
        elif size > ESConfig["max_retSize"]:
            self.size = ESConfig["max_retSize"]
        else:
            self.size = size
        wordCUI = self.wordCUI
        # use try block to aviod that the wordCUI is empty
        try:
            intWordCUI = cui2int(wordCUI)
        except:
            intWordCUI = 0
        # use try block to avoid that there is no alternatives exist for this input word in matrix
        try:
            alternatives = matrix[intWordCUI]
        except:
            alternatives = ""
        if alternatives is not "":
            res = convertCUI2Term(alternatives, self.size)
        return res
"""
# from a list of cuis, convert the cuis to terms by looking in the pre-loaded dict
# /data/cuis.csv
# size is the returned size
"""
def convertCUI2Term(alternatives, size):
    infos = []
    for key in alternatives.keys():
        term = ""
        # use try block to avoid key does not exist
        try:
            term = cui2titleDict[str(key)]
        except:
            term = ""
        if term is not "":
            info = {
                "score" : alternatives[key],
                "term" : term
            }
            infos.append(info)
    returned = []
    count = 0
    # sort the list by scores in descending order
    rankedInfo = sorted(infos, key = lambda i : i["score"], reverse = True)
    for item in rankedInfo:
        if count < size:
            count += 1
            returned.append(item)
    return returned

def minmax(list1, list2, size):
    maximumScoreTermL1 = max(list1, key=lambda x:x['score'])['score']
    minimumScoreTermL1 = min(list1, key=lambda x:x['score'])['score']
    maximumScoreTermL2 = max(list2, key=lambda x:x['score'])['score']
    minimumScoreTermL2 = min(list2, key=lambda x:x['score'])['score']
    for term1 in list1:
        term1['score'] = (term1['score'] - minimumScoreTermL1) / (maximumScoreTermL1 - minimumScoreTermL1)
    for term2 in list2:
        term2['score'] = (term2['score'] - minimumScoreTermL2) / (maximumScoreTermL2 - minimumScoreTermL2)
    unorderedRes = list1 + list2
    finalRes = sorted(unorderedRes, key = lambda i : i['score'], reverse = True)
    for t in finalRes:
        t['score'] = float("{0:.3f}".format(t['score']))
    if size < len(finalRes):
        return finalRes[0:size]
    else:
        return finalRes