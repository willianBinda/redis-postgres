from db.redis import redis_client
from db.postgres import pg_conn

def buscar_voos_em_curso():
    cursor = pg_conn.cursor()

    query = """
        SELECT
            id,
            codigo_voo,
            status,
            aeroporto_origem,
            aeroporto_destino
        FROM voos
        WHERE status = 'EM_CURSO'
    """

    cursor.execute(query)

    colunas = [desc[0] for desc in cursor.description]
    resultados = cursor.fetchall()

    cursor.close()

    voos = []

    for row in resultados:
        voo = dict(zip(colunas, row))
        voos.append(voo)

    return voos


def salvar_voos_redis(voos):
    # limpa lista antiga
    redis_client.delete("voos_em_curso")

    for voo in voos:
        voo_id = voo["id"]

        # salva hash individual
        redis_client.hset(
            f"voo:{voo_id}",
            mapping={
                "codigo_voo": voo["codigo_voo"],
                "status": voo["status"],
                "origem": voo["aeroporto_origem"],
                "destino": voo["aeroporto_destino"]
            }
        )

        # adiciona à lista de voos ativos
        redis_client.rpush("voos_em_curso", voo_id)


def executar():
    print("Consultando PostgreSQL...")

    voos = buscar_voos_em_curso()

    print(f"{len(voos)} voos encontrados")

    print("Atualizando Redis...")

    salvar_voos_redis(voos)

    print("Sincronização concluída")