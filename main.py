from fastapi import FastAPI
from db.base import redis_client;
import json

app = FastAPI()

@app.get("/buscarDadosTodosCliente")
def buscarDadosTodosCliente():
    
    dados_json = redis_client.get("dadosTodosClientes")

    if dados_json:
        return json.loads(dados_json)

    dados = consolidar_dados()

    redis_client.set("dadosTodosClientes", json.dumps(dados))

    return json.loads(dados)

@app.get("/buscarClientesAmigos")
def buscarClientesAmigos():
    
    dados_json = redis_client.get("clientesAmigos")

    if dados_json:
        return json.loads(dados_json)

    dados = buscarDadosClientesAmigos()

    redis_client.set("clientesAmigos", json.dumps(dados))

    return json.loads(dados)

@app.get("/buscarClientesCompra")
def buscarClientesCompra():
    
    dados_json = redis_client.get("clientesCompra")

    if dados_json:
        return json.loads(dados_json)

    dados = buscarDadosClientesCompra()

    redis_client.set("clientesCompra", json.dumps(dados))

    return json.loads(dados)

@app.get("/buscarAmigosClienteRecomendacao")
def buscarAmigosClienteRecomendacao():
    
    dados_json = redis_client.get("amigoClienteRecomendacao")

    if dados_json:
        return json.loads(dados_json)

    dados = buscarDadosAmigosClienteRecomendacao()

    redis_client.set("amigoClienteRecomendacao", json.dumps(dados))

    return json.loads(dados)

