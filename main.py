from flask import Flask, request
from flask_restful import Resource, Api
import json
from flask_jsonpify import jsonpify
from methods import *

app = Flask(__name__)
api = Api(app)
app.config["DEBUG"] = True

class getWordsSuggestions(Resource):
    def get(self):
        if 'term' in request.args and 'size' in request.args:
            word = request.args["term"]
            size = request.args["size"]
            res = getWordSuggestions(word, int(size))
            return jsonpify(res)
        else:
            return jsonpify([{"ERROR" : "No Term Or Size Provided."}])
    
api.add_resource(getWordsSuggestions, '/search')

if __name__ == '__main__':
    print("Service runs on port: 6688")
    app.run(port='6688')