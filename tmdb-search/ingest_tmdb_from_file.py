import requests
import json
import os

indexName = "tmdb"
mappingFolder = "./mapping"
headers = {"Content-Type": "application/json", "Accept": "application/json"}


def extract():
    with open('./tmdb.json') as f:
        return json.loads(f.read())


def reindex(settings, movieDict=None):
    if movieDict is None:
        movieDict = {}
    requests.delete(f"http://localhost:9200/{indexName}")
    data = json.dumps(settings, indent=4, sort_keys=True)
    print(f"settings:\n{data}")
    resp = requests.put(
        f"http://localhost:9200/{indexName}",
        headers=headers,
        data=data
    )

    print(f"Response for creating the index with the settings and mappings. {resp.text}")

    bulkMovies = ""
    for mid, movie in movieDict.items():
        addCmd = {"index": {"_index": indexName,
                            "_type": "_doc",
                            "_id": movie["id"]}}
        bulkMovies += json.dumps(addCmd) + "\n" + json.dumps(movie) + "\n"

    print("Start ingesting data......")
    resp = requests.post("http://localhost:9200/_bulk", headers={"content-type": "application/json"}, data=bulkMovies)
    print(resp.content)


def select_mapping():
    print("\r\n>> Please select the mapping file. Choose 0 for empty mapping\r\n")
    mappingList = os.listdir(mappingFolder)
    print("[0] empty mapping. It will use dynamic mapping with default settings")
    for idx, mappingItem in enumerate(mappingList):
        print(f"[{idx + 1}] {mappingItem}")
    userInput = input()
    try:
        selectIndex = int(userInput)
    except ValueError:
        selectIndex = -1

    if selectIndex == -1 or selectIndex > len(mappingList) + 1:
        print('\033[31mPlease provide a valid integer \033[0m')
        msg = f"from 0 to {len(mappingList)}."
        print(msg)
        exit()
    if selectIndex == 0:
        print("return empty")
        return {}
    mappingName = mappingList[selectIndex - 1]
    fileName = f"{mappingFolder}/{mappingName}"
    with open(fileName) as f:
        mapping = json.loads(f.read())
    return mapping


def main():
    movieDict = extract()
    mapping = select_mapping()
    reindex(settings=mapping, movieDict=movieDict)
    print("Done for ingesting TMDB data into Elasticsearch")


if __name__ == "__main__":
    main()
