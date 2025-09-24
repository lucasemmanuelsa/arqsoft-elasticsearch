import os
import re
import time
from elasticsearch import Elasticsearch
from constants import INDEX_NAME, ES_HOST

def search_articles(query, size=5):
    es = Elasticsearch(ES_HOST)
    response = es.search(
        index=INDEX_NAME,
        body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title", "text"]
                }
            }
        },
        size=size
    )

    results = []
    for hit in response["hits"]["hits"]:
        results.append(f"\nTítulo:{hit['_source']['title']}\nTrecho:{hit['_source']['text']}\nRelevância:{hit['_score']:.2f}\n")

    return results
