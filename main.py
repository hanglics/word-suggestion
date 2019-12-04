from flask import Flask, request
from flask_restful import Resource, Api
import json
from flask_jsonpify import jsonpify
from middleware import *

app = Flask(__name__)
api = Api(app)
app.config["DEBUG"] = True

class getWordsSuggestions(Resource):
    
    def get(self):
        if 'term' in request.args and 'retSize' in request.args and 'pool' in request.args:
            word = request.args["term"]
            size = request.args["retSize"]
            pool = request.args['pool']
            res = getWordSuggestions(word, int(size), int(pool))
            return jsonpify(res)
        elif 'term' not in request.args:
            res = []
            return res
        else:
            word = request.args["term"]
            res = getWordSuggestions(word, size=0, pool=0)
            return jsonpify(res)
            
# /search?retSize=5&pool=5&term=cancer
api.add_resource(getWordsSuggestions, '/search')

if __name__ == '__main__':
    print("Service runs on port: 6688")
    app.run(port='6688')