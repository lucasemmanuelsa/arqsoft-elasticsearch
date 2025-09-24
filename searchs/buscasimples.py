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

    # --- Salvar resultados em arquivos ---
    logs_dir = "elasticsearch-simple-search"
    os.makedirs(logs_dir, exist_ok=True)
    safe_query = re.sub(r'[^a-zA-Z0-9_\-]', '_', query.strip())[:100]
    query_dir = os.path.join(logs_dir, safe_query)
    os.makedirs(query_dir, exist_ok=True)
    # --- Fim salvar resultados ---

    # Exibe os artigos encontrados mas cortando o texto para os primeiros 300 caracteres
    for idx, hit in enumerate(response["hits"]["hits"], 1):
        title = hit["_source"]["title"]
        text = hit["_source"]["text"]
        print("Título:", title)
        print("Trecho:", text[:300], "...\n")
        # Salva cada artigo em um arquivo
        artigo_str = f"Título: {title}\nTrecho: {text}...\n"
        artigo_path = os.path.join(query_dir, f"artigo{idx}.txt")
        with open(artigo_path, "w", encoding="utf-8") as f:
            f.write(artigo_str)