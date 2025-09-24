from constants import ES_HOST, INDEX_NAME, STOPWORDS
from elasticsearch import Elasticsearch

def more_like_this_search(user_query, stopwords, size=10):
    es = Elasticsearch(ES_HOST)

    full_query = {
        "size": size,  # define aqui
        "query": {
            "more_like_this": {
                "fields": ["title", "text"],
                "like": user_query,
                "stop_words": stopwords,
                "min_term_freq": 1,
                "max_query_terms": 12,
                "min_word_length": 2
            }
        }
    }

    res = es.search(index=INDEX_NAME, body=full_query)
    results = []

    for hit in res['hits']['hits']:
        results.append(f"\nTítulo:{hit['_source']['title']}\nTrecho:{hit['_source']['text'][:300]}\nRelevância:{hit['_score']:.2f}\n")
    
    return results

