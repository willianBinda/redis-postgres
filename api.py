from db.base import redis_client, pg_conn, mongo_collection, neo4j_driver
from psycopg2.extras import RealDictCursor
import json

CACHE_KEYS = [
    "dadosTodosClientes",
    "clientesAmigos",
    "clientesCompra",
    "amigoClienteRecomendacao",
]


def _invalidate(*keys):
    redis_client.delete(*keys)


def clear_all_cache():
    redis_client.delete(*CACHE_KEYS)


def refresh_all_cache():
    clear_all_cache()
    buscarDadosTodosCliente()
    buscarDadosClientesAmigos()
    buscarDadosClientesCompras()
    buscarDadosAmigosClienteRecomendacao()


# ─── Redis Queries ────────────────────────────────────────────────────────────

def buscarDadosTodosCliente():
    with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM clientes")
        clientes = cursor.fetchall()
    redis_client.set("dadosTodosClientes", json.dumps(clientes, default=str))
    return clientes


def buscarDadosClientesAmigos():
    clientes_amigos = []

    with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM clientes")
        clientes = cursor.fetchall()

    with neo4j_driver.session() as session:
        for cliente in clientes:
            resultado = session.run("""
                MATCH (c:Pessoa {cpf: $cpf})-[:AMIGO_DE]->(a:Pessoa)
                RETURN a.id AS id, a.cpf AS cpf, a.nome AS nome
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
                "amigos": amigos,
            })

    redis_client.set("clientesAmigos", json.dumps(clientes_amigos, default=str))
    return clientes_amigos


def buscarDadosClientesCompras():
    with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("""
            SELECT
                co.data,
                cl.id, cl.cpf, cl.nome, cl.endereco, cl.cidade, cl.uf, cl.email,
                pr.produto, pr.valor, pr.quantidade, pr.tipo
            FROM compras co
            JOIN clientes cl ON cl.id = co.id_cliente
            JOIN produtos pr ON pr.id = co.id_produto
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
                "compras": [],
            }
        clientes[cpf]["compras"].append({
            "data": registro["data"],
            "produto": registro["produto"],
            "valor": float(registro["valor"]),
            "quantidade": registro["quantidade"],
            "tipo": registro["tipo"],
        })

    dados = list(clientes.values())
    redis_client.set("clientesCompra", json.dumps(dados, default=str))
    return dados


def buscarDadosAmigosClienteRecomendacao():
    resultado = []
    clientes_amigos = buscarDadosClientesAmigos()
    clientes_compras = buscarDadosClientesCompras()
    compras_por_cpf = {c["cpf"]: c["compras"] for c in clientes_compras}

    for cliente in clientes_amigos:
        amigos = []
        for amigo in cliente["amigos"]:
            amigos.append({
                "cpf": amigo["cpf"],
                "nome": amigo["nome"],
                "recomendacoes": compras_por_cpf.get(cliente["cpf"], []),
            })
        resultado.append({
            "cpf": cliente["cpf"],
            "nome": cliente["nome"],
            "amigos": amigos,
        })

    redis_client.set("amigoClienteRecomendacao", json.dumps(resultado, default=str))
    return resultado


# ─── Clientes CRUD (PostgreSQL) ───────────────────────────────────────────────

def get_all_clientes():
    with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM clientes ORDER BY id")
        return [dict(r) for r in cursor.fetchall()]


def get_cliente_by_id(id: int):
    with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM clientes WHERE id = %s", (id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def create_cliente(data):
    try:
        with pg_conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO clientes (id, cpf, nome, endereco, cidade, uf, email) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (data.id, data.cpf, data.nome, data.endereco, data.cidade, data.uf, data.email),
            )
        pg_conn.commit()
        _invalidate(*CACHE_KEYS)
    except Exception as e:
        pg_conn.rollback()
        raise e


def update_cliente(id: int, data):
    fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not fields:
        return False
    set_clause = ", ".join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [id]
    try:
        with pg_conn.cursor() as cursor:
            cursor.execute(f"UPDATE clientes SET {set_clause} WHERE id = %s", values)
            updated = cursor.rowcount
        pg_conn.commit()
        if updated:
            _invalidate(*CACHE_KEYS)
        return updated > 0
    except Exception as e:
        pg_conn.rollback()
        raise e


def delete_cliente(id: int):
    try:
        with pg_conn.cursor() as cursor:
            cursor.execute("DELETE FROM clientes WHERE id = %s", (id,))
            deleted = cursor.rowcount
        pg_conn.commit()
        if deleted:
            _invalidate(*CACHE_KEYS)
        return deleted > 0
    except Exception as e:
        pg_conn.rollback()
        raise e


# ─── Produtos CRUD (PostgreSQL) ───────────────────────────────────────────────

def get_all_produtos():
    with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM produtos ORDER BY id")
        return [dict(r) for r in cursor.fetchall()]


def get_produto_by_id(id: int):
    with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM produtos WHERE id = %s", (id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def create_produto(data):
    try:
        with pg_conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO produtos (id, produto, valor, quantidade, tipo) VALUES (%s,%s,%s,%s,%s)",
                (data.id, data.produto, data.valor, data.quantidade, data.tipo),
            )
        pg_conn.commit()
        _invalidate("clientesCompra", "amigoClienteRecomendacao")
    except Exception as e:
        pg_conn.rollback()
        raise e


def update_produto(id: int, data):
    fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not fields:
        return False
    set_clause = ", ".join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [id]
    try:
        with pg_conn.cursor() as cursor:
            cursor.execute(f"UPDATE produtos SET {set_clause} WHERE id = %s", values)
            updated = cursor.rowcount
        pg_conn.commit()
        if updated:
            _invalidate("clientesCompra", "amigoClienteRecomendacao")
        return updated > 0
    except Exception as e:
        pg_conn.rollback()
        raise e


def delete_produto(id: int):
    try:
        with pg_conn.cursor() as cursor:
            cursor.execute("DELETE FROM produtos WHERE id = %s", (id,))
            deleted = cursor.rowcount
        pg_conn.commit()
        if deleted:
            _invalidate("clientesCompra", "amigoClienteRecomendacao")
        return deleted > 0
    except Exception as e:
        pg_conn.rollback()
        raise e


# ─── Compras CRUD (PostgreSQL) ────────────────────────────────────────────────

def get_all_compras():
    with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM compras ORDER BY id")
        return [dict(r) for r in cursor.fetchall()]


def get_compra_by_id(id: int):
    with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM compras WHERE id = %s", (id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def create_compra(data):
    try:
        with pg_conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO compras (id, id_produto, data, id_cliente) VALUES (%s,%s,%s,%s)",
                (data.id, data.id_produto, data.data, data.id_cliente),
            )
        pg_conn.commit()
        _invalidate("clientesCompra", "amigoClienteRecomendacao")
    except Exception as e:
        pg_conn.rollback()
        raise e


def update_compra(id: int, data):
    fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not fields:
        return False
    set_clause = ", ".join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [id]
    try:
        with pg_conn.cursor() as cursor:
            cursor.execute(f"UPDATE compras SET {set_clause} WHERE id = %s", values)
            updated = cursor.rowcount
        pg_conn.commit()
        if updated:
            _invalidate("clientesCompra", "amigoClienteRecomendacao")
        return updated > 0
    except Exception as e:
        pg_conn.rollback()
        raise e


def delete_compra(id: int):
    try:
        with pg_conn.cursor() as cursor:
            cursor.execute("DELETE FROM compras WHERE id = %s", (id,))
            deleted = cursor.rowcount
        pg_conn.commit()
        if deleted:
            _invalidate("clientesCompra", "amigoClienteRecomendacao")
        return deleted > 0
    except Exception as e:
        pg_conn.rollback()
        raise e


# ─── Interesses CRUD (MongoDB) ────────────────────────────────────────────────

def get_all_interesses():
    return list(mongo_collection.find({}, {"_id": 0}))


def get_interesse_by_cpf(cpf: str):
    return mongo_collection.find_one({"cpf": cpf}, {"_id": 0})


def create_interesse(data):
    if mongo_collection.find_one({"cpf": data.cpf}):
        raise ValueError(f"Interesse para CPF {data.cpf} ja existe")
    mongo_collection.insert_one({"cpf": data.cpf, "nome": data.nome, "interesses": data.interesses})


def update_interesse(cpf: str, data):
    fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not fields:
        return False
    result = mongo_collection.update_one({"cpf": cpf}, {"$set": fields})
    return result.matched_count > 0


def delete_interesse(cpf: str):
    result = mongo_collection.delete_one({"cpf": cpf})
    return result.deleted_count > 0


# ─── Pessoas CRUD (Neo4j) ─────────────────────────────────────────────────────

def get_all_pessoas():
    with neo4j_driver.session() as session:
        resultado = session.run(
            "MATCH (p:Pessoa) RETURN p.id AS id, p.cpf AS cpf, p.nome AS nome ORDER BY p.id"
        )
        return [dict(r) for r in resultado]


def get_pessoa_by_cpf(cpf: str):
    with neo4j_driver.session() as session:
        resultado = session.run(
            "MATCH (p:Pessoa {cpf: $cpf}) RETURN p.id AS id, p.cpf AS cpf, p.nome AS nome",
            cpf=cpf,
        )
        row = resultado.single()
        return dict(row) if row else None


def create_pessoa(data):
    with neo4j_driver.session() as session:
        session.run(
            "CREATE (p:Pessoa {id: $id, cpf: $cpf, nome: $nome})",
            id=data.id, cpf=data.cpf, nome=data.nome,
        )
    _invalidate("clientesAmigos", "amigoClienteRecomendacao")


def delete_pessoa(cpf: str):
    with neo4j_driver.session() as session:
        check = session.run(
            "MATCH (p:Pessoa {cpf: $cpf}) RETURN count(p) AS total", cpf=cpf
        )
        total = check.single()["total"]
        if total:
            session.run("MATCH (p:Pessoa {cpf: $cpf}) DETACH DELETE p", cpf=cpf)
    if total:
        _invalidate("clientesAmigos", "amigoClienteRecomendacao")
    return total > 0


def get_amizades_by_cpf(cpf: str):
    with neo4j_driver.session() as session:
        resultado = session.run("""
            MATCH (p:Pessoa {cpf: $cpf})-[:AMIGO_DE]->(a:Pessoa)
            RETURN a.id AS id, a.cpf AS cpf, a.nome AS nome
        """, cpf=cpf)
        return [dict(r) for r in resultado]


# ─── Amizades CRUD (Neo4j) ────────────────────────────────────────────────────

def create_amizade(data):
    with neo4j_driver.session() as session:
        check = session.run("""
            MATCH (a:Pessoa {cpf: $cpf_origem}), (b:Pessoa {cpf: $cpf_destino})
            RETURN count(*) AS total
        """, cpf_origem=data.cpf_origem, cpf_destino=data.cpf_destino)
        if check.single()["total"] == 0:
            raise ValueError("Uma ou ambas as pessoas nao foram encontradas no Neo4j")
        session.run("""
            MATCH (a:Pessoa {cpf: $cpf_origem}), (b:Pessoa {cpf: $cpf_destino})
            MERGE (a)-[:AMIGO_DE]->(b)
            MERGE (b)-[:AMIGO_DE]->(a)
        """, cpf_origem=data.cpf_origem, cpf_destino=data.cpf_destino)
    _invalidate("clientesAmigos", "amigoClienteRecomendacao")


def delete_amizade(cpf_origem: str, cpf_destino: str):
    with neo4j_driver.session() as session:
        session.run("""
            MATCH (a:Pessoa {cpf: $cpf_origem})-[r:AMIGO_DE]->(b:Pessoa {cpf: $cpf_destino})
            DELETE r
        """, cpf_origem=cpf_origem, cpf_destino=cpf_destino)
        session.run("""
            MATCH (b:Pessoa {cpf: $cpf_destino})-[r:AMIGO_DE]->(a:Pessoa {cpf: $cpf_origem})
            DELETE r
        """, cpf_origem=cpf_origem, cpf_destino=cpf_destino)
    _invalidate("clientesAmigos", "amigoClienteRecomendacao")
