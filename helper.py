from similarity import *
from models import *
import time
import requests
import json

def constructElasticSearch(word):
    with open('config.json') as configFile:
        config = json.load(configFile)
    elasticsearchConfig = config["elasticsearch"]
    username = elasticsearchConfig["username"]
    secret = elasticsearchConfig["secret"]
    preurl = elasticsearchConfig["url"]
    indexName = elasticsearchConfig["index_name"]
    url = preurl + "/" + indexName + "/_search"
    return [url,username,secret]

def getWordsFromES(word="cancer", size=100):
    components = constructElasticSearch(word)
    param = {
        "size" : size,
        "q" : word
    }
    response = requests.get(param[0], params=param, auth=(components[1], components[2]))
    content = response.content
    res = json.loads(content)
    docs = res["hits"]["hits"]
    absTitleStr = []
    for item in docs:
        title = item["_source"]["title"]
        abstract = item["_source"]["abstract"]
        absTitleStr.append(title.strip())
        absTitleStr.append(abstract.strip())
    wordStr = ' '.join(absTitleStr)
    words = wordStr.split(' ')
    return words