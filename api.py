from db.base import redis_client,pg_conn,mongo_collection,neo4j_driver;
from psycopg2.extras import RealDictCursor
import json

def buscarDadosTodosCliente():
    with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("""
            select * from clientes cl;
        """)
        clientes = cursor.fetchall()
    

    redis_client.set("dadosTodosClientes", json.dumps(clientes, default=str))

    return clientes
    
def buscarDadosClientesAmigos():

    clientes_amigos = []

    with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("""
            SELECT *
            FROM clientes;
        """)

        clientes = cursor.fetchall()

    with neo4j_driver.session() as session:

        for cliente in clientes:

            resultado = session.run("""
                MATCH (c:Pessoa {cpf: $cpf})-[:AMIGO_DE]->(a:Pessoa)
                RETURN
                    a.id AS id,
                    a.cpf AS cpf,
                    a.nome AS nome
            """, cpf=cliente["cpf"])

            amigos = [dict(record) for record in resultado]

            clientes_amigos.append({
                "id": cliente["id"],
                "cpf": cliente["cpf"],
                "nome": cliente["nome"],
                "endereco": cliente["endereco"],
                "cidade": cliente["cidade"],
                "uf": cliente["uf"],
                "email": cliente["email"],
                "amigos": amigos
            })

    redis_client.set("clientesAmigos", json.dumps(clientes_amigos, default=str))

    return clientes_amigos

def buscarDadosClientesCompras():

    with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:

        cursor.execute("""
            SELECT
                co.data,

                cl.id,
                cl.cpf,
                cl.nome,
                cl.endereco,
                cl.cidade,
                cl.uf,
                cl.email,

                pr.produto,
                pr.valor,
                pr.quantidade,
                pr.tipo

            FROM compras co
            JOIN clientes cl
                ON cl.id = co.id_cliente
            JOIN produtos pr
                ON pr.id = co.id_produto
        """)

        registros = cursor.fetchall()

    clientes = {}

    for registro in registros:

        cpf = registro["cpf"]

        if cpf not in clientes:

            clientes[cpf] = {
                "id": registro["id"],
                "cpf": cpf,
                "nome": registro["nome"],
                "endereco": registro["endereco"],
                "cidade": registro["cidade"],
                "uf": registro["uf"],
                "email": registro["email"],
                "compras": []
            }

        clientes[cpf]["compras"].append({
            "data": registro["data"],
            "produto": registro["produto"],
            "valor": float(registro["valor"]),
            "quantidade": registro["quantidade"],
            "tipo": registro["tipo"]
        })

    dados = list(clientes.values())
    redis_client.set("clientesCompra", json.dumps(dados, default=str))

    
    return dados


def buscarDadosAmigosClienteRecomendacao():

    resultado = []

    clientes_amigos = buscarDadosClientesAmigos()
    clientes_compras = buscarDadosClientesCompras()

    compras_por_cpf = {
        cliente["cpf"]: cliente["compras"]
        for cliente in clientes_compras
    }

    for cliente in clientes_amigos:

        amigos = []

        for amigo in cliente["amigos"]:

            amigos.append({
                "cpf": amigo["cpf"],
                "nome": amigo["nome"],
                "recomendacoes": compras_por_cpf.get(
                    cliente["cpf"],
                    []
                )
            })

        resultado.append({
            "cpf": cliente["cpf"],
            "nome": cliente["nome"],
            "amigos": amigos
        })

    return resultado