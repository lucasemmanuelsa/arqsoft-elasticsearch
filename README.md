# arqsoft-elasticsearch
Repositório voltado para o desenvolvimento do projeto final da disciplina arquitetura de software


## Requerimentos:

CERTIFIQUE-SE DE TER O DOCKER !!!!!!!!!!!!!!!!

### Baixe o dataset do wikipedia no link abaixo e coloque-o na raiz do projeto

```
https://drive.google.com/file/d/1xS1q2Sm4fhPZeNL1YJ5qF5NkTPUuU3TD/view?usp=sharing
```

### Abra o terminal na mesma raiz do docker-compose.yml e execute:

```
docker-compose up
```

### Instale as dependencias do python

```
pip install -r requirements.txt
```

### Execute o script de indexação dos documentos no ElasticSearch (demora um pouco)
- Isso irá criar um index chamado ptwiki caso ele não exista

```
python index_ptwiki.py
```

### O elasticsearch estará com o index criado e todos os artigos do wikipedia pronto.

Execute ```buscasimples.py``` se quiser verificar se a indexação deu certo.


OBS: 
- A porta de conexão com a api do elasticsearch é 9200
- A porta de conexão com o postgresql é 5432
- Certifique-se de adicionar as dependências extras que for utilizar no arquivo requirements.txt