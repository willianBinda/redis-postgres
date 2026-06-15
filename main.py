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

    redis_client.set(
        "dadosTodosClientes",
        json.dumps(dados)
    )
    return json.loads(dados)

