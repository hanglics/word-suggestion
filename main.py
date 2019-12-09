from flask import Flask, request
from flask_restful import Resource, Api
import json
from flask_jsonpify import jsonpify
from middleware import *
from waitress import serve
from models import waitressConfig, ESConfig
import sys

app = Flask(__name__)
api = Api(app)

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
            res = getWordSuggestions(word, size=ESConfig["default_retSize"], pool=ESConfig["default_pool"])
            return jsonpify(res)
            
# example url -> /search?retSize=5&pool=5&term=cancer
api.add_resource(getWordsSuggestions, '/search')

if __name__ == '__main__':
    arguments = sys.argv
    if len(arguments) == 1:
        # Development server debug mode
        app.config["DEBUG"] = True
        print("App run in dev mode on port: ", waitressConfig["port"])
        app.run(port=waitressConfig["port"])
    elif len(arguments) == 2 and (arguments[1] == "--dev" or arguments[1] == "-d"):
        # Development server debug mode
        app.config["DEBUG"] = True
        print("App run in dev mode on port: ", waitressConfig["port"])
        app.run(port=waitressConfig["port"])
    elif len(arguments) == 2 and (arguments[1] == "--prod" or arguments[1] == "-p"):
        # Construct the production server using waitress
        # can be configured through changing in config.json
        serve (
            app, 
            host=waitressConfig["host"], 
            port=waitressConfig["port"],
            ipv4=waitressConfig["ipv4"], 
            ipv6=waitressConfig["ipv6"], 
            threads=waitressConfig["threads"],
            url_scheme=waitressConfig["url_scheme"]
        )
    else:
        print("Wrong arguments, please check your input.")

