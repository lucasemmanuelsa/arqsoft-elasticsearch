from elasticsearch import Elasticsearch

INDEX_NAME = "ptwiki" 

def search_articles(query, size=10):
    es = Elasticsearch("http://localhost:9200")
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
    # Exibe os artigos encontrados mas cortando o texto para os primeiros 300 caracteres
    for hit in response["hits"]["hits"]:
        print("Título:", hit["_source"]["title"])
        print("Trecho:", hit["_source"]["text"][:300], "...\n")

if __name__ == "__main__":
    search_articles("filósofos", size=5)