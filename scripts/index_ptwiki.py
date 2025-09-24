from tqdm import tqdm
import json
from elasticsearch import Elasticsearch, helpers
from elasticsearch.helpers import BulkIndexError
from constants import INDEX_NAME, ES_HOST
from utils.helper import load_wikipedia


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
                            "text": {"type": "text"},
                        }
                    }
                }
            )
            print("Índice criado com sucesso!")
        else:
            print("Índice já existe, pulando criação.")
            #es.indices.delete(index=INDEX_NAME)
            #print("índice deletado com sucesso!")
            
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
            "text": artigo["text"],
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