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

def insert_articles_from_wikipedia(jsonl_path, MAX_LEN_ARTIGOS=None):
    artigos = load_wikipedia(jsonl_path, MAX_LEN_ARTIGOS)
    for artigo in artigos:
        insert_article(artigo["title"], artigo["text"])
    print("Todos os artigos foram inseridos na tabela.")

# Dados de conexão
conn = psycopg2.connect(
    host="localhost",      # ou o nome do serviço no docker-compose se estiver em outra rede
    port=5432,
    database="arqsoft",
    user="user",
    password="password"
)

cur = conn.cursor()
# Criação da tabela
cur.execute("""
    CREATE TABLE IF NOT EXISTS artigos (
        id SERIAL PRIMARY KEY,
        title TEXT,
        text TEXT
    );
    """)
conn.commit()

insert_articles_from_wikipedia("ptwiki-latest.json", MAX_LEN_ARTIGOS=100) #aumentar o número para inserir mais artigos,ou retirar max len para rodar tudo


# Consultar dados
cur.execute("SELECT * FROM artigos;")
rows = cur.fetchall()
for r in rows:
    print(r)

cur.close()
conn.close()
