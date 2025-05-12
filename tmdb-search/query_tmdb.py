import requests
import json
import os
import sys
from typing import Dict, Any

INDEX_NAME = "tmdb"
QUERY_FOLDER = "./query"
ES_URL = "http://localhost:9200"
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

COLORS = {
    'RED': '\033[1;31;40m',
    'GREEN': '\033[0;32;40m',
    'RESET': '\033[0m'
}


def search(query: Dict[str, Any], print_highlight: bool) -> None:
    url = f"{ES_URL}/{INDEX_NAME}/_search"

    try:
        resp = requests.get(url, headers=HEADERS, data=json.dumps(query))
        resp.raise_for_status()
        hits = resp.json()["hits"]

        print("\n######################## Results ################################\n")
        print("No\tScore\t\t\tTitle")

        for idx, hit in enumerate(hits["hits"], 1):
            print(f"{idx}\t{hit['_score']}\t\t\t{hit['_source']['title']}")
            print("-" * 63)

            if not print_highlight:
                continue

            highlight = hit.get("highlight", {})
            for field in ["title", "overview"]:
                if field in highlight:
                    highlights = highlight[field]
                    colored_text = ";".join(highlights).replace("<em>", COLORS['RED']).replace("</em>", COLORS['RESET'])
                    print(f"{field}: {COLORS['GREEN']}{len(highlights)} hit(s){COLORS['RESET']}\n{colored_text}\n--")

    except requests.RequestException as e:
        print(f"Search Failed: {e}")
        sys.exit(1)


def select_query() -> Dict[str, Any]:
    print("\n>> Please select the query file.\n")

    try:
        query_files = os.listdir(QUERY_FOLDER)
        for idx, query_file in enumerate(query_files):
            print(f"[{idx}] {query_file}")

        select_index = int(input())
        if not 0 <= select_index < len(query_files):
            raise ValueError()

        file_path = os.path.join(QUERY_FOLDER, query_files[select_index])
        with open(file_path) as f:
            return json.load(f)

    except (ValueError, IndexError):
        print(f'{COLORS["RED"]}Please provide a valid integer from 0 to {len(query_files) - 1}.{COLORS["RESET"]}')
        sys.exit(1)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f'{COLORS["RED"]}Error loading query file: {e}{COLORS["RESET"]}')
        sys.exit(1)


def main() -> None:
    highlight = any(arg in ["h", "hl", "highlight"] for arg in sys.argv)
    query = select_query()
    search(query, highlight)


if __name__ == "__main__":
    main()
