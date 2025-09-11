import psycopg2
from tqdm import tqdm
import json

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
# Dados de conexão
conn = psycopg2.connect(
    host="localhost",      # ou o nome do serviço no docker-compose se estiver em outra rede
    port=5432,
    database="arqsoft",
    user="user",
    password="password"
)

cur = conn.cursor()

#Caso precise criar a tabela e adaptar para full-text search novamente basta executar os códigos abaixo
#create_table()
#insert_articles_from_wikipedia("ptwiki-latest.json")
#adapt_table_to_fulltextsearch()

#Caso precise apagar todos os artigos da tabela, descomente a linha abaixo
#apagar_todos_os_artigos()

while True:
    searchElement = input("Digite o termo de busca: ")
    if searchElement.lower() == ':sair':
        break
    # Transforma a string em formato AND para to_tsquery
    tsquery = ' & '.join(searchElement.strip().split())
    cur.execute("""
        SELECT *, ts_rank(tsv, to_tsquery('portuguese', %s)) AS rank
        FROM artigos
        WHERE tsv @@ to_tsquery('portuguese', %s)
        ORDER BY rank DESC
        LIMIT 20;
    """, (tsquery, tsquery))
    rows = cur.fetchall()
    for r in rows:
        print("Título:", r[1])
        print("Trecho:", r[2][:300], "...\n")
        print("Relevância:", r[-1], "\n")

cur.close()
conn.close()
