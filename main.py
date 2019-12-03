from flask import Flask, request
from flask_restful import Resource, Api
import json
from flask_jsonpify import jsonpify
from methods import *

app = Flask(__name__)
api = Api(app)

class getWordsSuggestions(Resource):
    def get(self, word, size=10):
        words = getWordSuggestions(word, int(size))
        return jsonpify(words)
    
api.add_resource(getWordsSuggestions, '/words/<word>/<size>')

if __name__ == '__main__':
    print("Service runs on port: 6688")
    app.run(port='6688')