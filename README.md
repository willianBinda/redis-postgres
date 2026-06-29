# Sistema de Recomendacao de Compras

Trabalho Final — Banco de Dados II · Unochapeco 2026/1

Integracao entre quatro bancos de dados (PostgreSQL, MongoDB, Neo4j e Redis) por meio de uma API REST construida com FastAPI. A API busca dados nas tres primeiras bases, faz a juncao entre eles e armazena o resultado no Redis como cache.

---

## Arquitetura

```
PostgreSQL  ─┐
              ├──► API FastAPI ──► Redis ──► Interface Web
Neo4j       ─┘        ▲
                       │
MongoDB     ───────────┘
```

| Base | Tecnologia | Responsabilidade |
|------|-----------|-----------------|
| BASE 1 | PostgreSQL | Clientes, Produtos e Compras (relacional) |
| BASE 2 | MongoDB | Interesses dos clientes (documentos) |
| BASE 3 | Neo4j | Clientes e amigos (grafo) |
| BASE 4 | Redis | Cache das consultas consolidadas (chave-valor) |

---

## Estrutura do Projeto

```
.
├── main.py                  # Rotas FastAPI (CRUD + consultas + cache)
├── api.py                   # Logica de negocio e acesso aos bancos
├── docker-compose.yml       # Containers dos 4 bancos
├── requests.http            # Requisicoes de teste (REST Client / IntelliJ)
│
└── db/
    ├── base.py              # Conexoes com os bancos
    ├── schemas.py           # Modelos Pydantic (validacao e Swagger)
    ├── script_postgres.py   # Populacao do PostgreSQL
    ├── script_mongo.py      # Populacao do MongoDB
    └── script_ne4j.py       # Populacao do Neo4j
```

---

## Requisitos

- Python 3.11+
- Docker e Docker Compose

Instalar dependencias Python:

```bash
pip install fastapi uvicorn psycopg2-binary pymongo neo4j redis
```

---

## Como Executar

### 1. Subir os containers

```bash
docker compose up -d
```

### 2. Popular os bancos de dados

```bash
cd db
python script_postgres.py
python script_mongo.py
python script_ne4j.py
cd ..
```

### 3. Iniciar a API

```bash
uvicorn main:app --reload
```

### 4. Acessar

| URL | Descricao |
|-----|-----------|
| `http://localhost:8000/docs` | Swagger UI (testes interativos) |
| `http://localhost:8000/redoc` | Documentacao ReDoc |

---

## Testando com o arquivo requests.http

O arquivo `requests.http` contem todas as requisicoes prontas e pode ser executado de duas formas:

### Opcao 1 — VS Code (REST Client)

1. Instale a extensao **REST Client** (`humao.rest-client`) no VS Code.
2. Abra o arquivo `requests.http`.
3. Clique em **"Send Request"** que aparece acima de cada bloco `###`.

### Opcao 2 — IntelliJ / PyCharm

O arquivo `.http` e suportado nativamente. Abra-o e clique no icone de play ao lado de cada requisicao.

### Estrutura do arquivo

```
@base = http://localhost:8000   ← variavel reutilizada em todas as rotas

### Descricao da requisicao
GET {{base}}/rota

### Requisicao com corpo JSON
POST {{base}}/rota
Content-Type: application/json

{ "campo": "valor" }

###   ← separador obrigatorio entre requisicoes
```

### Fluxo de demonstracao do cache (no proprio arquivo)

```
1. GET  /cache/status        → todas as chaves aparecem como MISS (false)
2. GET  /buscarTodosCliente  → busca no PostgreSQL e salva no Redis
3. GET  /cache/status        → dadosTodosClientes agora aparece HIT (true)
4. POST /clientes            → cria cliente, invalida as chaves de cache
5. GET  /cache/status        → cache foi invalidado (false novamente)
6. GET  /buscarTodosCliente  → recarrega do banco e salva no Redis
```

---

## Endpoints

### Consultas Redis

Buscam dados dos bancos, fazem a juncao e armazenam no Redis. Nas chamadas seguintes, retornam diretamente do cache.

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/buscarTodosCliente` | Todos os clientes (PostgreSQL) |
| GET | `/buscarClientesAmigos` | Clientes com amigos (PostgreSQL + Neo4j) |
| GET | `/buscarClientesCompra` | Clientes com compras (PostgreSQL) |
| GET | `/buscarAmigosClienteRecomendacao` | Amigos com recomendacoes (todos os BDs) |

### Cache

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/cache/status` | Status HIT/MISS de cada chave |
| DELETE | `/cache` | Limpa todo o cache |
| POST | `/cache/refresh` | Recarrega todos os dados no Redis |

### Clientes — PostgreSQL

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/clientes` | Listar todos |
| GET | `/clientes/{id}` | Buscar por ID |
| POST | `/clientes` | Criar |
| PUT | `/clientes/{id}` | Atualizar parcialmente |
| DELETE | `/clientes/{id}` | Remover |

### Produtos — PostgreSQL

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/produtos` | Listar todos |
| GET | `/produtos/{id}` | Buscar por ID |
| POST | `/produtos` | Criar |
| PUT | `/produtos/{id}` | Atualizar parcialmente |
| DELETE | `/produtos/{id}` | Remover |

### Compras — PostgreSQL

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/compras` | Listar todas |
| GET | `/compras/{id}` | Buscar por ID |
| POST | `/compras` | Criar |
| PUT | `/compras/{id}` | Atualizar parcialmente |
| DELETE | `/compras/{id}` | Remover |

### Interesses — MongoDB

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/interesses` | Listar todos |
| GET | `/interesses/{cpf}` | Buscar por CPF |
| POST | `/interesses` | Criar |
| PUT | `/interesses/{cpf}` | Atualizar parcialmente |
| DELETE | `/interesses/{cpf}` | Remover |

### Pessoas — Neo4j

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/pessoas` | Listar todas |
| GET | `/pessoas/{cpf}` | Buscar por CPF |
| GET | `/pessoas/{cpf}/amizades` | Listar amigos |
| POST | `/pessoas` | Criar |
| DELETE | `/pessoas/{cpf}` | Remover (e suas relacoes) |

### Amizades — Neo4j

| Metodo | Rota | Descricao |
|--------|------|-----------|
| POST | `/amizades` | Criar amizade bidirecional |
| DELETE | `/amizades/{cpf_origem}/{cpf_destino}` | Remover amizade bidirecional |

---

## Esquema dos Dados

### PostgreSQL

```sql
Clientes  (id, cpf, nome, endereco, cidade, uf, email)
Produtos  (id, produto, valor, quantidade, tipo)
Compras   (id, id_produto, data, id_cliente)
```

### MongoDB

```json
{
  "cpf": "11111111111",
  "nome": "Joao Silva",
  "interesses": ["Futebol", "Tecnologia"]
}
```

### Neo4j

```
(Pessoa {id, cpf, nome}) -[:AMIGO_DE]-> (Pessoa)
```

### Redis — Chaves de Cache

| Chave | Conteudo |
|-------|----------|
| `dadosTodosClientes` | Lista de clientes do PostgreSQL |
| `clientesAmigos` | Clientes com lista de amigos do Neo4j |
| `clientesCompra` | Clientes agrupados com suas compras |
| `amigoClienteRecomendacao` | Amigos de cada cliente com recomendacoes |

---

## Invalidacao de Cache

Toda operacao de escrita (POST, PUT, DELETE) invalida automaticamente as chaves Redis afetadas. Na proxima consulta, os dados sao buscados novamente nos bancos e o cache e recomposto.

```
Mutacao em Clientes → invalida todas as 4 chaves
Mutacao em Produtos → invalida clientesCompra e amigoClienteRecomendacao
Mutacao em Neo4j    → invalida clientesAmigos e amigoClienteRecomendacao
```

---

## Dados de Exemplo (seed)

**Clientes:** Joao, Maria, Pedro, Ana, Carlos

**Produtos:** Bola de Futebol, Notebook Gamer, Violao, Livro Python, Smart TV

**Amizades no grafo:**
- Joao ↔ Maria, Pedro, Carlos, Bruno
- Maria ↔ Ana, Julia
