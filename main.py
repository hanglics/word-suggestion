from flask import Flask, request
from flask_restful import Resource, Api
from flask_jsonpify import jsonpify
from middleware import *
from waitress import serve
# from flask_cors import CORS
from models import waitressConfig, ESConfig
import sys

app = Flask(__name__)
api = Api(app)
# CORS(app)


class getWordsSuggestions(Resource):
    def get(self):
        word = request.args["term"] if "term" in request.args else ""
        size = request.args["retSize"] if "retSize" in request.args and request.args["retSize"] != "" else ESConfig[
            "default_retSize"]
        pool = request.args["pool"] if "pool" in request.args and request.args["pool"] != "" else ESConfig[
            "default_pool"]
        merged = request.args["merged"] if "merged" in request.args and request.args["merged"] != "" else ESConfig[
            "merged"]
        sources = request.args["sources"] if "sources" in request.args and request.args["sources"] != "" else ESConfig[
            "sources"]

        if word == "":
            res = []
            return res
        else:
            res = getWordSuggestions(word, int(size), int(pool), merged, sources)
            return jsonpify(res)


class getSetting(Resource):
    def get(self):
        res = getSettings()
        return jsonpify(res)


# example url -> /search?retSize=5&pool=5&sources=cui,es&merged=false&term=cancer
api.add_resource(getWordsSuggestions, "/search")
api.add_resource(getSetting, "/settings")

if __name__ == "__main__":
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
        serve(
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
