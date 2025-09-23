import os
import re
import psycopg2
from tqdm import tqdm
import json
import time
from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
    
app = FastAPI()

class SearchRequest(BaseModel):
    searchElement: str

def load_wikipedia(jsonl_path, MAX_LEN_ARTIGOS=None):
    data = []
    print("Carregando e formatando dados...")
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in tqdm(f, desc="Artigos processados"):
            if MAX_LEN_ARTIGOS is not None and len(data) >= MAX_LEN_ARTIGOS:
                break

            obj = json.loads(line)
            title = obj.get("title", "")
            section_titles = obj.get("section_titles", [])
            section_texts = obj.get("section_texts", [])

            # Concatena título e seções sem tokens
            artigo = title + "\n"
            for i, text in enumerate(section_texts):
                subtitle = section_titles[i] if i < len(section_titles) else ""
                if subtitle:
                    artigo += subtitle + "\n"
                artigo += text.strip() + "\n"

            data.append({"title": title, "text": artigo.strip()})

    print(f"Total de artigos: {len(data)}")
    return data
def insert_article(title, text):
    cur.execute("""
    INSERT INTO artigos (title, text) VALUES (%s, %s)
    """, (title, text))
    conn.commit()
def create_table():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS artigos (
            id SERIAL PRIMARY KEY,
            title TEXT,
            text TEXT
        );
    """)
    conn.commit()
def insert_articles_from_wikipedia(jsonl_path, MAX_LEN_ARTIGOS=None):
    artigos = load_wikipedia(jsonl_path, MAX_LEN_ARTIGOS)
    for artigo in artigos:
        insert_article(artigo["title"], artigo["text"])
    print("Todos os artigos foram inseridos na tabela.")
def apagar_todos_os_artigos():
    """Apaga todos os artigos da tabela artigos."""
    cur.execute("DELETE FROM artigos;")
    conn.commit()
def adapt_table_to_fulltextsearch():
    """Cria a tabela artigos e adapta para busca full-text."""
    cur.execute("ALTER TABLE artigos ADD COLUMN IF NOT EXISTS tsv TSVECTOR;")
    cur.execute("UPDATE artigos SET tsv = to_tsvector('portuguese', coalesce(title,'') || ' ' || coalesce(text,''));")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_fts ON artigos USING GIN(tsv);")
    conn.commit()
def start_connection():
    global conn, cur
    conn = psycopg2.connect(
        host="localhost",      # ou o nome do serviço no docker-compose se estiver em outra rede
        port=5432,
        database="arqsoft",
        user="user",
        password="password"
    )
    cur = conn.cursor()


@app.post("/buscar-postgres")
def buscarPostgres(searchRequest: SearchRequest):
    logs_dir = "postgres-search"
    os.makedirs(logs_dir, exist_ok=True)
    # Limpa a query para ser um nome de subpasta válido
    safe_query = re.sub(r'[^a-zA-Z0-9_\-]', '_', searchRequest.searchElement.strip())[:100]
    query_dir = os.path.join(logs_dir, safe_query)
    os.makedirs(query_dir, exist_ok=True)

    stringRetorno = ""
    tsquery = ' & '.join(searchRequest.searchElement.strip().split())
    start_time = time.time()
    cur.execute("""
        SELECT *, ts_rank(tsv, to_tsquery('portuguese', %s)) AS rank
        FROM artigos
        WHERE tsv @@ to_tsquery('portuguese', %s)
        ORDER BY rank DESC
        LIMIT 5;
    """, (tsquery, tsquery))
    rows = cur.fetchall()
    end_time = time.time()
    response_time = end_time - start_time
    relevant_answers = [r for r in rows if r[-1] > 0.8]

    for idx, r in enumerate(rows, 1):
        print("Título:", r[1])
        print("Trecho:", r[2][:300], "...\n")
        print("Relevância:", r[-1], "\n")
        artigo_str = f"Título: {r[1]}\nTrecho: {r[2]}...\nRelevância: {r[-1]}\n"
        artigo_path = os.path.join(query_dir, f"artigo{idx}.txt")
        with open(artigo_path, "w", encoding="utf-8") as f:
            f.write(artigo_str)
        stringRetorno += artigo_str + "\n"

    print("Precisão da pesquisa (>0.8):", len(relevant_answers)/len(rows) if rows else 0)
    stringRetorno += "Precisão da pesquisa (>0.8): " + str(len(relevant_answers)/len(rows) if rows else 0) + "\n"
    print(f"Tempo de resposta: {response_time:.4f} segundos\n")
    stringRetorno += f"Tempo de resposta: {response_time:.4f} segundos\n"
    
    return stringRetorno



@app.get("/baixar-dependencias")
def baixar_dependencias():
    #Caso precise criar a tabela e adaptar para full-text search novamente basta executar a função
    create_table()
    insert_articles_from_wikipedia("ptwiki-latest.json")
    adapt_table_to_fulltextsearch()


if __name__ == "__main__":
    start_connection()
    uvicorn.run(app, host="127.0.0.1", port=8000)
    cur.close()
    conn.close()
