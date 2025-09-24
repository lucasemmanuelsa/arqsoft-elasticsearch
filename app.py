import os
import time
import re
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from searchs.more_like_this_search import more_like_this_search
from searchs.fuzzy_search import fuzzy_search
from searchs.buscasimples import search_articles
from constants import STOPWORDS
from utils.helper import starting_connection

app = FastAPI()

class SearchRequest(BaseModel):
    searchElement: str

@app.post("/busca-more-like-this")
def more_like_this_endpoint(query: SearchRequest):
    logs_dir = "more-like-this-search"
    safe_query = re.sub(r'[^a-zA-Z0-9_\-]', '_', query.searchElement.strip())[:100]
    query_dir = os.path.join(logs_dir, safe_query)
    os.makedirs(query_dir, exist_ok=True)

    start_time = time.time()
    search_results = more_like_this_search(query.searchElement, STOPWORDS, 5)
    end_time = time.time()
    response_time = end_time - start_time
    print(f"Busca concluída em {response_time:.2f} segundos.")

    for i , result in enumerate(search_results, start = 1):
        file_name = f"Artigo{i}.txt"
        full_file_path = os.path.join(query_dir, file_name)

        with open(full_file_path, "w", encoding="utf-8") as f:
            f.write(result)
            
    return search_results


@app.post("/busca-fuzzy")
def fuzzy_endpoint(query: SearchRequest):
    logs_dir = "fuzzy-search"
    safe_query = re.sub(r'[^a-zA-Z0-9_\-]', '_', query.searchElement.strip())[:100]
    query_dir = os.path.join(logs_dir, safe_query)
    os.makedirs(query_dir, exist_ok=True)

    start_time = time.time()
    search_results = fuzzy_search(query.searchElement, 5)
    end_time = time.time()
    response_time = end_time - start_time
    print(f"Busca concluída em {response_time:.2f} segundos.")

    for i , result in enumerate(search_results, start = 1):
        file_name = f"Artigo{i}.txt"
        full_file_path = os.path.join(query_dir, file_name)

        with open(full_file_path, "w", encoding="utf-8") as f:
            f.write(result)
            
    return search_results

@app.post("/busca-simples")
def busca_simples_endpoint(query: SearchRequest):
    logs_dir = "simple-search"
    safe_query = re.sub(r'[^a-zA-Z0-9_\-]', '_', query.searchElement.strip())[:100]
    query_dir = os.path.join(logs_dir, safe_query)
    os.makedirs(query_dir, exist_ok=True)

    start_time = time.time()
    search_results = search_articles(query.searchElement, 5)
    end_time = time.time()
    response_time = end_time - start_time
    print(f"Busca concluída em {response_time:.2f} segundos.")

    for i , result in enumerate(search_results, start = 1):
        file_name = f"Artigo{i}.txt"
        full_file_path = os.path.join(query_dir, file_name)

        with open(full_file_path, "w", encoding="utf-8") as f:
            f.write(result)

    return search_results

@app.post("/busca-postgres")
def busca_postgres_endpoint(query: SearchRequest):
    conn, cur = starting_connection()

    logs_dir = "postgres-search"
    os.makedirs(logs_dir, exist_ok=True)
    safe_query = re.sub(r'[^a-zA-Z0-9_\-]', '_', query.searchElement.strip())[:100]
    query_dir = os.path.join(logs_dir, safe_query)
    os.makedirs(query_dir, exist_ok=True)

    start_time = time.time()
    cur.execute("""
        SELECT title, text 
        FROM artigos 
        WHERE tsv @@ plainto_tsquery('portuguese', %s) 
        ORDER BY ts_rank(tsv, plainto_tsquery('portuguese', %s)) DESC 
        LIMIT 5;
    """, (query.searchElement, query.searchElement))
    rows = cur.fetchall()
    search_results = [f"Title: {row[0]}\n\n{row[1]}" for row in rows]
    end_time = time.time()
    response_time = end_time - start_time
    print(f"Busca concluída em {response_time:.2f} segundos.")

    for i , result in enumerate(search_results, start = 1):
        file_name = f"Artigo{i}.txt"
        full_file_path = os.path.join(query_dir, file_name)

        with open(full_file_path, "w", encoding="utf-8") as f:
            f.write(result)

    cur.close()
    conn.close()
    
    return search_results

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
