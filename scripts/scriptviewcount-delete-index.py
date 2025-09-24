import json
from elasticsearch import Elasticsearch, helpers

ES_HOST = "http://localhost:9200"
INDEX_NAME = "ptwiki"
def create_es_client():
    """Cria cliente Elasticsearch sem SSL"""
    return Elasticsearch(
        ES_HOST,
        verify_certs=False,  # Não verificar certificados
        ssl_show_warn=False
    )

es = create_es_client()

print(es.count(index=INDEX_NAME))
#es.indices.delete(index=INDEX_NAME, ignore=[400, 404])