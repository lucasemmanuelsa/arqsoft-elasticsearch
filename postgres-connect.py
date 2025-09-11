import psycopg2

# Dados de conexão
conn = psycopg2.connect(
    host="localhost",      # ou o nome do serviço no docker-compose se estiver em outra rede
    port=5432,
    database="arqsoft",
    user="user",
    password="password"
)

cur = conn.cursor()

# Exemplo: criar tabela
cur.execute("CREATE TABLE IF NOT EXISTS teste (id serial PRIMARY KEY, nome text);")

# Inserir dados
cur.execute("INSERT INTO teste (nome) VALUES (%s)", ("João",))

# Consultar dados
cur.execute("SELECT * FROM teste;")
rows = cur.fetchall()
for r in rows:
    print(r)

conn.commit()
cur.close()
conn.close()
