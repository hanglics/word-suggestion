# Word Suggestion Module for Search Refiner

Give a word, provide its alternatives based on PMI score (Elastic Search Index) and Cosine Similarity (CUI2Vec)

Wrapped in a waitress server as a RESTful API to provided alternative terms and their scores

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
pip3 install waitress flask flask-restful flask_jsonpify requests nltk
```

### Development

To run in development mode

Make sure to add a `config.json` file to configure the server and the elastic search index

After setting up the config file, use the following command to run the development server:

```
python3 main.py --dev
```
or
```
python3 main.py -d
```
or
```
python3 main.py
```

The service will be deployed to host and port specified in config

The API can be accessed through:

```
http://localhost:6688/search?retSize=5&pool=5&term=cancer
```

Where `retSize` and `pool` are optional params, `retSize` specifies the how many alternative terms to be returned from the search, `pool` specifies the number of relevant documents used in elastic search index for finding the alternative terms. (`retSize` default is 5 and the same as `pool`)

### Production

For production server, configure the host for waitress server in `config.json` file.
And using waitress server by calling

```
python3 main.py --prod
```
or
```
python3 main.py -p
```

By calling API:

```
http://localhost:6688/search?retSize=5&pool=20&term=cancer
```

The result is in `json` format:

```
{
    "CUI": [
        {
            "cui": 521158,
            "score": 0.226,
            "term": "neoplasm recurrence"
        },
        {
            "cui": 2939419,
            "score": 0.225,
            "term": "secondary malignancies"
        },
        {
            "cui": 445092,
            "score": 0.225,
            "term": "no metastases (tumor staging)"
        },
        {
            "cui": 741899,
            "score": 0.221,
            "term": "poorly differentiated carcinoma"
        },
        {
            "cui": 334277,
            "score": 0.221,
            "term": "metastatic adenocarcinoma"
        }
    ],
    "ES": [
        {
            "score": 0.25,
            "term": "surveys"
        },
        {
            "score": 0.134,
            "term": "medical"
        },
        {
            "score": 0.13,
            "term": "demand"
        },
        {
            "score": 0.118,
            "term": "reeducation"
        },
        {
            "score": 0.115,
            "term": "1958"
        }
    ]
}

```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
