from flask import Flask, request
from flask_restful import Resource, Api
import json
from flask.ext.jsonpify import jsonpify
from helper import *

app = Flask(__name__)
api = Api(app)

class getWordsSuggestions(Resource):
    def get(self, word, size):
        words = {
            "wordsFromES" : getWordsFromES(words, size)
        }
        return jsonpify(words)
    
api.add_resource(getWordsSuggestions, '/words')

if __name__ == '__main':
    app.run(port='6688')