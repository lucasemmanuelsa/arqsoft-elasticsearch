import psycopg2
from tqdm import tqdm
from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from utils.helper import load_wikipedia

app = FastAPI()

class SearchRequest(BaseModel):
    searchElement: str


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
