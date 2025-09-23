from constants import ES_HOST, INDEX_NAME
from elasticsearch import Elasticsearch

def fuzzy_search(user_query, size=10):
    es = Elasticsearch(ES_HOST)
    full_query = {
        "size": size,
        "query": {
             "bool": {
                "should": [
                    {"match": {"title": {"query": "texto", "fuzziness": "AUTO"}}},
                    {"match": {"text": {"query": "texto", "fuzziness": "AUTO", "boost": 2}}}
                ]
                }
        }
    }

    res = es.search(index=INDEX_NAME, body=full_query)
    results = []

    for hit in res['hits']['hits']:
        results.append(f"\nTítulo:{hit['_source']['title']}\nTrecho:{hit['_source']['text'][:300]}\nRelevância:{hit['_score']:.2f}\n")
    
    return results

if __name__ == "__main__":
    user_query = input("Digite a sua consulta: ")
    fuzzy_search(user_query, 10)
