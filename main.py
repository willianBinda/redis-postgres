from fastapi import FastAPI, HTTPException
from db.base import redis_client
from db.schemas import (
    ClienteCreate, ClienteUpdate,
    ProdutoCreate, ProdutoUpdate,
    CompraCreate, CompraUpdate,
    InteresseCreate, InteresseUpdate,
    PessoaCreate, AmizadeCreate,
)
from api import (
    CACHE_KEYS,
    clear_all_cache, refresh_all_cache,
    buscarDadosTodosCliente, buscarDadosClientesAmigos,
    buscarDadosClientesCompras, buscarDadosAmigosClienteRecomendacao,
    get_all_clientes, get_cliente_by_id, create_cliente, update_cliente, delete_cliente,
    get_all_produtos, get_produto_by_id, create_produto, update_produto, delete_produto,
    get_all_compras, get_compra_by_id, create_compra, update_compra, delete_compra,
    get_all_interesses, get_interesse_by_cpf, create_interesse, update_interesse, delete_interesse,
    get_all_pessoas, get_pessoa_by_cpf, create_pessoa, delete_pessoa,
    get_amizades_by_cpf, create_amizade, delete_amizade,
)
import json

app = FastAPI(
    title="Sistema de Recomendacao de Compras",
    description=(
        "Integracao entre **PostgreSQL** (relacional), **MongoDB** (documentos), "
        "**Neo4j** (grafos) e **Redis** (cache/chave-valor).\n\n"
        "A API busca dados nas bases, faz a juncao e armazena no Redis. "
        "Toda mutacao invalida as chaves relevantes do cache."
    ),
    version="1.0.0",
)


# ─── Cache ────────────────────────────────────────────────────────────────────

@app.get("/cache/status", tags=["Cache (Redis)"],
         summary="Status de cada chave no Redis (HIT ou MISS)")
def cache_status():
    return {"cache": {key: redis_client.get(key) is not None for key in CACHE_KEYS}}


@app.delete("/cache", tags=["Cache (Redis)"],
            summary="Limpa todo o cache Redis")
def limpar_cache():
    clear_all_cache()
    return {"message": "Cache limpo com sucesso"}


@app.post("/cache/refresh", tags=["Cache (Redis)"],
          summary="Recarrega todos os dados dos BDs e salva no Redis")
def recarregar_cache():
    refresh_all_cache()
    return {"message": "Cache recarregado com sucesso"}


# ─── Consultas Redis ──────────────────────────────────────────────────────────

@app.get("/buscarTodosCliente", tags=["Consultas Redis"],
         summary="Todos os clientes (PostgreSQL -> Redis)")
def buscarTodosCliente():
    dados_json = redis_client.get("dadosTodosClientes")
    if dados_json:
        return json.loads(dados_json)
    return buscarDadosTodosCliente()


@app.get("/buscarClientesAmigos", tags=["Consultas Redis"],
         summary="Clientes com seus amigos (PostgreSQL + Neo4j -> Redis)")
def buscarClientesAmigos():
    dados_json = redis_client.get("clientesAmigos")
    if dados_json:
        return json.loads(dados_json)
    return buscarDadosClientesAmigos()


@app.get("/buscarClientesCompra", tags=["Consultas Redis"],
         summary="Clientes com suas compras (PostgreSQL -> Redis)")
def buscarClientesCompra():
    dados_json = redis_client.get("clientesCompra")
    if dados_json:
        return json.loads(dados_json)
    return buscarDadosClientesCompras()


@app.get("/buscarAmigosClienteRecomendacao", tags=["Consultas Redis"],
         summary="Amigos dos clientes com recomendacoes de compras (todos os BDs -> Redis)")
def buscarAmigosClienteRecomendacao():
    dados_json = redis_client.get("amigoClienteRecomendacao")
    if dados_json:
        return json.loads(dados_json)
    return buscarDadosAmigosClienteRecomendacao()


# ─── Clientes CRUD (PostgreSQL) ───────────────────────────────────────────────

@app.get("/clientes", tags=["Clientes (PostgreSQL)"])
def listar_clientes():
    return get_all_clientes()


@app.get("/clientes/{id}", tags=["Clientes (PostgreSQL)"])
def obter_cliente(id: int):
    cliente = get_cliente_by_id(id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente nao encontrado")
    return cliente


@app.post("/clientes", tags=["Clientes (PostgreSQL)"], status_code=201)
def criar_cliente(data: ClienteCreate):
    try:
        create_cliente(data)
        return {"message": "Cliente criado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/clientes/{id}", tags=["Clientes (PostgreSQL)"])
def atualizar_cliente(id: int, data: ClienteUpdate):
    try:
        if not update_cliente(id, data):
            raise HTTPException(status_code=404, detail="Cliente nao encontrado")
        return {"message": "Cliente atualizado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/clientes/{id}", tags=["Clientes (PostgreSQL)"])
def remover_cliente(id: int):
    try:
        if not delete_cliente(id):
            raise HTTPException(status_code=404, detail="Cliente nao encontrado")
        return {"message": "Cliente removido com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─── Produtos CRUD (PostgreSQL) ───────────────────────────────────────────────

@app.get("/produtos", tags=["Produtos (PostgreSQL)"])
def listar_produtos():
    return get_all_produtos()


@app.get("/produtos/{id}", tags=["Produtos (PostgreSQL)"])
def obter_produto(id: int):
    produto = get_produto_by_id(id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")
    return produto


@app.post("/produtos", tags=["Produtos (PostgreSQL)"], status_code=201)
def criar_produto(data: ProdutoCreate):
    try:
        create_produto(data)
        return {"message": "Produto criado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/produtos/{id}", tags=["Produtos (PostgreSQL)"])
def atualizar_produto(id: int, data: ProdutoUpdate):
    try:
        if not update_produto(id, data):
            raise HTTPException(status_code=404, detail="Produto nao encontrado")
        return {"message": "Produto atualizado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/produtos/{id}", tags=["Produtos (PostgreSQL)"])
def remover_produto(id: int):
    try:
        if not delete_produto(id):
            raise HTTPException(status_code=404, detail="Produto nao encontrado")
        return {"message": "Produto removido com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─── Compras CRUD (PostgreSQL) ────────────────────────────────────────────────

@app.get("/compras", tags=["Compras (PostgreSQL)"])
def listar_compras():
    return get_all_compras()


@app.get("/compras/{id}", tags=["Compras (PostgreSQL)"])
def obter_compra(id: int):
    compra = get_compra_by_id(id)
    if not compra:
        raise HTTPException(status_code=404, detail="Compra nao encontrada")
    return compra


@app.post("/compras", tags=["Compras (PostgreSQL)"], status_code=201)
def criar_compra(data: CompraCreate):
    try:
        create_compra(data)
        return {"message": "Compra criada com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/compras/{id}", tags=["Compras (PostgreSQL)"])
def atualizar_compra(id: int, data: CompraUpdate):
    try:
        if not update_compra(id, data):
            raise HTTPException(status_code=404, detail="Compra nao encontrada")
        return {"message": "Compra atualizada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/compras/{id}", tags=["Compras (PostgreSQL)"])
def remover_compra(id: int):
    try:
        if not delete_compra(id):
            raise HTTPException(status_code=404, detail="Compra nao encontrada")
        return {"message": "Compra removida com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─── Interesses CRUD (MongoDB) ────────────────────────────────────────────────

@app.get("/interesses", tags=["Interesses (MongoDB)"])
def listar_interesses():
    return get_all_interesses()


@app.get("/interesses/{cpf}", tags=["Interesses (MongoDB)"])
def obter_interesse(cpf: str):
    doc = get_interesse_by_cpf(cpf)
    if not doc:
        raise HTTPException(status_code=404, detail="Interesse nao encontrado para este CPF")
    return doc


@app.post("/interesses", tags=["Interesses (MongoDB)"], status_code=201)
def criar_interesse(data: InteresseCreate):
    try:
        create_interesse(data)
        return {"message": "Interesse criado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@app.put("/interesses/{cpf}", tags=["Interesses (MongoDB)"])
def atualizar_interesse(cpf: str, data: InteresseUpdate):
    if not update_interesse(cpf, data):
        raise HTTPException(status_code=404, detail="Interesse nao encontrado para este CPF")
    return {"message": "Interesse atualizado com sucesso"}


@app.delete("/interesses/{cpf}", tags=["Interesses (MongoDB)"])
def remover_interesse(cpf: str):
    if not delete_interesse(cpf):
        raise HTTPException(status_code=404, detail="Interesse nao encontrado para este CPF")
    return {"message": "Interesse removido com sucesso"}


# ─── Pessoas CRUD (Neo4j) ─────────────────────────────────────────────────────

@app.get("/pessoas", tags=["Pessoas (Neo4j)"])
def listar_pessoas():
    return get_all_pessoas()


@app.get("/pessoas/{cpf}", tags=["Pessoas (Neo4j)"])
def obter_pessoa(cpf: str):
    pessoa = get_pessoa_by_cpf(cpf)
    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa nao encontrada")
    return pessoa


@app.get("/pessoas/{cpf}/amizades", tags=["Pessoas (Neo4j)"])
def listar_amizades(cpf: str):
    return get_amizades_by_cpf(cpf)


@app.post("/pessoas", tags=["Pessoas (Neo4j)"], status_code=201)
def criar_pessoa(data: PessoaCreate):
    try:
        create_pessoa(data)
        return {"message": "Pessoa criada com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/pessoas/{cpf}", tags=["Pessoas (Neo4j)"])
def remover_pessoa(cpf: str):
    if not delete_pessoa(cpf):
        raise HTTPException(status_code=404, detail="Pessoa nao encontrada")
    return {"message": "Pessoa removida com sucesso"}


# ─── Amizades CRUD (Neo4j) ────────────────────────────────────────────────────

@app.post("/amizades", tags=["Amizades (Neo4j)"], status_code=201)
def criar_amizade(data: AmizadeCreate):
    try:
        create_amizade(data)
        return {"message": "Amizade criada com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/amizades/{cpf_origem}/{cpf_destino}", tags=["Amizades (Neo4j)"])
def remover_amizade(cpf_origem: str, cpf_destino: str):
    delete_amizade(cpf_origem, cpf_destino)
    return {"message": "Amizade removida com sucesso"}
