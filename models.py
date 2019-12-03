import requests
import json
import string
from similarity import *
from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')

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

    def similarity(self, s1, s2):
        """
        calculates the similarity of two words in the collection
        """
        D = self.D
        f1 = self.getDocumentCount([s1])
        f2 = self.getDocumentCount([s2])
        f12 = self.getDocumentCount([s1, s2])
        return calculateSimilarity(D, f1, f2, f12)