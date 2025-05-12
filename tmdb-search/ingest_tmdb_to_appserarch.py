import requests
import json


def extract():
    with open('./tmdb.json') as f:
        return json.loads(f.read())


def index_all(movieDict=None):
    if movieDict is None:
        movieDict = {}
    for mid, movie in movieDict.items():
        index_doc(movie)
        print(mid)


def index_doc(doc):
    content = [doc]
    requests.post(
        "http://localhost:3002/api/as/v1/engines/tmdb/documents",
        headers={"content-type": "application/json", "Authorization": "Bearer private-vmnsw8mvzebbcpfeje5rzhxg"},
        data=json.dumps(content)
    )


def main():
    movieDict = extract()
    index_all(movieDict=movieDict)


if __name__ == "__main__":
    main()
