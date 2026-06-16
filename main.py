from fastapi import FastAPI
from db.base import redis_client;
import json
from api import buscarDadosTodosCliente,buscarDadosClientesAmigos,buscarDadosClientesCompras,buscarDadosAmigosClienteRecomendacao

app = FastAPI()

@app.get("/buscarTodosCliente")
def buscarTodosCliente():
    dados_json = redis_client.get("dadosTodosClientes")

    if dados_json:
        return json.loads(dados_json)

    dados = buscarDadosTodosCliente()

    return dados

@app.get("/buscarClientesAmigos")
def buscarClientesAmigos():
    dados_json = redis_client.get("clientesAmigos")

    if dados_json:
        return json.loads(dados_json)

    dados = buscarDadosClientesAmigos()

    return dados

@app.get("/buscarClientesCompra")
def buscarClientesCompra():
    
    dados_json = redis_client.get("clientesCompra")

    if dados_json:
        return json.loads(dados_json)

    dados = buscarDadosClientesCompras()

    return dados

@app.get("/buscarAmigosClienteRecomendacao")
def buscarAmigosClienteRecomendacao():
    
    dados_json = redis_client.get("amigoClienteRecomendacao")

    if dados_json:
        return json.loads(dados_json)

    dados = buscarDadosAmigosClienteRecomendacao()

    redis_client.set("amigoClienteRecomendacao", json.dumps(dados))

    return dados

