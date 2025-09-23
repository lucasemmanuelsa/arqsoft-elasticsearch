from constants import ES_HOST, INDEX_NAME
from elasticsearch import Elasticsearch
import nltk

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
    for hit in res['hits']['hits']:
        print(f"Score: {hit['_score']:.2f}")
        print(f"Título: {hit['_source']['title']}")
        print(f"Trecho: {hit['_source']['text'][:300]}...\n")

if __name__ == "__main__":
    nltk.download('stopwords')
    stopwords = nltk.corpus.stopwords.words('portuguese')
    user_query = input("Digite a sua consulta: ")
    more_like_this_search(user_query, stopwords, 10)
