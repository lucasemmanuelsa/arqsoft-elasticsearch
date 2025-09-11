from tqdm import tqdm
import json
from elasticsearch import Elasticsearch, helpers
from elasticsearch.helpers import BulkIndexError
from constants import INDEX_NAME, ES_HOST


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


# Use HTTP em vez de HTTPS

def create_es_client():
    """Cria cliente Elasticsearch sem SSL"""
    return Elasticsearch(
        ES_HOST,
        verify_certs=False,  # Não verificar certificados
        ssl_show_warn=False
    )

def create_index(es):
    try:
        # Testa a conexão primeiro
        print("Testando conexão com Elasticsearch...")
        info = es.info()
        print(f"Conectado ao Elasticsearch v{info['version']['number']}")
        
        exists = es.indices.exists(index=INDEX_NAME)
        print(f"Índice existe? {exists}")
        
        if not exists:
            print("Criando índice com mapeamento...")
            es.indices.create(
                index=INDEX_NAME,
                body={
                    "mappings": {
                        "properties": {
                            "title": {"type": "text"},
                            "text": {"type": "text"}
                        }
                    }
                }
            )
            print("Índice criado com sucesso!")
        else:
            print("Índice já existe, pulando criação.")
            
    except Exception as e:
        print("Erro ao checar/criar índice:", e)
        raise

def generate_actions(json_path):
    artigos = load_wikipedia(json_path)
    for i, artigo in enumerate(artigos):
        if i % 1000 == 0:
            print(f"Processando artigo {i}...")
        yield {
            "_index": INDEX_NAME,
            "_id": artigo["title"],
            "title": artigo["title"],
            "text": artigo["text"]
        }

def main():
    try:
        es = create_es_client()
        create_index(es)
        print("Iniciando indexação...")
        actions = generate_actions("ptwiki-latest.json")
        try:
            success, failed = helpers.bulk(es, actions, stats_only=True, chunk_size=500, request_timeout=120, max_retries=3)
            print(f"Indexação concluída! Sucessos: {success}, Falhas: {failed}")
        except BulkIndexError as bulk_error:
            print("Erro de indexação em lote:")
            for err in bulk_error.errors[:5]:  # Mostra os 5 primeiros erros
                error_info = err.get('index', {})
                doc_id = error_info.get('_id', 'N/A')
                error_reason = error_info.get('error', {}).get('reason', 'Sem motivo detalhado')
                print(f"ID: {doc_id} | Erro: {error_reason}")
            print(f"Total de erros: {len(bulk_error.errors)}")
    except Exception as e:
        print("Erro durante a execução:", e)

if __name__ == "__main__":
    main()