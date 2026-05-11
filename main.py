
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging
from db.redis import redis_client
from db.postgres import pg_conn

# Configuração básica de log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chaves utilizadas no Redis
REDIS_LIST_KEY = "voos_em_curso"
REDIS_HASH_PREFIX = "voo:"

def buscar_voos_ativos():
    consulta = """
    SELECT
        v.id,
        v.codigo_voo,
        orig.codigo AS origem,
        dest.codigo AS destino,
        v.saida_prevista,
        v.chegada_prevista,
        v.status,
        pv.percentual_concluido,
        pv.chegada_prevista_atualizada,
        pv.latitude,
        pv.longitude
    FROM voos v
    JOIN aeroportos orig ON v.aeroporto_origem_id = orig.id
    JOIN aeroportos dest ON v.aeroporto_destino_id = dest.id
    LEFT JOIN posicao_voo pv ON v.id = pv.voo_id
    WHERE v.status = 'EM_CURSO'
    ORDER BY v.id;
    """
    with pg_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(consulta)
        return cur.fetchall()

def atualizar_cache_redis(dados_voos):

    redis_client.delete(REDIS_LIST_KEY)

    for voo in dados_voos:
        voo_id = voo["id"]
        # Adiciona o ID do voo à lista de em curso
        redis_client.rpush(REDIS_LIST_KEY, voo_id)

        # Cria um hash com os dados resumidos do voo
        chave = f"{REDIS_HASH_PREFIX}{voo_id}"
        mapeamento = {
            "codigo_voo": voo["codigo_voo"],
            "origem": voo["origem"],
            "destino": voo["destino"],
            "saida_prevista": voo["saida_prevista"].isoformat()
                if isinstance(voo["saida_prevista"], datetime)
                else str(voo["saida_prevista"]),
            "chegada_prevista": voo["chegada_prevista"].isoformat()
                if isinstance(voo["chegada_prevista"], datetime)
                else str(voo["chegada_prevista"]),
            "status": voo["status"],
            "percentual_concluido": str(voo["percentual_concluido"])
                if voo["percentual_concluido"] is not None else "",
            "chegada_prevista_atualizada": voo["chegada_prevista_atualizada"].isoformat()
                if isinstance(voo.get("chegada_prevista_atualizada"), datetime)
                else str(voo.get("chegada_prevista_atualizada", "")),
            "latitude": str(voo["latitude"]) if voo["latitude"] is not None else "",
            "longitude": str(voo["longitude"]) if voo["longitude"] is not None else "",
            "ultima_atualizacao": datetime.now().isoformat()
        }
        redis_client.hset(chave, mapping=mapeamento)

    # Armazena metadados sobre o cache
    redis_client.hset("cache_metadados", mapping={
        "quantidade_voos": len(dados_voos),
        "atualizado_em": datetime.now().isoformat()
    })

    logger.info(f"Cache atualizado com {len(dados_voos)} voos em curso.")


def consultar_cache_redis():
    ids_voos = redis_client.lrange(REDIS_LIST_KEY, 0, -1)

    for voo_id in ids_voos:
        chave = f"{REDIS_HASH_PREFIX}{voo_id}"

        dados_voo = redis_client.hgetall(chave)

        print(f"\n{chave}")
        print(dados_voo)

    metadados = redis_client.hgetall("cache_metadados")

    print("\n=== METADADOS ===")
    print(metadados)

def main():
    try:
        voos_ativos = buscar_voos_ativos()
        pg_conn.close()

        atualizar_cache_redis(voos_ativos)

        consultar_cache_redis()
    except Exception as erro:
        logger.error(f"Erro na atualização do cache: {erro}", exc_info=True)

if __name__ == "__main__":
    main()